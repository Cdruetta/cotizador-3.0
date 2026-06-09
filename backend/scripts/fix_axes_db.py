#!/usr/bin/env python3
"""
Backup the SQLite DB and recreate axes_accesslog without the session_hash column.
Run from the project root with the virtualenv python, e.g.
  .\.venv\Scripts\python backend\scripts\fix_axes_db.py

This script is idempotent: if the table already lacks session_hash it will do nothing.
"""
import os
import shutil
import sqlite3
from datetime import datetime


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, 'db.sqlite3')
BACKUP_PATH = os.path.join(ROOT, f'db.sqlite3.bak.{datetime.utcnow().strftime("%Y%m%d%H%M%S")}')


def table_has_column(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    for row in cur.fetchall():
        if row[1] == column:
            return True
    return False


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return 1

    print(f"Creating backup {BACKUP_PATH}...")
    shutil.copy2(DB_PATH, BACKUP_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        if not table_has_column(conn, 'axes_accesslog', 'session_hash'):
            print('axes_accesslog already lacks session_hash — nothing to do')
            return 0

        print('Recreating axes_accesslog without session_hash...')

        cur = conn.cursor()
        # Create new table without session_hash
        cur.execute('''
        CREATE TABLE IF NOT EXISTS axes_accesslog_new (
            id INTEGER PRIMARY KEY,
            user_agent varchar(255) NOT NULL,
            ip_address char(39),
            username varchar(255),
            http_accept varchar(1025) NOT NULL,
            path_info varchar(255) NOT NULL,
            attempt_time datetime NOT NULL,
            logout_time datetime
        )
        ''')

        # Copy existing data (excluding session_hash)
        cur.execute('''
        INSERT INTO axes_accesslog_new (id,user_agent,ip_address,username,http_accept,path_info,attempt_time,logout_time)
        SELECT id,user_agent,ip_address,username,http_accept,path_info,attempt_time,logout_time FROM axes_accesslog
        ''')

        # Drop old table and rename
        cur.execute('DROP TABLE axes_accesslog')
        cur.execute('ALTER TABLE axes_accesslog_new RENAME TO axes_accesslog')
        conn.commit()
        print('Recreated axes_accesslog without session_hash — done')
        return 0
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())
