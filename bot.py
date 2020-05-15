from flask import Flask
from flask import request as flask_request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import datetime
import json
import urllib
from urllib import request, error

app = Flask(__name__)

BING_MAPS_API_KEY = 'AuAOUjlm2IJ09Ytc-cfQqjAXya4as2lPScgwaexKFv9ZDTorjj0Bvio6YlsZ-qLu'

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = flask_request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if incoming_msg == 'start':
        message_text = """Welcome to BusBud! Type '1.' and then enter your current location. Then type '-- 2.' and enter your final destination. \n\nExample: '1. 15 Ottawa St, Ottawa -- 2. 53 Wellington St, Ottawa'"""
        msg.body(message_text)
        responded = True
    elif ('1.' in incoming_msg) and ('2.' in incoming_msg) and ('--' in incoming_msg):
        split_message = incoming_msg.split()
        for index, text in enumerate(split_message):
            if text == '1.':
                first_position = index
            if text == '--':
                middle_position = index
            if text == '2.':
                second_position = index

        location_a = split_message[first_position + 1: middle_position]

        final_location_a = ''
        final_location_b = ''

        for word in location_a:
            final_location_a += ' ' + word

        location_b = split_message[second_position + 1: len(split_message)]

        for word in location_b:
            final_location_b += ' ' + word

        encoding_location_a = urllib.parse.quote(final_location_a, safe='')
        encoding_location_b = urllib.parse.quote(final_location_b, safe='')

        current_day = datetime.date.today()
        formatted_date = datetime.date.strftime(current_day, "%m/%d/%Y")

        route_url = "http://dev.virtualearth.net/REST/V1/Routes/Transit?wp.0=" + encoding_location_a + "&wp.1=" + encoding_location_b + "&tt=Departure" + "&dt=" + formatted_date + "&key=" + BING_MAPS_API_KEY

        try:
            response = urllib.request.urlopen(route_url)
            r = response.read().decode(encoding="utf-8")
            result = json.loads(r)
            itineraryItems = result["resourceSets"][0]["resources"][0]["routeLegs"][0]["itineraryItems"]
            text_message = ''

            for item in itineraryItems:
                text_message += item["instruction"]["text"] + "\n"
        except error.HTTPError:
            text_message = 'Invalid query. Please try again and if needed, type "start" for help.'
        msg.body(text_message)
        responded = True

    if not responded:
        text_message = 'Oops! You have typed in an invalid request. Type "start" for help.'
        msg.body(text_message)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)