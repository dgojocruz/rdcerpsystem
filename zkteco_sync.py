#!/usr/bin/env python3
"""
RHODECO ERP — ZKTeco Biometric Sync Service
============================================
Pulls attendance punches from ZKTeco device and pushes to ERP API.

Requirements:
    pip install pyzk requests schedule

Usage:
    python zkteco_sync.py --ip 192.168.1.201 --port 4370 --erp http://127.0.0.1:5000
    python zkteco_sync.py --test        # Test mode with dummy data

Config file: zkteco_config.json (auto-created on first run)
"""

import sys
import json
import time
import logging
import argparse
import sqlite3
import os
from datetime import datetime, timedelta

# ── Logging setup ────────────────────────────────────────────────────────────
LOG_FILE = 'zkteco_sync.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('zkteco_sync')

# ── Config ───────────────────────────────────────────────────────────────────
CONFIG_FILE = 'zkteco_config.json'
DEFAULT_CONFIG = {
    "devices": [
        {
            "name": "Main Entrance",
            "ip": "192.168.1.201",
            "port": 4370,
            "password": 0,
            "device_id": "DEVICE_001",
            "enabled": True
        },
        {
            "name": "Factory Floor",
            "ip": "192.168.1.202",
            "port": 4370,
            "password": 0,
            "device_id": "DEVICE_002",
            "enabled": False
        }
    ],
    "erp_url": "http://127.0.0.1:5000",
    "sync_interval_seconds": 60,
    "retry_on_fail": True,
    "retry_delay_seconds": 10,
    "max_retries": 3,
    "lookback_hours": 24,
    "log_file": "zkteco_sync.log"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        log.info(f"Created default config: {CONFIG_FILE}")
    with open(CONFIG_FILE) as f:
        return json.load(f)

# ── Local cache DB to avoid duplicate pushes ─────────────────────────────────
CACHE_DB = 'zkteco_cache.db'

def init_cache():
    conn = sqlite3.connect(CACHE_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS pushed_punches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        biometric_id TEXT NOT NULL,
        punch_datetime TEXT NOT NULL,
        punch_type TEXT NOT NULL,
        device_id TEXT,
        pushed_at TEXT DEFAULT (datetime('now')),
        status TEXT DEFAULT 'OK',
        UNIQUE(biometric_id, punch_datetime, punch_type)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS sync_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT,
        device_ip TEXT,
        synced_at TEXT DEFAULT (datetime('now')),
        punches_found INTEGER DEFAULT 0,
        punches_pushed INTEGER DEFAULT 0,
        punches_skipped INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        status TEXT DEFAULT 'OK',
        message TEXT
    )''')
    conn.commit()
    conn.close()

def is_already_pushed(biometric_id, punch_datetime, punch_type):
    conn = sqlite3.connect(CACHE_DB)
    row = conn.execute(
        "SELECT id FROM pushed_punches WHERE biometric_id=? AND punch_datetime=? AND punch_type=?",
        (biometric_id, str(punch_datetime), punch_type)
    ).fetchone()
    conn.close()
    return row is not None

def mark_pushed(biometric_id, punch_datetime, punch_type, device_id, status='OK'):
    conn = sqlite3.connect(CACHE_DB)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO pushed_punches (biometric_id, punch_datetime, punch_type, device_id, status) VALUES (?,?,?,?,?)",
            (biometric_id, str(punch_datetime), punch_type, device_id, status)
        )
        conn.commit()
    except:
        pass
    conn.close()

def log_sync(device_name, device_ip, found, pushed, skipped, errors, status, message=''):
    conn = sqlite3.connect(CACHE_DB)
    conn.execute(
        "INSERT INTO sync_log (device_name,device_ip,punches_found,punches_pushed,punches_skipped,errors,status,message) VALUES (?,?,?,?,?,?,?,?)",
        (device_name, device_ip, found, pushed, skipped, errors, status, message)
    )
    conn.commit()
    conn.close()

# ── Push to ERP ──────────────────────────────────────────────────────────────
def push_punch(erp_url, biometric_id, punch_datetime, punch_type, device_id, retries=3):
    import urllib.request
    payload = json.dumps({
        "biometric_id": str(biometric_id),
        "datetime": punch_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "type": punch_type,
        "device_id": device_id
    }).encode('utf-8')

    url = f"{erp_url}/timekeeping/biometric/punch"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                return True, result
        except Exception as e:
            log.warning(f"Push attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)

    return False, {"error": "Max retries exceeded"}

# ── Pull from ZKTeco device ──────────────────────────────────────────────────
def pull_from_device(device_config, lookback_hours=24):
    """Pull attendance records from ZKTeco device using pyzk library."""
    try:
        from zk import ZK, const
    except ImportError:
        log.error("pyzk not installed. Run: pip install pyzk")
        return None

    ip = device_config['ip']
    port = device_config.get('port', 4370)
    password = device_config.get('password', 0)

    zk = ZK(ip, port=port, timeout=10, password=password, force_udp=False, ommit_ping=False)
    conn = None
    try:
        log.info(f"Connecting to ZKTeco device at {ip}:{port}...")
        conn = zk.connect()
        conn.disable_device()

        # Get attendance records
        attendances = conn.get_attendance()
        log.info(f"Retrieved {len(attendances)} total records from device")

        # Filter by lookback window
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        recent = [a for a in attendances if a.timestamp >= cutoff]
        log.info(f"Filtered to {len(recent)} records in last {lookback_hours} hours")

        return recent

    except Exception as e:
        log.error(f"Error connecting to device {ip}: {e}")
        return None
    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()

def determine_punch_type(user_id, timestamp, all_punches):
    """
    Determine if a punch is IN or OUT based on the sequence for that user on that day.
    ZKTeco devices may store punch_type or just raw punches.
    """
    # Get all punches for this user on this date, sorted by time
    date_str = timestamp.strftime('%Y-%m-%d')
    user_punches = sorted([
        p for p in all_punches
        if str(p.user_id) == str(user_id) and p.timestamp.strftime('%Y-%m-%d') == date_str
    ], key=lambda x: x.timestamp)

    # Find position of current punch
    pos = next((i for i, p in enumerate(user_punches) if p.timestamp == timestamp), 0)

    # Odd positions (0,2,4) = IN, Even positions (1,3,5) = OUT
    return 'IN' if pos % 2 == 0 else 'OUT'

# ── Main sync function ────────────────────────────────────────────────────────
def sync_device(device_config, erp_url, lookback_hours=24):
    name = device_config['name']
    ip = device_config['ip']
    device_id = device_config.get('device_id', 'DEVICE_001')

    log.info(f"{'='*50}")
    log.info(f"Syncing: {name} ({ip})")

    punches = pull_from_device(device_config, lookback_hours)
    if punches is None:
        log_sync(name, ip, 0, 0, 0, 1, 'ERROR', f'Failed to connect to device')
        return

    found = len(punches)
    pushed = skipped = errors = 0

    for punch in punches:
        bio_id = str(punch.user_id)
        ts = punch.timestamp

        # Determine punch type
        if hasattr(punch, 'punch') and punch.punch in [0, 1]:
            punch_type = 'IN' if punch.punch == 0 else 'OUT'
        else:
            punch_type = determine_punch_type(bio_id, ts, punches)

        # Skip if already pushed
        if is_already_pushed(bio_id, ts, punch_type):
            skipped += 1
            continue

        # Push to ERP
        success, result = push_punch(erp_url, bio_id, ts, punch_type, device_id)
        if success:
            mark_pushed(bio_id, ts, punch_type, device_id, 'OK')
            pushed += 1
            log.info(f"  Pushed: Bio {bio_id} | {ts} | {punch_type}")
        else:
            mark_pushed(bio_id, ts, punch_type, device_id, 'FAILED')
            errors += 1
            log.error(f"  Failed: Bio {bio_id} | {ts} | {result}")

    status = 'OK' if errors == 0 else 'PARTIAL'
    log_sync(name, ip, found, pushed, skipped, errors, status)
    log.info(f"Done: {found} found, {pushed} pushed, {skipped} skipped, {errors} errors")

# ── Test mode with dummy data ─────────────────────────────────────────────────
def run_test_mode(erp_url):
    log.info("Running in TEST MODE — using dummy punch data")
    today = datetime.now().strftime('%Y-%m-%d')

    test_punches = [
        ('001', f'{today} 07:58:00', 'IN'),
        ('001', f'{today} 17:02:00', 'OUT'),
        ('002', f'{today} 08:03:00', 'IN'),
        ('002', f'{today} 19:15:00', 'OUT'),
        ('003', f'{today} 08:22:00', 'IN'),
        ('003', f'{today} 17:00:00', 'OUT'),
    ]

    pushed = 0
    for bio_id, ts_str, punch_type in test_punches:
        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
        if is_already_pushed(bio_id, ts, punch_type):
            log.info(f"  SKIP (already pushed): Bio {bio_id} | {ts_str} | {punch_type}")
            continue
        success, result = push_punch(erp_url, bio_id, ts, punch_type, 'TEST_DEVICE')
        if success:
            mark_pushed(bio_id, ts, punch_type, 'TEST_DEVICE', 'OK')
            log.info(f"  OK: Bio {bio_id} | {ts_str} | {punch_type} → {result}")
            pushed += 1
        else:
            log.error(f"  FAIL: Bio {bio_id} | {result}")

    log.info(f"Test complete: {pushed}/{len(test_punches)} pushed")

# ── Sync status report ────────────────────────────────────────────────────────
def print_status():
    conn = sqlite3.connect(CACHE_DB)
    print("\n=== SYNC STATUS REPORT ===")
    rows = conn.execute("""
        SELECT device_name, synced_at, punches_found, punches_pushed,
               punches_skipped, errors, status
        FROM sync_log ORDER BY synced_at DESC LIMIT 20
    """).fetchall()
    print(f"{'Device':<20} {'Time':<20} {'Found':>6} {'Pushed':>7} {'Skip':>5} {'Err':>4} {'Status'}")
    print('-' * 75)
    for r in rows:
        print(f"{r[0]:<20} {r[1]:<20} {r[2]:>6} {r[3]:>7} {r[4]:>5} {r[5]:>4} {r[6]}")

    total = conn.execute("SELECT COUNT(id) FROM pushed_punches").fetchone()[0]
    print(f"\nTotal unique punches in cache: {total}")
    conn.close()

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='RHODECO ZKTeco Sync Service')
    parser.add_argument('--ip', help='ZKTeco device IP address')
    parser.add_argument('--port', type=int, default=4370, help='ZKTeco device port (default: 4370)')
    parser.add_argument('--erp', default='http://127.0.0.1:5000', help='ERP base URL')
    parser.add_argument('--interval', type=int, default=60, help='Sync interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test', action='store_true', help='Test mode with dummy data')
    parser.add_argument('--status', action='store_true', help='Show sync status report')
    parser.add_argument('--lookback', type=int, default=24, help='Hours to look back for punches')
    args = parser.parse_args()

    init_cache()

    if args.status:
        print_status()
        return

    if args.test:
        run_test_mode(args.erp)
        return

    config = load_config()
    erp_url = args.erp or config.get('erp_url', 'http://127.0.0.1:5000')
    interval = args.interval or config.get('sync_interval_seconds', 60)
    lookback = args.lookback or config.get('lookback_hours', 24)

    # Override IP if provided via command line
    if args.ip:
        config['devices'] = [{
            'name': 'Command Line Device',
            'ip': args.ip,
            'port': args.port,
            'password': 0,
            'device_id': 'DEVICE_001',
            'enabled': True
        }]

    enabled_devices = [d for d in config['devices'] if d.get('enabled', True)]
    log.info(f"RHODECO ZKTeco Sync Service starting")
    log.info(f"ERP URL: {erp_url}")
    log.info(f"Devices: {len(enabled_devices)}")
    log.info(f"Interval: {interval}s")

    if args.once:
        for device in enabled_devices:
            sync_device(device, erp_url, lookback)
        return

    # Continuous sync loop
    log.info("Starting continuous sync loop. Press Ctrl+C to stop.")
    while True:
        try:
            for device in enabled_devices:
                sync_device(device, erp_url, lookback)
        except KeyboardInterrupt:
            log.info("Sync service stopped by user.")
            break
        except Exception as e:
            log.error(f"Unexpected error: {e}")

        log.info(f"Next sync in {interval} seconds...")
        time.sleep(interval)

if __name__ == '__main__':
    main()
