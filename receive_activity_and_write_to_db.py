import os
import time
import ssl
import mysql.connector
import pytz
import logging
import config
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import timezone

# Setting the basic configuration for logging
logging.basicConfig(filename='activity_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SLACK_API_TOKEN = config.SLACK_API_TOKEN
MYSQL_HOST = config.MYSQL_HOST
MYSQL_USER = config.MYSQL_USER
MYSQL_PASSWORD = config.MYSQL_PASSWORD
MYSQL_DB = config.MYSQL_DB
LAST_RUN_DATE_FILE = 'last_run_date.txt'

# Create a WebClient object using the Slack API access token
slack_client = WebClient(token=SLACK_API_TOKEN)

def get_users_list_from_database():
    """
    Gets a list of users from the database and returns it as a list of objects.
    """
    try:
        cnx = mysql.connector.connect(**config.MYSQL_CONNECTION_CONFIG)
        cursor = cnx.cursor()
        cursor.execute("SELECT user_id, user_name FROM users")
        users = cursor.fetchall()
        cnx.close()
        return users
    except mysql.connector.Error as e:
        print(f"Error getting users list from database: {e}")
        return []


def is_user_active(user_id):
    try:
        response = slack_client.users_getPresence(user=user_id)
        return response['presence'] == 'active'
    except SlackApiError as e:
        logging.error(f"Error getting user presence: {e}")
        return False

def get_user_timezone(user_id):
    try:
        cnx = mysql.connector.connect(**config.MYSQL_CONNECTION_CONFIG)
        cursor = cnx.cursor()
        cursor.execute("SELECT timezone FROM users WHERE user_id = %s", (user_id,))
        user_timezone = cursor.fetchone()
        cnx.close()

        if user_timezone:
            return user_timezone[0]
        else:
            return None
    except mysql.connector.Error as e:
        logging.error(f"Error getting user timezone: {e}")
        return None

def insert_user_activity(user_id, timestamp):
    try:
        if user_id is None or timestamp is None:
            logging.warning("User ID or timestamp is None, skipping insertion.")
            return

        cnx = mysql.connector.connect(**config.MYSQL_CONNECTION_CONFIG)
        cursor = cnx.cursor()
        cursor.execute("""
            INSERT INTO user_activity (user_id, timestamp)
            VALUES (%s, %s);
        """, (user_id, timestamp))
        cnx.commit()
        cnx.close()
        logging.info(f"Successfully inserted user activity for user {user_id} at {timestamp}.")
    except mysql.connector.Error as e:
        logging.error(f"Error inserting user activity: {e}")

# Function to update user activity
def update_user_activity_from_database():
    logging.info("Updating user activity from database.")
    users = get_users_list_from_database()
    for user in users:
        user_id, user_name = user
        if is_user_active(user_id):
            logging.info(f"User {user_name} ({user_id}) is active.")
            user_timezone = get_user_timezone(user_id)
            timestamp = datetime.utcnow()

            if user_timezone:
                local_tz = pytz.timezone(user_timezone)
                local_dt = timestamp.replace(tzinfo=timezone.utc).astimezone(local_tz)
                local_timestamp = local_tz.normalize(local_dt)
            else:
                local_timestamp = timestamp

            insert_user_activity(user_id, local_timestamp)
        else:
            logging.info(f"User {user_name} ({user_id}) is not active.")

# Main function
def main():
    logging.info("Starting user activity update.")
    try:
        update_user_activity_from_database()
    except Exception as e:
        logging.error(f"Error in updating user activity: {e}")

if __name__ == "__main__":
    main()