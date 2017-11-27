# Configuration options

PyAppointment requires a `config.ini` file to be provided that defines basic
configuration parameters. This is done in a standard INI-format with an extended
JSON format to allow the definition of more complex configuration parameters.
The INI file is split up into several blocks which are documented below.

## `django` block

This block defines basic Django configuration parameters.

| Option name   | Description                                                                                                               |
|---------------|---------------------------------------------------------------------------------------------------------------------------|
| SECRET_KEY    | A standard Django setting that defines a secret key used to hash your data.                                               |
| ALLOWED_HOSTS | When running in debug mode, lists the hosts that are allowed to access the development server. Defaults to local domains. |
| DEBUG         | Sets debug mode. Should be set to `false' for production.                                                                 |
| ADMINS        | A list of email addresses that are contacted with server errors.                                                          |

## `meetings` block

This block defines the booking types your installation will support. 

| Option name        | Description                                                                               |
|--------------------|-------------------------------------------------------------------------------------------|
| ORGANIZER_NAME     | The name of the organiser (probably you!)                                                 |
| ORGANIZER_EMAIL    | The email address of the organiser                                                        |
| ORGANIZER_GREETING | A shortened version of the name used in greetings, e.g. 'Dave' instead of your full name. |
| BOOKING_TYPES      | A dictionary that outlines the bookings and their configuration options                   |

### Configuring booking types

The `config.ini.sample` file gives an example of how bookings inside
`BOOKING_TYPES` are defined. A sample booking looks like:

```json
"tutorial": {
    "description": "Tutorial"
    "duration": 30,
    "slots": 30,
    "location": "My office",
    "lead_time": 2,
    "future_limit": 21,
    "hidden": false
}
```

In detail, these options control the following settings:

| Option name   | Description                                                                                                                               |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `description` | A short description of this booking type. This will be used to define the name of the event in your calendar.                             |
| `duration`    | The duration this booking should be, in minutes.                                                                                          |
| `slots`       | How frequently booking slots should appear on the weekly schedule, in minutes.                                                            |
| `location`    | A description of where the meeting will take place. This will appear in your calendar event.                                              |
| `lead_time`   | Number of hours lead time for bookings. For example if the current time is 12:00 and `lead_time` is 2, bookings are available from 14:00. |
| `future_time` | Number of days that bookings can be made in advance. Set to 0 to allow bookings at any future date.                                       |
| `hidden`      | If `true`, this booking will appear on the main index.                                                                                    |

## `email` block

This block defines which email server and address is used to send correspondence
to users. By default, the organiser and the attendee will receive email
notifications (this will be customisable in future versions, hopefully!)

| Option name   | Description                                         |
|---------------|-----------------------------------------------------|
| USE_SSL       | If `true`, use SSL to connect to the mail server.   |
| ADDRESS       | Email address to use for emails from PyAppointment. |
| HOST          | SMTP host                                           |
| HOST_USER     | Username for SMTP authentication.                   |
| HOST_PASSWORD | Password for SMTP authentication.                   |

## `cronofy` block

This block defines a single parameter, `ACCESS_TOKEN`, which is the developer
access token for your Cronofy account.

## `calendar` block

This block defines how PyAppointment should interact with your calendars.

| Option name               | Description                                                                                                                                                                                              |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TIMEZONE`                | Sets the timezone for your region, e.g. `Europe/London`.                                                                                                                                                 |
| `CHECK`                   | A list of calendar names to check your schedule for conflicts. These should be exactly as they appear in your list of calendars in Cronofy.                                                              |
| `BOOK`                    | The name of the calendar into which events will be created. This should probably be one of the calendars you name in the `CHECK` parameter.                                                              |
| `SHOW_REASONS`            | If set to `true`, will show the reason that an event is unavailable on the week view of appointment times.                                                                                               |
| `SHOW_CONFLICTING_EVENTS` | If set to `true` and `SHOW_REASONS` is `true`, the precise event that conflicts with a given time will appear in the tooltip. Recommended to set to `false` unless you're debugging for privacy reasons. |

## `availability` block

This block defines your regions of availability for each day of the
week, and controls what times are shown on the weekly view of slots.

Availability should be defined in 1 or more blocks of 24-hour formatted time
separated by commas. For example, the string `09:30-12:30, 13:30-16:30` means
that you'll be available for bookings between 09:30-12:30 and 13:30-16:30.

If you don't want to be available at all (e.g. on the weekends), enter the
string `"None"` or leave the string empty.
