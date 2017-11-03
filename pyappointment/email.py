import smtplib, icalendar, pytz, email
import datetime as dt

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from pyappointment.settings import ORGANIZER_EMAIL, ORGANIZER_NAME, ORGANIZER_GREETING, BOOKING_TYPES, EMAIL_ADDRESS

def send_organizer_email(start, finish, name, booking_type, notes, uid):
    template_params = {
        'date': start,
        'booking_info': BOOKING_TYPES[booking_type],
        'recipient': name,
        'organizer': ORGANIZER_GREETING
    }

    email_msg = EmailMultiAlternatives(
        'Booking received: ' + name + ' (' + BOOKING_TYPES[booking_type]['description'] + ')',
        render_to_string('emails/to-organizer.txt', template_params),
        EMAIL_ADDRESS,
        [ '%s <%s>' % (ORGANIZER_NAME, ORGANIZER_EMAIL) ]
    )

    email_msg.attach_alternative(render_to_string('emails/to-organizer.html', template_params), "text/html")
    email_msg.send()

def send_attendee_email(start, finish, name, booking_type, notes, uid, mail_address):
    cal = icalendar.Calendar()
    cal.add('prodid', '-//pyappointment//pyappointment//')
    cal.add('version', '2.0')
    cal.add('method', "REQUEST")

    tz         = start.tzinfo
    mail_recip = '%s <%s>' % (name, mail_address)

    event = icalendar.Event()
    event.add('attendee', 'MAILTO:%s' % mail_address)
    event.add('organizer', 'MAILTO:%s' % ORGANIZER_EMAIL)
    event.add('status', "confirmed")
    event.add('category', "Event")
    event.add('summary', BOOKING_TYPES[booking_type]['description'])
    event.add('description', 'Additional notes: ' + notes)
    event.add('location', BOOKING_TYPES[booking_type]['location'])
    event.add('dtstart', start)
    event.add('dtend', finish)
    event.add('dtstamp', tz.localize(dt.datetime.now()))
    event.add('created', tz.localize(dt.datetime.now()))
    event.add('priority', 5)
    event.add('sequence', 1)

    event['uid'] = uid # Generate some unique ID

    cal.add_component(event)

    template_params = {
        'date': start,
        'booking_info': BOOKING_TYPES[booking_type],
        'recipient': name,
        'organizer': ORGANIZER_GREETING
    }

    email_msg = EmailMultiAlternatives(
        'Booking confirmation',
        render_to_string('emails/to-attendee.txt', template_params),
        EMAIL_ADDRESS,
        [ mail_recip ],
        headers={'Content-class': "urn:content-classes:calendarmessage"},
    )

    email_msg.attach_alternative(render_to_string('emails/to-attendee.html', template_params), "text/html")
  
    filename = "invite.ics"
    part = email.mime.base.MIMEBase('text', "calendar", method="REQUEST", name=filename)
    part.set_payload(cal.to_ical())
    email.encoders.encode_base64(part)
    part.add_header('Content-Description', filename)
    part.add_header("Content-class", "urn:content-classes:calendarmessage")
    part.add_header("Filename", filename)
    part.add_header("Path", filename)
    email_msg.attach(part)

    email_msg.send()
