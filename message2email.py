from flask import Flask, request
import os
from postmark import PMMail

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/message', methods=['POST'])
def message():
    sms = request.form['Body']
    email = PMMail(api_key= os.environ.get('POSTMARK_API_TOKEN'),
                   subject="One Time Token",
                   sender="otptest@marklevitt.co.uk",
                   to="markotp@marklevitt.co.uk",
                   text_body=sms)
    email.send()
    return """<?xml version="1.0" encoding="UTF-8"?><Response></Response>"""



if __name__ == '__main__':
    app.run()
