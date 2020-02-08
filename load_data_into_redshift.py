#!/usr/bin/env python2

import pandas as pd
import os
import boto3
import sys
from StringIO import StringIO
from sqlalchemy import create_engine

####aws access information#####

aws_access_key_id = '******************' 
aws_secret_access_key = '*******************'

client = boto3.client('s3') #low-level functional API

resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket('patentinsight')

conn = create_engine('postgresql://user:password@redshift_endpoint:port_number')

###########load table uspc_current###############
obj = client.get_object(Bucket='patentinsight',Key='patent_data/uspc_current.tsv')

import datetime as dt
start = dt.datetime.now()
j = 0
index_start = 1

for uspc_current in pd.read_csv(obj['Body'],skiprows=120000,chunksize=10000,quotechar='"',sep='\t',iterator=True):
    uspc_current.columns = ['uuid', 'patent_id', 'mainclass_id','subcalss_id','sequence']
    uspc_current['mainclass_id'] = uspc_current['mainclass_id'].replace(to_replace=r'No longer published', value='0', regex=True)  
    uspc_current['subcalss_id'] = uspc_current['subcalss_id'].replace(to_replace=r'No longer published', value='0/0', regex=True)
    uspc_current.to_sql('uspc_current',conn, schema='patent_info',index=False, if_exists='append')
    j+=1
    print '{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*10000)
    
##############load table uspatent citation##############

obj = client.get_object(Bucket='patentinsight',Key='patent_data/uspatentcitation.tsv')
uspc_citation = pd.read_csv(obj['Body'],nrows=10,header=0,quotechar='"',sep='\t')

category = {'unknown':3,'cited by examiner': 1,'cited by applicant': 2, 'cited by other':0}
uspatentcitation1 = uspc_citation.replace(np.nan, 'u', regex=True)
uspatentcitation1.category = [category[item] for item in uspatentcitation1.category]

for uspc_citation in pd.read_csv(obj['Body'],chunksize=10000,header=0,quotechar='"',sep='\t'):
    uspatentcitation1 = uspc_citation.replace(np.nan, 'unknown', regex=True)  
    uspatentcitation1.to_sql('uspc_citation',conn, schema='patent_info',index=False, if_exists='append')



