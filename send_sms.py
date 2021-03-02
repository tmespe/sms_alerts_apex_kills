import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
messaging_sid = os.getenv("TWILIO_MESSAGE_SID")
client = Client(account_sid, auth_token)


def send_message(to, message):
    message = client.messages \
        .create(
        messaging_service_sid=messaging_sid,
        body=message,
        to=to
    )

    print(message.sid)
