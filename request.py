import requests
import matplotlib.pyplot as plt
import datetime as dt

response = requests.get("https://fish-assisstant.herokuapp.com/readdata")
data = response.json()

lists = sorted(data.items()) # sorted by key, return a list of tuples

x, y = zip(*lists) # unpack a list of pairs into two tuples

z = dt.datetime.now()
date = z.strftime("%B"+"%d")

plt.plot(x, y)
plt.xlabel("Time (s)")
plt.ylabel("Temperature (*C)")
plt.savefig(date+'waterTemp.png')
plt.show()