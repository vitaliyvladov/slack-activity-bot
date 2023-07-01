# -*-
import os
import mysql.connector
import argparse
import config
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime, timedelta


TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
MYSQL_CONNECTION_CONFIG = config.MYSQL_CONNECTION_CONFIG
CHAT_ID = config.CHAT_ID

def query_database(period):
    print("Querying the database...")
    results = []

    # Defining a condition depending on the passed period
    if period == 'today':
        time_condition = 'DATE(ua.timestamp) = CURDATE()'
    elif period == 'yesterday':
        time_condition = 'DATE(ua.timestamp) = CURDATE() - INTERVAL 1 DAY'
    elif period == 'week':
        time_condition = 'ua.timestamp >= CURDATE() - INTERVAL 1 WEEK'
    else:
        print("Invalid period. Please specify 'today', 'yesterday', or 'week'.")
        return

    try:
        with mysql.connector.connect(**MYSQL_CONNECTION_CONFIG) as conn:
            cursor = conn.cursor()

            # Use condition in SQL query
            cursor.execute(f"""
    WITH today_first_activity AS (
    SELECT
        ua.user_id,
        MIN(ua.timestamp) as first_activity_today
    FROM user_activity ua
    JOIN users u ON ua.user_id = u.user_id
    WHERE {time_condition}
    GROUP BY ua.user_id
),
last_activity AS (
    SELECT
        ua.user_id,
        MAX(ua.timestamp) as last_activity
    FROM user_activity ua
    JOIN users u ON ua.user_id = u.user_id
    GROUP BY ua.user_id
),
activity_hours AS (
    SELECT
        ua.user_id,
        GROUP_CONCAT(DISTINCT HOUR(ua.timestamp)) AS active_hours
    FROM user_activity ua
    JOIN users u ON ua.user_id = u.user_id
    WHERE {time_condition}
    GROUP BY ua.user_id
)

SELECT
    u.full_name AS User_Name,
    DATE_FORMAT(tfa.first_activity_today, '%H:%i') AS Start_today,
    DATE_FORMAT(la.last_activity, '%Y-%m-%d %H:%i') AS Last_time,
    COUNT(ua.timestamp) AS All_today,
    ah.active_hours AS Active_hours
FROM
    users u
LEFT JOIN
    today_first_activity tfa ON u.user_id = tfa.user_id
LEFT JOIN
    last_activity la ON u.user_id = la.user_id
LEFT JOIN
    activity_hours ah ON u.user_id = ah.user_id
LEFT JOIN
    user_activity ua ON u.user_id = ua.user_id AND {time_condition}
GROUP BY
    u.user_id
ORDER BY
    COUNT(ua.timestamp) DESC,
    u.user_id
        """)  

            results = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error querying database: {e}")

    print(f"Retrieved {len(results)} rows from the database.")
    return results

def process_active_hours(hours_str):
    if hours_str is None:
        return []
    hours = list(map(int, hours_str.split(',')))
    i = 0
    while i < len(hours) - 2:
        if hours[i+1] - hours[i] == 1 and hours[i+2] - hours[i+1] == 1:
            start = hours[i]
            while i < len(hours) - 1 and hours[i+1] - hours[i] == 1:
                i += 1
            end = hours[i]
            yield f"{start}-{end}"
        else:
            yield str(hours[i])
        i += 1
    while i < len(hours):
        yield str(hours[i])
        i += 1


def send_data_to_telegram(chat_id, data, date_range):
    print("Attempting to send data to Telegram...")
    bot = Updater(token=TELEGRAM_BOT_TOKEN).bot

    # Construct the message
    message = f"<b>Results from DB for {date_range}:</b>\n\n"

    # Add the headers
    headers = [
        "User_Name",
        "Start_time",
        "Last_time",
        "All_per_day",
        "Active_hours",
    ]

    # Calculate max width for each column
    col_widths = [len(header) for header in headers]
    for row in data:
        row = list(row)
        row[-1] = ', '.join(process_active_hours(row[-1]))
        for i, value in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(value)))

    # Format table with calculated widths
    message += "<pre>"
    for i, header in enumerate(headers):
        message += header.ljust(col_widths[i]) + " | "
    message = message[:-3] + "\n"  # Remove extra space and vertical bar from the last header

    message += "-" * (sum(col_widths) + len(headers) * 3 - 1) + "\n"

    for row in data:
        row = list(row)
        if row[-1] is not None:
            row[-1] = ', '.join(process_active_hours(row[-1]))
        for i, value in enumerate(row):
            message += str(value).ljust(col_widths[i]) + " | "
        message = message[:-3] + "\n"  # Remove extra space and vertical bar from the last value


    message += "</pre>"

    # Send the message to Telegram in parts if it's too long
    try:
        MAX_MESSAGE_LENGTH = 4096
        while len(message) > 0:
            if len(message) <= MAX_MESSAGE_LENGTH:
                bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                message = ""
            else:
                part = message[:MAX_MESSAGE_LENGTH].rsplit('\n', 1)[0]
                if '</pre>' not in part:
                    part += "</pre>"
                bot.send_message(chat_id=chat_id, text=part, parse_mode='HTML')
                message = "<pre>" + message[len(part) - 5:]
        print("Data sent to Telegram successfully.")
    except Exception as e:
        print(f"Error sending data to Telegram: {e}")

        
def main():
    parser = argparse.ArgumentParser(description='Query database and send results to Telegram.')
    parser.add_argument('period', type=str, choices=['today', 'yesterday', 'week'], help='Time period for which to get the data.')
    args = parser.parse_args()

    if args.period == 'today':
        date_range = datetime.now().date()
    elif args.period == 'yesterday':
        date_range = datetime.now().date() - timedelta(days=1)
    elif args.period == 'week':
        date_range = f"{datetime.now().date() - timedelta(days=7)} - {datetime.now().date()}"

    data = query_database(args.period)
    send_data_to_telegram(CHAT_ID, data, date_range)

if __name__ == "__main__":
    main()