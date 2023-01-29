import streamlit as st
import functions as funk
from functions import *

if 'stage' not in st.session_state:
    st.session_state.stage = 0

def set_stage(stage):
    st.session_state.stage = stage

col1, col2, col3 = st.columns(3)


    
with st.form('Authorisation1'):
    with col1:
        aut1=st.text_input('ITkdb Authentication code1',type="password")
    
    with col2:
        aut2=st.text_input('ITkdb Authentication code2',type="password")
    st.form_submit_button('First Button', on_click=set_stage, args=(1,))
    if st.session_state.stage > 0:
        y=funk.user_aut_itkdb(aut1,aut2)
        x=funk.GetInstitutesCodes(y)
        selected_locations = st.multiselect("Institute Codes:",x)
        st.form_submit_button('Second Button', on_click=set_stage, args=(2,))
    if st.session_state.stage > 1:
        st.write('step1')
        funk.influxClient()
        charts=[]
        for i in range(len(selected_locations)):
        #charts=[]
            st.write('Making graph'+str(i))


            funk.getbuckets(selected_locations[i])


            x=funk.query(selected_locations[i])

            #charts.append(dp.Text("### Institute: "+str(selected_locations[i])))
            #charts.append(dp.Plot(funk.alt_chart(selected_locations)))
            #charts.append(dp.DataTable(x))
            st.altair_chart(funk.alt_chart(selected_locations[i]))
        st.write('All done.')
st.button('Reset', on_click=set_stage, args=(0,))
