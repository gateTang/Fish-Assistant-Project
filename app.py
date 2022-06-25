# app.py
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify, render_template
from flask_mqtt import Mqtt
import numpy as np
import json
from datetime import datetime
import io
import urllib, base64
import requests
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

#JSON key for firebase.
cred = credentials.Certificate('fish-key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

#Initialise firebase documents.
doc_ref = db.collection(u'users').document(u'tempData')
date_ref = db.collection(u'users').document (u'date')

date = datetime.now().day
date_ref.set({u'date': date})

thislist = []

#Flask framework.
app = Flask(__name__)

#MQTT setup.
app.config['MQTT_BROKER_URL'] = 'maqiatto.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'gate.tang@gmail.com'
app.config['MQTT_PASSWORD'] = 'letmein'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

#Flask framework routes. 
@app.route('/readdata', methods=['GET']) #path of link. 
def respond():
    doc = doc_ref.get()
    a = doc.to_dict()
    return json.dumps(a)

@app.route('/',methods=['GET'])
def hub():
    return render_template("hub_2.html")


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('gate.tang@gmail.com/LED')

@mqtt.on_message()
def time():
    #updates time stamps every hour E.g. 1AM, 2AM everytime a MQTT Message comes in. 
    time = datetime.now().strftime("%H%M")
    thislist.append(time)
    return thislist

def handle_mqtt_message(client, userdata, message):
    x = datetime.now().day
    dateD = date_ref.get()
    dateC = dateD.to_dict()
    previous = dateC["date"]
    #Erase data after one day. 
    if (previous != x):
        doc_ref.set({})
        thislist=[]
        previous = x
    
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
        )
    numkey=len(doc_ref.get().to_dict())
    doc_ref.update({
        str(numkey): float(data['payload'])
            })

    return render_template("home.html",thislist=thislist)

@app.route('/graph', methods=['POST','GET'])
def graph():
    response = requests.get("https://fish-assisstant.herokuapp.com/readdata")
    data = response.json()

    dataarray = [0]*len(data)

    for key in data:
        dataarray[int(key)] = data[key] #Orders converted array into order
    
    #Creates graph.
    plt.clf()
    z = datetime.now()
    date = z.strftime("%B"+"%d"+"-%y")
    plt.xlabel("Time (5s)")
    plt.ylabel("Temperature (*C)")
    plt.title("Aquarium Temp Over Time - "+date)
    plt.grid(True)
    plt.savefig(date+'waterTemp.png')
    plt.plot(dataarray, 'bx')
    fig = plt.gcf()

    amount = len(dataarray)-1
    current_amount = (dataarray[amount])
    if dataarray == []:
        current_amount - 0
    else:
        current_amount = (dataarray[amount])

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    url = urllib.parse.quote(string)

    Dict = { i : dataarray[i] for i in range(0,len(dataarray) ) }
    xy=Dict.items()
    reset_response = "RESET Attempted"
    if request.method == 'POST':
        reset = str(request.form.get('reset'))
        print (reset)
        if reset == 'RESET':
            doc_ref.set({})
            reset_response = "RESET Attempted"
        if reset != 'RESET':
            reset_response = "RESET Attempted"

    return render_template("home.html",data=url,current_amount=current_amount,history=dataarray,time=thislist,xy=xy,reset_response=reset_response)

@app.route('/feed')
def index():
    return render_template("feed.html")
@app.route('/feed', methods = ['POST', 'GET'])
def feed():
    if request.method == 'POST':
        weight = request.form.get('amount')
        mqtt.publish('gate.tang@gmail.com/food', payload = weight, qos=0, retain=False)
        print(weight) # for debugging
        return render_template("feed.html", weight=weight)

@app.route('/water')
def waterIndex():
    return render_template("water.html")

@app.route('/water', methods = ['POST', 'GET'])
def water():
    if request.method == 'POST':
        waterState = request.form.get('waterState')
        if waterState == None:
            waterState="OFF"
        if waterState == "1":
            waterState="ON"
        mqtt.publish('gate.tang@gmail.com/water', payload = waterState, qos=0, retain=False)
        print(waterState) # for debugging
        return render_template("water.html", waterState=waterState)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)