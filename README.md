# About

PyAppointment is a Django-based web application that allows people to book
appointments in your schedule, based on gaps in your calendar and defined
regions of availability. When people book an appointment, an event will be
created in your calendar and both attendee and organizer will receive an email
to notify that the booking has been made.

It relies on a (free) developer account with the calendar service
[Cronofy](https://www.cronofy.com). This means that it can use any of the
calendar services it supports, including Google Calendar, iCloud Calendar and
Outlook Exchange.

This webapp functions somewhat similarly to commerical services such as
[Calendly](https://calendly.com) and [YouCanBookMe](https://youcanbook.me), but
for a single user only and without quite a bit of the functionality and support
that these services offer.

# Requirements

- Python 3
- A method of deployment (e.g. `uwsgi`)
- A [Cronofy](https://www.cronofy.com) account

# Installation

PyAppointment works best using `virtualenv`. To install required dependencies,
clone the repository, `cd` into the root source directory and run the commands:

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

Deployment can be done as usual for Django webapps using `uwsgi`. A sample INI
file for deployment can be found [in the doc directory](doc/uwsgi.ini). Note
that due to a presently unresolved bug, you need to set the
`max-worker-lifetime` parameter to a reasonably short interval -- I suggest 1
hour (3600 seconds), otherwise the Cronofy service becomes unavailable.

# Configuration options

PyAppointment requires a `config.ini` file to be provided in the main directory,
which sets up the types of bookings you want to provide and their configuration
-- how long they should be, where they are held, and so on.

You can find a [sample config.ini file](config.ini.sample) in the sources, and
[more detailed documentation in the doc directory](doc/config.md).

# FAQs

- **This doesn't work at all/for my workflow.**  
  This is thoroughly beta-level software and has not been tested extensively! I
  welcome bug reports and, better, bug fixes through pull requests.

- **Will you implement feature xyz?**  
  Probably not, unless it aligns with my own feature requirements. However I
  certainly welcome requests and pull requests to make this better.
