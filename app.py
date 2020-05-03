# app.py
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify, render_template
from flask_mqtt import Mqtt
import json
from datetime import datetime
import io
import time
import urllib, base64
import requests
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

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
    x = datetime.now().day
    time.sleep(5)
    currentdate = datetime.now().day
    if (currentdate != x):
        doc_ref.set({})
        currentdate = x

    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
        )
    numkey=len(doc_ref.get().to_dict())
    doc_ref.update({
        str(numkey): float(data['payload'])
            })

@app.route('/graph', methods=['GET'])
def graph():
    response = requests.get("https://fish-assisstant.herokuapp.com/readdata")
    data = response.json()

    dataarray = [0]*len(data)

    for key in data:
        dataarray[int(key)] = data[key] #Orders converted array into order


    plt.clf()
    z = datetime.now()
    date = z.strftime("%B"+"%d"+"-%y")
    plt.xlabel("Time (5s)")
    plt.ylabel("Temperature (*C)")
    plt.title("Aquarium Temp Over Time - "+date)
    plt.grid(True)
    plt.savefig(date+'waterTemp.png')
    plt.plot(dataarray)
    fig = plt.gcf()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    url = urllib.parse.quote(string)

    return render_template("home.html",data=url)

@app.route('/feed', methods = ['POST', 'GET'])
def feed():
    if request.method == 'POST':
        amount = request.form.get('amount')
        mqtt.publish('gate.tang@gmail.com/food', payload = amount, qos=0, retain=False)
        print(amount) # for debugging
        return '''<h1>Submitted Form: amount is {} gram(s).</h>
        <form>
        <button formaction="https://fish-assisstant.herokuapp.com/feed">Feed More!</button>
        </form>'''. format(amount)

    return '''<form method = "POST">
    Amount (g): <input type = "number" name="amount">
    <input type = "submit">
    </form> '''

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)