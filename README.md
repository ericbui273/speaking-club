# Language speaking club

## Application functionalities

* In the app, users can look for members to join speaking sessions of chosen languages and look for sessions to join. An announcement includes the language spoken, targeted number of members, and date, time and location.
* User can create an account and log in to the web application.
* Users can publish, edit and delete announcements.
* The users can see the announcements posted by themselves and the others.
* The meetup host can see the list of participants.
* Users can look for speaking sessions by specific keywords.
* The user page displays the number of announcements that they have posted and the number of sessions that they have participated in.
* The user can classify their sessions by languages, locations, and levels (beginner/intermediate/advanced).
* The users can register for a sessions, and the announcement can update the numbers of slots left after each user registration.

## User guidance
After cloning the project from Github, follow the commands below to get the application started.

Install the `flask` library:
```
$ pip install flask
```
Create and initialize a new database (on Linux):
```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```
Create and initialize a new database on Windows Powershell:
```
sqlite3 database.db
sqlite> .read schema.sql
sqlite> .read init.sql
```
Launch the application:
```
$ flask run
```

## Test with large amount of data
Run the following command to inject the seed data and test the processing of large data amount by yourself:
```
$ python3 seed.py
```

### Test setup
A seed file was created to inject a large amount of data into the database to test how the application process when the amount of data is large.

The test was done with 1000 user accounts, 10^5 meetups created by random users, and 10^6 meetup participants randomly distributed to all meetups.

### Overall result
In overall, the application works well with the seed data. Pagination was added to the front page, user page, and search page to ensure a logical and easy-to-use interface.

### Runtime result
The application does not have a site where all the primary data (meetups) and secondary data (participant list) are queried and shown together. Instead, the participant list is only visible to the meetup host, and was queried only with its own meetup. As a result, it does not take long at all to load the front page even with a large amount of meetups.

Loading the front page only took _**0.0 to 0.07 seconds**_.

This runtime is achieved even without the database index. Therefore, there was no need to add the database index.

