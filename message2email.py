from flask import Flask, request
from werkzeug.contrib.cache import MemcachedCache
import os
from postmark import PMMail
from operator import itemgetter
import pylibmc

app = Flask(__name__)

cache = MemcachedCache(os.environ.get('MEMCACHIER_SERVERS'))


def send_sms_email(sms):
    if app.debug:
        print("Debug: Email not sent")
    else:
        email = PMMail(api_key= os.environ.get('POSTMARK_API_TOKEN'),
                   subject="One Time Token",
                   sender="otptest@marklevitt.co.uk",
                   to="markotptest@marklevitt.co.uk",
                   text_body=sms)
        email.send()



def search_parts(list_of_parts, part_to_check):
    """
    Given a list of parts, checks to see if it exists already
    Returns The part found if the part to check is already in the list
    """
    return next((part for part in list_of_parts if part['part'] == part_to_check), None)


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
    if request.args.get('concat') == u"true":
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

        sms_parts = cache.get(concat_reference)
        if sms_parts is not None:
            """We've got an existing entry add this message"""
            print("Found reference in the cache")

            if search_parts(sms_parts, concat_part):
                print("Duplicate part received. Ignoring.")
                return "<html><body>Duplicate Part</body></html>", 200

            sms_parts.append({"part": concat_part, "text": text})

            if len(sms_parts) == int(concat_total):
                """We've got all parts of the message"""
                print("All parts arrived")
                sms_message = ""
                for part in sorted(sms_parts, key=itemgetter('part')):
                    sms_message += part['text']

                print(sms_message)
                cache.clear()
                send_sms_email(sms_message)
            else:
                cache.set(concat_reference, sms_parts)

        else:
            print("Cache entry not found")
            sms_message_part = {"part": concat_part, "text": text}
            sms_parts = [sms_message_part]
            cache.set(concat_reference, sms_parts)
    else:
        send_sms_email(request.args.get('text'))

    return "<html><body>OK</body></html>", 200

if __name__ == '__main__':
    app.run(debug=True)
