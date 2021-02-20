# sms_alerts_apex_kills
A Python project to send sms alerts for kill milestones in Apex Legends.

This project uses the twilio api and tracker.gg Apex Legend api to send sms alerts when a certain treshold of kills is reached for selected players. By default sms are sent for every 50 kills. The project uses apscheduler to run on an interval, with a default of every 1 minutes. 

The project requires a .env file with the following keys 

- TWILIO_AUTH_TOKEN ([Twilio authentication token](https://www.twilio.com/docs/iam/api#authentication))
- TWILIO_MESSAGE_SID ([Twilio message SID](https://www.twilio.com/docs/sms/send-messages))
- PHONES (List of numbers, comma separated)
