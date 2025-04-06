from appData import AppData

import json
import pickle

sam = AppData()
sam.configASV.voltage1=1
print(pickle.loads(pickle.dumps(sam)).configASV.voltage1)