### get itkdb for PDB interaction
import os
import sys
#from turtle import fillcolor, shapetransform
import itertools
#!{sys.executable} -m pip install pandas==1.4.1
import pandas as pd
import copy
import json
from datetime import datetime, timedelta
import time
#!{sys.executable} -m pip install itkdb==0.3.15
import itkdb
import itkdb.exceptions as itkX
# visualisation
import altair as alt
#import datapane as dp
# influx 
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

org_remote="CERN"
token_remote=""
url_remote=""

def influxClient():
    #st.write('chicken nuggets')
    global clientV2_local
    clientV2_local = influxdb_client.InfluxDBClient(
   url=url_remote,
   token=token_remote,
   org=org_remote)
    #st.write('got client')
    return(clientV2_local)

def user_aut_itkdb(x,y):
    user = itkdb.core.User(accessCode1=x, accessCode2=y)
    user.authenticate()
    global myClient 
    myClient = itkdb.Client(user=user)
    #st.write(user.name+" your token expires in "+str(myClient.user.expires_in)+" seconds")
    return myClient

def GetInstitutesCodes(myClient):
    clusterInfo=myClient.get('listClusters', json={})
    df_clusterInfo=pd.json_normalize(clusterInfo, sep='_')
    x=df_clusterInfo['code'].values.tolist()
    instlist=[]
    codestr='code=="xyz"'
    for i in range(len(x)):
        y=codestr.replace('xyz',str(x[i]))
        l=pd.DataFrame(df_clusterInfo.query(y)['instituteList'].values[0])['code'].to_list()
        instlist.append(l)
    instlist=sorted(list(dict.fromkeys(list(itertools.chain.from_iterable(instlist)))))
    return instlist

def loc(x,y):
    a=df_data_grp.loc[x,y]
    return(a)

def pd_to_lineProto_write(x,bucket,df_data):
    print("writing data at",datetime.now())
    for i in range(len(df_data_grp)):
            global data
            data ="Strips_in_"+str(x)+",componentType_code="+str(loc(i,"componentType_code"))+",type_code="+str(loc(i,"type_code"))+",currentStage_code="+str(loc(i,"currentStage_code"))+",trashed="+str(loc(i,"trashed"))+" "+"code="+str(loc(i,"code"))
            write_api_local = clientV2_local.write_api(write_options=SYNCHRONOUS)
            write_api_local.write(bucket, 'CERN', data)
            print(data)
    return(data)

def get_strips_info(x):
    global df_data_grp
    df_data_grp=[]
    myProjCode="S" #s for strips 
    myCompCode="MODULE"
    myInstCode=x
    print(x)
    compList = myClient.get('listComponents', json={'project':myProjCode, 'currentLocation':myInstCode})
    print(compList.page_info)
    #put data into a pd datafram 

    myData=myClient.get('listComponents', json={'project':"S",'currentLocation':myInstCode})
    df_data=pd.json_normalize(myData, sep = "_")
    ("The data is now in a pandas dataframe")
    groupby="componentType_code"
    print("Just gonna quickly group by",groupby, "and reset the index")
    df_data_grp=df_data.groupby(by=["componentType_code","type_code","currentStage_code","trashed"]).count().reset_index().replace(' ','_',regex=True)#,inplace=True)
    #df_data_grp=df_data_grp1.replace(' ','_',regex=True,inplace=True)
    return(df_data_grp)

def bucket_list(x):
    string='Strips_in_xyz'
    bucket_list=list()
    for i in range(len(x)):
        c=string.replace('xyz',str(x[i]))
        print(c)
        bucket_list.append(c)
    return bucket_list
