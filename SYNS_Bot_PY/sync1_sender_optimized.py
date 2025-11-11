#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNS API Server - Dual Port Flask Server
Port 80: API for MT4 EA (CSDL data) - MT4 WebRequest only supports port 80/443
Port 9070: Dashboard for monitoring (Japanese Minimalist Style)

Author: Claude
Date: 2025-10-18
Version: 1.2 (Improved: Reduced log spam, Ctrl+C protection, Weekly auto-restart)
"""

from flask import Flask, jsonify, request, render_template_string, Response
import json
from collections import OrderedDict  # Preserve JSON key order
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from threading import Thread, Lock
import glob
import logging
import ctypes

# ==============================================================================
# AUTO REQUEST ADMIN PRIVILEGES (Windows Only)
# ==============================================================================

def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """Request administrator privileges and restart"""
    if sys.platform == 'win32' and not is_admin():
        print("=" * 60)
        print("⚠️  ADMINISTRATOR PRIVILEGES REQUIRED")
        print("=" * 60)
        print("This server needs admin rights to create symbolic links.")
        print("Requesting administrator privileges...")
        print("=" * 60)

        # Re-run the program with admin rights
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )
            sys.exit(0)
        except:
            print("❌ Failed to request admin privileges.")
            print("Please run this script as Administrator manually.")
            input("Press Enter to exit...")
            sys.exit(1)

# ==============================================================================
# LOAD CONFIG FIRST (needed for SmartLogFilter)
# ==============================================================================
# Need to load bot_config.json early to check quiet_mode
# This is a temporary load - will be reloaded later at line 280
import json as json_temp
BOT_CONFIG_FILE_TEMP = "bot_config.json"
try:
    if os.path.exists(BOT_CONFIG_FILE_TEMP):
        with open(BOT_CONFIG_FILE_TEMP, 'r', encoding='utf-8') as f:
            bot_config_temp = json_temp.load(f)
    else:
        bot_config_temp = {"quiet_mode": False}
except:
    bot_config_temp = {"quiet_mode": False}

# ==============================================================================
# ADVANCED LOG SUPPRESSION (Reduce CMD spam while keeping important errors)
# ==============================================================================
# Suppress Flask development server request logs
log = logging.getLogger('werkzeug')

# ✅ CUSTOM FILTER: Suppress slow client warnings and scanner spam
# IMPORTANT: These are NOT errors - just network slowness warnings
class SmartLogFilter(logging.Filter):
    def filter(self, record):
        """Filter out spam logs while keeping real errors

        SUPPRESS (when QUIET_MODE=ON):
        - ⏱️ TimeoutError: SLOW CLIENT warning (client kết nối chậm, KHÔNG phải lỗi server)
        - 🤖 Bad request: Scanner bots (bot quét tự động, KHÔNG phải EA của bạn)

        KEEP (always show):
        - ❌ 500 Internal Server Error (lỗi thật trong code)
        - ❌ Connection errors (lỗi kết nối server)
        - ❌ Other critical errors (lỗi nghiêm trọng khác)
        """
        # Get quiet_mode from temp config
        quiet = bot_config_temp.get('quiet_mode', False)

        if not quiet:
            return True  # Normal mode: show all logs

        # QUIET MODE: Filter spam logs
        msg = record.getMessage()

        # ⏱️ SUPPRESS: Slow client warning (client chậm, KHÔNG phải lỗi)
        if 'TimeoutError' in msg or 'Request timed out' in msg:
            return False  # SUPPRESS (chỉ là cảnh báo client chậm)

        # 🤖 SUPPRESS: Scanner bots (bot quét port 80, KHÔNG phải EA/Bot2)
        if 'code 400' in msg or 'Bad request syntax' in msg or 'Bad request version' in msg:
            return False  # SUPPRESS (chỉ là bot quét, không phải lỗi)

        # ✅ KEEP: Real errors (500, crashes, etc.)
        return True

log.addFilter(SmartLogFilter())
log.setLevel(logging.ERROR)  # Only show errors, not every request

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Unified config file
BOT_CONFIG_FILE = "bot_config.json"
# Legacy config files (for migration)
CONFIG_FILE = "config.json"
SYMLINK_CONFIG_FILE = "symlink_config.json"
AUTOSTART_CONFIG_FILE = "autostart_config.json"

def create_default_bot_config():
    """Create default unified bot configuration"""
    return {
        "quiet_mode": False,
        "sender": {
            "api_key": "9016",
            "vps_ip": "147.189.173.121",
            "api_port": 80,
            "dashboard_port": 9070,
            "server_ip": "0.0.0.0",
            "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/",
            "history_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/",
            "polling_interval": 1,
            "log_history_limit": 50,
            "stats_retention_days": 7,
            "stats_save_interval": 3600,
            "server_timezone_offset": 2,
            "vietnam_timezone_offset": 7
        },
        "symlink": {
            "source_folders": {
                "files": "E:/PRO_ONER/MQL4/Files",
                "presets": "E:/PRO_ONER/MQL4/Presets",
                "data_oner": "E:/PRO_ONER/MQL4/Data Oner"
            },
            "target_folders": ["Files", "Presets", "Data Oner"],
            "mt_platforms": []
        },
        "autostart": {
            "bot_folder": os.path.dirname(os.path.abspath(__file__)),
            "start_script": "START_SERVER.bat",
            "task_name": "SYNS_Bot_AutoStart",
            "mt_platforms": []
        }
    }

def migrate_to_unified_config():
    """Migrate from 3 separate config files to unified bot_config.json"""
    print("[CONFIG] Migrating from legacy config files to unified bot_config.json...")

    bot_config = create_default_bot_config()
    migrated = False

    # Migrate server config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
                bot_config['sender'] = old_config
                # Remove _note field if it exists
                bot_config['sender'].pop('_note', None)
                print(f"[CONFIG] Migrated sender config from {CONFIG_FILE}")
                migrated = True
        except Exception as e:
            print(f"[CONFIG] Error migrating {CONFIG_FILE}: {e}")

    # Migrate symlink config
    if os.path.exists(SYMLINK_CONFIG_FILE):
        try:
            with open(SYMLINK_CONFIG_FILE, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
                bot_config['symlink'] = old_config
                print(f"[CONFIG] Migrated symlink config from {SYMLINK_CONFIG_FILE}")
                migrated = True
        except Exception as e:
            print(f"[CONFIG] Error migrating {SYMLINK_CONFIG_FILE}: {e}")

    # Migrate autostart config
    if os.path.exists(AUTOSTART_CONFIG_FILE):
        try:
            with open(AUTOSTART_CONFIG_FILE, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
                # Handle old mt4_mt5_platforms migration
                if 'mt4_mt5_platforms' in old_config and 'mt_platforms' not in old_config:
                    old_config['mt_platforms'] = []
                    for platform in old_config.get('mt4_mt5_platforms', []):
                        if platform.get('enabled') and platform.get('path'):
                            old_config['mt_platforms'].append({
                                "path": platform.get('path'),
                                "task_name": platform.get('task_name')
                            })
                    del old_config['mt4_mt5_platforms']
                # Ensure mt_platforms exists
                if 'mt_platforms' not in old_config:
                    old_config['mt_platforms'] = []
                # Remove extra fields that might exist
                old_config.pop('restart_on_failure', None)
                old_config.pop('restart_interval_minutes', None)
                old_config.pop('restart_attempts', None)
                bot_config['autostart'] = old_config
                print(f"[CONFIG] Migrated autostart config from {AUTOSTART_CONFIG_FILE}")
                migrated = True
        except Exception as e:
            print(f"[CONFIG] Error migrating {AUTOSTART_CONFIG_FILE}: {e}")

    # Save unified config
    if migrated:
        try:
            with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(bot_config, f, indent=2, ensure_ascii=False)
            print(f"[CONFIG] Created unified config: {BOT_CONFIG_FILE}")

            # Backup old files
            for old_file in [CONFIG_FILE, SYMLINK_CONFIG_FILE, AUTOSTART_CONFIG_FILE]:
                if os.path.exists(old_file):
                    backup_file = old_file + '.bak'
                    try:
                        import shutil
                        shutil.copy2(old_file, backup_file)
                        print(f"[CONFIG] Backed up {old_file} to {backup_file}")
                    except Exception as e:
                        print(f"[CONFIG] Warning: Could not backup {old_file}: {e}")
        except Exception as e:
            print(f"[CONFIG] Error saving unified config: {e}")

    return bot_config

def load_bot_config():
    """Load unified bot_config.json with automatic migration"""
    # Check if unified config exists
    if not os.path.exists(BOT_CONFIG_FILE):
        # Check if old files exist - migrate them
        if os.path.exists(CONFIG_FILE) or os.path.exists(SYMLINK_CONFIG_FILE) or os.path.exists(AUTOSTART_CONFIG_FILE):
            return migrate_to_unified_config()
        else:
            # Create new default config
            print("[CONFIG] Creating default bot_config.json...")
            bot_config = create_default_bot_config()
            try:
                with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(bot_config, f, indent=2, ensure_ascii=False)
                print(f"[CONFIG] Created default config: {BOT_CONFIG_FILE}")
            except Exception as e:
                print(f"[CONFIG] Error creating default config: {e}")
            return bot_config

    # Load existing unified config
    try:
        with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            bot_config = json.load(f)

            # Validate structure - ensure all sections exist
            default_config = create_default_bot_config()
            if 'sender' not in bot_config:
                bot_config['sender'] = default_config['sender']
            if 'symlink' not in bot_config:
                bot_config['symlink'] = default_config['symlink']
            if 'autostart' not in bot_config:
                bot_config['autostart'] = default_config['autostart']

            return bot_config
    except Exception as e:
        print(f"[CONFIG] Error loading {BOT_CONFIG_FILE}: {e}")
        # Fallback to old files if unified config is corrupted
        if os.path.exists(CONFIG_FILE) or os.path.exists(SYMLINK_CONFIG_FILE) or os.path.exists(AUTOSTART_CONFIG_FILE):
            print("[CONFIG] Falling back to legacy config files...")
            return migrate_to_unified_config()
        else:
            print("[CONFIG] Using default config...")
            return create_default_bot_config()

def save_bot_config(bot_config):
    """Save unified bot configuration"""
    try:
        with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(bot_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[CONFIG] Error saving {BOT_CONFIG_FILE}: {e}")
        return False

def load_config():
    """Load server configuration (backward compatible wrapper)"""
    bot_config = load_bot_config()
    return bot_config.get('sender', {})

def save_config(new_config):
    """Save server configuration while preserving other sections"""
    try:
        # Load current bot config
        bot_config = load_bot_config()

        # Update only the sender section
        bot_config['sender'] = new_config

        # Save unified config
        return save_bot_config(bot_config)
    except Exception as e:
        print(f"[CONFIG] Error saving sender config: {e}")
        return False

def reload_config():
    """Reload configuration from file"""
    global config
    config = load_config()
    print(f"[CONFIG] Configuration reloaded")

# ==============================================================================
# LOAD CONFIG ONCE AT STARTUP (Optimization)
# ==============================================================================
# Load unified bot_config.json ONCE at startup
bot_config = load_bot_config()

# Extract sender config from bot_config
config = bot_config.get('sender', {})

# ==============================================================================
# QUIET MODE LOGGING (Reduce console spam for VPS 24/7)
# ==============================================================================

# Use global bot_config (already loaded above)
QUIET_MODE = bot_config.get('quiet_mode', False)

def log_print(message, level="INFO"):
    """Print log with QUIET mode support

    Args:
        message: Log message
        level: "INFO", "WARN", "ERROR"

    QUIET MODE:
        - INFO: Silent when quiet_mode=ON (spam logs like 60s summary)
        - WARN/ERROR: Always print (important messages)

    NOTE: Startup logs (1-time banners) use print() directly, not this function.
    """
    if QUIET_MODE:
        if level in ["ERROR", "WARN"]:
            print(message)
        # INFO is silent in QUIET mode
    else:
        print(message)  # Normal mode: print all

# Global variables
file_cache = {}      # Cache CSDL live files {symbol: {data, mtime, updates, size}}
history_cache = {}   # Cache CSDL history files {symbol: {data, mtime, filepath}}
stats = {}           # Statistics {symbol: {request_count, unique_ips, last_requests}}
ea_activity = {}     # EA activity tracking {symbol: {request_count_60s, ips, last_request_time}}
server_start_time = time.time()
cache_lock = Lock()  # Thread safety for cache access
stats_lock = Lock()  # Thread safety for stats access
ea_activity_lock = Lock()  # Thread safety for EA activity tracking
shutdown_flag = False  # Graceful shutdown flag
ctrl_c_count = 0    # Count Ctrl+C presses
last_ctrl_c_time = 0  # Last Ctrl+C timestamp

# ==============================================================================
# MEMORY LEAK PREVENTION (Cache Cleanup)
# ==============================================================================
MAX_HISTORY_CACHE_ENTRIES = 100   # Max symbols to track in history_cache
MAX_HISTORY_DATA_LOADED = 50      # Max symbols with data loaded in memory
HISTORY_DATA_TTL = 1800           # Clear data after 30 minutes (seconds)
CLEANUP_INTERVAL = 3600           # Run cleanup every 1 hour (seconds)

def cleanup_history_cache():
    """Clean up history_cache to prevent memory leak"""
    with cache_lock:
        now = time.time()

        # Step 1: Clear expired data (TTL > 30 minutes)
        cleared_count = 0
        for symbol, cache in history_cache.items():
            if cache.get("data") is not None:
                last_access = cache.get("last_access", 0)
                if now - last_access > HISTORY_DATA_TTL:
                    cache["data"] = None
                    cleared_count += 1

        if cleared_count > 0:
            log_print(f"[CLEANUP] Cleared {cleared_count} expired history data (TTL: {HISTORY_DATA_TTL}s)", "INFO")

        # Step 2: Limit loaded data count
        loaded_symbols = [(s, c.get("last_access", 0)) for s, c in history_cache.items() if c.get("data") is not None]
        if len(loaded_symbols) > MAX_HISTORY_DATA_LOADED:
            loaded_symbols.sort(key=lambda x: x[1])
            to_clear = len(loaded_symbols) - MAX_HISTORY_DATA_LOADED
            for symbol, _ in loaded_symbols[:to_clear]:
                history_cache[symbol]["data"] = None
            log_print(f"[CLEANUP] Cleared {to_clear} oldest history data (limit: {MAX_HISTORY_DATA_LOADED})", "INFO")

        # Step 3: Limit total cache entries
        if len(history_cache) > MAX_HISTORY_CACHE_ENTRIES:
            all_entries = [(s, c.get("mtime", 0)) for s, c in history_cache.items()]
            all_entries.sort(key=lambda x: x[1])
            to_remove = len(history_cache) - MAX_HISTORY_CACHE_ENTRIES
            for symbol, _ in all_entries[:to_remove]:
                del history_cache[symbol]
            log_print(f"[CLEANUP] Removed {to_remove} oldest cache entries (limit: {MAX_HISTORY_CACHE_ENTRIES})", "INFO")

def cleanup_deleted_symbols():
    """Remove symbols from file_cache if their files no longer exist"""
    with cache_lock:
        live_files, _ = scan_csdl_files()
        current_symbols = set([extract_symbol_from_filename(f, is_live=True) for f in live_files])
        cached_symbols = set(file_cache.keys())
        deleted_symbols = cached_symbols - current_symbols

        if deleted_symbols:
            for symbol in deleted_symbols:
                del file_cache[symbol]
            log_print(f"[CLEANUP] Removed {len(deleted_symbols)} deleted symbols from cache", "INFO")

def periodic_cleanup():
    """Periodic cleanup thread - runs every hour"""
    print(f"[CLEANUP] Started periodic cleanup thread (interval: {CLEANUP_INTERVAL}s / {CLEANUP_INTERVAL//3600}h)")

    while not shutdown_flag:
        try:
            time.sleep(CLEANUP_INTERVAL)
            if shutdown_flag:
                break

            log_print(f"[CLEANUP] Running periodic cleanup...", "INFO")
            cleanup_history_cache()
            cleanup_deleted_symbols()
            log_print(f"[CLEANUP] Cleanup completed. Next cleanup in {CLEANUP_INTERVAL//3600}h", "INFO")

        except Exception as e:
            print(f"[CLEANUP] Error in cleanup thread: {e}")

# ==============================================================================
# SIGNAL HANDLERS (Ctrl+C Protection)
# ==============================================================================

def signal_handler(sig, frame):
    """Handle Ctrl+C signal - require double press to exit"""
    global shutdown_flag, ctrl_c_count, last_ctrl_c_time

    current_time = time.time()

    # Reset count if more than 3 seconds since last Ctrl+C
    if current_time - last_ctrl_c_time > 3:
        ctrl_c_count = 0

    ctrl_c_count += 1
    last_ctrl_c_time = current_time

    if ctrl_c_count == 1:
        print("\n")
        print("=" * 60)
        print("⚠️  WARNING: Ctrl+C detected!")
        print("Press Ctrl+C again within 3 seconds to stop server")
        print("=" * 60)
    else:
        print("\n")
        print("=" * 60)
        print("🛑 Shutting down server...")
        print("=" * 60)
        shutdown_flag = True
        save_stats_to_file()  # Save stats before exit
        sys.exit(0)

# ==============================================================================
# FILE POLLING SYSTEM (Background Thread with Summary Logging)
# ==============================================================================

def scan_csdl_files():
    """Scan CSDL folder and return both live and history files
    Returns: (live_files, history_files)
    - live_files: List of *_LIVE.json files
    - history_files: List of *.json files (excluding *_LIVE.json)
    """
    folder = config["csdl_folder"]

    # Find all JSON files
    all_json = glob.glob(os.path.join(folder, "*.json"))

    # Separate live files from history files
    live_files = [f for f in all_json if f.endswith("_LIVE.json")]
    history_files = [f for f in all_json if not f.endswith("_LIVE.json")]

    return live_files, history_files

def extract_symbol_from_filename(filepath, is_live=True):
    """Extract symbol name from filepath
    Examples:
    - E:/PRO_ONER/.../BTCUSD_LIVE.json -> BTCUSD (is_live=True)
    - E:/PRO_ONER/.../BTCUSD.json -> BTCUSD (is_live=False)
    """
    basename = os.path.basename(filepath)
    if is_live:
        symbol = basename.replace("_LIVE.json", "")
    else:
        symbol = basename.replace(".json", "")
    return symbol

def poll_files():
    """Background thread: Poll LIVE files every N seconds
    - Đọc LIVE files và cache vào memory cho Bot 2 (Receiver) PULL qua API
    - HISTORY files chỉ đọc khi User request (on-demand)
    - Log tổng kết mỗi 60 giây để tránh spam
    """
    global shutdown_flag

    # Startup logs (1-time only) - ALWAYS show, not affected by quiet mode
    print(f"[POLLING] Started polling thread (interval: {config['polling_interval']}s)")
    print(f"[POLLING] Reading LIVE files every {config['polling_interval']}s")
    print(f"[POLLING] Bot 2 will PULL data via API /api/csdl/<symbol>")
    print(f"[POLLING] HISTORY files: on-demand only")
    print(f"[POLLING] Summary log every 60 seconds")

    # Track updates for summary logging
    live_updates = []  # List of (symbol, timestamp)
    last_summary_time = time.time()

    while not shutdown_flag:
        try:
            # OPTIMIZATION: Sync to EVEN seconds when polling=2 (avoid conflict with Bot SPY odd-second writes)
            if config["polling_interval"] == 2:
                # Wait until next even second (0, 2, 4, 6, 8...)
                while int(time.time()) % 2 != 0:
                    time.sleep(0.05)  # Check every 50ms
                # RACE CONDITION FIX: Wait 150ms buffer to ensure Bot SPY finished writing files
                time.sleep(0.15)  # Buffer: 150ms safety margin

            live_files, history_files = scan_csdl_files()

            # Đọc LIVE files (cho Port 80 - EA)
            if True:  # Always read LIVE files
                # Process LIVE files only
                for filepath in live_files:
                    symbol = extract_symbol_from_filename(filepath, is_live=True)

                    # Get file modification time
                    try:
                        mtime = os.path.getmtime(filepath)
                        size = os.path.getsize(filepath)
                    except:
                        continue  # File deleted or inaccessible

                    with cache_lock:
                        # Check if file is new or updated
                        if symbol not in file_cache:
                            # New file discovered
                            file_cache[symbol] = {
                                "data": None,
                                "mtime": 0,
                                "updates": [],
                                "size": 0,
                                "filepath": filepath
                            }

                        cached_mtime = file_cache[symbol]["mtime"]

                        # File updated? (mtime changed)
                        if mtime > cached_mtime:
                            # Read file content as RAW STRING (preserve column order | giu nguyen thu tu cot)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    raw_content = f.read()  # ✅ Read as string, NOT parse!

                                # Parse with OrderedDict to PRESERVE column order | Parse voi OrderedDict de GIU thu tu cot
                                try:
                                    parsed_data = json.loads(raw_content, object_pairs_hook=OrderedDict)
                                    if not isinstance(parsed_data, list) or len(parsed_data) < 7:
                                        log_print(f"[POLLING] Invalid data structure in {symbol}: expected 7+ rows", "ERROR")
                                        continue
                                except json.JSONDecodeError as e:
                                    log_print(f"[POLLING] Invalid JSON in {symbol}: {e}", "ERROR")
                                    continue

                                # Update cache with OrderedDict (preserves column order 100%)
                                file_cache[symbol]["data"] = parsed_data  # ✅ Store OrderedDict (order preserved!)
                                file_cache[symbol]["mtime"] = mtime
                                file_cache[symbol]["size"] = size

                                # Keep last 4 update times
                                updates = file_cache[symbol]["updates"]
                                updates.insert(0, mtime)
                                file_cache[symbol]["updates"] = updates[:4]

                                # Track for summary log
                                live_updates.append((symbol, mtime))

                            except Exception as e:
                                log_print(f"[POLLING] Error reading LIVE {symbol}: {e}", "ERROR")

            # Scan for HISTORY files but DON'T auto-read them
            # Just track their existence for User viewing
            for filepath in history_files:
                symbol = extract_symbol_from_filename(filepath, is_live=False)
                with cache_lock:
                    if symbol not in history_cache:
                        # Just register the file, don't read it yet
                        history_cache[symbol] = {
                            "data": None,
                            "mtime": 0,
                            "filepath": filepath,
                            "last_access": 0  # Track last access for TTL cleanup
                        }

            # Log summary every 60 seconds
            now = time.time()
            if now - last_summary_time >= 60:
                if live_updates:
                    live_symbols = set([s for s, t in live_updates])
                    log_print(f"[POLLING] Last 60s: LIVE files updated: {len(live_symbols)} ({', '.join(sorted(live_symbols))})", "INFO")

                    # Reset counter
                    live_updates = []

                last_summary_time = now

            # Sleep before next poll
            time.sleep(config["polling_interval"])

        except Exception as e:
            log_print(f"[POLLING] Error in polling thread: {e}", "ERROR")
            time.sleep(config["polling_interval"])

# ==============================================================================
# EA ACTIVITY TRACKING (for Dashboard and Summary Logging)
# ==============================================================================

def track_ea_activity(symbol, ip):
    """Track EA request activity for summary logging and dashboard"""
    with ea_activity_lock:
        now = time.time()

        if symbol not in ea_activity:
            ea_activity[symbol] = {
                "request_count_60s": 0,
                "request_count_10m": 0,
                "request_count_1h": 0,
                "ips": set(),
                "last_request_time": now,
                "requests_60s": [],  # List of timestamps
                "requests_10m": [],
                "requests_1h": []
            }

        # Add current timestamp
        ea_activity[symbol]["requests_60s"].append(now)
        ea_activity[symbol]["requests_10m"].append(now)
        ea_activity[symbol]["requests_1h"].append(now)

        # Add IP
        ea_activity[symbol]["ips"].add(ip)
        ea_activity[symbol]["last_request_time"] = now

        # Clean old timestamps (keep only recent ones)
        ea_activity[symbol]["requests_60s"] = [t for t in ea_activity[symbol]["requests_60s"] if now - t <= 60]
        ea_activity[symbol]["requests_10m"] = [t for t in ea_activity[symbol]["requests_10m"] if now - t <= 600]
        ea_activity[symbol]["requests_1h"] = [t for t in ea_activity[symbol]["requests_1h"] if now - t <= 3600]

        # Update counts
        ea_activity[symbol]["request_count_60s"] = len(ea_activity[symbol]["requests_60s"])
        ea_activity[symbol]["request_count_10m"] = len(ea_activity[symbol]["requests_10m"])
        ea_activity[symbol]["request_count_1h"] = len(ea_activity[symbol]["requests_1h"])

def ea_activity_summary_thread():
    """Background thread: Log EA activity summary every 60 seconds"""
    global shutdown_flag
    print(f"[EA ACTIVITY] Started EA activity summary thread (interval: 60s)")

    while not shutdown_flag:
        time.sleep(60)

        if shutdown_flag:
            break

        with ea_activity_lock:
            if ea_activity:
                # Build summary message
                summary_parts = []
                for symbol in sorted(ea_activity.keys()):
                    count_60s = ea_activity[symbol]["request_count_60s"]
                    ip_count = len(ea_activity[symbol]["ips"])

                    if count_60s > 0:
                        summary_parts.append(f"{symbol}({count_60s} reqs from {ip_count} IP{'s' if ip_count > 1 else ''})")

                if summary_parts:
                    print(f"[EA ACTIVITY] Last 60s: {', '.join(summary_parts)}")

# ==============================================================================
# STATISTICS TRACKING
# ==============================================================================

def log_request(symbol, ip, status):
    """Log API request to statistics"""
    with stats_lock:
        if symbol not in stats:
            stats[symbol] = {
                "request_count": 0,
                "unique_ips": set(),
                "last_requests": []
            }

        # Increment count
        stats[symbol]["request_count"] += 1

        # Add IP to set
        stats[symbol]["unique_ips"].add(ip)

        # Add to history (keep last N requests)
        history = stats[symbol]["last_requests"]
        history.insert(0, {
            "time": time.time(),
            "ip": ip,
            "status": status
        })
        stats[symbol]["last_requests"] = history[:config["log_history_limit"]]

def get_stats_summary():
    """Get statistics summary for all symbols"""
    with stats_lock:
        summary = {}
        for symbol, data in stats.items():
            summary[symbol] = {
                "request_count": data["request_count"],
                "unique_ips": len(data["unique_ips"]),
                "last_requests": data["last_requests"][:10]  # Last 10
            }
        return summary

def save_stats_to_file():
    """Save stats to file (DISABLED - user requested no JSON log files)"""
    # This function is intentionally disabled to avoid creating JSON log files
    # Stats are kept in memory only
    pass

def load_stats_from_file():
    """Load stats from file (DISABLED - user requested no JSON log files)"""
    # This function is intentionally disabled
    # Stats start fresh on each boot
    pass

# ==============================================================================
# HTML TABLE HELPERS (for CSDL data display)
# ==============================================================================

def build_signal_badge(signal):
    """Build colored signal badge"""
    if signal == 1:
        return '<span style="background: #4caf50; color: white; padding: 4px 12px; border-radius: 3px; font-weight: bold;">🟢 BUY</span>'
    elif signal == -1:
        return '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 3px; font-weight: bold;">🔴 SELL</span>'
    else:
        return '<span style="background: #9e9e9e; color: white; padding: 4px 12px; border-radius: 3px; font-weight: bold;">⚪ NEUTRAL</span>'

def format_timestamp(ts):
    """Format timestamp to readable datetime"""
    if ts and ts > 0:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return '<span style="color: #999;">No cross</span>'

def build_ea_live_table(data):
    """Build HTML table for EA LIVE data (6 columns only - matching actual JSON structure)"""
    if not data or not isinstance(data, list):
        return '<p>No data available</p>'

    html = '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse; font-size: 13px; background: white;"><thead><tr style="background: #00A651; color: white; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;">'
    html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">Signal</th>'
    html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">Timestamp</th>'
    html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Price Diff</th>'
    html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Time Diff</th>'
    html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">News</th>'
    html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Max Loss</th>'
    html += '</tr></thead><tbody>'

    for row in data:
        html += '<tr style="border-bottom: 1px solid #e0e0e0;">'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center;">{build_signal_badge(row.get("signal", 0))}</td>'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center; font-size: 11px;">{format_timestamp(row.get("timestamp", 0))}</td>'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace;">{row.get("pricediff", 0):.2f}</td>'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right;">{row.get("timediff", 0)}</td>'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center;">{row.get("news", 0)}</td>'
        html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace; color: #f44336;">{row.get("max_loss", 0):.2f}</td>'
        html += '</tr>'

    html += '</tbody></table></div>'
    return html

# ==============================================================================
# FLASK APP - PORT 80 (API for EA)
# ==============================================================================

app_api = Flask(__name__)

# CORS support - allow Dashboard to call API from different port
@app_api.after_request
def add_cors_headers(response):
    """Add CORS headers to all API responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response

@app_api.route('/api/csdl/<path:symbol>', methods=['GET', 'OPTIONS'])
def sync_csdl(symbol):
    """API endpoint for Bot 2/3/... (Receivers) to PULL CSDL data

    Bot 2 will call this API every 1 second to get latest data.
    No authentication required - Bot 1 is a public data source.

    FORMAT: /api/csdl/SYMBOL_LIVE.json
    RETURNS: {"type": "data", "symbol": "BTCUSD", "mtime": ..., "data": [7 rows]}
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    client_ip = request.remote_addr

    # Extract symbol
    clean_symbol = symbol.replace("_LIVE.json", "").replace(".json", "")

    # Check cache
    with cache_lock:
        if clean_symbol not in file_cache:
            return jsonify({"error": f"Symbol not found: {clean_symbol}"}), 404

        data = file_cache[clean_symbol]["data"]  # OrderedDict (column order preserved!)
        mtime = file_cache[clean_symbol]["mtime"]

        if data is None:
            return jsonify({"error": f"Data not loaded yet for {clean_symbol}"}), 500

    # Return wrapper JSON (same format as PUSH payload)
    # Use json.dumps(sort_keys=False) to PRESERVE column order | Dung sort_keys=False de GIU thu tu cot
    response = {
        "type": "data",
        "symbol": clean_symbol,
        "mtime": int(mtime),
        "data": data,  # OrderedDict with original column order
        "timestamp": int(time.time())
    }

    # ✅ SUPPRESSED: No need to log every Bot 2 request (spam reduction)
    # Bot 2 polls every 1s → 10 symbols = 600 logs/min = SPAM!
    # log_print(f"[API] Sent {clean_symbol} to Bot 2 at {client_ip} (mtime: {mtime})", "INFO")

    # Track EA/Bot2 activity for dashboard monitoring
    track_ea_activity(clean_symbol, client_ip)

    # Log request for statistics
    log_request(clean_symbol, client_ip, 200)

    # ✅ CRITICAL: Use json.dumps(sort_keys=False) instead of jsonify()
    # jsonify() sorts keys alphabetically, breaking column order!
    json_output = json.dumps(response, sort_keys=False, ensure_ascii=False)
    return Response(json_output, mimetype='application/json'), 200

@app_api.route('/api/symbols', methods=['GET'])
def get_symbols():
    """API endpoint: Return list of all available symbols | Tra ve danh sach tat ca symbols hien co

    Bot 2 will call this to auto-detect all symbols without hardcoding.
    Bot 2 goi API nay de tu dong phat hien tat ca symbols ma khong can hardcode.

    RETURNS: {"symbols": ["BTCUSD", "ETHUSD", ...], "count": 7, "timestamp": ...}
    """
    with cache_lock:
        symbols = list(file_cache.keys())

    response = {
        "symbols": symbols,
        "count": len(symbols),
        "timestamp": int(time.time())
    }

    # ✅ SUPPRESSED: No need to log every 60s request (spam reduction)
    # print(f"[API] Symbols list requested: {len(symbols)} symbols available")

    return jsonify(response), 200

@app_api.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }), 200

@app_api.route('/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        "name": "SYNS API Server",
        "version": "1.0",
        "port": config["api_port"],
        "endpoints": {
            "/api/csdl/<symbol>": "Get CSDL data for EA (LIVE files only)",
            "/api/health": "Health check"
        }
    }), 200

# ==============================================================================
# FLASK APP - PORT 9070 (Dashboard)
# ==============================================================================

app_dashboard = Flask(__name__)

# Japanese Minimalist Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYNS Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #fafafa;
            color: #2c2c2c;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            border: 1px solid #d0d0d0;
            padding: 15px 20px;
            margin-bottom: 20px;
            background: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            font-size: 18px;
            font-weight: 400;
            letter-spacing: 2px;
        }

        .status {
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 12px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4caf50;
            display: inline-block;
            margin-right: 5px;
        }

        /* Main Panel */
        .panel {
            border: 1px solid #d0d0d0;
            background: white;
            margin-bottom: 20px;
        }

        .panel-header {
            padding: 12px 20px;
            border-bottom: 1px solid #00A651;
            background: #00A651;
            color: white;
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .panel-body {
            padding: 20px;
        }

        /* Table */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #d0d0d0;
            font-weight: 400;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #666;
        }

        td {
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }

        tr:hover {
            background: #fafafa;
        }

        /* Status indicators */
        .status-ok { color: #4caf50; }
        .status-warning { color: #ff9800; }
        .status-error { color: #f44336; }

        /* Buttons */
        .btn {
            display: inline-block;
            padding: 8px 16px;
            border: 1px solid #d0d0d0;
            background: white;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 5px;
            text-decoration: none;
            color: #2c2c2c;
            transition: all 0.2s;
        }

        .btn:hover {
            background: #2c2c2c;
            color: white;
        }

        .btn.active {
            background: #2c2c2c;
            color: white;
        }

        /* Hidden sections */
        .hidden {
            display: none;
        }

        /* Polling selector */
        .polling-selector {
            display: flex;
            gap: 5px;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 11px;
            color: #999;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>SYNS API SERVER</h1>
            <div class="status">
                <span><span class="status-dot"></span>Running</span>
                <span>Uptime: {{ uptime }}</span>
                <span>Polling:
                    <span class="polling-selector">
                        <button class="btn {{ 'active' if polling == 1 else '' }}" onclick="setPolling(1)">1s</button>
                        <button class="btn {{ 'active' if polling == 2 else '' }}" onclick="setPolling(2)">2s</button>
                    </span>
                </span>
                <span>Port: 9070</span>
            </div>
        </div>

        <!-- CSDL Files Panel -->
        <div class="panel">
            <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
                <span>CSDL Files — Updated {{ last_poll }} ago</span>
                <div style="display: flex; gap: 5px;">
                    <a href="/csdl/user" class="btn" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📜 CSDL 1 USER</a>
                    <a href="/csdl/ea-live" class="btn" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📊 CSDL 2 EA LIVE</a>
                    <a href="/csdl/history" class="btn" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📊 MONTHLY HISTORY</a>
                    <button class="btn" onclick="location.reload()" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0;">🔄 REFRESH</button>
                </div>
            </div>
            <div class="panel-body">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Status</th>
                            <th>Last Update (Server GMT+2)</th>
                            <th>Last Update (VN GMT+7)</th>
                            <th>Ago</th>
                            <th>-1</th>
                            <th>-2</th>
                            <th>-3</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for symbol in symbols %}
                        <tr>
                            <td><strong>{{ symbol.name }}</strong></td>
                            <td class="{{ symbol.status_class }}">{{ symbol.status_icon }}</td>
                            <td>{{ symbol.last_update_server }}</td>
                            <td>{{ symbol.last_update_vn }}</td>
                            <td>{{ symbol.ago }}</td>
                            <td>{{ symbol.update_1 }}</td>
                            <td>{{ symbol.update_2 }}</td>
                            <td>{{ symbol.update_3 }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- EA Activity Monitor Panel -->
        <div class="panel">
            <div class="panel-header">🤖 EA ACTIVITY MONITOR — Real-time EA Request Tracking</div>
            <div class="panel-body">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Last 60s</th>
                            <th>Last 10min</th>
                            <th>Last 1hour</th>
                            <th>EA Count</th>
                            <th>EA IP Addresses</th>
                            <th>Last Request</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ea in ea_data %}
                        <tr>
                            <td><strong>{{ ea.symbol }}</strong></td>
                            <td>{{ ea.count_60s }}</td>
                            <td>{{ ea.count_10m }}</td>
                            <td>{{ ea.count_1h }}</td>
                            <td>{{ ea.ip_count }}</td>
                            <td style="font-size: 11px;">{{ ea.ips }}</td>
                            <td>{{ ea.last_request }}</td>
                        </tr>
                        {% endfor %}
                        {% if not ea_data %}
                        <tr>
                            <td colspan="7" style="text-align: center; color: #999; padding: 40px;">No EA activity yet</td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Statistics Panel -->
        <div class="panel">
            <div class="panel-header">📈 REQUEST STATISTICS — Last 24 hours</div>
            <div class="panel-body">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Requests</th>
                            <th>Unique IPs</th>
                            <th>Chart</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for stat in stats_data %}
                        <tr>
                            <td><strong>{{ stat.symbol }}</strong></td>
                            <td>{{ "{:,}".format(stat.count) }}</td>
                            <td>{{ stat.ips }}</td>
                            <td><div style="height: 20px; background: #4caf50; display: inline-block; width: {{ stat.bar_width }}px;"></div></td>
                        </tr>
                        {% endfor %}
                        {% if not stats_data %}
                        <tr>
                            <td colspan="4" style="text-align: center; color: #999; padding: 40px;">No statistics yet</td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Action Buttons -->
        <div style="text-align: center; margin: 20px 0;">
            <a href="/ea-activity" class="btn">📊 EA Activity Monitor</a>
            <a href="/csdl/ea-live" class="btn">📋 CSDL EA LIVE</a>
            <a href="/settings" class="btn">⚙️ Settings</a>
        </div>

        <!-- Footer -->
        <div class="footer">
            SYNS API Server v1.0 — Japanese Minimalist Design
        </div>
    </div>

    <script>
        // Polling interval selector (placeholder - would need backend implementation)
        function setPolling(interval) {
            // TODO: Send AJAX request to update polling interval
            console.log('Set polling to ' + interval + 's');
        }
    </script>
</body>
</html>
"""

def format_uptime(seconds):
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def format_ago(seconds):
    """Format time ago in human-readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    else:
        return f"{int(seconds // 3600)}h"

def get_status_indicator(ago_seconds):
    """Get status indicator based on time since last update"""
    if ago_seconds < 60:
        return "●", "status-ok"      # Green
    elif ago_seconds < 300:
        return "◐", "status-warning"  # Yellow
    else:
        return "○", "status-error"    # Red

@app_dashboard.route('/')
def dashboard_home():
    """Main dashboard page"""
    uptime = format_uptime(time.time() - server_start_time)

    # Get symbols data
    symbols_data = []

    with cache_lock:
        for symbol, cache in file_cache.items():
            if cache["data"] is None:
                continue

            mtime = cache["mtime"]
            updates = cache["updates"]

            # Calculate time ago
            now = time.time()
            ago_seconds = now - mtime

            # Get status indicator
            status_icon, status_class = get_status_indicator(ago_seconds)

            # Format times
            # Server time (GMT+2)
            server_time = datetime.fromtimestamp(mtime) + timedelta(hours=config["server_timezone_offset"])
            # Vietnam time (GMT+7)
            vn_time = datetime.fromtimestamp(mtime) + timedelta(hours=config["vietnam_timezone_offset"])

            # Format previous updates
            update_1 = ""
            update_2 = ""
            update_3 = ""

            if len(updates) > 1:
                update_1 = (datetime.fromtimestamp(updates[1]) + timedelta(hours=config["server_timezone_offset"])).strftime("%H:%M:%S")
            if len(updates) > 2:
                update_2 = (datetime.fromtimestamp(updates[2]) + timedelta(hours=config["server_timezone_offset"])).strftime("%H:%M:%S")
            if len(updates) > 3:
                update_3 = (datetime.fromtimestamp(updates[3]) + timedelta(hours=config["server_timezone_offset"])).strftime("%H:%M:%S")

            symbols_data.append({
                "name": symbol,
                "status_icon": status_icon,
                "status_class": status_class,
                "last_update_server": server_time.strftime("%H:%M:%S"),
                "last_update_vn": vn_time.strftime("%H:%M:%S"),
                "ago": format_ago(ago_seconds),
                "update_1": update_1,
                "update_2": update_2,
                "update_3": update_3
            })

    # Sort by symbol name
    symbols_data.sort(key=lambda x: x["name"])

    # Get EA Activity data
    ea_data = []
    now = time.time()
    with ea_activity_lock:
        for symbol in sorted(ea_activity.keys()):
            activity = ea_activity[symbol]
            ips_list = ', '.join(sorted(list(activity["ips"])))
            ago_seconds = now - activity["last_request_time"]
            ago_text = format_ago(ago_seconds)

            ea_data.append({
                "symbol": symbol,
                "count_60s": activity["request_count_60s"],
                "count_10m": activity["request_count_10m"],
                "count_1h": activity["request_count_1h"],
                "ips": ips_list,
                "ip_count": len(activity["ips"]),
                "last_request": ago_text
            })

    # Get Statistics data
    stats_summary = get_stats_summary()
    stats_data = []
    for symbol, data in sorted(stats_summary.items()):
        count = data["request_count"]
        ips = data["unique_ips"]
        stats_data.append({
            "symbol": symbol,
            "count": count,
            "ips": ips,
            "bar_width": min(count * 2, 400)
        })

    return render_template_string(
        DASHBOARD_HTML,
        uptime=uptime,
        polling=config["polling_interval"],
        last_poll=f"{config['polling_interval']}s",
        symbols=symbols_data,
        ea_data=ea_data,
        stats_data=stats_data
    )

@app_dashboard.route('/ea-activity')
def dashboard_ea_activity():
    """EA Activity Monitor page"""
    # Get EA activity data
    ea_data = []
    now = time.time()

    with ea_activity_lock:
        for symbol in sorted(ea_activity.keys()):
            activity = ea_activity[symbol]

            # Get IP list
            ips_list = ', '.join(sorted(list(activity["ips"])))

            # Calculate time since last request
            ago_seconds = now - activity["last_request_time"]
            ago_text = format_ago(ago_seconds)

            ea_data.append({
                "symbol": symbol,
                "count_60s": activity["request_count_60s"],
                "count_10m": activity["request_count_10m"],
                "count_1h": activity["request_count_1h"],
                "ips": ips_list,
                "ip_count": len(activity["ips"]),
                "last_request": ago_text
            })

    # Build table rows
    rows_html = ""
    for data in ea_data:
        rows_html += f"""
                        <tr>
                            <td><strong>{data['symbol']}</strong></td>
                            <td>{data['count_60s']}</td>
                            <td>{data['count_10m']}</td>
                            <td>{data['count_1h']}</td>
                            <td>{data['ip_count']}</td>
                            <td style="font-size: 11px;">{data['ips']}</td>
                            <td>{data['last_request']}</td>
                        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SYNS Dashboard - EA Activity Monitor</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
            .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651; color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
            .panel-body {{ padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
            th {{ font-size: 11px; text-transform: uppercase; color: #666; letter-spacing: 1px; }}
            .btn {{ display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                   background: white; text-decoration: none; color: #2c2c2c; margin: 10px; }}
            .btn:hover {{ background: #2c2c2c; color: white; }}
            .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel">
                <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>🤖 EA ACTIVITY MONITOR — Real-time EA Request Tracking</span>
                    <span style="background: white; color: #00A651; padding: 6px 12px; font-size: 10px; border-radius: 3px;">Auto-refresh every 5s</span>
                </div>
                <div class="panel-body">
                    <div class="info">
                        <strong>About EA Activity Monitor:</strong><br>
                        • Tracks which EA (by IP) is requesting which symbol<br>
                        • Shows request counts for Last 60s, Last 10min, Last 1hour<br>
                        • Updates automatically every 5 seconds<br>
                        • CMD shows summary every 60 seconds (no spam logging)
                    </div>

                    <table>
                        <tr>
                            <th>Symbol</th>
                            <th>Last 60s</th>
                            <th>Last 10min</th>
                            <th>Last 1hour</th>
                            <th>EA Count</th>
                            <th>EA IP Addresses</th>
                            <th>Last Request</th>
                        </tr>
                        {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; color: #999; padding: 40px;">No EA activity yet</td></tr>'}
                    </table>
                </div>
            </div>
            <div style="text-align: center;">
                <a href="/" class="btn">← Back to Dashboard</a>
                <button class="btn" onclick="location.reload()">🔄 Refresh Now</button>
            </div>
        </div>
    </body>
    </html>
    """

    return html

@app_dashboard.route('/csdl/ea-live')
def dashboard_csdl_ea_live():
    """CSDL 2 EA LIVE - List of SYMBOL_LIVE.json files"""
    # Get available symbols from LIVE files (file_cache)
    symbols_list = []
    with cache_lock:
        # Get all symbols that have LIVE data loaded with filename
        for symbol in sorted(file_cache.keys()):
            if file_cache[symbol]["data"] is not None:
                filename = os.path.basename(file_cache[symbol]["filepath"])
                symbols_list.append({
                    "name": symbol,
                    "filename": filename
                })

    # Build table rows
    rows_html = ""
    for sym in symbols_list:
        rows_html += f"""
                        <tr>
                            <td><strong>{sym['name']}</strong></td>
                            <td>{sym['filename']}</td>
                            <td>
                                <a href="/csdl/ea-live/{sym['name']}" class="btn btn-small">📊 View Data</a>
                            </td>
                        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SYNS Dashboard - CSDL 2 EA LIVE</title>
        <style>
            body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
            .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                           color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
            .panel-body {{ padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
            th {{ font-size: 11px; text-transform: uppercase; color: #666; letter-spacing: 1px; }}
            .btn {{ display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                   background: white; text-decoration: none; color: #2c2c2c; margin: 5px;
                   font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
            .btn:hover {{ background: #2c2c2c; color: white; }}
            .btn-small {{ padding: 6px 12px; font-size: 10px; }}
            .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel">
                <div class="panel-header">📊 CSDL 2 EA LIVE — Symbol_LIVE.json Files (for EA Consumption)</div>
                <div class="panel-body">
                    <div class="info">
                        <strong>About CSDL 2 EA LIVE:</strong><br>
                        • Files: SYMBOL_LIVE.json (with _LIVE suffix)<br>
                        • Contains real-time signal data for EA consumption (Port 80)<br>
                        • Click "View Data" to see full JSON content
                    </div>

                    <table>
                        <tr>
                            <th>Symbol</th>
                            <th>Filename</th>
                            <th>Action</th>
                        </tr>
                        {rows_html if rows_html else '<tr><td colspan="3" style="text-align: center; color: #999; padding: 40px;">No EA LIVE files found</td></tr>'}
                    </table>
                </div>
            </div>
            <div style="text-align: center;">
                <a href="/" class="btn">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """

    return html

@app_dashboard.route('/csdl/ea-live/<symbol>')
def dashboard_view_ea_live_data(symbol):
    """View CSDL 2 EA LIVE data for a symbol (SYMBOL_LIVE.json)"""
    with cache_lock:
        if symbol not in file_cache or file_cache[symbol]["data"] is None:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error - Symbol Not Found</title>
                <style>
                    body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; text-align: center; }}
                    .error {{ color: #f44336; font-size: 18px; margin: 40px 0; }}
                    .btn {{ display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                           background: white; text-decoration: none; color: #2c2c2c; margin: 10px; }}
                    .btn:hover {{ background: #2c2c2c; color: white; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">❌ Error: Symbol "{symbol}" not found or no EA LIVE data available</div>
                    <a href="/csdl/ea-live" class="btn">← Back to EA LIVE List</a>
                </div>
            </body>
            </html>
            """, 404

        # Get EA LIVE data
        ea_live_data = file_cache[symbol]["data"]

    # Calculate metadata
    timestamp = ea_live_data[0].get('timestamp', 0) if isinstance(ea_live_data, list) and len(ea_live_data) > 0 else 0
    rows = len(ea_live_data) if isinstance(ea_live_data, list) else 0

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SYNS Dashboard - {symbol} EA LIVE Data</title>
        <style>
            body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
            .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                           color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
            .panel-body {{ padding: 20px; }}
            .btn {{ display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                   background: white; text-decoration: none; color: #2c2c2c; margin: 5px;
                   font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
            .btn:hover {{ background: #2c2c2c; color: white; }}
            pre {{ background: #f5f5f5; padding: 20px; border: 1px solid #d0d0d0;
                  overflow-x: auto; font-size: 12px; line-height: 1.5; }}
            .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel">
                <div class="panel-header">📊 {symbol} — CSDL 2 EA LIVE DATA</div>
                <div class="panel-body">
                    <div class="info">
                        <strong>Symbol:</strong> {symbol}<br>
                        <strong>File:</strong> {symbol}_LIVE.json (EA LIVE data)<br>
                        <strong>Total Rows:</strong> {rows}<br>
                        <strong>Last Update:</strong> {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'}<br>
                        <strong>Purpose:</strong> Real-time signal data for EA consumption (Port 80 API)
                    </div>

                    <h3 style="margin-top: 30px; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                        Signal Data Table:
                    </h3>
                    {build_ea_live_table(ea_live_data)}
                </div>
            </div>
            <div style="text-align: center;">
                <a href="/csdl/ea-live" class="btn">← Back to EA LIVE List</a>
                <a href="/" class="btn">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    """

    return html

@app_dashboard.route('/api/config/save', methods=['POST'])
def api_save_config():
    """API endpoint to save configuration"""
    try:
        data = request.get_json()

        # Update config
        config['vps_ip'] = data.get('vps_ip', config['vps_ip'])
        # api_key removed - no authentication
        config['csdl_folder'] = data.get('csdl_folder', config['csdl_folder'])
        config['history_folder'] = data.get('history_folder', config['history_folder'])
        config['polling_interval'] = int(data.get('polling_interval', config['polling_interval']))
        config['server_timezone_offset'] = int(data.get('server_timezone_offset', config['server_timezone_offset']))
        config['vietnam_timezone_offset'] = int(data.get('vietnam_timezone_offset', config['vietnam_timezone_offset']))

        # Update quiet_mode in bot_config.json (root level)
        if 'quiet_mode' in data:
            bot_config['quiet_mode'] = (data['quiet_mode'] == 'true' or data['quiet_mode'] == True)

            # Update runtime QUIET_MODE (applies immediately without restart)
            global QUIET_MODE
            QUIET_MODE = bot_config['quiet_mode']

            # Save bot_config.json
            try:
                with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(bot_config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                return jsonify({"success": False, "error": f"Failed to save quiet_mode: {e}"}), 500

        # Save to file
        if save_config(config):
            return jsonify({"success": True, "message": "Configuration saved successfully!"})
        else:
            return jsonify({"success": False, "error": "Failed to save config"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app_dashboard.route('/settings')
def dashboard_settings():
    """Settings page with editable form"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SYNS Dashboard - Settings</title>
        <style>
            body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
            .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                           color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
            .panel-body {{ padding: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
                    color: #666; margin-bottom: 8px; font-weight: bold; }}
            input, select {{ width: 100%; padding: 10px; font-family: inherit; font-size: 13px;
                    border: 1px solid #d0d0d0; background: #fafafa; }}
            input:focus, select:focus {{ outline: none; border-color: #00A651; background: white; }}
            .btn {{ display: inline-block; padding: 12px 24px; border: 1px solid #d0d0d0;
                   background: white; color: #2c2c2c; margin: 10px 5px; cursor: pointer;
                   font-family: inherit; font-size: 11px; text-transform: uppercase;
                   letter-spacing: 1px; text-decoration: none; }}
            .btn:hover {{ background: #2c2c2c; color: white; }}
            .btn-save {{ background: #00A651; color: white; border-color: #00A651; }}
            .btn-save:hover {{ background: #008f45; }}
            .alert {{ padding: 15px; margin: 20px 0; border-radius: 4px; display: none; }}
            .alert-success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .alert-error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .note {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;
                    margin: 20px 0; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel">
                <div class="panel-header">⚙️ SERVER SETTINGS — Edit & Save</div>
                <div class="panel-body">
                    <div class="note">
                        <strong>⚠️ Lưu ý:</strong> Thay đổi cấu hình sẽ lưu vào file <code>bot_config.json</code> (server section).<br>
                        • <strong>Polling Interval</strong>: Áp dụng ngay lập tức<br>
                        • <strong>CSDL Folder Path</strong>: Cần khởi động lại server<br>
                        • <strong>History Folder Path</strong>: Cần khởi động lại server
                    </div>

                    <div id="alert" class="alert"></div>

                    <form id="settingsForm">
                        <div class="form-group">
                            <label>VPS IP Address</label>
                            <input type="text" name="vps_ip" value="{config.get('vps_ip', '147.189.173.121')}" placeholder="147.189.173.121">
                        </div>

                        <!-- API Key removed - no authentication -->

                        <div class="form-group">
                            <label>CSDL Folder Path</label>
                            <input type="text" name="csdl_folder" value="{config['csdl_folder']}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner3/">
                        </div>

                        <div class="form-group">
                            <label>History Folder Path</label>
                            <input type="text" name="history_folder" value="{config['history_folder']}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/">
                        </div>

                        <div class="form-group">
                            <label>EA Polling Interval (Port 80)</label>
                            <select name="polling_interval">
                                <option value="1" {'selected' if config['polling_interval'] == 1 else ''}>1 second (Fast)</option>
                                <option value="2" {'selected' if config['polling_interval'] == 2 else ''}>2 seconds (Normal)</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>🔇 Quiet Mode (Reduce Console Spam)</label>
                            <select name="quiet_mode">
                                <option value="false" {'selected' if not bot_config.get('quiet_mode', False) else ''}>❌ OFF - Show all logs (Debug mode)</option>
                                <option value="true" {'selected' if bot_config.get('quiet_mode', False) else ''}>✅ ON - Only show ERROR/WARN (VPS 24/7)</option>
                            </select>
                            <p style="font-size: 11px; color: #666; margin-top: 5px; line-height: 1.4;">
                                💡 <strong>OFF:</strong> Show all INFO logs (for debugging)<br>
                                💡 <strong>ON:</strong> Silent mode - Only ERROR/WARN (prevents console spam on VPS 24/7)
                            </p>
                        </div>

                        <div class="form-group">
                            <label>Server Timezone Offset (hours from GMT)</label>
                            <input type="number" name="server_timezone_offset" value="{config['server_timezone_offset']}" min="-12" max="14">
                        </div>

                        <div class="form-group">
                            <label>Vietnam Timezone Offset (hours from GMT)</label>
                            <input type="number" name="vietnam_timezone_offset" value="{config['vietnam_timezone_offset']}" min="-12" max="14">
                        </div>

                        <div style="text-align: center; margin-top: 30px;">
                            <button type="submit" class="btn btn-save">💾 SAVE SETTINGS</button>
                            <a href="/" class="btn">← Back to Dashboard</a>
                        </div>
                    </form>

                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                        <p style="font-size: 11px; color: #999; text-align: center;">
                            <strong>Read-only settings:</strong><br>
                            API Port: {config['api_port']} | Dashboard Port: {config['dashboard_port']} |
                            Server IP: {config['server_ip']}
                        </p>
                    </div>
                </div>
            </div>

        </div>

        <script>
            const form = document.getElementById('settingsForm');
            const alert = document.getElementById('alert');

            form.addEventListener('submit', async (e) => {{
                e.preventDefault();

                const formData = new FormData(form);
                const data = {{}};
                formData.forEach((value, key) => {{
                    data[key] = value;
                }});

                try {{
                    const response = await fetch('/api/config/save', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(data)
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        alert.className = 'alert alert-success';
                        alert.textContent = '✅ ' + result.message;
                        alert.style.display = 'block';

                        setTimeout(() => {{
                            window.location.href = '/';
                        }}, 2000);
                    }} else {{
                        alert.className = 'alert alert-error';
                        alert.textContent = '❌ Error: ' + result.error;
                        alert.style.display = 'block';
                    }}
                }} catch (error) {{
                    alert.className = 'alert alert-error';
                    alert.textContent = '❌ Error: ' + error.message;
                    alert.style.display = 'block';
                }}
            }});
        </script>
    </body>
    </html>
    """

    return html

# ==============================================================================
# SERVER STARTUP
# ==============================================================================

def run_api_server():
    """Run API server on port 80 with HTTP (MT4 WebRequest only supports port 80/443)"""
    print(f"[API] Starting API server on {config['server_ip']}:{config['api_port']} (HTTP)")
    print(f"[API] NOTE: Using HTTP instead of HTTPS because MT4 WebRequest only supports port 80/443")

    app_api.run(
        host=config['server_ip'],
        port=config['api_port'],
        debug=False,
        threaded=True
    )

def run_dashboard_server():
    """Run Dashboard server on port 9070"""
    print(f"[DASHBOARD] Starting Dashboard server on {config['server_ip']}:{config['dashboard_port']}")
    app_dashboard.run(
        host=config['server_ip'],
        port=config['dashboard_port'],
        debug=False,
        threaded=True
    )

def main():
    """Main entry point"""
    print("=" * 60)
    print("SYNS API SERVER - Dual Port Flask Server")
    print("=" * 60)
    print(f"API Port:       {config['api_port']}")
    print(f"Dashboard Port: {config['dashboard_port']}")
    print(f"CSDL Folder:    {config['csdl_folder']}")
    print(f"Polling:        {config['polling_interval']}s")
    print(f"Server Time:    GMT+{config['server_timezone_offset']}")
    print(f"Vietnam Time:   GMT+{config['vietnam_timezone_offset']}")
    print("=" * 60)

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Start file polling thread
    polling_thread = Thread(target=poll_files, daemon=True)
    polling_thread.start()

    # Start EA activity summary thread
    ea_activity_thread = Thread(target=ea_activity_summary_thread, daemon=True)
    ea_activity_thread.start()

    # Start periodic cleanup thread (prevent memory leak)
    cleanup_thread = Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()

    # Start API server thread
    api_thread = Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # Start Dashboard server in main thread (blocking)
    run_dashboard_server()

if __name__ == "__main__":
    main()

