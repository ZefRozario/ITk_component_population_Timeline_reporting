import functions as funk
from functions import * 


funk.sign_in_db()
intu_code=['IZM']
intu_name=['Fraunhofer IZM']
charts=[]

for j in range(0,len(intu_code)):
    found = False
    while found is False:
        try:
            funk.get_strips_info(intu_code[j])
            found=True
        except itkX.ServerError:
            print("try again")
            pass
        funk.influxClient()

        funk.getbuckets()

        funk.pd_to_lineProto_write(intu_code[j])
        
        x=funk.query(intu_code[j])

        charts.append(dp.Text("### Institute: "+intu_name[j]))
        charts.append(dp.Plot(funk.alt_chart(intu_name[j])))
        charts.append(dp.DataTable(x))
    
funk.upload(charts)

    
    



print("Good hustle, waiting till the next loop")

