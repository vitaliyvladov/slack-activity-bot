import mysql.connector
from datetime import datetime, timedelta
import config

def transfer_old_data():
    twenty_days_ago = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')

    try:
        with mysql.connector.connect(**config.MYSQL_CONNECTION_CONFIG) as conn:
            cursor = conn.cursor()

            # Copy data older than 20 days to the new table
            copy_sql = f"""
                INSERT INTO user_activity_backup
                SELECT * FROM user_activity 
                WHERE timestamp < '{twenty_days_ago}'
            """
            cursor.execute(copy_sql)

            # Delete data older than 20 days from the original table
            delete_sql = f"""
                DELETE FROM user_activity 
                WHERE timestamp < '{twenty_days_ago}'
            """
            cursor.execute(delete_sql)

            conn.commit()

            print(f"Data older than {twenty_days_ago} has been transferred.")
    except mysql.connector.Error as e:
        print(f"Error transferring data: {e}")

if __name__ == "__main__":
    transfer_old_data()
