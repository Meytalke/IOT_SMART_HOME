import sqlite3
from sqlite3 import Error
import pandas as pd
import datetime

def time_format():
    return f'{datetime.datetime.now()}  |> '

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"{time_format()} Conected to version: {sqlite3.version}")
        return conn
    except Error as e:
        print(f"{time_format()} {e}")
    return conn


def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"{time_format()} {e}")


def init_db(database):
    """Initialize the database with tables for kitchen monitoring data."""
    tables = [
        """ CREATE TABLE IF NOT EXISTS `kitchen_data` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `timestamp` TEXT NOT NULL,
            `gas_level` REAL,
            `smoke_level` REAL,
            `temperature` REAL,
            `warning` TEXT,
            `alarm` TEXT
        ); """
    ]
    conn = create_connection(database)
    if conn is not None:
        for table in tables:
            create_table(conn, table)
        conn.close()
    else:
        print(f"{time_format()} Error! cannot create the database connection.")



def store_data(database, timestamp, gas_level, smoke_level, temperature, warning, alarm):
    """Store sensor data, warnings, and alarms in the database."""
    conn = create_connection(database)
    if conn:
        try:
            sql = ''' INSERT INTO kitchen_data(timestamp, gas_level, smoke_level, temperature, warning, alarm)
                      VALUES(?,?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, (timestamp, gas_level, smoke_level, temperature, warning, alarm))
            conn.commit()
            print(f"{time_format()} Data stored in database.")
        except Error as e:
            print(f"{time_format()} Error storing data: {e}")
        finally:
            conn.close()



def fetch_data(database, table_name, start_time, end_time):
    """Fetch data from the database within a specified time range."""
    conn = create_connection(database)
    try:
        query = f"SELECT * FROM {table_name} WHERE timestamp BETWEEN ? AND ?"
        df = pd.read_sql_query(query, conn, params=(start_time, end_time))
        return df
    except Error as e:
        print(f"{time_format()} Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
    finally:
        conn.close()

if __name__ == '__main__':
    DB_NAME = "test_kitchen_data.db"
    init_db(DB_NAME)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    store_data(DB_NAME, now, 35.5, None, 28.1, "Test Warning", None)
    start = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = fetch_data(DB_NAME, 'kitchen_data', start, end)
    print("\nData fetched from database:")
    print(data)
