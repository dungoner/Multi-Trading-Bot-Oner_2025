#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECEIVER SERVER (BOT 2/3/...) - PULL MODE
==========================================
Chức năng: TỰ ĐỘNG PULL dữ liệu từ Bot 1 (VPS) và ghi local files
Mode: PULL (Bot 2 chủ động lấy từ Bot 1 mỗi 1 giây)
Port: 9070 (Dashboard only - không cần API port 8888 nữa)
Output: C:/PRO_ONER/MQL4/Files/DataAutoOner3/{SYMBOL}_LIVE.json

LUỒNG HOẠT ĐỘNG:
1. Bot 2 polling: GET http://BOT1_URL/api/csdl/SYMBOL_LIVE.json (mỗi 1s)
2. Nhận data (7 rows) từ Bot 1
3. Ghi file local: C:/PRO_ONER/MQL4/Files/DataAutoOner3/SYMBOL_LIVE.json
4. EA đọc file local (không có network call)

ƯU ĐIỂM:
- Bot 2 bật lên ở BẤT KỲ MỖI MẠNG NÀO đều hoạt động (không cần Port Forwarding)
- Bot 1 KHÔNG CẦN BIẾT địa chỉ Bot 2
- Dễ scale: Chạy 10 Bot 2 cùng lúc, mỗi máy khác mạng

Author: ONER Trading System
Version: 2.0 (PULL MODE)
"""

import os
import sys
import json
import time
import threading
import requests
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ============================================
# SECTION 1: GLOBAL CONFIGURATION
# ============================================

# Load unified bot_config.json
BOT_CONFIG_FILE = "bot_config.json"

def load_bot_config():
    """Load unified bot_config.json"""
    if not os.path.exists(BOT_CONFIG_FILE):
        print(f"❌ ERROR: Config file not found: {BOT_CONFIG_FILE}")
        print("Please create bot_config.json or run Bot 3 to generate it.")
        sys.exit(1)

    try:
        with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Cannot load {BOT_CONFIG_FILE}: {e}")
        sys.exit(1)

# Load config
bot_config = load_bot_config()

# Extract receiver config with fallback defaults
RECEIVER_CONFIG = bot_config.get('receiver', {
    "bot1_url": "",
    "polling_interval": 1,
    "output_folder": "C:/PRO_ONER/MQL4/Files/DataAutoOner3/",
    "output_folder2": "C:/PRO_ONER/MQL4/Files/DataAutoOner2/",
    "dashboard_port": 9070,
    "http_timeout": 5,
})

# Auto-detect symbols (populated at runtime from Bot 1)
RECEIVER_CONFIG["symbols"] = []

# QUIET MODE support (reduce console spam for VPS 24/7)
QUIET_MODE = bot_config.get('quiet_mode', False)

# Global state tracking
receiver_state = {
    "bot1_status": "unknown",  # "online" / "offline" / "unknown"
    "last_bot1_contact": 0,
    "total_data_received": 0,
    "total_files_written": 0,
    "total_errors": 0,
    "last_data_symbol": "",
    "last_data_time": 0,
    "symbols_received": {},  # {symbol: {count, last_update, last_mtime}}
}

# Health check: Track last error log time per symbol (1h interval)
# Giống EA: CheckSPYBotHealth (8h/16h), nhưng ở đây 1h/lần
error_log_tracker = {}  # {symbol: {"last_log_time": timestamp, "error_count": count}}

# Flask app (Dashboard only)
app_dashboard = Flask(__name__)
CORS(app_dashboard)

# ==============================================================================
# ADVANCED LOG SUPPRESSION (Reduce CMD spam)
# ==============================================================================
# Suppress Flask development server request logs
log = logging.getLogger('werkzeug')

# ✅ CUSTOM FILTER: Suppress slow client warnings and scanner spam
# IMPORTANT: These are NOT errors - just network slowness warnings
class SmartLogFilter(logging.Filter):
    def filter(self, record):
        """Filter out spam logs while keeping real errors

        SUPPRESS: ⏱️ Slow client warnings, 🤖 Scanner bots (KHÔNG phải lỗi)
        KEEP: ❌ Real errors (500, crashes, etc.)
        """
        quiet = bot_config.get('quiet_mode', False)
        if not quiet:
            return True

        msg = record.getMessage()
        # ⏱️ SUPPRESS: Slow client warning (client chậm, KHÔNG phải lỗi)
        if 'TimeoutError' in msg or 'Request timed out' in msg:
            return False  # SUPPRESS (chỉ là cảnh báo client chậm)
        # 🤖 SUPPRESS: Scanner bots (KHÔNG phải EA/Bot2)
        if 'code 400' in msg or 'Bad request syntax' in msg or 'Bad request version' in msg:
            return False  # SUPPRESS (chỉ là bot quét, không phải lỗi)
        return True  # ✅ KEEP: Real errors

log.addFilter(SmartLogFilter())
log.setLevel(logging.ERROR)  # Only show errors, not every request

# ============================================
# SECTION 2: HELPER FUNCTIONS
# ============================================

def ensure_folders():
    """Create output folders if not exist | Tao cac thu muc output neu chua ton tai"""
    folders = [
        RECEIVER_CONFIG["output_folder"],   # Folder 3 (DataAutoOner3)
        RECEIVER_CONFIG["output_folder2"]   # Folder 2 (DataAutoOner2)
    ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[INIT] Created folder: {folder}")

def write_atomic(filepath, content):
    """Atomic file write: write to .tmp then rename

    Purpose: Tránh EA đọc file incomplete khi đang ghi

    Args:
        filepath: Full path to target file
        content: String content to write

    Returns:
        bool: True if success, False if error
    """
    try:
        tmp_filepath = filepath + ".tmp"

        # Write to temp file
        with open(tmp_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Rename (atomic operation on Windows)
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rename(tmp_filepath, filepath)

        return True
    except Exception as e:
        print(f"[ERROR] write_atomic failed: {e}")
        return False

def set_file_mtime(filepath, mtime):
    """Set file modification time to match Bot 1's mtime

    Purpose: Đồng bộ timestamp giữa Bot 1 và Bot 2

    Args:
        filepath: Full path to file
        mtime: Unix timestamp (int or float)
    """
    try:
        os.utime(filepath, (mtime, mtime))
    except Exception as e:
        print(f"[WARN] Cannot set mtime: {e}")

def fetch_symbols_from_bot1():
    """Fetch list of all available symbols from Bot 1 | Lay danh sach tat ca symbols tu Bot 1

    AUTO-DETECT MODE:
    - Goi API Bot 1: GET /api/symbols
    - Nhan danh sach TAT CA symbols hien co
    - Cap nhat vao RECEIVER_CONFIG["symbols"]

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        url = f"{RECEIVER_CONFIG['bot1_url']}/api/symbols"
        response = requests.get(url, timeout=RECEIVER_CONFIG["http_timeout"])

        if response.status_code == 200:
            data = response.json()
            symbols = data.get("symbols", [])

            if symbols:
                RECEIVER_CONFIG["symbols"] = symbols
                log_message("INFO", f"AUTO-DETECT: Found {len(symbols)} symbols from Bot 1")
                log_message("INFO", f"Symbols: {', '.join(symbols)}")
                return True
            else:
                log_message("ERROR", "Bot 1 returned empty symbol list")
                return False
        else:
            log_message("ERROR", f"Failed to fetch symbols: HTTP {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        log_message("ERROR", "Timeout while fetching symbols from Bot 1")
        return False
    except requests.exceptions.ConnectionError:
        log_message("ERROR", "Connection error: Bot 1 offline or wrong URL")
        return False
    except Exception as e:
        log_message("ERROR", f"fetch_symbols_from_bot1 failed: {e}")
        return False

def format_timestamp(ts):
    """Format Unix timestamp to readable string"""
    if ts == 0:
        return "Never"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def should_log_error(symbol, error_type="timeout"):
    """Check if error should be logged (1h interval health check)

    Similar to EA's CheckSPYBotHealth (8h/16h), but 1h interval here.
    Purpose: Reduce log spam for transient network errors.

    Args:
        symbol: Symbol name (e.g. "BTCUSD")
        error_type: Error type (e.g. "timeout", "connection")

    Returns:
        bool: True if should log (>= 1h since last log), False otherwise
    """
    current_time = time.time()
    tracker_key = f"{symbol}_{error_type}"

    if tracker_key not in error_log_tracker:
        # First error for this symbol/type → Log immediately
        error_log_tracker[tracker_key] = {
            "last_log_time": current_time,
            "error_count": 1
        }
        return True

    # Check time since last log
    last_log_time = error_log_tracker[tracker_key]["last_log_time"]
    time_since_last_log = current_time - last_log_time

    # Increment error count (always track, even if not logging)
    error_log_tracker[tracker_key]["error_count"] += 1

    # Log if >= 1 hour (3600 seconds) since last log
    if time_since_last_log >= 3600:
        error_log_tracker[tracker_key]["last_log_time"] = current_time
        error_count = error_log_tracker[tracker_key]["error_count"]

        # Include error count in decision (will be printed by caller)
        return True

    return False

def log_message(level, message):
    """Write log to console only (file writing removed for simplification)

    Args:
        level: "INFO", "WARN", "ERROR"
        message: Log message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"

    # QUIET MODE support
    if QUIET_MODE:
        if level in ["ERROR", "WARN"]:
            print(log_line)
        # INFO is silent in QUIET mode
    else:
        print(log_line)  # Normal mode: print all

# ============================================
# SECTION 3: PULL MODE - POLLING BOT 1
# ============================================

def poll_bot1():
    """Background thread: PULL data from Bot 1 every N seconds

    PULL MODE:
    - Bot 2 chủ động GỌI API Bot 1 mỗi 1 giây
    - Nhận data (7 rows) và ghi file local
    - Bot 1 KHÔNG CẦN BIẾT địa chỉ Bot 2

    AUTO-DETECT MODE:
    - Mỗi 60 giây, refresh danh sách symbols từ Bot 1
    - Tự động sync các symbols mới mà không cần restart
    """
    # Startup logs (1-time only) - ALWAYS show, not affected by quiet mode
    print(f"[POLLING] Started PULL mode (interval: {RECEIVER_CONFIG['polling_interval']}s)")
    print(f"[POLLING] Bot 1 URL: {RECEIVER_CONFIG['bot1_url']}")
    print(f"[POLLING] Symbols: {', '.join(RECEIVER_CONFIG['symbols'])}")

    last_summary_time = time.time()
    last_symbol_refresh = time.time()  # AUTO-DETECT: Track last refresh time
    refresh_interval = 60  # AUTO-DETECT: Refresh symbols every 60 seconds
    symbols_updated_last_60s = []

    while True:
        try:
            # AUTO-DETECT: Refresh symbols every 60s
            current_time = time.time()
            if current_time - last_symbol_refresh >= refresh_interval:
                log_message("INFO", f"[AUTO-DETECT] Refreshing symbol list from Bot 1...")
                if fetch_symbols_from_bot1():
                    log_message("INFO", f"[AUTO-DETECT] Symbol list updated: {len(RECEIVER_CONFIG['symbols'])} symbols")
                last_symbol_refresh = current_time

            # Loop through AUTO-DETECTED symbols
            for symbol in RECEIVER_CONFIG["symbols"]:
                try:
                    # Call Bot 1 API
                    url = f"{RECEIVER_CONFIG['bot1_url']}/api/csdl/{symbol}_LIVE.json"
                    response = requests.get(
                        url,
                        timeout=RECEIVER_CONFIG["http_timeout"]
                    )

                    if response.status_code == 200:
                        # Parse JSON response
                        json_response = response.json()

                        # Extract data
                        data = json_response.get("data", [])
                        mtime = json_response.get("mtime", 0)

                        # Validate data (must be 7 rows for 7 timeframes)
                        if not isinstance(data, list) or len(data) < 7:
                            log_message("ERROR", f"Invalid data from Bot 1: {symbol} (expected 7 rows, got {len(data) if isinstance(data, list) else 'non-array'})")
                            continue

                        # Check if data changed (compare mtime)
                        last_mtime = receiver_state["symbols_received"].get(symbol, {}).get("last_mtime", 0)

                        if mtime > last_mtime:
                            # Data changed! Write to BOTH folders | Du lieu moi! Ghi vao CA 2 thu muc

                            # ✅ CRITICAL: sort_keys=False to preserve column order | giu nguyen thu tu cot
                            file_content = json.dumps(data, indent=2, sort_keys=False)

                            # Define output files for BOTH folders
                            output_file3 = os.path.join(
                                RECEIVER_CONFIG["output_folder"],   # Folder 3
                                f"{symbol}_LIVE.json"
                            )
                            output_file2 = os.path.join(
                                RECEIVER_CONFIG["output_folder2"],  # Folder 2
                                f"{symbol}_LIVE.json"
                            )

                            # Write to Folder 3 (main)
                            success3 = write_atomic(output_file3, file_content)
                            if success3:
                                set_file_mtime(output_file3, mtime)

                            # Write to Folder 2 (backup)
                            success2 = write_atomic(output_file2, file_content)
                            if success2:
                                set_file_mtime(output_file2, mtime)

                            # Update state if at least one write succeeded
                            if success3 or success2:
                                receiver_state["total_data_received"] += 1
                                receiver_state["total_files_written"] += 1  # Count as 1 update (even if 2 files)
                                receiver_state["last_data_symbol"] = symbol
                                receiver_state["last_data_time"] = int(time.time())
                                receiver_state["bot1_status"] = "online"
                                receiver_state["last_bot1_contact"] = int(time.time())

                                # Track per-symbol stats
                                if symbol not in receiver_state["symbols_received"]:
                                    receiver_state["symbols_received"][symbol] = {"count": 0, "last_update": 0, "last_mtime": 0}
                                receiver_state["symbols_received"][symbol]["count"] += 1
                                receiver_state["symbols_received"][symbol]["last_update"] = int(time.time())
                                receiver_state["symbols_received"][symbol]["last_mtime"] = mtime

                                # Track for summary log
                                symbols_updated_last_60s.append(symbol)

                                # Log result
                                if success3 and success2:
                                    log_message("INFO", f"PULL: {symbol} updated → Folder2 + Folder3 (mtime={mtime})")
                                elif success3:
                                    log_message("WARN", f"PULL: {symbol} updated → Folder3 only (Folder2 failed)")
                                elif success2:
                                    log_message("WARN", f"PULL: {symbol} updated → Folder2 only (Folder3 failed)")
                            else:
                                receiver_state["total_errors"] += 1
                                log_message("ERROR", f"Failed to write file: {symbol} (both folders failed)")
                        else:
                            # Data not changed, skip (silent)
                            receiver_state["bot1_status"] = "online"
                            receiver_state["last_bot1_contact"] = int(time.time())

                    else:
                        receiver_state["total_errors"] += 1

                        # Health check: Only log every 1 hour (3600s) to reduce spam
                        if should_log_error(symbol, f"http_{response.status_code}"):
                            error_count = error_log_tracker.get(f"{symbol}_http_{response.status_code}", {}).get("error_count", 0)
                            log_message("ERROR", f"Bot 1 API error: {symbol} (HTTP {response.status_code}) (errors in last 1h: {error_count})")

                except requests.exceptions.Timeout:
                    receiver_state["total_errors"] += 1
                    receiver_state["bot1_status"] = "offline"

                    # Health check: Only log every 1 hour (3600s) to reduce spam
                    if should_log_error(symbol, "timeout"):
                        error_count = error_log_tracker.get(f"{symbol}_timeout", {}).get("error_count", 0)
                        log_message("ERROR", f"Timeout pulling {symbol} from Bot 1 (errors in last 1h: {error_count})")

                except requests.exceptions.ConnectionError:
                    receiver_state["total_errors"] += 1
                    receiver_state["bot1_status"] = "offline"

                    # Health check: Only log every 1 hour (3600s) to reduce spam
                    if should_log_error(symbol, "connection"):
                        error_count = error_log_tracker.get(f"{symbol}_connection", {}).get("error_count", 0)
                        log_message("ERROR", f"Connection error to Bot 1 (pulling {symbol}) (errors in last 1h: {error_count})")

                except Exception as e:
                    receiver_state["total_errors"] += 1
                    log_message("ERROR", f"Failed to pull {symbol}: {e}")

            # Log summary every 60 seconds
            now = time.time()
            if now - last_summary_time >= 60:
                if symbols_updated_last_60s:
                    unique_symbols = set(symbols_updated_last_60s)
                    log_message("INFO", f"[POLLING] Last 60s: Updated {len(symbols_updated_last_60s)} times ({len(unique_symbols)} symbols: {', '.join(sorted(unique_symbols))})")
                    symbols_updated_last_60s = []
                last_summary_time = now

            # Sleep before next poll
            time.sleep(RECEIVER_CONFIG["polling_interval"])

        except Exception as e:
            log_message("ERROR", f"Polling thread error: {e}")
            time.sleep(RECEIVER_CONFIG["polling_interval"])

# ============================================
# SECTION 4: DASHBOARD PAGE (Port 9070)
# ============================================

@app_dashboard.route('/')
def dashboard_home():
    """Dashboard page showing receiver status"""

    now = int(time.time())
    bot1_contact_age = now - receiver_state["last_bot1_contact"]
    bot1_status = receiver_state["bot1_status"]
    bot1_color = "#00A651" if bot1_status == "online" else "#FF5722"

    # Build symbols table
    symbols_rows = ""
    for symbol, stats in sorted(receiver_state["symbols_received"].items()):
        age = now - stats["last_update"]
        symbols_rows += f"""
        <tr>
            <td>{symbol}</td>
            <td>{stats['count']}</td>
            <td>{format_timestamp(stats['last_update'])}</td>
            <td>{age}s ago</td>
        </tr>
        """

    if not symbols_rows:
        symbols_rows = "<tr><td colspan='4' style='text-align:center; color:#999;'>No data received yet</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot 2 Receiver Dashboard (PULL MODE)</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
            .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                           color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
            .panel-body {{ padding: 20px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }}
            .stat-box {{ border: 1px solid #e0e0e0; padding: 15px; text-align: center; }}
            .stat-label {{ font-size: 10px; text-transform: uppercase; color: #999; letter-spacing: 1px; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #2c2c2c; margin-top: 5px; }}
            .bot1-box {{ border: 2px solid {bot1_color}; background: {bot1_color}15; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; font-size: 12px; }}
            th {{ background: #f5f5f5; font-weight: bold; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
            .info-label {{ color: #666; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
            .info-value {{ font-weight: bold; color: #2c2c2c; }}
            .status-online {{ color: #00A651; }}
            .status-offline {{ color: #FF5722; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel">
                <div class="panel-header">📡 BOT 2 RECEIVER (PULL MODE) — Status Dashboard</div>
                <div class="panel-body">
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-label">Data Received</div>
                            <div class="stat-value">{receiver_state['total_data_received']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Files Written</div>
                            <div class="stat-value">{receiver_state['total_files_written']}</div>
                        </div>
                        <div class="stat-box bot1-box">
                            <div class="stat-label">Bot 1 Status</div>
                            <div class="stat-value" style="color: {bot1_color};">{bot1_status.upper()}</div>
                            <div style="font-size: 10px; color: #666; margin-top: 5px;">{bot1_contact_age}s ago</div>
                        </div>
                    </div>

                    <div class="info-row">
                        <span class="info-label">Bot 1 URL</span>
                        <span class="info-value">{RECEIVER_CONFIG['bot1_url']}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Last Bot 1 Contact</span>
                        <span class="info-value">{format_timestamp(receiver_state['last_bot1_contact'])}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Last Data Received</span>
                        <span class="info-value">{receiver_state['last_data_symbol']} at {format_timestamp(receiver_state['last_data_time'])}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Total Errors</span>
                        <span class="info-value">{receiver_state['total_errors']}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Output Folder</span>
                        <span class="info-value">{RECEIVER_CONFIG['output_folder']}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Polling Interval</span>
                        <span class="info-value">{RECEIVER_CONFIG['polling_interval']} second(s)</span>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">📊 Symbols Received</div>
                <div class="panel-body">
                    <table>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Count</th>
                                <th>Last Update</th>
                                <th>Age</th>
                            </tr>
                        </thead>
                        <tbody>
                            {symbols_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #999; font-size: 11px;">
                Mode: PULL (Bot 2 chủ động lấy từ Bot 1) | Auto-refresh every 5 seconds | Dashboard Port: {RECEIVER_CONFIG['dashboard_port']}
            </div>
        </div>
    </body>
    </html>
    """

    return html

# ============================================
# SECTION 5: MAIN SERVER START
# ============================================

def run_dashboard_server():
    """Run Dashboard server on Port 9070"""
    print(f"[DASHBOARD] Starting on port {RECEIVER_CONFIG['dashboard_port']}...")
    app_dashboard.run(
        host='0.0.0.0',
        port=RECEIVER_CONFIG['dashboard_port'],
        debug=False,
        threaded=True
    )

if __name__ == "__main__":
    print("=" * 60)
    print("RECEIVER SERVER (BOT 2/3/...) - PULL MODE (DUAL FOLDERS)")
    print("=" * 60)
    print(f"Bot 1 URL: {RECEIVER_CONFIG['bot1_url']}")
    print(f"Dashboard Port: {RECEIVER_CONFIG['dashboard_port']}")
    print(f"Output Folder 3: {RECEIVER_CONFIG['output_folder']}")
    print(f"Output Folder 2: {RECEIVER_CONFIG['output_folder2']}")
    print(f"Polling Interval: {RECEIVER_CONFIG['polling_interval']} second(s)")
    print("=" * 60)

    # Ensure folders exist
    ensure_folders()

    # AUTO-DETECT: Fetch symbols from Bot 1 BEFORE starting polling
    print("\n[INIT] Fetching symbols from Bot 1...")
    if not fetch_symbols_from_bot1():
        print("\n⚠️  WARNING: Cannot fetch symbols from Bot 1 at startup.")
        print(f"  Bot 1 URL: {RECEIVER_CONFIG['bot1_url']}")
        print(f"  Dashboard will start anyway - Polling thread will retry connection.")
        print(f"  Please check Bot 1 is running on Port 80.")
    else:
        print(f"✅ Found {len(RECEIVER_CONFIG['symbols'])} symbols: {', '.join(RECEIVER_CONFIG['symbols'])}")
    print("=" * 60)

    # Start polling thread
    polling_thread = threading.Thread(target=poll_bot1, daemon=True)
    polling_thread.start()

    # Start dashboard server
    dashboard_thread = threading.Thread(target=run_dashboard_server, daemon=True)
    dashboard_thread.start()

    print("\n✅ Bot 2 started in PULL MODE!")
    print(f"📊 Dashboard: http://localhost:{RECEIVER_CONFIG['dashboard_port']}/")
    print(f"🔄 Polling Bot 1 every {RECEIVER_CONFIG['polling_interval']}s")
    print("\nPress Ctrl+C to stop...\n")

    log_message("INFO", "Receiver Bot 2 started successfully (PULL MODE)")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        log_message("INFO", "Receiver Bot 2 stopped by user")
        sys.exit(0)

