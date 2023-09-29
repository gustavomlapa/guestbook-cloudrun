import json
import os
import datetime
import time
from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
import dateutil.relativedelta
import bleach

app = Flask(__name__)

# Create an in-memory store for messages
messages = []

def get_messages():
    msg_list = list(messages)
    return jsonify(msg_list)

def add_message(newmessage):
    newjson = json.loads(newmessage)
    msg_data = {'author':bleach.clean(newjson['author']),
                'message':bleach.clean(newjson['message']),
                'date':time.time()}
    messages.append(msg_data)
    return  jsonify({})

@app.route('/')
def main():
    response = get_messages()
    json_response = json.loads(response.data)
    return render_template('home.html', messages=json_response)


@app.route('/post', methods=['POST'])
def post():
    """ Send the new message to the backend and redirect to the homepage """
    new_message = {'author': request.form['name'],
                   'message':  request.form['message']}
    add_message(jsonify(new_message).data)
    return redirect(url_for('main'))

def format_duration(timestamp):
    """ Format the time since the input timestamp in a human readable way """
    now = datetime.datetime.fromtimestamp(time.time())
    prev = datetime.datetime.fromtimestamp(timestamp)
    rd = dateutil.relativedelta.relativedelta(now, prev)

    for n, unit in [(rd.years, "year"), (rd.days, "day"), (rd.hours, "hour"),
                    (rd.minutes, "minute")]:
        if n == 1:
            return "{} {} ago".format(n, unit)
        elif n > 1:
            return "{} {}s ago".format(n, unit)
    return "just now"


if __name__ == '__main__':
    # register format_duration for use in html template
    app.jinja_env.globals.update(format_duration=format_duration)

    # start Flask server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
