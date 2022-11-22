### get itkdb for PDB interaction
import os
import sys
from turtle import fillcolor, shapetransform
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
    credDir="/home/ppe/z/zrozario/QT/Strips_trashed"
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
    df_data_grp=df_data.groupby(by=["componentType_code","type_code","currentStage_code","trashed"]).count().reset_index().replace(' ','_',regex=True)#,inplace=True)
    #df_data_grp=df_data_grp1.replace(' ','_',regex=True,inplace=True)
    return(df_data_grp)





def loc(x,y):
    a=df_data_grp.loc[x,y]
    return(a)
    


org_local = "CERN"
token_local = "ZsQeKNr1x4no5JIAZ4vTMGJOwvy7sWi5PY-3-3G1DvOO1W-BWqfyTdaEtaN7l94GdmASTqcNu8bec3vHNSFPew=="
# Store the URL of your InfluxDB instance
url_local="http://localhost:8086"


org_remote="PPE"
token_remote="yj3CpGdnrn0ghL2zJYVWrF9XJykjq4Xb-eLvxuusu7syVQeOY66O5INKVFOswAzTOlPglbV5_vcWV6Z-Ij-Vsw=="
url_remote="http://194.36.1.20:8086/"

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
    bucketName="Strips_trashed"
    buckets_api_local = clientV2_local.buckets_api()
    try:
        #print([x.name for x in buckets_api_remote.find_buckets().buckets])
        database_list=[x.name for x in clientV2_local.buckets_api().find_buckets().buckets]
        print(database_list)
    except:
        print("cannot get buckets")
    bucketName="Strips_trashed"
    buckets_api_local.find_bucket_by_name(bucketName)
    return(bucketName)

def pd_to_lineProto_write(x):
    print("writing data at",datetime.now())
    for i in range(len(df_data_grp)):
            global data
            data ="Strips_in_"+str(x)+",componentType_code="+str(loc(i,"componentType_code"))+",type_code="+str(loc(i,"type_code"))+",currentStage_code="+str(loc(i,"currentStage_code"))+",trashed="+str(loc(i,"trashed"))+" "+"code="+str(loc(i,"code"))
            write_api_local = clientV2_local.write_api(write_options=SYNCHRONOUS)
            write_api_local.write(bucketName, org_remote, data)
            print(data)
    return(data)


def query(p):
    global query_result
    d = {'True': True, 'False': False}
    query_api_local = clientV2_local.query_api(
    )
    query1='''
            from(bucket: "Strips_trashed")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "Strips_in_XYZ")
        |> filter(fn: (r) => r["_field"] == "code")
        |> filter(fn: (r) => r["componentType_code"] == "ABC" or r["componentType_code"] == "MODULE" or r["componentType_code"] == "PWB" or r["componentType_code"] == "HYBRID" or r["componentType_code"] == "HYBRID_ASSEMBLY")
        |> yield(name: "mean")
            '''
    c=query1.replace("XYZ",str(p))
    query_result = query_api_local.query_data_frame(org=org_remote, query=c)
    query_result['trashed']=query_result['trashed'].map(d)
    query_result['trashed']=query_result['trashed'].astype(bool)

    if query_result.empty:
        query2='''
            from(bucket: "Strips_trashed")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "Strips_in_XYZ")
        |> filter(fn: (r) => r["_field"] == "code")
        |> yield(name: "mean")
            '''
        c=query2.replace("XYZ",str(p))
        query_result = query_api_local.query_data_frame(org=org_remote, query=c)
        print("Default query didn't work. Will un filtered query")
        query_result['trashed']=query_result['trashed'].astype(bool)
    return(query_result)

def alt_chart(q):
    #query_result['trashed']=query_result['trashed'].astype(bool)
    print(query_result['trashed'])
    a=query_result.drop_duplicates(subset='componentType_code')
    b1=query_result.drop_duplicates(subset='type_code')
    b=query_result.drop_duplicates(subset='currentStage_code')
    c=query_result.drop_duplicates(subset='trashed')
    query_list1=[None] + list(a['componentType_code'])
    query_list3=[None] + list(b1['type_code'])
    query_list2=[None] + list(b['currentStage_code'])
    query_list4=[None] + list(c['trashed'])
    input_dropdown1 = alt.binding_select(options=query_list1,name="Component Type Code:   ")
    input_dropdown3 = alt.binding_select(options=query_list3,name="Type Code:   ")
    input_dropdown2= alt.binding_select(options=query_list2,name="Component Stage:   ")
    input_dropdown4= alt.binding_select(options=query_list4,name="Trashed:   ")
    selection1 = alt.selection_single(
    fields=["componentType_code"], bind=input_dropdown1,
    )
    selection2 = alt.selection_single(
    fields=["currentStage_code"], bind=input_dropdown2,
    )
    selection3 = alt.selection_single(
    fields=["type_code"], bind=input_dropdown3,
    )
    selection4 = alt.selection_single(
    fields=["trashed"], bind=input_dropdown4,
    )
    ### plot some data
    ### plot some data
    alt.data_transformers.disable_max_rows()
    chart=alt.Chart(query_result).transform_calculate(
                    comb="datum.componentType_code + '-' + datum.type_code + '-' + datum.currentStage_code + '-' + datum.trashed"
            ).mark_line(point=True).encode(
        x=alt.X('_time',title='Timeline'),
        y=alt.Y('_value',title='Population'), #scale=alt.Scale(7),
        #z=alt.Z('componentType_code',title='Component Code'),
        color=alt.Color('type_code',legend=alt.Legend(title='Type Code',orient="right",columns=2)),# filter
        shape=alt.Shape('componentType_code', legend=alt.Legend(title='Component Code',orient="right",columns=2)),
        strokeDash=alt.StrokeDash('currentStage_code',legend=alt.Legend(title='Stage',orient="right",columns=2,type="symbol",zindex=1)),
        strokeOpacity=alt.StrokeOpacity('comb:N'),#alt.Legend(title='Stage',orient="right",columns=2)),
        #shape='id', # filter
     tooltip=['_time','_value','componentType_code','currentStage_code','type_code','trashed']
    ).properties(
        title={
        "text": "Component Stage population", 
        "subtitle": "Strips"
        },
        width=600,
        height=350
    ).interactive().add_selection(selection4).transform_filter(selection4).add_selection(selection2).transform_filter(selection2).add_selection(selection3).transform_filter(selection3).add_selection(selection1).transform_filter(selection1)
    
    
    return(chart)

def upload(x):
    dp.Report(
        *x
    ).upload(name="Component stage population (with trashed): Strips",publicly_visible=True)
    return()
