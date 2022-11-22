### get itkdb for PDB interaction
import os
import sys
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
import datapane as dp
# influx 
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

##### First we get to the ITk db


def sign_in_db():
    user = itkdb.core.User(accessCode1="", accessCode2="")
    ##you got to use your own path 
    credDir="<path to>/Strips_stages"
    if os.path.isdir(credDir):
        print("directory found:",credDir)
        sys.path.insert(1, credDir)
        import myDetails
        credDict=myDetails.GetITkCredentials()
        #print(credDict)
        user = itkdb.core.User(accessCode1=credDict['ac1'], accessCode2=credDict['ac2'])
        print("done.")
    else:
        print("no directory found:",credDir)
    user.authenticate()
    global myClient 
    myClient = itkdb.Client(user=user)
    print(user.name+" your token expires in "+str(myClient.user.expires_in)+" seconds")
    return(myClient)


###now get the strip data for glasgow 



def get_strips_info(x):
    global df_data_grp
    df_data_grp=[]
    myProjCode="S" #s for strips 
    myCompCode="MODULE"
    myInstCode=x
    compList = myClient.get('listComponents', json={'project':myProjCode, 'currentLocation':myInstCode})
    print(compList.page_info)
    #put data into a pd datafram 

    myData=myClient.get('listComponents', json={'project':"S",'currentLocation':myInstCode})
    df_data=pd.json_normalize(myData, sep = "_")
    ("The data is now in a pandas dataframe")
    groupby="componentType_code"
    print("Just gonna quickly group by",groupby, "and reset the index")
    df_data_grp=df_data.groupby(by=["componentType_code","currentStage_code"]).count().reset_index().replace(' ','_',regex=True)#,inplace=True)
    #df_data_grp=df_data_grp1.replace(' ','_',regex=True,inplace=True)
    return(df_data_grp)





def loc(x,y):
    a=df_data_grp.loc[x,y]
    return(a)
    



org_remote="name of org"
token_remote="token"
url_remote="url"

def influxClient():
    global clientV2_local
    clientV2_local = influxdb_client.InfluxDBClient(
   url=url_remote,
   token=token_remote,
   org=org_remote)
    return(clientV2_local)

##lets get a list of buckets and 

def getbuckets():
    global  bucketName
    bucketName="Strips_stage_pop"
    buckets_api_local = clientV2_local.buckets_api()
    try:
        #print([x.name for x in buckets_api_remote.find_buckets().buckets])
        database_list=[x.name for x in clientV2_local.buckets_api().find_buckets().buckets]
        print(database_list)
    except:
        print("cannot get buckets")
    bucketName="Strips_stage_pop"
    buckets_api_local.find_bucket_by_name(bucketName)
    return(bucketName)

def pd_to_lineProto_write(x):
    print("writing data at",datetime.now())
    for i in range(len(df_data_grp)):
            global data
            data ="Strips_in_"+str(x)+",componentType_code="+str(loc(i,"componentType_code"))+",currentStage_code="+str(loc(i,"currentStage_code"))+",id="+str(loc(i,"id"))+" "+"code="+str(loc(i,"code"))
            write_api_local = clientV2_local.write_api(write_options=SYNCHRONOUS)
            write_api_local.write(bucketName, org_remote, data)
            print(data)
    return(data)


def query(p):
    global query_result
    query_api_local = clientV2_local.query_api(
    )
    query1='''
            from(bucket: "Strips_stage_pop")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "Strips_in_XYZ")
        |> filter(fn: (r) => r["_field"] == "code")
        |> filter(fn: (r) => r["componentType_code"] == "ABC" or r["componentType_code"] == "MODULE" or r["componentType_code"] == "PWB" or r["componentType_code"] == "HYBRID" or r["componentType_code"] == "HYBRID_ASSEMBLY")
        |> yield(name: "mean")
            '''
    c=query1.replace("XYZ",str(p))
    query_result = query_api_local.query_data_frame(org=org_remote, query=c)

    if query_result.empty:
        query2='''
            from(bucket: "Strips_stage_pop")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "Strips_in_XYZ")
        |> filter(fn: (r) => r["_field"] == "code")
        |> yield(name: "mean")
            '''
        c=query2.replace("XYZ",str(p))
        query_result = query_api_local.query_data_frame(org=org_remote, query=c)
        print("Default query didn't work. Will un filtered query")
    return(query_result)

def alt_chart(q):

    a=query_result.drop_duplicates(subset='componentType_code')
    b=query_result.drop_duplicates(subset='currentStage_code')
    query_list1=[None] + list(a['componentType_code'])
    query_list2=[None] + list(b['currentStage_code'])
    input_dropdown1 = alt.binding_select(options=query_list1,name="Component Type Code:   ")
    input_dropdown2= alt.binding_select(options=query_list2,name="Component Stage:   ")
    selection1 = alt.selection_single(
        fields=["componentType_code"], bind=input_dropdown1,
    )
    selection2 = alt.selection_single(
        fields=["currentStage_code"], bind=input_dropdown2,
    )
    ### plot some data
### plot some data
    alt.data_transformers.disable_max_rows()
    chart=alt.Chart(query_result).transform_calculate(
                    comb="datum.componentType_code + '-' + datum.componentStage_code"
            ).mark_line(point=True).encode(
        x=alt.X('_time',title='Timeline'),
        y=alt.Y('_value',title='Population'), #scale=alt.Scale(7),
        #z=alt.Z('componentType_code',title='Component Code'),
        shape=alt.Shape('componentType_code', legend=alt.Legend(title='Component Code',orient="right",columns=2)),# filter
        color=alt.Color('currentStage_code',legend=alt.Legend(title='Stage',orient="right",columns=2)),
        strokeDash=alt.StrokeDash('comb:N',legend=None),#alt.Legend(title='Stage',orient="right",columns=2)),
        #shape='id', # filter
        tooltip=['_time','_value','componentType_code','currentStage_code']
    ).properties(
        title={
        "text": "Component Stage population", 
        "subtitle": "Strips"
        },
        width=600,
        height=350
    ).interactive().add_selection(selection2).transform_filter(selection2).add_selection(selection1).transform_filter(selection1)
    
    
    return(chart)

def upload(x):
    dp.Report(
        *x
    ).upload(name="Component stage population: Strips",publicly_visible=True)
    return()


    
    
