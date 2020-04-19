# app.py
import matplotlib.pyplot as plt
import firebase_admin
import numpy
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask import Flask
from flask_mqtt import Mqtt
import json

cred = credentials.Certificate('fish-key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection(u'users').document(u'tempData')

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'maqiatto.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'gate.tang@gmail.com'
app.config['MQTT_PASSWORD'] = 'letmein'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

@app.route('/readdata', methods=['GET']) #path of link. 
def respond():
    doc = doc_ref.get()
    a = doc.to_dict()
    return json.dumps(a)

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

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)