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

# Suppress Flask development server request logs
log = logging.getLogger('werkzeug')
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
            time.sleep(config["polling_interval"])

        except Exception as e:
            print(f"[POLLING] Error in polling thread: {e}")
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

# ==============================================================================
# STATS BACKUP SYSTEM (7-Day Rolling Log)
# ==============================================================================

STATS_FOLDER = "stats_logs"

def get_today_stats_filename():
    """Get today's stats filename: stats_YYYY-MM-DD.json"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(STATS_FOLDER, f"stats_{today}.json")

def save_stats_to_file():
    """Save current stats to today's file"""
    # Create stats folder if not exists
    if not os.path.exists(STATS_FOLDER):
        os.makedirs(STATS_FOLDER)

    filename = get_today_stats_filename()

    with stats_lock:
        # Convert stats to JSON-serializable format
        stats_data = {}
        for symbol, data in stats.items():
            stats_data[symbol] = {
                "request_count": data["request_count"],
                "unique_ips": list(data["unique_ips"]),  # Convert set to list
                "last_requests": data["last_requests"]
            }

        # Save to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2)
            print(f"[STATS] Saved stats to {filename}")
        except Exception as e:
            print(f"[STATS] Error saving stats: {e}")

def load_stats_from_file():
    """Load today's stats from file (if exists)"""
    filename = get_today_stats_filename()

    if not os.path.exists(filename):
        print(f"[STATS] No stats file found for today, starting fresh")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            stats_data = json.load(f)

        with stats_lock:
            for symbol, data in stats_data.items():
                stats[symbol] = {
                    "request_count": data["request_count"],
                    "unique_ips": set(data["unique_ips"]),  # Convert list back to set
                    "last_requests": data["last_requests"]
                }

        print(f"[STATS] Loaded stats from {filename}")
    except Exception as e:
        print(f"[STATS] Error loading stats: {e}")

def cleanup_old_stats():
    """Delete stats files older than 7 days"""
    if not os.path.exists(STATS_FOLDER):
        return

    now = time.time()
    retention_seconds = config.get("stats_retention_days", 7) * 86400

    for filename in os.listdir(STATS_FOLDER):
        if not filename.startswith("stats_") or not filename.endswith(".json"):
            continue

        filepath = os.path.join(STATS_FOLDER, filename)
        file_age = now - os.path.getmtime(filepath)

        if file_age > retention_seconds:
            try:
                os.remove(filepath)
                print(f"[STATS] Deleted old stats file: {filename}")
            except Exception as e:
                print(f"[STATS] Error deleting {filename}: {e}")

def stats_backup_thread():
    """Background thread: Save stats periodically"""
    global shutdown_flag
    interval = config.get("stats_save_interval", 3600)  # Default 1 hour
    print(f"[STATS] Started stats backup thread (interval: {interval}s)")

    while not shutdown_flag:
        time.sleep(interval)
        if not shutdown_flag:
            save_stats_to_file()
            cleanup_old_stats()

# ==============================================================================
# AUTO-RESTART SYSTEM (Weekly Saturday 00:01 GMT+2)
# ==============================================================================

def check_weekly_restart():
    """Background thread: Check if it's Saturday 00:01 GMT+2"""
    global shutdown_flag
    print(f"[RESTART] Started weekly restart thread")
    print(f"[RESTART] Will restart every Saturday at 00:01 (Server GMT+{config['server_timezone_offset']})")

    while not shutdown_flag:
        # Sleep 60 seconds between checks
        time.sleep(60)

        if shutdown_flag:
            break

        # Get current time in server timezone (GMT+2)
        now_utc = datetime.utcnow()
        server_time = now_utc + timedelta(hours=config["server_timezone_offset"])

        # Check if it's Saturday (weekday() == 5) at 00:01
        if server_time.weekday() == 5 and server_time.hour == 0 and server_time.minute == 1:
            print("=" * 60)
            print("[RESTART] Weekly restart time reached!")
            print(f"[RESTART] Server time: {server_time.strftime('%Y-%m-%d %H:%M:%S')} (GMT+{config['server_timezone_offset']})")
            print("[RESTART] Saving stats and restarting...")
            print("=" * 60)

            save_stats_to_file()

            # Exit Python process - Windows scheduler/startup script will restart it
            os._exit(0)

# ==============================================================================
# SYMLINK MANAGER (MT4/MT5 Folder Symbolic Links)
# ==============================================================================

def load_symlink_config():
    """Load symlink configuration (backward compatible wrapper)"""
    # Use global bot_config (already loaded at startup)
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
    # Use global bot_config (already loaded at startup)
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

    print(f"[API] Symbols list requested: {len(symbols)} symbols available")

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
            <a href="/history" class="btn">📝 Request History</a>
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
            <div class="info">
                Total months: <strong>{len(symbol_files)}</strong>
            </div>
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

    # Load today's stats from file (if exists)
    load_stats_from_file()

    # Start file polling thread
    polling_thread = Thread(target=poll_files, daemon=True)
    polling_thread.start()

    # Start EA activity summary thread
    ea_activity_thread = Thread(target=ea_activity_summary_thread, daemon=True)
    ea_activity_thread.start()

    # Start stats backup thread
    stats_thread = Thread(target=stats_backup_thread, daemon=True)
    stats_thread.start()

    # Start weekly restart thread
    restart_thread = Thread(target=check_weekly_restart, daemon=True)
    restart_thread.start()

    # Start API server thread
    api_thread = Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # Start Dashboard server in main thread (blocking)
    run_dashboard_server()

if __name__ == "__main__":
    main()

