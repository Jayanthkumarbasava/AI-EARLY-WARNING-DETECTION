import sqlite3
from datetime import datetime

DB_NAME = "system_monitor.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# CREATE TABLE
# =====================================================
def create_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cpu REAL,
                memory REAL,
                disk REAL,
                latency REAL,
                errors INTEGER,
                prediction INTEGER,
                probability REAL
            )
        """)

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database creation error:", e)


# =====================================================
# INSERT DATA
# =====================================================
def insert_data(data, prediction, probability):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO system_data (
                timestamp, cpu, memory, disk, latency, errors,
                prediction, probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["CPU"],
            data["Memory"],
            data["Disk"],
            data["Latency"],
            data["Errors"],
            int(prediction),
            float(probability)
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Insert error:", e)


# =====================================================
# LOAD LAST 100 RECORDS
# =====================================================
def load_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM system_data
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print("Load error:", e)
        return []


# =====================================================
# FILTER DATA (Admin Dashboard)
# =====================================================
def filter_data(start_date=None, end_date=None,
                risk=None, min_cpu=None, max_cpu=None):

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM system_data WHERE 1=1"
        params = []

        if start_date:
            query += " AND date(timestamp) >= date(?)"
            params.append(start_date)

        if end_date:
            query += " AND date(timestamp) <= date(?)"
            params.append(end_date)

        if risk is not None:
            query += " AND prediction = ?"
            params.append(risk)

        if min_cpu is not None:
            query += " AND cpu >= ?"
            params.append(min_cpu)

        if max_cpu is not None:
            query += " AND cpu <= ?"
            params.append(max_cpu)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print("Filter error:", e)
        return []
