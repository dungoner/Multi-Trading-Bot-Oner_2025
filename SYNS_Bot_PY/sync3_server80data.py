#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNC SERVER 80 DATA - Bot 3 Integrated (STANDALONE)
====================================================
Mode 0: SENDER (Bot 1) - Transmit CSDL from SPY Bot
Mode 1: RECEIVER (Bot 2) - Pull CSDL from Bot 1

Author: Claude
Date: 2025-10-25
Version: 3.0 (STANDALONE - Contains full Bot 1 + Bot 2 code)

⚠️ THIS FILE IS COMPLETELY STANDALONE ⚠️
File size: ~4500 lines (Bot 1 + Bot 2)
"""

import json
import os
import sys

# ==============================================================================
# LOAD CONFIG & MODE SELECTION
# ==============================================================================

BOT_CONFIG_FILE = "bot_config.json"

print("=" * 60)
print("SYNC SERVER 80 DATA - Bot 3 (STANDALONE)")
print("=" * 60)

# Load config
if not os.path.exists(BOT_CONFIG_FILE):
    print(f"ERROR: Config file not found: {BOT_CONFIG_FILE}")
    sys.exit(1)

with open(BOT_CONFIG_FILE, 'r') as f:
    bot_config = json.load(f)

mode = bot_config.get("mode", 0)
print(f"Selected mode: {mode}")

if mode == 0:
    print("Mode: SENDER (Bot 1)")
elif mode == 1:
    print("Mode: RECEIVER (Bot 2)")
else:
    print(f"ERROR: Invalid mode: {mode}")
    sys.exit(1)

print("=" * 60)
print()

# ==============================================================================
# MODE 0: SENDER (Bot 1) - FULL CODE EMBEDDED
# ==============================================================================

if mode == 0:

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
            # Get the global QUIET_MODE variable
            # Note: bot_config is loaded at line 36-37
            quiet = bot_config.get('quiet_mode', False)

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
            "server": {
                "api_key": "9016",
                "vps_ip": "",
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
                    bot_config['server'] = old_config
                    # Remove _note field if it exists
                    bot_config['server'].pop('_note', None)
                    print(f"[CONFIG] Migrated server config from {CONFIG_FILE}")
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
                if 'server' not in bot_config:
                    bot_config['server'] = default_config['server']
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
            # Update sender section (Mode 0)
            bot_config['sender'] = new_config
            # Also update 'server' for backward compatibility
            bot_config['server'] = new_config
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
    # QUIET MODE LOGGING (Reduce console spam for VPS 24/7)
    # ==============================================================================

    # Use bot_config from global scope (already loaded at line 36-37)
    # Optimization: Avoid loading config file multiple times
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

    # Extract sender config from global bot_config (already loaded at line 36-37)
    # Optimization: Avoid loading config file multiple times
    config = bot_config.get('sender', {})
    # Global variables
    file_cache = {}      # Cache CSDL live files {symbol: {data, mtime, updates, size}}
    history_cache = {}   # Cache CSDL history files {symbol: {data, mtime, filepath}}
    server_start_time = time.time()
    cache_lock = Lock()  # Thread safety for cache access
    shutdown_flag = False  # Graceful shutdown flag
    ctrl_c_count = 0    # Count Ctrl+C presses
    last_ctrl_c_time = 0  # Last Ctrl+C timestamp
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
                                            print(f"[POLLING] Invalid data structure in {symbol}: expected 7+ rows")
                                            continue
                                    except json.JSONDecodeError as e:
                                        print(f"[POLLING] Invalid JSON in {symbol}: {e}")
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
                                    print(f"[POLLING] Error reading LIVE {symbol}: {e}")
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
                                "filepath": filepath
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
                # OPTIMIZATION: Smart sleep based on polling_interval
                if config["polling_interval"] == 1:
                    time.sleep(1)
                elif config["polling_interval"] == 2:
                    time.sleep(2)  # Sleep 2s to next even second
                else:
                    time.sleep(config["polling_interval"])  # Fallback
            except Exception as e:
                print(f"[POLLING] Error in polling thread: {e}")
                # Same smart sleep in error handler
                if config["polling_interval"] == 1:
                    time.sleep(1)
                elif config["polling_interval"] == 2:
                    time.sleep(2)
                else:
                    time.sleep(config["polling_interval"])
    # ==============================================================================
    # REMOVED: EA ACTIVITY, REQUEST STATISTICS, AUTO-RESTART (Simplified)
    # ==============================================================================
    # These features were removed for simplification:
    # - EA Activity tracking (60s/10m/1h counters) → Now use simple file_cache status
    # - Request Statistics (24h stats + file backup) → Removed (unnecessary complexity)
    # - Auto-restart thread (Weekly Saturday restart) → Removed (manual restart is fine)
    # Dashboard now shows simple "EA CONNECTION STATUS" from file_cache only.
    # ==============================================================================
    # SYMLINK MANAGER (MT4/MT5 Folder Symbolic Links)
    # ==============================================================================
    def load_symlink_config():
        """Load symlink configuration (backward compatible wrapper)"""
        bot_config = load_bot_config()
        return bot_config.get('symlink', {})
    def save_symlink_config(symlink_config):
        """Save symlink configuration while preserving other sections"""
        try:
            # Load current bot config
            bot_config = load_bot_config()
            # Update only the symlink section
            bot_config['symlink'] = symlink_config
            # Save unified config
            return save_bot_config(bot_config)
        except Exception as e:
            print(f"[SYMLINK] Error saving config: {e}")
            return False
    import subprocess
    import shutil
    def is_symlink(path):
        """Check if a path is a symbolic link"""
        return os.path.islink(path)
    def is_junction(path):
        """Check if a path is a junction (Windows)"""
        if not os.path.exists(path):
            return False
        import stat
        try:
            return bool(os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except:
            return False
    def remove_directory_safe(path):
        """Remove a directory (regular or symlink/junction)"""
        if not os.path.exists(path):
            return True, "Path does not exist"
        try:
            if is_symlink(path) or is_junction(path):
                # Remove symlink/junction (do not delete target)
                os.rmdir(path)
            else:
                # Regular directory - backup first
                backup_path = f"{path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(path, backup_path)
                return True, f"Backed up to {backup_path}"
            return True, "Removed successfully"
        except Exception as e:
            return False, str(e)
    def create_symlink(source, target):
        """Create symbolic link from target to source
        Args:
            source: The actual folder (E:/PRO_ONER/MQL4/Files)
            target: The MT4/MT5 folder path (C:/Program Files/MT4/MQL4/Files)
        """
        try:
            # Ensure source exists
            if not os.path.exists(source):
                return False, f"Source folder does not exist: {source}"
            # Remove target if exists
            if os.path.exists(target):
                success, msg = remove_directory_safe(target)
                if not success:
                    return False, f"Failed to remove existing folder: {msg}"
            # Create symlink using mklink /D (Windows)
            cmd = f'mklink /D "{target}" "{source}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Symlink created successfully"
            else:
                return False, f"mklink failed: {result.stderr}"
        except Exception as e:
            return False, str(e)
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
    def build_user_table(data):
        """Build HTML table for USER data (current signals only)"""
        if not data or not isinstance(data, dict):
            return '<p>No data available</p>'
        rows = data.get('data', [])
        if not rows:
            return '<p>No timeframe data available</p>'
        html = '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse; font-size: 13px; background: white; margin-bottom: 30px;"><thead><tr style="background: #2196F3; color: white; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;">'
        html += '<th style="padding: 12px; text-align: left; border: 1px solid #d0d0d0;">Timeframe</th>'
        html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">Signal</th>'
        html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Price</th>'
        html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">Cross</th>'
        html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">Timestamp</th>'
        html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Price Diff</th>'
        html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Time Diff</th>'
        html += '<th style="padding: 12px; text-align: center; border: 1px solid #d0d0d0;">News</th>'
        html += '<th style="padding: 12px; text-align: right; border: 1px solid #d0d0d0;">Max Loss</th>'
        html += '</tr></thead><tbody>'
        for row in rows:
            html += '<tr style="border-bottom: 1px solid #e0e0e0;">'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; font-weight: bold;">{row.get("timeframe_name", row.get("timeframe", "-"))}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center;">{build_signal_badge(row.get("signal", 0))}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace;">{row.get("price", 0):.5f}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center; font-size: 11px; color: #666;">{format_timestamp(row.get("cross", 0))}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center; font-size: 11px;">{format_timestamp(row.get("timestamp", 0))}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace;">{row.get("pricediff", 0):.2f}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right;">{row.get("timediff", 0)}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center;">{row.get("news", 0)}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace; color: #f44336;">{row.get("max_loss", 0):.2f}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        return html
    def build_history_tables(data):
        """Build HTML tables for HISTORY data (7 signals per timeframe)"""
        if not data or not isinstance(data, dict):
            return '<p>No history data available</p>'
        history = data.get('history', {})
        history_count = data.get('history_count', {})
        if not history:
            return '<p>No history data available</p>'
        html = ''
        timeframes = ['m1', 'm5', 'm15', 'm30', 'h1', 'h4', 'd1']
        timeframe_names = {'m1': 'M1', 'm5': 'M5', 'm15': 'M15', 'm30': 'M30', 'h1': 'H1', 'h4': 'H4', 'd1': 'D1'}
        for tf in timeframes:
            signals = history.get(tf, [])
            count = history_count.get(tf, 0)
            if not signals or count == 0:
                continue
            tf_name = timeframe_names.get(tf, tf.upper())
            html += f'''
            <div style="margin-bottom: 30px;">
                <h4 style="margin: 15px 0 10px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px;">
                    📊 {tf_name} History ({count} signals)
                </h4>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; background: white;">
                        <thead>
                            <tr style="background: #e3f2fd; color: #1976d2; text-transform: uppercase; font-size: 10px; letter-spacing: 1px;">
                                <th style="padding: 10px; text-align: center; border: 1px solid #d0d0d0;">#</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #d0d0d0;">Signal</th>
                                <th style="padding: 10px; text-align: right; border: 1px solid #d0d0d0;">Price</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #d0d0d0;">Cross</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #d0d0d0;">Timestamp</th>
                                <th style="padding: 10px; text-align: right; border: 1px solid #d0d0d0;">Price Diff</th>
                                <th style="padding: 10px; text-align: right; border: 1px solid #d0d0d0;">Time Diff</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #d0d0d0;">News</th>
                            </tr>
                        </thead>
                        <tbody>
            '''
            for idx, signal in enumerate(signals, 1):
                html += '<tr style="border-bottom: 1px solid #e0e0e0;">'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: center; color: #999; font-weight: bold;">{idx}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: center;">{build_signal_badge(signal.get("signal", 0))}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace;">{signal.get("price", 0):.5f}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: center; font-size: 10px; color: #666;">{format_timestamp(signal.get("cross", 0))}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: center; font-size: 10px;">{format_timestamp(signal.get("timestamp", 0))}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: right; font-family: monospace;">{signal.get("pricediff", 0):.2f}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: right;">{signal.get("timediff", 0)}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e0e0e0; text-align: center;">{signal.get("news", 0)}</td>'
                html += '</tr>'
            html += '''
                        </tbody>
                    </table>
                </div>
            </div>
            '''
        return html
    def check_mt_platform(mt_path):
        """Check if MT path is valid and detect MQL4 or MQL5
        Returns: (is_valid, platform_type, mql_path)
        - platform_type: 'MT4' or 'MT5'
        - mql_path: Full path to MQL4 or MQL5 folder
        """
        mt_path = mt_path.strip().rstrip('\\').rstrip('/')
        # Check for MQL4
        mql4_path = os.path.join(mt_path, "MQL4")
        if os.path.exists(mql4_path) and os.path.isdir(mql4_path):
            return True, "MT4", mql4_path
        # Check for MQL5
        mql5_path = os.path.join(mt_path, "MQL5")
        if os.path.exists(mql5_path) and os.path.isdir(mql5_path):
            return True, "MT5", mql5_path
        return False, None, None
    def get_folder_status(mql_path, folder_name):
        """Check status of a folder in MQL path
        Returns: (exists, is_symlink, target_path)
        """
        folder_path = os.path.join(mql_path, folder_name)
        if not os.path.exists(folder_path):
            return False, False, None
        if is_symlink(folder_path) or is_junction(folder_path):
            # Get target
            try:
                target = os.readlink(folder_path)
                return True, True, target
            except:
                return True, True, "Unknown"
        else:
            return True, False, None
    # ==============================================================================
    # AUTO-START MANAGER HELPERS
    # ==============================================================================
    def load_autostart_config():
        """Load auto-start configuration (backward compatible wrapper)"""
        bot_config = load_bot_config()
        autostart_config = bot_config.get('autostart', {})
        # Ensure mt_platforms exists
        if 'mt_platforms' not in autostart_config:
            autostart_config['mt_platforms'] = []
        return autostart_config
    def save_autostart_config(config_data):
        """Save auto-start configuration while preserving other sections"""
        try:
            # Load current bot config
            bot_config = load_bot_config()
            # Update only the autostart section
            bot_config['autostart'] = config_data
            # Save unified config
            return save_bot_config(bot_config)
        except Exception as e:
            print(f"[AUTOSTART] Error saving config: {e}")
            return False
    def check_task_status(task_name):
        """Check if Windows Task Scheduler task exists and is enabled"""
        try:
            result = subprocess.run(['schtasks', '/Query', '/TN', task_name, '/FO', 'LIST'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout
                # Parse output to get status
                status_line = [line for line in output.split('\n') if 'Status:' in line]
                status = status_line[0].split(':', 1)[1].strip() if status_line else 'Unknown'
                return {
                    "installed": True,
                    "status": status
                }
            else:
                return {"installed": False, "status": "Not installed"}
        except Exception as e:
            return {"installed": False, "status": f"Error: {str(e)}"}
    def install_autostart_task(config_data):
        """Install Windows Task Scheduler task for auto-start with restart-on-failure"""
        task_name = config_data.get('task_name', 'SYNS_Bot_AutoStart')
        bot_folder = config_data.get('bot_folder', '')
        start_script = config_data.get('start_script', 'START_SERVER.bat')
        restart_attempts = config_data.get('restart_attempts', 999)
        restart_interval = config_data.get('restart_interval_minutes', 1)
        bat_path = os.path.join(bot_folder, start_script)
        # Check if file exists
        if not os.path.exists(bat_path):
            return {"success": False, "message": f"File not found: {bat_path}"}
        try:
            # Delete existing task if any
            subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                          capture_output=True, timeout=10)
            # Create XML task definition with restart-on-failure settings
            xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <RegistrationInfo>
        <Date>{datetime.now().isoformat()}</Date>
        <Author>SYNS Bot Auto-Start Manager</Author>
        <URI>\\{task_name}</URI>
      </RegistrationInfo>
      <Triggers>
        <BootTrigger>
          <Enabled>true</Enabled>
        </BootTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>HighestAvailable</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <AllowHardTerminate>false</AllowHardTerminate>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
          <StopOnIdleEnd>false</StopOnIdleEnd>
          <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
        <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
        <Priority>7</Priority>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>{bat_path}</Command>
          <WorkingDirectory>{bot_folder}</WorkingDirectory>
        </Exec>
      </Actions>
    </Task>'''
            # Save XML to temporary file
            xml_path = os.path.join(bot_folder, f'{task_name}_temp.xml')
            with open(xml_path, 'w', encoding='utf-16') as f:
                f.write(xml_content)
            # Create task from XML
            cmd = ['schtasks', '/Create', '/TN', task_name, '/XML', xml_path, '/F']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Delete temporary XML file
            try:
                os.remove(xml_path)
            except:
                pass
            if result.returncode == 0:
                return {"success": True, "message": f"Task '{task_name}' installed successfully! ✅ Auto-start on boot only (no auto-restart)"}
            else:
                return {"success": False, "message": f"Failed to create task: {result.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    def uninstall_autostart_task(task_name):
        """Uninstall Windows Task Scheduler task"""
        try:
            result = subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return {"success": True, "message": f"Task '{task_name}' uninstalled successfully!"}
            else:
                return {"success": False, "message": f"Task not found or already deleted"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    def install_mt_autostart_task(platform_config):
        """Install Windows Task Scheduler task for MT4/MT5 auto-start"""
        task_name = platform_config.get('task_name', '')
        mt_exe_path = platform_config.get('path', '')
        # Validate inputs
        if not task_name:
            return {"success": False, "message": "Task name is required"}
        if not mt_exe_path or not os.path.exists(mt_exe_path):
            return {"success": False, "message": f"MT4/MT5 executable not found: {mt_exe_path}"}
        # Get working directory (folder containing the exe)
        mt_folder = os.path.dirname(mt_exe_path)
        try:
            # Delete existing task if any
            subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                          capture_output=True, timeout=10)
            # Create XML task definition for MT4/MT5
            xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <RegistrationInfo>
        <Date>{datetime.now().isoformat()}</Date>
        <Author>SYNS Bot Auto-Start Manager</Author>
        <URI>\\{task_name}</URI>
      </RegistrationInfo>
      <Triggers>
        <BootTrigger>
          <Enabled>true</Enabled>
          <Delay>PT30S</Delay>
        </BootTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>HighestAvailable</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <AllowHardTerminate>false</AllowHardTerminate>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
          <StopOnIdleEnd>false</StopOnIdleEnd>
          <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
        <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
        <Priority>7</Priority>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>{mt_exe_path}</Command>
          <WorkingDirectory>{mt_folder}</WorkingDirectory>
        </Exec>
      </Actions>
    </Task>'''
            # Save XML to temporary file
            xml_path = os.path.join(os.path.dirname(__file__), f'{task_name}_temp.xml')
            with open(xml_path, 'w', encoding='utf-16') as f:
                f.write(xml_content)
            # Create task from XML
            cmd = ['schtasks', '/Create', '/TN', task_name, '/XML', xml_path, '/F']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Delete temporary XML file
            try:
                os.remove(xml_path)
            except:
                pass
            if result.returncode == 0:
                return {"success": True, "message": f"Task '{task_name}' installed successfully! ✅ Auto-start on boot (30s delay)"}
            else:
                return {"success": False, "message": f"Failed to create task: {result.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    def uninstall_mt_autostart_task(task_name):
        """Uninstall MT4/MT5 Windows Task Scheduler task"""
        return uninstall_autostart_task(task_name)
    def check_mt_task_status(task_name):
        """Check if MT4/MT5 Windows Task Scheduler task exists"""
        return check_task_status(task_name)
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
        log_print(f"[API] Sent {clean_symbol} to Bot 2 at {client_ip} (mtime: {mtime})", "INFO")
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
        # log_print(f"[API] Symbols list requested: {len(symbols)} symbols available", "INFO")
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

            <!-- Mode Selector Panel -->
            <div class="panel" style="background: #f5f5f5; border-left: 4px solid #00A651;">
                <div class="panel-body" style="padding: 12px 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 12px; color: #666;">
                            ⚙️ <strong>Currently Running:</strong> <span style="color: #00A651; font-weight: bold;">MODE 0 (SENDER)</span>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <a href="/" class="btn active" style="background: #00A651; color: white; border-color: #00A651;">📊 MODE 0 DATA</a>
                            <a href="/mode1-view" class="btn" style="background: white; color: #666; border-color: #d0d0d0;">📥 MODE 1 DATA</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CSDL Files Panel -->
            <div class="panel">
                <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>CSDL Files — Updated {{ last_poll }} ago</span>
                    <div style="display: flex; gap: 5px;">
                        <a href="/csdl/user" class="btn" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📜 CSDL 1 USER</a>
                        <a href="/csdl/ea-live" class="btn" style="background: white; color: #00A651; border-color: white; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📊 CSDL 2 EA LIVE</a>
                        <a href="/csdl/history" class="btn" style="background: #FF6600; color: white; border-color: #FF6600; padding: 6px 12px; font-size: 10px; margin: 0; text-decoration: none;">📊 MONTHLY HISTORY</a>
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
            <!-- EA Connection Status Panel (Simplified) -->
            <div class="panel">
                <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>🤖 EA CONNECTION STATUS — Simple Monitoring</span>
                    <button class="btn" onclick="location.reload()" style="background: #00A651; color: white; padding: 6px 12px; font-size: 10px; margin: 0;">🔄 REFRESH</button>
                </div>
                <div class="panel-body">
                    <p style="font-size: 11px; color: #666; margin-bottom: 15px;">
                        💡 Shows symbols with active CSDL data. Click REFRESH to update.
                    </p>
                    <table>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Status</th>
                                <th>Last Update (Server)</th>
                                <th>Last Update (VN)</th>
                                <th>Time Ago</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for symbol in symbols %}
                            <tr>
                                <td><strong>{{ symbol.name }}</strong></td>
                                <td><span class="{{ symbol.status_class }}">{{ symbol.status_icon }}</span></td>
                                <td>{{ symbol.last_update_server }}</td>
                                <td>{{ symbol.last_update_vn }}</td>
                                <td>{{ symbol.ago }}</td>
                            </tr>
                            {% endfor %}
                            {% if not symbols %}
                            <tr>
                                <td colspan="5" style="text-align: center; color: #999; padding: 40px;">No CSDL data yet</td>
                            </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- Action Buttons -->
            <div style="text-align: center; margin: 20px 0;">
                <a href="/symlink" class="btn">🔗 Symlink Manager</a>
                <a href="/auto-start" class="btn">🔄 Auto-Start Manager</a>
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
        return render_template_string(
            DASHBOARD_HTML,
            uptime=uptime,
            polling=config["polling_interval"],
            last_poll=f"{config['polling_interval']}s",
            symbols=symbols_data
        )

    @app_dashboard.route('/mode1-view')
    def dashboard_mode1_view():
        """Show warning: Mode 1 data not available (currently running Mode 0)"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mode 1 Data - Not Available</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }
                .container { max-width: 800px; margin: 50px auto; text-align: center; }
                .warning-box { background: #fff3cd; border: 2px solid #ffc107; padding: 40px; border-radius: 8px; }
                .warning-icon { font-size: 64px; margin-bottom: 20px; }
                h1 { color: #856404; margin-bottom: 20px; }
                p { color: #666; font-size: 14px; line-height: 1.8; margin: 15px 0; }
                .btn { display: inline-block; padding: 12px 24px; background: #00A651; color: white;
                       text-decoration: none; border-radius: 4px; margin: 20px 10px 0; font-size: 14px; }
                .btn:hover { background: #008040; }
                .btn-secondary { background: #6c757d; }
                .btn-secondary:hover { background: #5a6268; }
                .info { background: #f5f5f5; padding: 20px; margin-top: 30px; border-left: 4px solid #00A651; }
                .info strong { color: #00A651; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="warning-box">
                    <div class="warning-icon">⚠️</div>
                    <h1>MODE 1 DATA NOT AVAILABLE</h1>
                    <p>You are currently running <strong>MODE 0 (SENDER)</strong>.</p>
                    <p>MODE 1 data is not available because the receiver is not running.</p>
                    <div class="info">
                        <p style="margin: 0;">
                            💡 <strong>To view Mode 1 data:</strong><br>
                            Go to Settings → Change mode to "1" → Restart Bot 3
                        </p>
                    </div>
                    <a href="/" class="btn">← Back to MODE 0 Dashboard</a>
                    <a href="/settings" class="btn btn-secondary">⚙️ Go to Settings</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @app_dashboard.route('/stats')
    def dashboard_stats():
        """Statistics page"""
        stats_summary = get_stats_summary()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - Statistics</title>
            <style>
                body { font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .panel { border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }
                .panel-header { padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651; color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }
                .panel-body { padding: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #f0f0f0; }
                .btn { display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                       background: white; text-decoration: none; color: #2c2c2c; margin: 10px; }
                .btn:hover { background: #2c2c2c; color: white; }
                .bar { height: 20px; background: #4caf50; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="panel">
                    <div class="panel-header">REQUEST STATISTICS — Last 24 hours</div>
                    <div class="panel-body">
                        <table>
                            <tr>
                                <th>Symbol</th>
                                <th>Requests</th>
                                <th>Unique IPs</th>
                                <th>Chart</th>
                            </tr>
        """
        for symbol, data in sorted(stats_summary.items()):
            count = data["request_count"]
            ips = data["unique_ips"]
            bar_width = min(count * 2, 400)  # Max 400px
            html += f"""
                            <tr>
                                <td><strong>{symbol}</strong></td>
                                <td>{count:,}</td>
                                <td>{ips}</td>
                                <td><div class="bar" style="width: {bar_width}px;"></div></td>
                            </tr>
            """
        html += """
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
    @app_dashboard.route('/history')
    def dashboard_history():
        """Request history page"""
        # Collect all requests from all symbols
        all_requests = []
        with stats_lock:
            for symbol, data in stats.items():
                for req in data["last_requests"]:
                    all_requests.append({
                        "symbol": symbol,
                        "time": req["time"],
                        "ip": req["ip"],
                        "status": req["status"]
                    })
        # Sort by time (newest first)
        all_requests.sort(key=lambda x: x["time"], reverse=True)
        # Take last 50
        all_requests = all_requests[:50]
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - History</title>
            <style>
                body { font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .panel { border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }
                .panel-header { padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651; color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }
                .panel-body { padding: 20px; }
                table { width: 100%; border-collapse: collapse; font-size: 13px; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #f0f0f0; }
                .btn { display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                       background: white; text-decoration: none; color: #2c2c2c; margin: 10px; }
                .btn:hover { background: #2c2c2c; color: white; }
                .status-200 { color: #4caf50; }
                .status-401 { color: #ff9800; }
                .status-404 { color: #f44336; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="panel">
                    <div class="panel-header">REQUEST HISTORY — Last 50 requests</div>
                    <div class="panel-body">
                        <table>
                            <tr>
                                <th>Time (Server)</th>
                                <th>Time (VN)</th>
                                <th>IP Address</th>
                                <th>Symbol</th>
                                <th>Status</th>
                            </tr>
        """
        for req in all_requests:
            req_time = datetime.fromtimestamp(req["time"])
            server_time = (req_time + timedelta(hours=config["server_timezone_offset"])).strftime("%H:%M:%S")
            vn_time = (req_time + timedelta(hours=config["vietnam_timezone_offset"])).strftime("%H:%M:%S")
            status_class = f"status-{req['status']}"
            status_text = "OK" if req["status"] == 200 else f"Error {req['status']}"
            html += f"""
                            <tr>
                                <td>{server_time}</td>
                                <td>{vn_time}</td>
                                <td>{req['ip']}</td>
                                <td><strong>{req['symbol']}</strong></td>
                                <td class="{status_class}">{status_text}</td>
                            </tr>
            """
        html += """
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
            # Save to file
            if save_config(config):
                return jsonify({"success": True, "message": "Configuration saved successfully!"})
            else:
                return jsonify({"success": False, "error": "Failed to save config"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    @app_dashboard.route('/api/config/save-unified', methods=['POST'])
    def api_save_config_unified():
        """API endpoint to save unified configuration for both Mode 0 and Mode 1"""
        try:
            data = request.get_json()

            # Load current bot_config.json
            if os.path.exists(BOT_CONFIG_FILE):
                with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    bot_config = json.load(f)
            else:
                bot_config = {}

            # Update mode
            if 'mode' in data:
                bot_config['mode'] = int(data['mode'])

            # Update quiet_mode (root level)
            if 'quiet_mode' in data:
                bot_config['quiet_mode'] = (data['quiet_mode'] == 'true' or data['quiet_mode'] == True)

            # Update sender settings (Mode 0)
            if 'sender' in data and data['sender']:
                if 'sender' not in bot_config:
                    bot_config['sender'] = {}
                for key, value in data['sender'].items():
                    bot_config['sender'][key] = value

                # Also update 'server' section for backward compatibility
                if 'server' not in bot_config:
                    bot_config['server'] = {}
                for key, value in data['sender'].items():
                    bot_config['server'][key] = value

            # Update receiver settings (Mode 1)
            if 'receiver' in data and data['receiver']:
                if 'receiver' not in bot_config:
                    bot_config['receiver'] = {}
                for key, value in data['receiver'].items():
                    bot_config['receiver'][key] = value

            # Save to file
            with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(bot_config, f, indent=2, ensure_ascii=False)

            # Update runtime config if current mode matches
            current_mode = bot_config.get('mode', 0)
            if current_mode == 0 and 'sender' in data:
                # Update runtime config for Mode 0
                for key, value in data['sender'].items():
                    if key in config:
                        config[key] = value

            # Update runtime QUIET_MODE (applies to both Mode 0 and Mode 1)
            if 'quiet_mode' in data:
                global QUIET_MODE
                QUIET_MODE = bot_config.get('quiet_mode', False)

            return jsonify({
                "success": True,
                "message": f"Settings saved successfully! Current mode: {current_mode}. Please RESTART bot if you changed mode."
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    @app_dashboard.route('/settings')
    def dashboard_settings():
        """Unified Settings page for Bot 3 - supports both Mode 0 (SENDER) and Mode 1 (RECEIVER)"""

        # Load bot_config.json to get current mode and all settings
        try:
            with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                bot_config = json.load(f)
        except:
            bot_config = {"mode": 0, "sender": {}, "receiver": {}}

        current_mode = bot_config.get("mode", 0)

        # Load sender settings (Mode 0) - fallback to runtime config
        if current_mode == 0:
            sender_config = config  # Use runtime config directly when in Mode 0
        else:
            sender_config = bot_config.get("sender", {
                "vps_ip": "",
                "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/",
                "history_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/",
                "polling_interval": 1,
                "server_timezone_offset": 2,
                "vietnam_timezone_offset": 7
            })

        # Load receiver settings (Mode 1) - fallback to defaults
        receiver_config = bot_config.get("receiver", {
            "bot1_url": "",
            "output_folder": "C:/PRO_ONER/MQL4/Files/DataAutoOner3/",
            "output_folder2": "C:/PRO_ONER/MQL4/Files/DataAutoOner2/",
            "polling_interval": 1,
            "http_timeout": 5
        })

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot 3 Settings - Unified Configuration</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
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
                .mode-section {{ display: none; }}
                .mode-section.active {{ display: block; }}
                .mode-badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 10px;
                             font-weight: bold; margin-left: 10px; }}
                .mode-0 {{ background: #2196F3; color: white; }}
                .mode-1 {{ background: #FF9800; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- MODE SELECTOR -->
                <div class="panel">
                    <div class="panel-header">🔄 BOT MODE SELECTOR</div>
                    <div class="panel-body">
                        <div class="note">
                            <strong>⚠️ Current Mode:</strong>
                            <span class="mode-badge mode-{current_mode}" id="currentModeBadge">
                                MODE {current_mode} - {{'SENDER (Bot 1)' if current_mode == 0 else 'RECEIVER (Bot 2)'}}
                            </span><br>
                            • Thay đổi mode sẽ yêu cầu <strong>RESTART BOT</strong> để có hiệu lực<br>
                            • Mode 0: SENDER - Truyền CSDL từ SPY Bot qua Port 80<br>
                            • Mode 1: RECEIVER - Nhận CSDL từ Bot 1 và ghi local files
                        </div>
                        <div class="form-group">
                            <label>Select Bot Mode</label>
                            <select id="modeSelector" name="mode">
                                <option value="0" {'selected' if current_mode == 0 else ''}>Mode 0 - SENDER (Bot 1)</option>
                                <option value="1" {'selected' if current_mode == 1 else ''}>Mode 1 - RECEIVER (Bot 2)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div id="alert" class="alert"></div>

                <form id="settingsForm">
                    <!-- MODE 0: SENDER SETTINGS -->
                    <div id="mode0Settings" class="mode-section {'active' if current_mode == 0 else ''}">
                        <div class="panel">
                            <div class="panel-header">⚙️ MODE 0: SENDER SETTINGS (Bot 1)</div>
                            <div class="panel-body">
                                <div class="form-group">
                                    <label>VPS IP Address</label>
                                    <input type="text" name="sender_vps_ip" value="{sender_config.get('vps_ip', '')}" placeholder="your-domain.duckdns.org">
                                </div>
                                <div class="form-group">
                                    <label>CSDL Folder Path (Source from SPY Bot)</label>
                                    <input type="text" name="sender_csdl_folder" value="{sender_config.get('csdl_folder', 'E:/PRO_ONER/MQL4/Files/DataAutoOner3/')}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner3/">
                                </div>
                                <div class="form-group">
                                    <label>History Folder Path</label>
                                    <input type="text" name="sender_history_folder" value="{sender_config.get('history_folder', 'E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/')}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/">
                                </div>
                                <div class="form-group">
                                    <label>File Polling Interval (Check CSDL changes)</label>
                                    <select name="sender_polling_interval">
                                        <option value="1" {'selected' if sender_config.get('polling_interval', 1) == 1 else ''}>1 second (Fast - Scan every 1s)</option>
                                        <option value="2" {'selected' if sender_config.get('polling_interval', 1) == 2 else ''}>2 seconds (Normal - Scan on EVEN seconds only)</option>
                                    </select>
                                    <p style="font-size: 11px; color: #666; margin-top: 5px; line-height: 1.4;">
                                        💡 <strong>Fast:</strong> Scan every 1 second (high CPU, fastest response)<br>
                                        💡 <strong>Normal:</strong> Scan on EVEN seconds only (0,2,4,6,8...) - Optimized for Bot SPY odd-second writes
                                    </p>
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
                                    <input type="number" name="sender_timezone_offset" value="{sender_config.get('server_timezone_offset', 2)}" min="-12" max="14">
                                </div>
                                <div class="form-group">
                                    <label>Vietnam Timezone Offset (hours from GMT)</label>
                                    <input type="number" name="sender_vietnam_timezone_offset" value="{sender_config.get('vietnam_timezone_offset', 7)}" min="-12" max="14">
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                                    <p style="font-size: 11px; color: #999;">
                                        <strong>💡 Access Settings:</strong> <code>http://localhost:9070/settings</code><br>
                                        <strong>Ports:</strong> API: 80 | Dashboard: 9070
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- MODE 1: RECEIVER SETTINGS -->
                    <div id="mode1Settings" class="mode-section {'active' if current_mode == 1 else ''}">
                        <div class="panel">
                            <div class="panel-header">⚙️ MODE 1: RECEIVER SETTINGS (Bot 2)</div>
                            <div class="panel-body">
                                <div class="form-group">
                                    <label>Bot 1 URL (VPS Address with Port 80)</label>
                                    <input type="text" name="receiver_bot1_url" value="{receiver_config.get('bot1_url', '')}" placeholder="http://your-domain.duckdns.org:80">
                                </div>
                                <div class="form-group">
                                    <label>Output Folder 3 (Main - DataAutoOner3)</label>
                                    <input type="text" name="receiver_output_folder" value="{receiver_config.get('output_folder', 'C:/PRO_ONER/MQL4/Files/DataAutoOner3/')}" placeholder="C:/PRO_ONER/MQL4/Files/DataAutoOner3/">
                                </div>
                                <div class="form-group">
                                    <label>Output Folder 2 (Backup - DataAutoOner2)</label>
                                    <input type="text" name="receiver_output_folder2" value="{receiver_config.get('output_folder2', 'C:/PRO_ONER/MQL4/Files/DataAutoOner2/')}" placeholder="C:/PRO_ONER/MQL4/Files/DataAutoOner2/">
                                </div>
                                <div class="form-group">
                                    <label>Polling Interval (Pull from Bot 1)</label>
                                    <select name="receiver_polling_interval">
                                        <option value="1" selected>1 second (RECEIVER pulls via HTTP - no I/O conflict)</option>
                                    </select>
                                    <p style="font-size: 11px; color: #666; margin-top: 5px;">
                                        💡 Bot 2 (RECEIVER) pulls data via HTTP from Bot 1, not reading files directly.<br>
                                        No need for even-second sync. Always use 1 second polling.
                                    </p>
                                </div>
                                <div class="form-group">
                                    <label>HTTP Timeout (seconds)</label>
                                    <input type="number" name="receiver_http_timeout" value="{receiver_config.get('http_timeout', 5)}" min="1" max="30">
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                                    <p style="font-size: 11px; color: #999;">
                                        <strong>💡 Access Settings:</strong> <code>http://localhost:9070/settings</code><br>
                                        <strong>Dashboard Port:</strong> 9070
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn btn-save">💾 SAVE ALL SETTINGS</button>
                        <a href="/" class="btn">← Back to Dashboard</a>
                    </div>
                </form>
            </div>

            <script>
                // Mode selector logic
                const modeSelector = document.getElementById('modeSelector');
                const mode0Settings = document.getElementById('mode0Settings');
                const mode1Settings = document.getElementById('mode1Settings');
                const modeBadge = document.getElementById('currentModeBadge');

                modeSelector.addEventListener('change', function() {{
                    const selectedMode = this.value;
                    if (selectedMode === '0') {{
                        mode0Settings.classList.add('active');
                        mode1Settings.classList.remove('active');
                        modeBadge.className = 'mode-badge mode-0';
                        modeBadge.textContent = 'MODE 0 - SENDER (Bot 1)';
                    }} else {{
                        mode0Settings.classList.remove('active');
                        mode1Settings.classList.add('active');
                        modeBadge.className = 'mode-badge mode-1';
                        modeBadge.textContent = 'MODE 1 - RECEIVER (Bot 2)';
                    }}
                }});

                // Form submission
                const form = document.getElementById('settingsForm');
                const alert = document.getElementById('alert');

                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();

                    const formData = new FormData(form);
                    const mode = modeSelector.value;
                    const data = {{ mode: parseInt(mode) }};

                    // Collect sender settings
                    data.sender = {{}};
                    if (formData.get('sender_vps_ip')) data.sender.vps_ip = formData.get('sender_vps_ip');
                    if (formData.get('sender_csdl_folder')) data.sender.csdl_folder = formData.get('sender_csdl_folder');
                    if (formData.get('sender_history_folder')) data.sender.history_folder = formData.get('sender_history_folder');
                    if (formData.get('sender_polling_interval')) data.sender.polling_interval = parseInt(formData.get('sender_polling_interval'));
                    if (formData.get('sender_server_timezone_offset')) data.sender.server_timezone_offset = parseInt(formData.get('sender_server_timezone_offset'));
                    if (formData.get('sender_vietnam_timezone_offset')) data.sender.vietnam_timezone_offset = parseInt(formData.get('sender_vietnam_timezone_offset'));

                    // Collect receiver settings
                    data.receiver = {{}};
                    if (formData.get('receiver_bot1_url')) data.receiver.bot1_url = formData.get('receiver_bot1_url');
                    if (formData.get('receiver_output_folder')) data.receiver.output_folder = formData.get('receiver_output_folder');
                    if (formData.get('receiver_output_folder2')) data.receiver.output_folder2 = formData.get('receiver_output_folder2');
                    if (formData.get('receiver_polling_interval')) data.receiver.polling_interval = parseInt(formData.get('receiver_polling_interval'));
                    if (formData.get('receiver_http_timeout')) data.receiver.http_timeout = parseInt(formData.get('receiver_http_timeout'));

                    // Collect quiet_mode (root level)
                    if (formData.get('quiet_mode')) data.quiet_mode = formData.get('quiet_mode');

                    try {{
                        const response = await fetch('/api/config/save-unified', {{
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
                            }}, 3000);
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
    @app_dashboard.route('/csdl/user')
    def dashboard_csdl_user():
        """CSDL 1 USER - List of SYMBOL.json files (no _LIVE)"""
        # Get available symbols with USER data (history_cache = SYMBOL.json without _LIVE)
        symbols_list = []
        with cache_lock:
            for symbol in sorted(history_cache.keys()):
                cache = history_cache[symbol]
                # Read file on-demand if not loaded yet
                if cache["data"] is None:
                    filepath = cache["filepath"]
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            cache["data"] = json.load(f)
                            cache["mtime"] = os.path.getmtime(filepath)
                    except:
                        continue
                if cache["data"] is not None:
                    filename = os.path.basename(cache["filepath"])
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
                                    <a href="/csdl/user/{sym['name']}" class="btn btn-small">📜 View Data</a>
                                </td>
                            </tr>
            """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - CSDL 1 USER</title>
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
                    <div class="panel-header">📜 CSDL 1 USER — Symbol.json Files (for User Analysis)</div>
                    <div class="panel-body">
                        <div class="info">
                            <strong>About CSDL 1 USER:</strong><br>
                            • Files: SYMBOL.json (without _LIVE suffix)<br>
                            • Contains signal data with history (pricediff, timediff)<br>
                            • Click "View Data" to see full JSON for analysis
                        </div>
                        <table>
                            <tr>
                                <th>Symbol</th>
                                <th>Filename</th>
                                <th>Action</th>
                            </tr>
                            {rows_html if rows_html else '<tr><td colspan="3" style="text-align: center; color: #999; padding: 40px;">No USER files found</td></tr>'}
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
    @app_dashboard.route('/csdl/user/<symbol>')
    def dashboard_view_user_data(symbol):
        """View CSDL 1 USER data for a symbol (SYMBOL.json without _LIVE)"""
        with cache_lock:
            if symbol not in history_cache or history_cache[symbol]["data"] is None:
                # Try to load on-demand
                if symbol in history_cache:
                    filepath = history_cache[symbol]["filepath"]
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            history_cache[symbol]["data"] = json.load(f)
                            history_cache[symbol]["mtime"] = os.path.getmtime(filepath)
                    except:
                        pass
            if symbol not in history_cache or history_cache[symbol]["data"] is None:
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
                        <div class="error">❌ Error: Symbol "{symbol}" not found or no USER data available</div>
                        <a href="/csdl/user" class="btn">← Back to USER List</a>
                    </div>
                </body>
                </html>
                """, 404
            # Get USER data
            user_data = history_cache[symbol]["data"]
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - {symbol} USER Data</title>
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
                    <div class="panel-header">📜 {symbol} — CSDL 1 USER DATA</div>
                    <div class="panel-body">
                        <div class="info">
                            <strong>Symbol:</strong> {symbol}<br>
                            <strong>File:</strong> {symbol}.json (USER data)<br>
                            <strong>Total Rows:</strong> {user_data.get('rows', 'N/A')}<br>
                            <strong>Columns:</strong> {user_data.get('columns', 'N/A')}<br>
                            <strong>Type:</strong> {user_data.get('type', 'N/A')}<br>
                            <strong>Last Update:</strong> {datetime.fromtimestamp(user_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S') if user_data.get('timestamp') else 'N/A'}
                        </div>
                        <h3 style="margin-top: 30px; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                            📍 Current Signals (7 Timeframes):
                        </h3>
                        {build_user_table(user_data)}
                        <h3 style="margin-top: 40px; margin-bottom: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #2196F3; border-bottom: 3px solid #2196F3; padding-bottom: 8px;">
                            📜 Signal History (Last 7 Signals per Timeframe):
                        </h3>
                        {build_history_tables(user_data)}
                    </div>
                </div>
                <div style="text-align: center;">
                    <a href="/csdl/user" class="btn">← Back to USER List</a>
                    <a href="/" class="btn">🏠 Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    @app_dashboard.route('/csdl/history')
    def dashboard_csdl_history():
        """MONTHLY HISTORY - List of symbols grouped"""
        # Read directly from history_folder (like CSDL1/CSDL2 pattern)
        history_folder = config.get("history_folder", "")
        files = []
        if history_folder and os.path.exists(history_folder):
            try:
                # Find all *.json files in HISTORY folder
                pattern = os.path.join(history_folder, "*.json")
                file_paths = glob.glob(pattern)
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    # Parse filename: SYMBOL_YYYY_MM.json
                    try:
                        name_part = filename.replace('.json', '')
                        parts = name_part.split('_')
                        if len(parts) >= 3:
                            symbol = '_'.join(parts[:-2])  # Handle symbols with underscores
                            year = int(parts[-2])
                            month = int(parts[-1])
                        else:
                            symbol = name_part
                            year = 0
                            month = 0
                    except:
                        symbol = filename
                        year = 0
                        month = 0
                    files.append({
                        "filename": filename,
                        "symbol": symbol,
                        "year": year,
                        "month": month
                    })
            except Exception as e:
                files = []
        # Group files by symbol
        symbols_dict = {}
        for f in files:
            symbol = f['symbol']
            if symbol not in symbols_dict:
                symbols_dict[symbol] = []
            symbols_dict[symbol].append(f)
        # Build symbols list with stats
        symbols_list = []
        for symbol, symbol_files in symbols_dict.items():
            # Sort files by year, month desc to get latest
            symbol_files.sort(key=lambda x: (x['year'], x['month']), reverse=True)
            latest = symbol_files[0] if symbol_files else None
            symbols_list.append({
                "symbol": symbol,
                "file_count": len(symbol_files),
                "latest_year": latest['year'] if latest else 0,
                "latest_month": latest['month'] if latest else 0
            })
        # Sort symbols alphabetically
        symbols_list.sort(key=lambda x: x['symbol'])
        # Build table rows - List symbols
        table_rows = ""
        if symbols_list:
            for sym_info in symbols_list:
                symbol = sym_info['symbol']
                file_count = sym_info['file_count']
                latest_year = sym_info['latest_year']
                latest_month = sym_info['latest_month']
                # Format latest month
                month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                latest_str = f"{month_names[latest_month]} {latest_year}" if latest_month > 0 else "N/A"
                table_rows += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{file_count} files</td>
                    <td>{latest_str}</td>
                    <td style="text-align: center;">
                        <a href="/csdl/history/{symbol}" class="btn" style="display: inline-block; padding: 5px 12px;">📊 View History</a>
                    </td>
                </tr>
                """
        else:
            table_rows = """
            <tr>
                <td colspan="4" style="text-align: center; padding: 20px; color: #999;">No history files found</td>
            </tr>
            """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - MONTHLY HISTORY</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; margin: 0; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                h1 {{ color: #333; text-align: center; border-bottom: 3px solid #00A651; padding-bottom: 10px; }}
                .info {{ background: #f0f0f0; padding: 10px; border-left: 4px solid #00A651; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                th {{ background: #00A651; color: white; padding: 12px; text-align: left; font-weight: bold; }}
                td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
                tr:hover {{ background: #f9f9f9; }}
                .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #00A651; color: white; text-decoration: none; border-radius: 3px; transition: background 0.3s; }}
                .btn:hover {{ background: #008040; }}
                .footer {{ text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 MONTHLY HISTORY</h1>
                <div class="info">
                    Total symbols: <strong>{len(symbols_list)}</strong> | Total files: <strong>{len(files)}</strong>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Total Files</th>
                            <th>Latest Month</th>
                            <th style="text-align: center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <div class="footer">
                    <a href="/" class="btn">🏠 Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    @app_dashboard.route('/csdl/history/<symbol>')
    def dashboard_history_symbol(symbol):
        """MONTHLY HISTORY - List months for a symbol with summary stats"""
        # Read directly from history_folder
        history_folder = config.get("history_folder", "")
        symbol_files = []
        all_years = set()  # Collect all available years
        if history_folder and os.path.exists(history_folder):
            try:
                # Find all *.json files for this symbol
                pattern = os.path.join(history_folder, "*.json")
                file_paths = glob.glob(pattern)
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    # Parse filename: SYMBOL_YYYY_MM.json
                    try:
                        name_part = filename.replace('.json', '')
                        parts = name_part.split('_')
                        if len(parts) >= 3:
                            file_symbol = '_'.join(parts[:-2])
                            year = int(parts[-2])
                            month = int(parts[-1])
                        else:
                            continue
                    except:
                        continue
                    # Only include files for this symbol
                    if file_symbol == symbol:
                        all_years.add(year)  # Track available years
                        # Read file to get summary stats
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            symbol_files.append({
                                "filename": filename,
                                "year": year,
                                "month": month,
                                "net_profit": data.get('net_profit', 0.0),
                                "win_rate": data.get('win_rate', 0.0),
                                "total_trades": data.get('total_trades', 0)
                            })
                        except:
                            continue
            except Exception as e:
                symbol_files = []

        # Get selected year from URL parameter
        from flask import request
        selected_year = request.args.get('year', None)
        if selected_year:
            try:
                selected_year = int(selected_year)
                # Filter by selected year
                symbol_files = [f for f in symbol_files if f['year'] == selected_year]
            except:
                selected_year = None

        # Sort available years (descending)
        years_list = sorted(all_years, reverse=True)

        # Sort by year desc, month desc
        symbol_files.sort(key=lambda x: (x['year'], x['month']), reverse=True)
        # Build table rows
        table_rows = ""
        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if symbol_files:
            for f in symbol_files:
                month_str = f"{month_names[f['month']]} {f['year']}"
                net_profit = f['net_profit']
                win_rate = f['win_rate']
                total_trades = f['total_trades']
                filename = f['filename']
                # Color and icon based on profit
                profit_color = '#2e7d32' if net_profit >= 0 else '#c62828'
                profit_icon = '✅' if net_profit >= 0 else '❌'
                table_rows += f"""
                <tr>
                    <td>{month_str}</td>
                    <td style="color: {profit_color}; font-weight: bold;">${net_profit:,.2f} {profit_icon}</td>
                    <td>{win_rate:.2f}%</td>
                    <td>{total_trades}</td>
                    <td style="text-align: center;">
                        <a href="/csdl/history/view/{filename}" class="btn-small">📜 Full Details</a>
                    </td>
                </tr>
                """
        else:
            table_rows = """
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #999;">No monthly data found for this symbol</td>
            </tr>
            """
        # Build year filter dropdown
        year_filter_html = ""
        if years_list:
            year_options = '<option value="">-- All Years --</option>'
            for year in years_list:
                selected_attr = 'selected' if selected_year == year else ''
                year_options += f'<option value="{year}" {selected_attr}>{year}</option>'
            year_filter_html = f"""
            <div style="background: #fff; padding: 15px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px;">
                <label style="font-weight: bold; margin-right: 10px;">📅 Filter by Year:</label>
                <select onchange="location.href='/csdl/history/{symbol}?year=' + this.value" style="padding: 8px 12px; font-size: 14px; border: 2px solid #00A651; border-radius: 4px; background: white; cursor: pointer;">
                    {year_options}
                </select>
                <span style="margin-left: 15px; color: #666; font-size: 13px;">Showing: <strong>{len(symbol_files)} months</strong></span>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - {symbol} History</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; margin: 0; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                h1 {{ color: #333; text-align: center; border-bottom: 3px solid #00A651; padding-bottom: 10px; }}
                .info {{ background: #f0f0f0; padding: 10px; border-left: 4px solid #00A651; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                th {{ background: #00A651; color: white; padding: 12px; text-align: left; font-weight: bold; }}
                td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
                tr:hover {{ background: #f9f9f9; }}
                .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #00A651; color: white; text-decoration: none; border-radius: 3px; transition: background 0.3s; }}
                .btn:hover {{ background: #008040; }}
                .btn-small {{ display: inline-block; padding: 6px 12px; background: #00A651; color: white; text-decoration: none; border-radius: 3px; font-size: 12px; }}
                .btn-small:hover {{ background: #008040; }}
                .footer {{ text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 {symbol} - Monthly History</h1>
                {year_filter_html}
                <table>
                    <thead>
                        <tr>
                            <th>Period</th>
                            <th>Net Profit</th>
                            <th>Win Rate</th>
                            <th>Total Trades</th>
                            <th style="text-align: center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <div class="footer">
                    <a href="/csdl/history" class="btn">← Back to Symbol List</a>
                    <a href="/" class="btn">🏠 Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    def build_trades_table(data):
        """Build HTML table for trade details"""
        trades = data.get('trades', [])
        if not trades:
            return ""
        # Build trade rows
        trade_rows = ""
        for i, trade in enumerate(trades, 1):
            ticket = trade.get('ticket', 'N/A')
            open_time = trade.get('open_time', 'N/A')
            close_time = trade.get('close_time', 'N/A')
            trade_type = trade.get('type', 'N/A')
            lots = trade.get('lots', 0.0)
            open_price = trade.get('open_price', 0.0)
            close_price = trade.get('close_price', 0.0)
            profit = trade.get('profit', 0.0)
            duration = trade.get('duration', 'N/A')
            # Color for profit
            profit_color = '#2e7d32' if profit >= 0 else '#c62828'
            profit_icon = '✅' if profit >= 0 else '❌'
            # Type color
            type_color = '#1976d2' if trade_type == 'BUY' else '#d32f2f'
            trade_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{ticket}</td>
                <td>{open_time}</td>
                <td>{close_time}</td>
                <td style="color: {type_color}; font-weight: bold;">{trade_type}</td>
                <td>{lots:.2f}</td>
                <td>{open_price:.5f}</td>
                <td>{close_price:.5f}</td>
                <td style="color: {profit_color}; font-weight: bold;">${profit:,.2f} {profit_icon}</td>
                <td>{duration}</td>
            </tr>
            """
        html = f"""
        <h3 style="color: #333; margin-top: 30px;">Trade Details ({len(trades)} trades)</h3>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Ticket</th>
                        <th>Open Time</th>
                        <th>Close Time</th>
                        <th>Type</th>
                        <th>Lots</th>
                        <th>Open Price</th>
                        <th>Close Price</th>
                        <th>Profit</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    {trade_rows}
                </tbody>
            </table>
        </div>
        """
        return html
    @app_dashboard.route('/csdl/history/view/<filename>')
    def dashboard_view_history_stats(filename):
        """MONTHLY HISTORY - View detailed statistics for a specific file"""
        # Read directly from history_folder (like CSDL1/CSDL2 pattern)
        # Security: Prevent path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            data = None
        else:
            history_folder = config.get("history_folder", "")
            if history_folder and os.path.exists(history_folder):
                file_path = os.path.join(history_folder, filename)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except Exception as e:
                        data = None
                else:
                    data = None
            else:
                data = None
        if not data:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SYNS Dashboard - History Stats</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; text-align: center; }}
                    .error {{ background: #ffebee; color: #c62828; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                    .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #00A651; color: white; text-decoration: none; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Error</h1>
                    <div class="error">Failed to load history file: {filename}</div>
                    <a href="/csdl/history" class="btn">← Back to History List</a>
                    <a href="/" class="btn">🏠 Home</a>
                </div>
            </body>
            </html>
            """
            return html
        # Extract data fields
        symbol = data.get('symbol', 'N/A')
        year = data.get('year', 'N/A')
        month = data.get('month', 'N/A')
        total_trades = data.get('total_trades', 0)
        winning_trades = data.get('winning_trades', 0)
        losing_trades = data.get('losing_trades', 0)
        total_profit = data.get('total_profit', 0.0)
        total_loss = data.get('total_loss', 0.0)
        net_profit = data.get('net_profit', 0.0)
        win_rate = data.get('win_rate', 0.0)
        avg_win = data.get('avg_win', 0.0)
        avg_loss = data.get('avg_loss', 0.0)
        largest_win = data.get('largest_win', 0.0)
        largest_loss = data.get('largest_loss', 0.0)
        total_lots = data.get('total_lots', 0.0)
        # Determine profit/loss color
        profit_color = '#2e7d32' if net_profit >= 0 else '#c62828'
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - {symbol} Stats</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; margin: 0; }}
                .container {{ max-width: 900px; margin: 0 auto; }}
                h1 {{ color: #333; text-align: center; border-bottom: 3px solid #00A651; padding-bottom: 10px; }}
                .header-info {{ text-align: center; background: #00A651; color: white; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 15px; border-left: 4px solid #00A651; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .profit {{ color: #2e7d32; }}
                .loss {{ color: #c62828; }}
                table {{ width: 100%; border-collapse: collapse; background: white; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                th {{ background: #00A651; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
                .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #00A651; color: white; text-decoration: none; border-radius: 3px; transition: background 0.3s; }}
                .btn:hover {{ background: #008040; }}
                .footer {{ text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Monthly Statistics</h1>
                <div class="header-info">
                    <h2 style="margin: 0;">{symbol}</h2>
                    <p style="margin: 5px 0;">Period: {year}/{month:02d}</p>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Net Profit</div>
                        <div class="stat-value" style="color: {profit_color};">${net_profit:,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Trades</div>
                        <div class="stat-value">{total_trades}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Win Rate</div>
                        <div class="stat-value">{win_rate:.2f}%</div>
                    </div>
                </div>
                <h3 style="color: #333; margin-top: 30px;">Trade Summary</h3>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Winning Trades</td>
                        <td class="profit">{winning_trades}</td>
                    </tr>
                    <tr>
                        <td>Losing Trades</td>
                        <td class="loss">{losing_trades}</td>
                    </tr>
                    <tr>
                        <td>Total Profit</td>
                        <td class="profit">${total_profit:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Total Loss</td>
                        <td class="loss">${total_loss:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Average Win</td>
                        <td>${avg_win:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Average Loss</td>
                        <td>${avg_loss:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Largest Win</td>
                        <td class="profit">${largest_win:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Largest Loss</td>
                        <td class="loss">${largest_loss:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Total Lots</td>
                        <td>{total_lots:.2f}</td>
                    </tr>
                </table>
                {build_trades_table(data)}
                <div class="footer">
                    <a href="/csdl/history/{symbol}" class="btn">← Back to {symbol} History</a>
                    <a href="/csdl/history" class="btn">📊 All Symbols</a>
                    <a href="/" class="btn">🏠 Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    @app_dashboard.route('/symlink')
    def dashboard_symlink():
        """Symlink Manager page"""
        # Load symlink config
        symlink_cfg = load_symlink_config()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - Symlink Manager</title>
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
                .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                               color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
                .panel-body {{ padding: 20px; }}
                .btn {{ display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0;
                       background: white; text-decoration: none; color: #2c2c2c; margin: 5px;
                       font-size: 11px; text-transform: uppercase; letter-spacing: 1px; cursor: pointer; }}
                .btn:hover {{ background: #2c2c2c; color: white; }}
                .btn-primary {{ background: #00A651; color: white; border-color: #00A651; }}
                .btn-primary:hover {{ background: #008f45; }}
                .btn-danger {{ background: #f44336; color: white; border-color: #f44336; }}
                .btn-danger:hover {{ background: #d32f2f; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
                        color: #666; margin-bottom: 8px; font-weight: bold; }}
                input {{ width: 100%; padding: 10px; font-family: inherit; font-size: 13px;
                        border: 1px solid #d0d0d0; background: #fafafa; box-sizing: border-box; }}
                input:focus {{ outline: none; border-color: #00A651; background: white; }}
                .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; font-size: 13px; }}
                .warning {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; font-size: 13px; }}
                .success {{ background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; font-size: 13px; }}
                .error {{ background: #f8d7da; padding: 15px; border-left: 4px solid #f44336; margin: 20px 0; font-size: 13px; }}
                #result {{ display: none; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
                th {{ font-size: 11px; text-transform: uppercase; color: #666; letter-spacing: 1px; }}
                .status-ok {{ color: #28a745; }}
                .status-warning {{ color: #ffc107; }}
                .status-error {{ color: #f44336; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="panel">
                    <div class="panel-header">🔗 SYMLINK MANAGER — MT4/MT5 Folder Symbolic Links</div>
                    <div class="panel-body">
                        <div class="info">
                            <strong>About Symlink Manager:</strong><br>
                            • Tạo symbolic links để tất cả MT4/MT5 dùng chung 1 nguồn data<br>
                            • Tự động backup thư mục cũ trước khi tạo symlink<br>
                            • Paste đường dẫn MT4/MT5 → Hệ thống tự detect MQL4/MQL5 → Tạo symlink cho 3 thư mục
                        </div>
                        <h3 style="margin: 20px 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                            SOURCE CONFIG (Thư Mục Chính - Nguồn Data)
                        </h3>
                        <div class="form-group">
                            <label>Files Source Folder</label>
                            <input type="text" id="source_files" value="{symlink_cfg['source_folders']['files']}" placeholder="E:/PRO_ONER/MQL4/Files">
                        </div>
                        <div class="form-group">
                            <label>Presets Source Folder</label>
                            <input type="text" id="source_presets" value="{symlink_cfg['source_folders']['presets']}" placeholder="E:/PRO_ONER/MQL4/Presets">
                        </div>
                        <div class="form-group">
                            <label>Data Oner Source Folder</label>
                            <input type="text" id="source_data_oner" value="{symlink_cfg['source_folders']['data_oner']}" placeholder="E:/PRO_ONER/MQL4/Data Oner">
                        </div>
                        <div style="text-align: center; margin: 20px 0;">
                            <button class="btn btn-primary" onclick="saveSourceConfig()">💾 SAVE SOURCE CONFIG</button>
                        </div>
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e0e0e0;">
                        <h3 style="margin: 20px 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                            ADD MT4/MT5 PLATFORM
                        </h3>
                        <div class="form-group">
                            <label>MT4/MT5 Root Path (Paste đường dẫn vào đây)</label>
                            <input type="text" id="mt_path" placeholder="C:/Program Files (x86)/MetaTrader 4 IC Markets Global">
                        </div>
                        <div style="text-align: center; margin: 20px 0;">
                            <button class="btn btn-primary" onclick="checkMTPlatform()">🔍 CHECK & CREATE SYMLINKS</button>
                        </div>
                        <div id="result"></div>
                    </div>
                </div>
                <div style="text-align: center;">
                    <a href="/" class="btn">← Back to Dashboard</a>
                </div>
            </div>
            <script>
                async function saveSourceConfig() {{
                    const data = {{
                        source_files: document.getElementById('source_files').value,
                        source_presets: document.getElementById('source_presets').value,
                        source_data_oner: document.getElementById('source_data_oner').value
                    }};
                    try {{
                        const response = await fetch('/api/symlink/config/save', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(data)
                        }});
                        const result = await response.json();
                        if (result.success) {{
                            alert('✅ Source config saved successfully!');
                        }} else {{
                            alert('❌ Error: ' + result.error);
                        }}
                    }} catch (error) {{
                        alert('❌ Error: ' + error.message);
                    }}
                }}
                async function checkMTPlatform() {{
                    const mtPath = document.getElementById('mt_path').value.trim();
                    const resultDiv = document.getElementById('result');
                    if (!mtPath) {{
                        alert('❌ Please enter MT4/MT5 path');
                        return;
                    }}
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<div class="info">⏳ Checking MT platform and creating symlinks...</div>';
                    try {{
                        const response = await fetch('/api/symlink/create', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ mt_path: mtPath }})
                        }});
                        const result = await response.json();
                        if (result.success) {{
                            let html = '<div class="success"><strong>✅ SUCCESS!</strong><br>';
                            html += `Platform: ${{result.platform_type}}<br>`;
                            html += `MQL Path: ${{result.mql_path}}<br><br>`;
                            html += '<strong>Symlinks Created:</strong><br>';
                            html += '<table>';
                            html += '<tr><th>Folder</th><th>Source</th><th>Target</th><th>Status</th></tr>';
                            for (const item of result.symlinks) {{
                                const statusClass = item.success ? 'status-ok' : 'status-error';
                                const statusIcon = item.success ? '✅' : '❌';
                                html += `<tr>`;
                                html += `<td>${{item.folder}}</td>`;
                                html += `<td style="font-size: 11px;">${{item.source}}</td>`;
                                html += `<td style="font-size: 11px;">${{item.target}}</td>`;
                                html += `<td class="${{statusClass}}">${{statusIcon}} ${{item.message}}</td>`;
                                html += `</tr>`;
                            }}
                            html += '</table></div>';
                            resultDiv.innerHTML = html;
                            // Clear input
                            document.getElementById('mt_path').value = '';
                        }} else {{
                            resultDiv.innerHTML = `<div class="error"><strong>❌ ERROR:</strong><br>${{result.error}}</div>`;
                        }}
                    }} catch (error) {{
                        resultDiv.innerHTML = `<div class="error"><strong>❌ ERROR:</strong><br>${{error.message}}</div>`;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return html
    @app_dashboard.route('/api/symlink/config/save', methods=['POST'])
    def api_save_symlink_config():
        """API endpoint to save symlink source config"""
        try:
            data = request.get_json()
            # Load current config
            symlink_cfg = load_symlink_config()
            # Update source folders
            symlink_cfg['source_folders']['files'] = data.get('source_files', symlink_cfg['source_folders']['files'])
            symlink_cfg['source_folders']['presets'] = data.get('source_presets', symlink_cfg['source_folders']['presets'])
            symlink_cfg['source_folders']['data_oner'] = data.get('source_data_oner', symlink_cfg['source_folders']['data_oner'])
            # Save config
            if save_symlink_config(symlink_cfg):
                return jsonify({"success": True, "message": "Source config saved successfully!"})
            else:
                return jsonify({"success": False, "error": "Failed to save config"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    @app_dashboard.route('/api/symlink/create', methods=['POST'])
    def api_create_symlink():
        """API endpoint to create symlinks for MT platform"""
        try:
            data = request.get_json()
            mt_path = data.get('mt_path', '').strip()
            if not mt_path:
                return jsonify({"success": False, "error": "MT path is required"}), 400
            # Check MT platform
            is_valid, platform_type, mql_path = check_mt_platform(mt_path)
            if not is_valid:
                return jsonify({"success": False, "error": f"Invalid MT path. No MQL4 or MQL5 folder found in: {mt_path}"}), 400
            # Load symlink config
            symlink_cfg = load_symlink_config()
            # Create symlinks for each target folder
            symlink_results = []
            # Files
            source_files = symlink_cfg['source_folders']['files']
            target_files = os.path.join(mql_path, "Files")
            success, message = create_symlink(source_files, target_files)
            symlink_results.append({
                "folder": "Files",
                "source": source_files,
                "target": target_files,
                "success": success,
                "message": message
            })
            # Presets
            source_presets = symlink_cfg['source_folders']['presets']
            target_presets = os.path.join(mql_path, "Presets")
            success, message = create_symlink(source_presets, target_presets)
            symlink_results.append({
                "folder": "Presets",
                "source": source_presets,
                "target": target_presets,
                "success": success,
                "message": message
            })
            # Data Oner
            source_data_oner = symlink_cfg['source_folders']['data_oner']
            target_data_oner = os.path.join(mql_path, "Data Oner")
            success, message = create_symlink(source_data_oner, target_data_oner)
            symlink_results.append({
                "folder": "Data Oner",
                "source": source_data_oner,
                "target": target_data_oner,
                "success": success,
                "message": message
            })
            return jsonify({
                "success": True,
                "platform_type": platform_type,
                "mql_path": mql_path,
                "symlinks": symlink_results
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    @app_dashboard.route('/auto-start')
    def dashboard_autostart():
        """Auto-Start Manager page"""
        autostart_cfg = load_autostart_config()
        task_status = check_task_status(autostart_cfg.get('task_name', 'SYNS_Bot_AutoStart'))
        # Build full path
        bot_folder = autostart_cfg.get('bot_folder', '')
        start_script = autostart_cfg.get('start_script', 'START_SERVER.bat')
        full_path = os.path.join(bot_folder, start_script)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYNS Dashboard - Auto-Start Manager</title>
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .panel {{ border: 1px solid #d0d0d0; background: white; margin-bottom: 20px; }}
                .panel-header {{ padding: 12px 20px; border-bottom: 1px solid #00A651; background: #00A651;
                               color: white; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
                .panel-body {{ padding: 20px; }}
                .btn {{ display: inline-block; padding: 10px 20px; border: 1px solid #d0d0d0;
                       background: white; text-decoration: none; color: #2c2c2c; margin: 5px;
                       font-size: 11px; text-transform: uppercase; letter-spacing: 1px; cursor: pointer; }}
                .btn:hover {{ background: #2c2c2c; color: white; }}
                .btn-primary {{ background: #00A651; color: white; border-color: #00A651; }}
                .btn-primary:hover {{ background: #008a42; }}
                .btn-danger {{ background: #f44336; color: white; border-color: #f44336; }}
                .btn-danger:hover {{ background: #d32f2f; }}
                .form-group {{ margin-bottom: 15px; }}
                .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; font-size: 12px; }}
                .form-group input {{ width: 100%; padding: 10px; border: 1px solid #d0d0d0; font-family: 'Consolas', monospace; }}
                .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; font-size: 13px; }}
                .success {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #4caf50; margin: 20px 0; font-size: 13px; }}
                .error {{ background: #ffebee; padding: 15px; border-left: 4px solid #f44336; margin: 20px 0; font-size: 13px; }}
                .status-badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 11px; font-weight: bold; }}
                .status-installed {{ background: #4caf50; color: white; }}
                .status-not-installed {{ background: #9e9e9e; color: white; }}
                hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 30px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="panel">
                    <div class="panel-header">AUTO-START MANAGER</div>
                    <div class="panel-body">
                        <h3 style="margin-top: 0; margin-bottom: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                            CAU HINH DUONG DAN
                        </h3>
                        <div class="form-group">
                            <label>Bot Folder Path:</label>
                            <input type="text" id="bot_folder" value="{autostart_cfg.get('bot_folder', '')}" />
                        </div>
                        <div class="form-group">
                            <label>Start Script Name:</label>
                            <input type="text" id="start_script" value="{autostart_cfg.get('start_script', '')}" />
                        </div>
                        <div class="form-group">
                            <label>Task Name:</label>
                            <input type="text" id="task_name" value="{autostart_cfg.get('task_name', '')}" />
                        </div>
                        <button class="btn btn-primary" onclick="saveConfig()">LUU CAU HINH</button>
                        <hr>
                        <h3 style="margin-bottom: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                            TRANG THAI HIEN TAI
                        </h3>
                        <div class="info">
                            <strong>Full Path:</strong> {full_path}<br>
                            <strong>Task Name:</strong> {autostart_cfg.get('task_name', 'SYNS_Bot_AutoStart')}<br>
                            <strong>Installation:</strong> {'✅ Installed' if task_status['installed'] else '❌ Not Installed'}<br>
                            <strong>Status:</strong> {task_status['status']}
                        </div>
                        <button class="btn btn-primary" onclick="installTask()">CAI DAT AUTO-START</button>
                        <button class="btn btn-danger" onclick="uninstallTask()">GO BO AUTO-START</button>
                        <button class="btn" onclick="window.location.reload()">KIEM TRA TRANG THAI</button>
                        <hr>
                        <div id="message" style="display: none;"></div>
                    </div>
                </div>
                <!-- MT4/MT5 AUTO-START SECTION -->
                <div class="panel">
                    <div class="panel-header">🎮 MT4/MT5 AUTO-START MANAGER</div>
                    <div class="panel-body">
                        <div class="info" style="margin-bottom: 20px;">
                            <strong>Note:</strong> Each MT4/MT5 platform will auto-start 30 seconds after boot. No auto-restart on failure.
                        </div>
                        <h3>Them Platform Moi:</h3>
                        <div class="form-group">
                            <label>Duong dan .exe file:</label>
                            <input type="text" id="new_mt_path" placeholder="C:\\Program Files\\MetaTrader 5\\terminal64.exe" style="width: 100%;" />
                        </div>
                        <div class="form-group">
                            <label>Ten Task:</label>
                            <input type="text" id="new_mt_task" placeholder="MT5_ICMarkets_AutoStart" style="width: 100%;" />
                        </div>
                        <button class="btn btn-primary" onclick="addMtPlatform()">THEM PLATFORM</button>
                        <hr>
                        <h3>Platforms da cai:</h3>
                        <div id="mt_platforms_list">
                            <!-- Dynamically filled by JavaScript -->
                        </div>
                    </div>
                </div>
                <div style="text-align: center;">
                    <a href="/" class="btn">Home</a>
                </div>
            </div>
            <script>
                function saveConfig() {{
                    const data = {{
                        bot_folder: document.getElementById('bot_folder').value,
                        start_script: document.getElementById('start_script').value,
                        task_name: document.getElementById('task_name').value,
                        restart_on_failure: true,
                        restart_interval_minutes: 1,
                        restart_attempts: 999
                    }};
                    fetch('/api/autostart/save-config', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(data)
                    }})
                    .then(res => res.json())
                    .then(data => {{
                        showMessage(data.success ? 'success' : 'error', data.message);
                        if (data.success) setTimeout(() => window.location.reload(), 1500);
                    }})
                    .catch(err => showMessage('error', 'Error: ' + err));
                }}
                function installTask() {{
                    if (!confirm('Cai dat Auto-Start cho bot?')) return;
                    fetch('/api/autostart/install', {{method: 'POST'}})
                    .then(res => res.json())
                    .then(data => {{
                        showMessage(data.success ? 'success' : 'error', data.message);
                        if (data.success) setTimeout(() => window.location.reload(), 2000);
                    }})
                    .catch(err => showMessage('error', 'Error: ' + err));
                }}
                function uninstallTask() {{
                    if (!confirm('Go bo Auto-Start? Bot se khong tu dong chay khi VPS reboot.')) return;
                    fetch('/api/autostart/uninstall', {{method: 'POST'}})
                    .then(res => res.json())
                    .then(data => {{
                        showMessage(data.success ? 'success' : 'error', data.message);
                        if (data.success) setTimeout(() => window.location.reload(), 1500);
                    }})
                    .catch(err => showMessage('error', 'Error: ' + err));
                }}
                function addMtPlatform() {{
                    const path = document.getElementById('new_mt_path').value.trim();
                    const taskName = document.getElementById('new_mt_task').value.trim();
                    if (!path) {{
                        showMessage('error', 'Vui long nhap duong dan .exe file!');
                        return;
                    }}
                    if (!taskName) {{
                        showMessage('error', 'Vui long nhap ten task!');
                        return;
                    }}
                    if (!path.toLowerCase().endsWith('.exe')) {{
                        showMessage('error', 'Duong dan phai la file .exe!');
                        return;
                    }}
                    if (!confirm('Them va cai dat platform nay?')) return;
                    const data = {{
                        path: path,
                        task_name: taskName
                    }};
                    fetch('/api/autostart/mt-add', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(data)
                    }})
                    .then(res => res.json())
                    .then(data => {{
                        showMessage(data.success ? 'success' : 'error', data.message);
                        if (data.success) {{
                            document.getElementById('new_mt_path').value = '';
                            document.getElementById('new_mt_task').value = '';
                            setTimeout(() => window.location.reload(), 1500);
                        }}
                    }})
                    .catch(err => showMessage('error', 'Error: ' + err));
                }}
                function removeMtPlatform(taskName) {{
                    if (!confirm('Go bo platform nay?')) return;
                    const data = {{
                        task_name: taskName
                    }};
                    fetch('/api/autostart/mt-remove', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(data)
                    }})
                    .then(res => res.json())
                    .then(data => {{
                        showMessage(data.success ? 'success' : 'error', data.message);
                        if (data.success) setTimeout(() => window.location.reload(), 1500);
                    }})
                    .catch(err => showMessage('error', 'Error: ' + err));
                }}
                function loadMtPlatformsList() {{
                    fetch('/api/autostart/mt-list')
                    .then(res => res.json())
                    .then(data => {{
                        if (data.success) {{
                            const container = document.getElementById('mt_platforms_list');
                            if (data.platforms.length === 0) {{
                                container.innerHTML = '<div class="info">Chua co platform nao duoc cai dat.</div>';
                            }} else {{
                                let html = '';
                                data.platforms.forEach((platform, idx) => {{
                                    const statusIcon = platform.installed ? '✅' : '❌';
                                    const statusText = platform.installed ? 'Ready' : 'Not Installed';
                                    html += `
                                        <div class="info" style="margin-bottom: 15px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                                            <strong>${{idx + 1}}. ${{platform.task_name}}</strong><br>
                                            <span style="font-size: 12px; color: #666;">Path: ${{platform.path}}</span><br>
                                            <span style="font-size: 12px;">Status: ${{statusIcon}} ${{statusText}}</span><br>
                                            <button class="btn btn-danger" style="margin-top: 10px;" onclick="removeMtPlatform('${{platform.task_name}}')">GO BO</button>
                                        </div>
                                    `;
                                }});
                                container.innerHTML = html;
                            }}
                        }}
                    }})
                    .catch(err => console.error('Error loading platforms:', err));
                }}
                // Load platforms list on page load
                window.addEventListener('load', loadMtPlatformsList);
                function showMessage(type, message) {{
                    const msgDiv = document.getElementById('message');
                    msgDiv.className = type;
                    msgDiv.innerHTML = message;
                    msgDiv.style.display = 'block';
                }}
            </script>
        </body>
        </html>
        """
        return html
    @app_dashboard.route('/api/autostart/save-config', methods=['POST'])
    def api_autostart_save_config():
        """Save auto-start configuration"""
        try:
            data = request.get_json()
            save_autostart_config(data)
            return jsonify({"success": True, "message": "Cau hinh da duoc luu thanh cong!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Loi: {str(e)}"})
    @app_dashboard.route('/api/autostart/install', methods=['POST'])
    def api_autostart_install():
        """Install auto-start task"""
        try:
            autostart_cfg = load_autostart_config()
            result = install_autostart_task(autostart_cfg)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "message": f"Loi: {str(e)}"})
    @app_dashboard.route('/api/autostart/uninstall', methods=['POST'])
    def api_autostart_uninstall():
        """Uninstall auto-start task"""
        try:
            autostart_cfg = load_autostart_config()
            task_name = autostart_cfg.get('task_name', 'SYNS_Bot_AutoStart')
            result = uninstall_autostart_task(task_name)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "message": f"Loi: {str(e)}"})
    @app_dashboard.route('/api/autostart/mt-list', methods=['GET'])
    def api_mt_list():
        """List all installed MT4/MT5 platforms"""
        try:
            autostart_cfg = load_autostart_config()
            platforms = autostart_cfg.get('mt_platforms', [])
            # Add installation status to each platform
            platforms_with_status = []
            for platform in platforms:
                task_name = platform.get('task_name', '')
                status = check_mt_task_status(task_name)
                platforms_with_status.append({
                    'path': platform.get('path', ''),
                    'task_name': task_name,
                    'installed': status['installed']
                })
            return jsonify({
                "success": True,
                "platforms": platforms_with_status
            })
        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}", "platforms": []})
    @app_dashboard.route('/api/autostart/mt-add', methods=['POST'])
    def api_mt_add():
        """Add and install new MT4/MT5 platform"""
        try:
            data = request.get_json()
            path = data.get('path', '').strip()
            task_name = data.get('task_name', '').strip()
            if not path or not task_name:
                return jsonify({"success": False, "message": "Path and task name are required"})
            if not os.path.exists(path):
                return jsonify({"success": False, "message": f"File not found: {path}"})
            # Load config and check if task name already exists
            autostart_cfg = load_autostart_config()
            platforms = autostart_cfg.get('mt_platforms', [])
            for platform in platforms:
                if platform.get('task_name') == task_name:
                    return jsonify({"success": False, "message": f"Task name '{task_name}' already exists!"})
            # Add new platform to config
            new_platform = {
                'path': path,
                'task_name': task_name
            }
            platforms.append(new_platform)
            autostart_cfg['mt_platforms'] = platforms
            save_autostart_config(autostart_cfg)
            # Install the task immediately
            result = install_mt_autostart_task(new_platform)
            if result['success']:
                return jsonify({"success": True, "message": f"Platform added and installed successfully! ✅"})
            else:
                # Remove from config if installation failed
                platforms.remove(new_platform)
                autostart_cfg['mt_platforms'] = platforms
                save_autostart_config(autostart_cfg)
                return jsonify({"success": False, "message": f"Failed to install: {result['message']}"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}"})
    @app_dashboard.route('/api/autostart/mt-remove', methods=['POST'])
    def api_mt_remove():
        """Remove and uninstall MT4/MT5 platform"""
        try:
            data = request.get_json()
            task_name = data.get('task_name', '').strip()
            if not task_name:
                return jsonify({"success": False, "message": "Task name is required"})
            # Load config
            autostart_cfg = load_autostart_config()
            platforms = autostart_cfg.get('mt_platforms', [])
            # Find and remove platform
            platform_found = False
            for platform in platforms:
                if platform.get('task_name') == task_name:
                    platforms.remove(platform)
                    platform_found = True
                    break
            if not platform_found:
                return jsonify({"success": False, "message": f"Platform with task name '{task_name}' not found"})
            # Save updated config
            autostart_cfg['mt_platforms'] = platforms
            save_autostart_config(autostart_cfg)
            # Uninstall the task
            result = uninstall_mt_autostart_task(task_name)
            if result['success']:
                return jsonify({"success": True, "message": f"Platform removed successfully! ✅"})
            else:
                return jsonify({"success": True, "message": f"Platform removed from config (uninstall warning: {result['message']})"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}"})
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
        # Start API server thread
        api_thread = Thread(target=run_api_server, daemon=True)
        api_thread.start()
        # Start Dashboard server in main thread (blocking)
        run_dashboard_server()
    if __name__ == "__main__":
        main()


# ==============================================================================
# MODE 1: RECEIVER (Bot 2) - FULL CODE EMBEDDED
# ==============================================================================

elif mode == 1:

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

    # ==============================================================================
    # ADVANCED LOG SUPPRESSION (Bot 2 - Same as Bot 1)
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

    # Use bot_config from global scope (already loaded at line 36-37)
    # Optimization: Avoid loading config file multiple times

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
    # Purpose: Reduce log spam (similar to EA's CheckSPYBotHealth)
    error_log_tracker = {}  # {symbol: {"last_log_time": timestamp, "error_count": count}}
    # Flask app (Dashboard only)
    app_dashboard = Flask(__name__)
    CORS(app_dashboard)
    # ============================================
    # SECTION 2: HELPER FUNCTIONS
    # ============================================
    def ensure_folders():
        """Create output and log folders if not exist | Tao cac thu muc output neu chua ton tai"""
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
            if should_log_error("global", "timeout"):
                error_count = error_log_tracker.get("global_timeout", {}).get("error_count", 0)
                log_message("ERROR", f"Timeout while fetching symbols from Bot 1 (errors in last 1h: {error_count})")
            return False
        except requests.exceptions.ConnectionError:
            if should_log_error("global", "connection"):
                error_count = error_log_tracker.get("global_connection", {}).get("error_count", 0)
                log_message("ERROR", f"Connection error: Bot 1 offline or wrong URL (errors in last 1h: {error_count})")
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
            symbol: Symbol name or "global" for non-symbol errors
            error_type: Type of error ("timeout", "connection", "http_500", etc.)

        Returns:
            bool: True if error should be logged, False to suppress

        Example:
            if should_log_error("EURUSD", "timeout"):
                log_message("ERROR", f"Timeout pulling EURUSD...")
        """
        current_time = time.time()
        tracker_key = f"{symbol}_{error_type}"

        # First time seeing this error
        if tracker_key not in error_log_tracker:
            error_log_tracker[tracker_key] = {
                "last_log_time": current_time,
                "error_count": 1
            }
            return True

        # Check time since last log
        last_log_time = error_log_tracker[tracker_key]["last_log_time"]
        time_since_last_log = current_time - last_log_time

        # Increment error count
        error_log_tracker[tracker_key]["error_count"] += 1

        # Log if 1 hour (3600s) has passed
        if time_since_last_log >= 3600:
            error_log_tracker[tracker_key]["last_log_time"] = current_time
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

                            if should_log_error(symbol, f"http_{response.status_code}"):
                                error_count = error_log_tracker.get(f"{symbol}_http_{response.status_code}", {}).get("error_count", 0)
                                log_message("ERROR", f"Bot 1 API error: {symbol} (HTTP {response.status_code}) (errors in last 1h: {error_count})")
                    except requests.exceptions.Timeout:
                        receiver_state["total_errors"] += 1
                        receiver_state["bot1_status"] = "offline"

                        if should_log_error(symbol, "timeout"):
                            error_count = error_log_tracker.get(f"{symbol}_timeout", {}).get("error_count", 0)
                            log_message("ERROR", f"Timeout pulling {symbol} from Bot 1 (errors in last 1h: {error_count})")
                    except requests.exceptions.ConnectionError:
                        receiver_state["total_errors"] += 1
                        receiver_state["bot1_status"] = "offline"

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
                <!-- Mode Selector Panel -->
                <div class="panel" style="background: #f5f5f5; border-left: 4px solid #00A651; margin-bottom: 20px;">
                    <div class="panel-body" style="padding: 12px 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 12px; color: #666;">
                                ⚙️ <strong>Currently Running:</strong> <span style="color: #00A651; font-weight: bold;">MODE 1 (RECEIVER)</span>
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <a href="/mode0-view" class="btn" style="display: inline-block; padding: 8px 16px; border: 1px solid #d0d0d0; background: white; color: #666; text-decoration: none; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">📊 MODE 0 DATA</a>
                                <a href="/" class="btn active" style="display: inline-block; padding: 8px 16px; border: 1px solid #00A651; background: #00A651; color: white; text-decoration: none; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">📥 MODE 1 DATA</a>
                            </div>
                        </div>
                    </div>
                </div>

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

    @app_dashboard.route('/mode0-view')
    def dashboard_mode0_view():
        """Show warning: Mode 0 data not available (currently running Mode 1)"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mode 0 Data - Not Available</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }
                .container { max-width: 800px; margin: 50px auto; text-align: center; }
                .warning-box { background: #fff3cd; border: 2px solid #ffc107; padding: 40px; border-radius: 8px; }
                .warning-icon { font-size: 64px; margin-bottom: 20px; }
                h1 { color: #856404; margin-bottom: 20px; }
                p { color: #666; font-size: 14px; line-height: 1.8; margin: 15px 0; }
                .btn { display: inline-block; padding: 12px 24px; background: #00A651; color: white;
                       text-decoration: none; border-radius: 4px; margin: 20px 10px 0; font-size: 14px; }
                .btn:hover { background: #008040; }
                .btn-secondary { background: #6c757d; }
                .btn-secondary:hover { background: #5a6268; }
                .info { background: #f5f5f5; padding: 20px; margin-top: 30px; border-left: 4px solid #00A651; }
                .info strong { color: #00A651; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="warning-box">
                    <div class="warning-icon">⚠️</div>
                    <h1>MODE 0 DATA NOT AVAILABLE</h1>
                    <p>You are currently running <strong>MODE 1 (RECEIVER)</strong>.</p>
                    <p>MODE 0 data is not available because the sender is not running.</p>
                    <div class="info">
                        <p style="margin: 0;">
                            💡 <strong>To view Mode 0 data:</strong><br>
                            Go to Settings → Change mode to "0" → Restart Bot 3
                        </p>
                    </div>
                    <a href="/" class="btn">← Back to MODE 1 Dashboard</a>
                    <a href="/settings" class="btn btn-secondary">⚙️ Go to Settings</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @app_dashboard.route('/settings')
    def dashboard_settings():
        """Unified Settings page for Bot 3 - supports both Mode 0 (SENDER) and Mode 1 (RECEIVER)"""

        # Load bot_config.json to get current mode and all settings
        try:
            with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                bot_config = json.load(f)
        except:
            bot_config = {"mode": 1, "sender": {}, "receiver": {}}

        current_mode = bot_config.get("mode", 1)

        # Load sender settings (Mode 0) - fallback to defaults
        sender_config = bot_config.get("sender", {
            "vps_ip": "",
            "csdl_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner3/",
            "history_folder": "E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/",
            "polling_interval": 1,
            "server_timezone_offset": 2,
            "vietnam_timezone_offset": 7
        })

        # Load receiver settings (Mode 1) - fallback to runtime config
        if current_mode == 1:
            receiver_config = RECEIVER_CONFIG  # Use runtime config directly when in Mode 1
        else:
            receiver_config = bot_config.get("receiver", {
                "bot1_url": "",
                "output_folder": "C:/PRO_ONER/MQL4/Files/DataAutoOner3/",
                "output_folder2": "C:/PRO_ONER/MQL4/Files/DataAutoOner2/",
                "polling_interval": 1,
                "http_timeout": 5
            })

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot 3 Settings - Unified Configuration</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Consolas', monospace; background: #fafafa; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
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
                .mode-section {{ display: none; }}
                .mode-section.active {{ display: block; }}
                .mode-badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 10px;
                             font-weight: bold; margin-left: 10px; }}
                .mode-0 {{ background: #2196F3; color: white; }}
                .mode-1 {{ background: #FF9800; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- MODE SELECTOR -->
                <div class="panel">
                    <div class="panel-header">🔄 BOT MODE SELECTOR</div>
                    <div class="panel-body">
                        <div class="note">
                            <strong>⚠️ Current Mode:</strong>
                            <span class="mode-badge mode-{current_mode}" id="currentModeBadge">
                                MODE {current_mode} - {{'SENDER (Bot 1)' if current_mode == 0 else 'RECEIVER (Bot 2)'}}
                            </span><br>
                            • Thay đổi mode sẽ yêu cầu <strong>RESTART BOT</strong> để có hiệu lực<br>
                            • Mode 0: SENDER - Truyền CSDL từ SPY Bot qua Port 80<br>
                            • Mode 1: RECEIVER - Nhận CSDL từ Bot 1 và ghi local files
                        </div>
                        <div class="form-group">
                            <label>Select Bot Mode</label>
                            <select id="modeSelector" name="mode">
                                <option value="0" {'selected' if current_mode == 0 else ''}>Mode 0 - SENDER (Bot 1)</option>
                                <option value="1" {'selected' if current_mode == 1 else ''}>Mode 1 - RECEIVER (Bot 2)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div id="alert" class="alert"></div>

                <form id="settingsForm">
                    <!-- MODE 0: SENDER SETTINGS -->
                    <div id="mode0Settings" class="mode-section {'active' if current_mode == 0 else ''}">
                        <div class="panel">
                            <div class="panel-header">⚙️ MODE 0: SENDER SETTINGS (Bot 1)</div>
                            <div class="panel-body">
                                <div class="form-group">
                                    <label>VPS IP Address</label>
                                    <input type="text" name="sender_vps_ip" value="{sender_config.get('vps_ip', '')}" placeholder="your-domain.duckdns.org">
                                </div>
                                <div class="form-group">
                                    <label>CSDL Folder Path (Source from SPY Bot)</label>
                                    <input type="text" name="sender_csdl_folder" value="{sender_config.get('csdl_folder', 'E:/PRO_ONER/MQL4/Files/DataAutoOner3/')}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner3/">
                                </div>
                                <div class="form-group">
                                    <label>History Folder Path</label>
                                    <input type="text" name="sender_history_folder" value="{sender_config.get('history_folder', 'E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/')}" placeholder="E:/PRO_ONER/MQL4/Files/DataAutoOner/HISTORY/">
                                </div>
                                <div class="form-group">
                                    <label>File Polling Interval (Check CSDL changes)</label>
                                    <select name="sender_polling_interval">
                                        <option value="1" {'selected' if sender_config.get('polling_interval', 1) == 1 else ''}>1 second (Fast - Scan every 1s)</option>
                                        <option value="2" {'selected' if sender_config.get('polling_interval', 1) == 2 else ''}>2 seconds (Normal - Scan on EVEN seconds only)</option>
                                    </select>
                                    <p style="font-size: 11px; color: #666; margin-top: 5px; line-height: 1.4;">
                                        💡 <strong>Fast:</strong> Scan every 1 second (high CPU, fastest response)<br>
                                        💡 <strong>Normal:</strong> Scan on EVEN seconds only (0,2,4,6,8...) - Optimized for Bot SPY odd-second writes
                                    </p>
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
                                    <input type="number" name="sender_timezone_offset" value="{sender_config.get('server_timezone_offset', 2)}" min="-12" max="14">
                                </div>
                                <div class="form-group">
                                    <label>Vietnam Timezone Offset (hours from GMT)</label>
                                    <input type="number" name="sender_vietnam_timezone_offset" value="{sender_config.get('vietnam_timezone_offset', 7)}" min="-12" max="14">
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                                    <p style="font-size: 11px; color: #999;">
                                        <strong>💡 Access Settings:</strong> <code>http://localhost:9070/settings</code><br>
                                        <strong>Ports:</strong> API: 80 | Dashboard: 9070
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- MODE 1: RECEIVER SETTINGS -->
                    <div id="mode1Settings" class="mode-section {'active' if current_mode == 1 else ''}">
                        <div class="panel">
                            <div class="panel-header">⚙️ MODE 1: RECEIVER SETTINGS (Bot 2)</div>
                            <div class="panel-body">
                                <div class="form-group">
                                    <label>Bot 1 URL (VPS Address with Port 80)</label>
                                    <input type="text" name="receiver_bot1_url" value="{receiver_config.get('bot1_url', '')}" placeholder="http://your-domain.duckdns.org:80">
                                </div>
                                <div class="form-group">
                                    <label>Output Folder 3 (Main - DataAutoOner3)</label>
                                    <input type="text" name="receiver_output_folder" value="{receiver_config.get('output_folder', 'C:/PRO_ONER/MQL4/Files/DataAutoOner3/')}" placeholder="C:/PRO_ONER/MQL4/Files/DataAutoOner3/">
                                </div>
                                <div class="form-group">
                                    <label>Output Folder 2 (Backup - DataAutoOner2)</label>
                                    <input type="text" name="receiver_output_folder2" value="{receiver_config.get('output_folder2', 'C:/PRO_ONER/MQL4/Files/DataAutoOner2/')}" placeholder="C:/PRO_ONER/MQL4/Files/DataAutoOner2/">
                                </div>
                                <div class="form-group">
                                    <label>Polling Interval (Pull from Bot 1)</label>
                                    <select name="receiver_polling_interval">
                                        <option value="1" selected>1 second (RECEIVER pulls via HTTP - no I/O conflict)</option>
                                    </select>
                                    <p style="font-size: 11px; color: #666; margin-top: 5px;">
                                        💡 Bot 2 (RECEIVER) pulls data via HTTP from Bot 1, not reading files directly.<br>
                                        No need for even-second sync. Always use 1 second polling.
                                    </p>
                                </div>
                                <div class="form-group">
                                    <label>HTTP Timeout (seconds)</label>
                                    <input type="number" name="receiver_http_timeout" value="{receiver_config.get('http_timeout', 5)}" min="1" max="30">
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                                    <p style="font-size: 11px; color: #999;">
                                        <strong>💡 Access Settings:</strong> <code>http://localhost:9070/settings</code><br>
                                        <strong>Dashboard Port:</strong> 9070
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn btn-save">💾 SAVE ALL SETTINGS</button>
                        <a href="/" class="btn">← Back to Dashboard</a>
                    </div>
                </form>
            </div>

            <script>
                // Mode selector logic
                const modeSelector = document.getElementById('modeSelector');
                const mode0Settings = document.getElementById('mode0Settings');
                const mode1Settings = document.getElementById('mode1Settings');
                const modeBadge = document.getElementById('currentModeBadge');

                modeSelector.addEventListener('change', function() {{
                    const selectedMode = this.value;
                    if (selectedMode === '0') {{
                        mode0Settings.classList.add('active');
                        mode1Settings.classList.remove('active');
                        modeBadge.className = 'mode-badge mode-0';
                        modeBadge.textContent = 'MODE 0 - SENDER (Bot 1)';
                    }} else {{
                        mode0Settings.classList.remove('active');
                        mode1Settings.classList.add('active');
                        modeBadge.className = 'mode-badge mode-1';
                        modeBadge.textContent = 'MODE 1 - RECEIVER (Bot 2)';
                    }}
                }});

                // Form submission
                const form = document.getElementById('settingsForm');
                const alert = document.getElementById('alert');

                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();

                    const formData = new FormData(form);
                    const mode = modeSelector.value;
                    const data = {{ mode: parseInt(mode) }};

                    // Collect sender settings
                    data.sender = {{}};
                    if (formData.get('sender_vps_ip')) data.sender.vps_ip = formData.get('sender_vps_ip');
                    if (formData.get('sender_csdl_folder')) data.sender.csdl_folder = formData.get('sender_csdl_folder');
                    if (formData.get('sender_history_folder')) data.sender.history_folder = formData.get('sender_history_folder');
                    if (formData.get('sender_polling_interval')) data.sender.polling_interval = parseInt(formData.get('sender_polling_interval'));
                    if (formData.get('sender_server_timezone_offset')) data.sender.server_timezone_offset = parseInt(formData.get('sender_server_timezone_offset'));
                    if (formData.get('sender_vietnam_timezone_offset')) data.sender.vietnam_timezone_offset = parseInt(formData.get('sender_vietnam_timezone_offset'));

                    // Collect receiver settings
                    data.receiver = {{}};
                    if (formData.get('receiver_bot1_url')) data.receiver.bot1_url = formData.get('receiver_bot1_url');
                    if (formData.get('receiver_output_folder')) data.receiver.output_folder = formData.get('receiver_output_folder');
                    if (formData.get('receiver_output_folder2')) data.receiver.output_folder2 = formData.get('receiver_output_folder2');
                    if (formData.get('receiver_polling_interval')) data.receiver.polling_interval = parseInt(formData.get('receiver_polling_interval'));
                    if (formData.get('receiver_http_timeout')) data.receiver.http_timeout = parseInt(formData.get('receiver_http_timeout'));

                    // Collect quiet_mode (root level)
                    if (formData.get('quiet_mode')) data.quiet_mode = formData.get('quiet_mode');

                    try {{
                        const response = await fetch('/api/config/save-unified', {{
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
                            }}, 3000);
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
    @app_dashboard.route('/api/config/save-unified', methods=['POST'])
    def api_save_config_unified():
        """API endpoint to save unified configuration for both Mode 0 and Mode 1"""
        try:
            data = request.get_json()

            # Load current bot_config.json
            if os.path.exists(BOT_CONFIG_FILE):
                with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    bot_config = json.load(f)
            else:
                bot_config = {}

            # Update mode
            if 'mode' in data:
                bot_config['mode'] = int(data['mode'])

            # Update quiet_mode (root level)
            if 'quiet_mode' in data:
                bot_config['quiet_mode'] = (data['quiet_mode'] == 'true' or data['quiet_mode'] == True)

            # Update sender settings (Mode 0)
            if 'sender' in data and data['sender']:
                if 'sender' not in bot_config:
                    bot_config['sender'] = {}
                for key, value in data['sender'].items():
                    bot_config['sender'][key] = value

                # Also update 'server' section for backward compatibility
                if 'server' not in bot_config:
                    bot_config['server'] = {}
                for key, value in data['sender'].items():
                    bot_config['server'][key] = value

            # Update receiver settings (Mode 1)
            if 'receiver' in data and data['receiver']:
                if 'receiver' not in bot_config:
                    bot_config['receiver'] = {}
                for key, value in data['receiver'].items():
                    bot_config['receiver'][key] = value

            # Save to file
            with open(BOT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(bot_config, f, indent=2, ensure_ascii=False)

            # Update runtime config if current mode matches
            current_mode = bot_config.get('mode', 1)
            if current_mode == 1 and 'receiver' in data:
                # Update runtime config for Mode 1
                for key, value in data['receiver'].items():
                    if key in RECEIVER_CONFIG:
                        RECEIVER_CONFIG[key] = value

            return jsonify({
                "success": True,
                "message": f"Settings saved successfully! Current mode: {current_mode}. Please RESTART bot if you changed mode."
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
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
