# Language speaking club

## Application functionalities

* In the app, users can look for members to join speaking sessions of chosen languages and look for sessions to join. An announcement includes the language spoken, targeted number of members, and date, time and location.
* User can create an account and log in to the web application.
* Users can publish, edit and delete announcements.
* The users can see the announcements posted by themselves and the others.
* Users can look for speaking sessions by specific keywords.
* The user page displays the number of announcements that they have posted, the number of sessions that they have participated in, the languages they speak and their levels (beginner/intermediate/advanced/native).
* The user can classify their sessions by languages, locations, and levels (beginner/intermediate/advanced).
* The users can register for a sessions, and the announcement can update the numbers of slots left after each user registration.
* The user can send message to the session hosts (I am not sure if this is doable though).

## User guidance
After cloning the project from Github, follow the commands below to get the application started.

Install the `flask` library:
```
$ pip install flask
```
Create a new database (on Linux):
```
$ sqlite3 database.db < schema.sql
```
Create a new database on Windows Powershell:
```
sqlite3 database.db
sqlite> .read schema.sql
```
Launch the application:
```
flask run
```
