from threading import Thread
from app import app
from mailjet_rest import Client
from flask import render_template, url_for
import re
import datetime
from dateutil.parser import parse


def verify_quote(quote):
    # Use fallback quote if request fails
    if quote is not None:
        message = quote.json()[0]['q']
        author = quote.json()[0]['a']
        quote_header = "<strong>Random inspirational quote of the day:</strong><br/>"
    else:
        message = "We don't have to do all of it alone. We were never meant to."
        author = "Brene Brown"
        quote_header = ""
    return message, author, quote_header


def send_contact_email(user, message, subject):
    api_key = app.config['MAILJET_KEY']
    api_secret = app.config['MAILJET_SECRET']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {
                    "Email": app.config['MAIL_USERNAME'],
                    "Name": "Danny Pernik"
                },
                "To": [
                    {
                    "Email": app.config['MAIL_USERNAME']
                    }
                ],
                "Subject": "Open Path Tutoring: " + subject + " from " + user.first_name,
                "ReplyTo": { "Email": user.email },
                "TextPart": render_template('email/inquiry-form.txt',
                                         user=user, message=message),
                "HTMLPart": render_template('email/inquiry-form.html',
                                         user=user, message=message)
            }
        ]
    }

    result = mailjet.send.create(data=data)

    if result.status_code is 200:
        send_confirmation_email(user, message)
        print("Confirmation email sent to " + user.email)
    else:
        print("Contact email failed with code " + result.status_code)
    print(result.json())


def send_confirmation_email(user, message):
    api_key = app.config['MAILJET_KEY']
    api_secret = app.config['MAILJET_SECRET']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {
                    "Email": app.config['MAIL_USERNAME'],
                    "Name": "Open Path Tutoring"
                },
                "To": [
                    {
                    "Email": user.email
                    }
                ],
                "Subject": "Email confirmation + a quote from Brene Brown",
                "TextPart": render_template('email/confirmation.txt',
                                         user=user, message=message),
                "HTMLPart": render_template('email/confirmation.html',
                                         user=user, message=message)
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code is 200:
        print(result.json())
    else:
        print("Confirmation email failed to send with code " + result.status_code, result.reason)


def send_reminder_email(event, client, tutor, quote):
    api_key = app.config['MAILJET_KEY']
    api_secret = app.config['MAILJET_SECRET']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    dt = datetime.datetime

    start_time = event['start'].get('dateTime')
    start_date = dt.strftime(parse(start_time), format="%A, %b %-d, %Y")
    start_time_formatted = re.sub(r'([-+]\d{2}):(\d{2})(?:(\d{2}))?$', r'\1\2\3', start_time)

    tz_difference = client.timezone - teacher.timezone

    start_offset = dt.strptime(start_time_formatted, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(hours = tz_difference)
    end_time = event['end'].get('dateTime')
    end_time_formatted = re.sub(r'([-+]\d{2}):(\d{2})(?:(\d{2}))?$', r'\1\2\3', end_time)
    end_offset = dt.strptime(end_time_formatted, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(hours = tz_difference)
    start_display = dt.strftime(start_offset, "%-I:%M%p").lower()
    end_display = dt.strftime(end_offset, "%-I:%M%p").lower()

    message, author, quote_header = verify_quote(quote)

    if client.timezone is -2:
        timezone = "Pacific"
    elif client.timezone is -1:
        timezone = "Mountain"
    elif client.timezone is 0:
        timezone = "Central"
    elif client.timezone is 1:
        timezone = "Eastern"
    else:
        timezone = "your"

    location = event.get('location')
    if location is None:
        location = client.location

    cc_email = [{ "Email": client.parent_email }]
    if client.secondary_email:
        cc_email.append({ "Email": client.secondary_email })
    if teacher.email:
        cc_email.append({ "Email": teacher.email })

    data = {
        'Messages': [
            {
                "From": {
                    "Email": app.config['MAIL_USERNAME'],
                    "Name": "Open Path Tutoring"
                },
                "To": [
                    {
                    "Email": client.email
                    }
                ],
                "Cc": cc_email,
                "Subject": "Reminder for " + event.get('summary') + " + a quote from " + author,
                "HTMLPart": "Hi " + client.first_name + ", this is an automated reminder " + \
                    " that you are scheduled for a tutoring session with " + teacher.first_name + " " + \
                    teacher.last_name + " on " + start_date + " from  " + start_display + " to " + \
                    end_display + " " + timezone + " time. <br/><br/>" + "Location: " + location + \
                    "<br/><br/>" + "You are welcome to reply to this email with any questions. " + \
                    "Please provide at least 24 hours notice when cancelling or rescheduling " + \
                    "in order to avoid being charged for the session. Note that you will not receive " + \
                    "a reminder email for sessions scheduled less than 2 days in advance. Thank you!" + \
                    "<br/><br/><br/>" + \
                    quote_header + '"' + message + '"' + "<br/>&ndash; " + author
            }
        ]
    }

    result = mailjet.send.create(data=data)

    if result.status_code is 200:
        print(client.first_name, client.last_name, start_display, timezone)
    else:
        print("Error for " + client.first_name + " with code " + str(result.status_code), result.reason)


def weekly_report_email(scheduled_session_count, scheduled_hours, scheduled_client_count, \
    unscheduled_list, outsourced_session_count, outsourced_hours, \
    outsourced_scheduled_client_count, outsourced_unscheduled_list, \
    paused, now, quote):

    api_key = app.config['MAILJET_KEY']
    api_secret = app.config['MAILJET_SECRET']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    dt = datetime.datetime
    start = (now + datetime.timedelta(hours=39)).isoformat() + 'Z'
    start_date = dt.strftime(parse(start), format="%b %-d")
    end = (now + datetime.timedelta(days=7, hours=31)).isoformat() + 'Z'
    end_date = dt.strftime(parse(end), format="%b %-d")
    unscheduled_clients = ', '.join(unscheduled_list)
    if unscheduled_clients == '':
        unscheduled_clients = "None"
    outsourced_unscheduled_clients = ', '.join(outsourced_unscheduled_list)
    if outsourced_unscheduled_clients == '':
        outsourced_unscheduled_clients = "None"
    paused_clients = ', '.join(paused)
    if paused_clients == '':
        paused_clients = "None"

    message, author, quote_header = verify_quote(quote)

    data = {
        'Messages': [
            {
                "From": {
                    "Email": app.config['MAIL_USERNAME'],
                    "Name": "Open Path Tutoring"
                },
                "To": [
                    {
                    "Email": app.config['MAIL_USERNAME']
                    },
                    {
                    "Email": app.config['MOM_EMAIL']
                    },
                    {
                    "Email": app.config['DAD_EMAIL']
                    }
                ],
                "Subject": "Weekly tutoring report for " + start_date + " to " + end_date,
                "HTMLPart": "A total of " + scheduled_hours + " hours (" + scheduled_session_count + " sessions) " + \
                    "are scheduled with Danny for " + scheduled_client_count + " clients next week. <br/><br/>" + \
                    "An additional " + outsourced_hours + " hours (" + outsourced_session_count + " sessions) " + \
                    "are scheduled with other tutors for " + outsourced_scheduled_client_count + " clients. " + \
                    "<br/><br/>Unscheduled active clients for Danny: " + unscheduled_clients + \
                    "<br/>Unscheduled active clients for other tutors: " + outsourced_unscheduled_clients + \
                    "<br/>Paused clients: " + paused_clients + \
                    "<br/><br/><br/>" + quote_header + '"' + message + '"' + "<br/>&ndash; " + author
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code is 200:
        print("\nWeekly report email sent.\n")
    else:
        print("\nWeekly report email error:", str(result.status_code), result.reason, "\n")
    print(result.json())
