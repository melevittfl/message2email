from flask import Flask, request
import os
from postmark import PMMail

app = Flask(__name__)


def send_sms_email(sms):
    email = PMMail(api_key= os.environ.get('POSTMARK_API_TOKEN'),
                   subject="One Time Token",
                   sender="otptest@marklevitt.co.uk",
                   to="markotp@marklevitt.co.uk",
                   text_body=sms)
    email.send()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/message', methods=['POST'])  # From Twilio.com
def message():
    sms = request.form['Body']
    send_sms_email(sms)
    return """<?xml version="1.0" encoding="UTF-8"?><Response></Response>"""

@app.route('/message2')  # From Nexmo.com
def message2():
    sms = request.args.get('text', "Not Sent")
    print sms
    if sms is not "Not Sent":
        send_sms_email(sms)
    return "<html><body>OK</body></html>", 200

if __name__ == '__main__':
    app.run()
