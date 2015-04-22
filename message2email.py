from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache
import os
from postmark import PMMail

app = Flask(__name__)
cache = SimpleCache()


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
    concat = request.args.get('concat')
    if concat == u"true":
        """We have one part of a multipart message. We need to
         check the cache and see if we have another part already. If so,
         concatinate the parts and send the e-mail
         If not, store this message in the cache
        """
        print("Got part of a multi-part message")
        concat_reference = request.args.get("concat-ref")
        concat_total = request.args.get("concat-total")
        concat_part = request.args.get("concat-part")
        text = request.args.get("text", "Not Sent")

        if cache.get(concat_reference):
            """We've got an existing entry add this message"""
            print("Found reference in the cache")
            other_message = cache.get(concat_reference)
            if other_message['part'] == "1":
                sms_text = other_message['text'] + text
            else:
                sms_text = text + other_message['text']

            print sms_text
            send_sms_email(sms_text)
        else:
            print("Cache entry not found")
            sms_message_part = {"part": concat_part, "text": text}
            cache.set(concat_reference, sms_message_part)

    return "<html><body>OK</body></html>", 200

if __name__ == '__main__':
    app.run()
