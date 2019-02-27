
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


###############  KBC FORM ##########


### IN KBC
with open("/data/config.json", mode="r") as config_file:
    config_dict = json.load(config_file)
        




USERNAME = config_dict["parameters"]["username"]
PASSWORD = config_dict["parameters"]["#password"]
PAST_DAYS = config_dict["parameters"]["past"]
FROM = config_dict["parameters"]["from"]
TO = config_dict["parameters"]["to"]
VARLIST = config_dict["parameters"]["VARLIST"].replace(" ","").split(",")
OUTPUT_FILE = config_dict["parameters"]["Output_file_name"]




############# INPUT manipulation and chceks

if FROM == "" or TO == "":
    FROM_date = date.today()- timedelta(PAST_DAYS) ### tisíciny vteřiny
    TO_date = date.today()- timedelta(1)
else: 
    FROM_date = min(datetime.strptime(FROM, "%Y/%m/%d").date(),date.today()- timedelta(PAST_DAYS))
    TO_date = min(datetime.strptime(TO, "%Y/%m/%d").date(),date.today()- timedelta(1)) 
    
FROM_dt = datetime.combine(FROM_date, datetime.min.time())
TO_dt = datetime.combine(TO_date, datetime.min.time())
FROM_ms = FROM_dt.timestamp() * 1000
TO_ms = TO_dt.timestamp() * 1000


##########  PARAMETERS  #####################

WEB_login = "https://www.arukereso.hu/admin/Login"
WEB_stat = "https://www.arukereso.hu/admin/AkStatistics"
WEB_ajax = "https://www.arukereso.hu/admin/AjaxStats"



######## LOGIN #####


login_form = {"PostBack" : "true", "Operation" : "Login", "Type" : "" ,"Identifier" : USERNAME, "Password": PASSWORD}


## !!! přidat specifikaci header

#log=requests.post(WEB_login, data = login_form)
s = Session()
req = Request('POST',WEB_login, data=login_form)
prepped = req.prepare()
log = s.send(prepped)

# check: Login proceeds correctly  -- přidat failure
#print("Logged-in? " + str(BeautifulSoup(log.text, "lxml").title.string == 'Árukereső.hu - Admin'))



######### get the list to download --- Loop over chunks
OUTPUT = pd.DataFrame()
counter = 0
day = int(FROM_ms)

while day <= int(TO_ms):
    while_check = 1
    chunk = 0

    datestring = str(day)+ "-" + str(day) #!!!! vždy pouze jeden den 


    while while_check==1:  #chunk<5
        payload = {"type":"productstat" , 'datestring': datestring , 'chunk': str(chunk)}
        r=s.get(WEB_ajax, params=payload, data=payload)
        d = json.loads(r.text)

        if d == {'End': True, 'SumAllowance': 0, 'Sum': []}:
            while_check = 0
        else:
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
        time.sleep(1)
        
    day += 86400*1000  #one day in ms
    

####### úprava OUTPUTU


OUTPUT.index = range( 0,len(OUTPUT))

OUTPUT["Date"]=OUTPUT["Date"].apply(lambda x: datetime.fromtimestamp(int(x)*0.001).strftime("%Y/%m/%d"))

VARLIST.insert(0, "ProductId") 
OUTPUT = OUTPUT[VARLIST]

print(OUTPUT)

#### COMPONENT:::
with open( "out/tables/" + OUTPUT_FILE , 'a') as f:
        OUTPUT.to_csv(f, header=True, index=False)



