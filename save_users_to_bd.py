import os
import ssl
import mysql.connector
import config
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_API_TOKEN = config.SLACK_API_TOKEN

# Create a WebClient object using the Slack API token
client = WebClient(token=SLACK_API_TOKEN)

try:
    # Get a list of all users in the Slack workspace
    response = client.users_list(include_locale=True, is_bot=False)
    users = response['members']

    # Create a connection to the MySQL database
    cnx = mysql.connector.connect(**config.MYSQL_CONNECTION_CONFIG)

    # Use a cursor to execute SQL queries and write data to the database
    cursor = cnx.cursor()
    for user in users:
        # Check if the user is not a bot or deleted
        if not user.get('is_bot', False) and not user['deleted']:
            # Extract the user ID, name, full name, and timezone from the user object
            user_id = user['id']
            user_name = user['name']
            full_name = user['profile']['real_name']
            timezone = user['tz']

            # Check if the user already exists in the database
            select_user = ("SELECT * FROM users WHERE user_id = %s")
            cursor.execute(select_user, (user_id,))
            existing_user = cursor.fetchone()

            if existing_user is not None:
                # Update the timezone for the existing user
                update_user = ("UPDATE users SET timezone = %s WHERE user_id = %s")
                cursor.execute(update_user, (timezone, user_id))
                print(f"Updated timezone for user {user_id}")

            else:
                # Insert the user into the database
                add_user = ("INSERT INTO users "
                            "(user_id, user_name, full_name, timezone) "
                            "VALUES (%s, %s, %s, %s)")

                cursor.execute(add_user, (user_id, user_name, full_name, timezone))
                print(f"Added new user {user_id}")

            # Commit the changes to the database
            cnx.commit()

except SlackApiError as e:
    print("Error accessing the Slack API: {}".format(e))

except mysql.connector.Error as err:
    print("Error while working with the database: {}".format(err))

finally:
    # Close the connection to the MySQL database
    if 'cnx' in locals():
        cnx.close()
