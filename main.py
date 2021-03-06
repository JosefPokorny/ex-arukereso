
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 11:37:42 2019
Title: Arukereso scraper to KBC
@author: Josef
"""



######## Libraries

#import csv
import datetime
from datetime import date, timedelta, datetime
import pandas as pd
#from lxml import html
import time
#import mechanicalsoup
from bs4 import BeautifulSoup
import requests
from requests import Request, Session
import json


### KBC CONFIG FORM ###


with open("/data/config.json", mode="r") as config_file:
    config_dict = json.load(config_file)
        

USERNAME = config_dict["parameters"]["username"]
PASSWORD = config_dict["parameters"]["#password"]
PAST_DAYS = config_dict["parameters"]["past"]
FROM = config_dict["parameters"]["from"]
TO = config_dict["parameters"]["to"]
VARLIST = config_dict["parameters"]["VARLIST"].replace(" ","").split(",")
OUTPUT_FILE = config_dict["parameters"]["Output_file_name"]
DESTINATION_BUCKET = config_dict["parameters"]["destination_bucket"]
INKREMENTAL = config_dict["parameters"]["incremental"]
PK = config_dict["parameters"]["PK"].replace(" ","").split(",")
DESTINATION = DESTINATION_BUCKET + "." + OUTPUT_FILE.replace(".csv","")



### INPUT manipulation and chceks ###

if FROM == "" or TO == "":
    FROM_date = date.today()- timedelta(PAST_DAYS) 
    TO_date = date.today()- timedelta(1)
else: 
    FROM_date = min(datetime.strptime(FROM, "%Y/%m/%d").date(),date.today()- timedelta(PAST_DAYS))
    TO_date = min(datetime.strptime(TO, "%Y/%m/%d").date(),date.today()- timedelta(1)) 
    
FROM_dt = datetime.combine(FROM_date, datetime.min.time())
TO_dt = datetime.combine(TO_date, datetime.min.time())
FROM_ms = FROM_dt.timestamp() * 1000
TO_ms = TO_dt.timestamp() * 1000


###  PARAMETERS  ###

WEB_login = "https://www.arukereso.hu/admin/Login"
WEB_stat = "https://www.arukereso.hu/admin/AkStatistics"
WEB_ajax = "https://www.arukereso.hu/admin/AjaxStats"



### LOGIN ###


login_form = {"PostBack" : "true", "Operation" : "Login", "Type" : "" ,"Identifier" : USERNAME, "Password": PASSWORD

s = Session()
req = Request('POST',WEB_login, data=login_form)
prepped = req.prepare()
log = s.send(prepped)

# check: Login proceeds correctly 
#print("Logged-in? " + str(BeautifulSoup(log.text, "lxml").title.string == 'Árukereső.hu - Admin'))


### MAIN Loop over chunks ###
OUTPUT = pd.DataFrame()
counter = 0
day = int(FROM_ms) #starting from date from

while day <= int(TO_ms): #loop over every day in period  by adding one day until the date TO
    while_check = 1
    chunk = 0
    datestring = str(day)+ "-" + str(day) 


    while while_check==1:  # loop over all chunk of data in given day
        payload = {"type":"productstat" , 'datestring': datestring , 'chunk': str(chunk)}
        r=s.get(WEB_ajax, params=payload, data=payload)
        d = json.loads(r.text)

        if d == {'End': True, 'SumAllowance': 0, 'Sum': []}:  # the empty chunk looks like this
            while_check = 0 # which stops the loop
        else: #processing the chunk
            temp_out = pd.DataFrame(d["ProductId"])
            temp_out.columns = ['ProductId','xx']

            for i in VARLIST:
                temp = pd.DataFrame(d[i])
                temp.columns = ['ProductId',i]
                temp_out = pd.merge(temp_out, temp, left_on = 'ProductId', right_on = 'ProductId', how = "left")
            
            # append data
            counter += len(temp_out)
            print(counter)
            OUTPUT=OUTPUT.append(pd.DataFrame(temp_out),ignore_index=False)
 
        chunk += 1
        time.sleep(1) ## minimal time delay between two hits of arukereso page
        
    day += 86400*1000  #one day in ms
    

### Processing of output data ###


OUTPUT.index = range( 0,len(OUTPUT))

OUTPUT["Date"]=OUTPUT["Date"].apply(lambda x: datetime.fromtimestamp(int(x)*0.001).strftime("%Y/%m/%d"))

VARLIST.insert(0, "ProductId") 
OUTPUT = OUTPUT[VARLIST]

print(OUTPUT.iloc[1,:]) #visual check of output data

### Writing to Keboola storage ###
from keboola import docker

# initialize the library
cfg = docker.Config()

out_file = "out/tables/" + OUTPUT_FILE
COLUMNS = OUTPUT.columns.values.tolist()

with open( out_file , 'a') as f:
        cfg.write_table_manifest(out_file, destination=DESTINATION, 
                                    primary_key=PK, 
                                    incremental=INKREMENTAL,
                                    columns = COLUMNS)
        OUTPUT.to_csv(f,sep=",", header=False, index=False)



