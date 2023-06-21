<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![LinkedIn][linkedin-shield]][linkedin-url]

<div>
<h3 align="center">Slack users activity bot</h3>

  <p align="center">
    A bot that automatically regularly checks the activity of Slack users and sends the results for the day or another selected period to Telegram
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

The bot, which requests the activity of each Slack user every 5 minutes (the time can be changed), writes the information to the database and then sends the following information about the user to the telegram channel via the cron:
- When the user appeared in Slack for the first time in a day
- When was the last time that day appeared in slack.
- How many times its activity was recorded.
- Daytime hours when the user was active

![Product Name Screen Shot][product-screenshot]
<!-- HOW TO INSTALL AND USE -->
## How to install and use

1. First you need to copy all the files to your server.
2. Install the dependencies specified in the requirements.txt file
3. Create a MySQL database and specify access to it in the config.py file
4. Get the TOKEN SLACK API and specify it in the config.py file
5. Create a telegram bot and a telegram channel and specify their data in the config.py file
6. Create tables in the database using the following migration from the create_db.sql file
7. Make a separate screen and run tg_bot_asker.py in it
8. Set up the following tasks in the scheduler:
  - python3 your_path/save_users_to_bd.py. _//Save to the database once a day_
  - python3 your_path/receive_activity_and_write_to_db.py. _//Get active users and write to the database. Every 5 minutes_
  - python3 your_path/send_activity_report_to_telegram.py yesterday. _//Sends data for yesterday to telegram every day_
  - python3 your_path/db_cleaner.py _//Move data to backup table. Once a week, at a different time than other schedulers.
_
How it works.
1. The **script save_users_to_bd.py** gets users from Slack, connects to the MySQL database and saves all users there that are not bots and not deleted.
2. The **receive_activity_and_write_to_db.py** script receives user activity in Slack and writes the activity time to the MySQL database.
3. The **send_activity_report_to_telegram.py** script selects data from the database on request with a period and sends a report to the telegram channel.
4. The **db_cleaner.py** script copies the data from the main table to the backup table and deletes the data from the main table.
5. The **tg_bot_asker.py** script allows you to request statistics from the bot's telegrams at any time.

<!-- USAGE EXAMPLES -->
## Settings and how it works

With this bot, I can see who starts the working day at what time. 

I see the time of the first Slack for today. 

Also, in the next column, I see the date and time of the user's last activity in Slack, even if it was not today. This allows you to understand, for example, that a person worked until night and you must say "thank you" to him. Or vice versa, has not entered the slack for a couple of days. 

The next column shows how many total user activities were recorded in slack for the specified period. User activity is recorded every five minutes, this indicator allows you to understand how active he is. 

The last column indicates the hours of the day when this user's activity was recorded. This indicator allows you to see, for example, those remote employees who leave the computer for 2-3 hours at lunchtime.

DO NOT USE THIS BOT FOR ANY MANAGEMENT DECISIONS OR FOR MICROMANAGEMENT. THIS BOT IS DESIGNED TO OBTAIN ADDITIONAL INFORMATION, BUT NOT TO USE IT AGAINST COLLEAGUES.


<!-- LICENSE -->
## License

Distributed under the MIT License.


<!-- CONTACT -->
## Contact

[![LinkedIn][linkedin-shield]][linkedin-url]




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/vitalii-vladov-65473511a/
[product-screenshot]: slack_activity.png
Footer
© 2023 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
