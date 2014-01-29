import MySQLdb as db
import json
from random import shuffle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import math
import pickle

jsonfiles=[]
for i in range(500):
    jsonfiles.append(str(749+i) )

loanjson=[]
loanjson_funded=[]
loanjson_expired=[]
for file in jsonfiles:
    #Use Kiva loan data in json format and populate MySQL database
    path = '/Users/saba/Documents/Insight/KivaProjectResources/kiva_ds_json/loans/' + file + '.json'
    
    loanjson = [json.loads(line) for line in open(path)][0]['loans']
    for i in range( len(loanjson)):
        if loanjson[i]['status'] == 'expired':
            loanjson_expired.append(loanjson[i])
        elif loanjson[i]['status'] == 'inactive_expired':
            loanjson_expired.append(loanjson[i])
        elif loanjson[i]['status'] == 'paid':
            loanjson_funded.append(loanjson[i])
        elif loanjson[i]['status'] == 'funded':
            loanjson_funded.append(loanjson[i])
        elif loanjson[i]['status'] == 'in_repayment':
            loanjson_funded.append(loanjson[i])
        elif loanjson[i]['status'] == 'defaulted':
            loanjson_funded.append(loanjson[i])

print 'Done'

pickle.dump( (loanjson_expired), open( "expired.pkl", "wb" ) )

print 'dumped expired'

shuffle(loanjson_funded)
totexp=len(loanjson_expired)
loanjson_funded_trunc=loanjson_funded[0:totexp]

print 'shuffled',totexp, '  ', len(loanjson_funded),len(loanjson_funded_trunc)

pickle.dump( (loanjson_funded_trunc), open( "funded.pkl", "wb" ) )

print 'trunc funded dumped'
