# coding: utf-8

################################################################################
## Tableau Database extractor

################################################################################
from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import urllib
import pyodbc
import pandas as pd
import config
import warnings
import tempfile

################################################################################
## Variable declarations
################################################################################
# Import MSSQL credentials from config file
PGusername = config.POSTGRES_USERNAME
PGpassword = config.POSTGRES_PASS
PGhost = config.POSTGRES_HOST
PGport = config.POSTGRES_PORT
PGdatabase = config.POSTGRES_DB
PGdriver = config.POSTGRES_DRIVER
PGschema = config.POSTGRES_SCHEMA

# Import MSSQL credentials from config file
MSusername = config.PYMSSQL_USERNAME
MSpassword = config.PYMSSQL_PASS
MShost = config.PYMSSQL_HOST
MSport = config.PYMSSQL_PORT
MSdatabase = config.PYMSSQL_DB
MSschema = config.PYMSSQL_SCHEMA
MSdriver = config.PYMSSQL_DRIVER

################################################################################
## Establish connection to required databases
################################################################################
# Establish connection to Tableau Postgres DB
print('[{}]: Connection to PSQL...'.format(datetime.now()))
PGengine = create_engine('{}://{}:{}@{}:{}/{}'.format(PGdriver,PGusername,PGpassword,PGhost,PGport,PGdatabase))
PGconn = PGengine.connect()
print('[{}]: Connected to PSQL...'.format(datetime.now()))

# Establish connection to MSSQL DB
#MSengine = create_engine('{}://{}:{}@{}:{}/{}'.format(MSdriver,MSusername,MSpassword,MShost,MSport,MSdatabase))
print('[{}]: Connection to MSSQL...'.format(datetime.now()))
MSengine = create_engine(
    'mssql+pyodbc:///?odbc_connect=%s?charset=utf8' % (
        urllib.parse.quote_plus(
            'DRIVER={FreeTDS};SERVER=localhost;'
            'DATABASE=db;UID=user;PWD=pwd;port=1433;'
            'TDS_Version=8.0;ClientCharset=UTF-8')),encoding="utf8")
MSconn = MSengine.connect()
print('[{}]: Connected to MSSQL...'.format(datetime.now()))

################################################################################
## Define common DB queries
################################################################################

target_tables = ['public.users'
                ,'public.system_users'
                ,'public.hist_projects'
                ,'public.hist_users'
                ,'public.hist_views'
                ,'public.hist_workbooks'
                ,'public.historical_event_types'
                ,'public.historical_events'
                ,'public.licensing_roles'
                ,'public.http_requests']


# faster version of read_sql
def read_sql_tmp(query,db_engine):
    with tempfile.TemporaryFile() as tmpfile:
        copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(query=query,head="HEADER")
        conn = db_engine.raw_connection()
        cur = conn.cursor()
        cur.copy_expert(copy_sql,tmpfile)
        tmpfile.seek(0)
        df = pd.read_csv(tmpfile)
        return df

def sql_generator (src_engine,src_schema,dst_engine,dst_schema,table):
    try:
        i = 0
        for chunk in pd.read_sql_table(table,src_engine,src_schema,chunksize=1000):
            if i == 0:
                ie = 'replace'
            else:
                ie = 'append'
            chunk.to_sql(table,con=dst_engine,schema=dst_schema,if_exists=ie,chunksize=50,method='multi',index=False)
            i = i+1
    except Exception as e:
        print('{}'.format(e))

def sql_generator_query (src_engine,src_schema,dst_engine,dst_schema,query,table):
    try:
        chunk = read_sql_tmp(query,PGengine)
        chunk.to_sql(table,con=dst_engine,schema=dst_schema,if_exists='replace',chunksize=50,method='multi',index=False)

    except Exception as e:
        print('{}'.format(e))

# Return users table
for table in target_tables:
    dbschema,tablename = table.split('.')
    print('[{}]: Extracting table [{}]'.format(datetime.now(),tablename))
    try:
        if tablename=='http_requests':
            query = "SELECT user_id,controller,action,http_request_uri,created_at,currentsheet FROM public.http_requests where strpos(controller,\'cross\')>0"
        else:
            #sql_generator(PGconn,dbschema,MSconn,'imports_test',tablename)
            query = "SELECT * FROM {}".format(table)
        
        sql_generator_query(PGconn,dbschema,MSconn,'tableau',query,tablename)
        print('[{}]: Successfully exported data to [{}]'.format(datetime.now(),tablename))
    except Exception as e:
        print('Transfer failed for [{}]: {}'.format(tablename,e))
        

