from threading import Thread
from app import app
from mailjet_rest import Client
from flask import render_template, url_for
import re
import datetime
from dateutil.parser import parse


def send_contact_email(user, message, subject):
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


def send_invite_email(user):
    token = user.get_email_verification_token()
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
                "Subject": "Welcome to Lahoma Healing Arts",
                "ReplyTo": { "Email": user.email },
                "TextPart": render_template('email/welcome.txt',
                                         user=user, token=token),
                "HTMLPart": render_template('email/welcome.html',
                                         user=user, token=token)
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code == 200:
        print(result.json())
    else:
        print("Verification email failed to send with code " + str(result.status_code), result.reason)
    
    return result