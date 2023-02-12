import cern_functions as cern_funk
from cern_functions import * 


x=cern_funk.user_aut_itkdb('rtj42020','lizlemon30')
print('ajdksfakjdlf')
intu_codes=cern_funk.GetInstitutesCodes(x)
print('step 2')
cern_funk.influxClient()
bucket_list=cern_funk.bucket_list(intu_codes)
print('step3')
for i in range(len(intu_codes)):
            try:
                df_data=cern_funk.get_strips_info(intu_codes[i])
                
                cern_funk.pd_to_lineProto_write(intu_codes[i],bucket_list[i],df_data)
            except KeyError:
                continue
                cern_funk.pd_to_lineProto_write(intu_codes[i],bucket_list[i],df_data)
            except NameError:
                continue