# app.py
import matplotlib.pyplot as plt
import firebase_admin
import numpy
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask import Flask
from flask_mqtt import Mqtt

cred = credentials.Certificate('fish-key.json') #Not sure if new .json file must be created.
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection(u'users').document(u'tempData')

app = Flask(__name__)
appM = Flask(__name__)
appM.config['MQTT_BROKER_URL'] = 'maqiatto.com'
appM.config['MQTT_BROKER_PORT'] = 1883
appM.config['MQTT_USERNAME'] = 'gate.tang@gmail.com'
appM.config['MQTT_PASSWORD'] = 'letmein'
appM.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(appM)

@app.route('/senddata/', methods=['GET']) #path of link. 
def respond():
    # Retrieve the name from url parameter
    data = request.args.get("data", None)

    # For debugging
    print(f"got data {data}")

    response = {}

    # Check if user sent a name at all
    if str(data) == "ON":
        response["MESSAGE"] = f"SendData Status: {data}"
        @appM.route('/')
        def index_M():
            return 'hello'

        @mqtt.on_connect()
        def handle_connect(client, userdata, flags, rc):
            mqtt.subscribe('gate.tang@gmail.com/LED')

        @mqtt.on_message()
        def handle_mqtt_message(client, userdata, message):
            data = dict(
                topic=message.topic,
                payload=message.payload.decode()
            )
            numkey=len(doc_ref.get().to_dict())
            doc_ref.update({
                str(numkey): float(data['payload'])
            })
    elif str(data) == "OFF":
        response["MESSAGE"] = f"SendData Status: {data}"
        #Place Firestore_Closer script here.
    else:
        response["ERROR"] = f"Input not recognised."

    # Return the response in json format
    return jsonify(response)

@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('data')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Welcome {data} to our awesome platform!!",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no name found, please send a name."
        })

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
    appM.run()