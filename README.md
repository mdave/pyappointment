# What's this?

PyAppointment is a Django-based web application that allows people to book
appointments in your schedule, based on gaps in your calendar(s) and defined
regions of availability. When people book a slot, a booking will be created in
your calendar and both attendee and organizer will receive an email.

It functions somewhat similarly to fancier services like Calendly and
YouCanBook.Me, but for a single user only and without many of the bells and
whistles these services supply (or much support!)

PyAppointment relies on you having a (free) developer account with the calendar
service [https://www.cronofy.com](Cronofy). This means that it can use any of
the calendar services it supports, including Google Calendar, iCloud Calendar
and Outlook Exchange calendars.

# Installation

PyAppointment requires Python 3, and works best using `virtualenv`. To install
required dependencies, clone the repository, `cd` into the root source directory
and run the commands:

```bash
$ virtualenv -p python3 env
$ source env/bin/activate
$ pip install -r requirements.txt
```

For the frontend components (right now, just Bootstrap), you also need `yarn`
which can be installed through the node package manager `npm`.

```bash
$ npm install -g yarn   # If you don't have yarn.
$ yarn install          # Install front-end requirements.
```

Copy the `config.ini.sample` file to `config.ini` and modify the settings to
align with your desired meeting types and email configuration. Finally, perform
initial setup with:

```bash
$ python manage.py migrate
$ python manage.py collectstatic
```

Deployment can be done as usual for Django webapps using `uwsgi`.

# FAQs

- **This doesn't work at all/for my workflow.**  
  This is thoroughly beta-level software and has not been tested extensively! I
  welcome bug reports and, better, bug fixes through pull requests.

- **Will you implement feature xyz?**  
  Probably not unless it aligns with my own feature requirements. However I
  certainly welcome requests and pull requests to make this better.
