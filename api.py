
import requests
import os  
from io import BytesIO
from zipfile import ZipFile
import shutil 
from db import Database
import time
import fnmatch
import configparser 

db = Database('db/database.db')

config = configparser.ConfigParser()
config.read(r'settings/config.txt') 

tenantPath =  config.get('tenant_config', 'tenant_path')

named_tuple = time.localtime() # get struct_time
filename_date = time.strftime("%m%d%Y_%H%M%S", named_tuple)
date = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)

#get record from database
record = db.fetchSetting()
cccode = record[1]
ip_server = record[3]
port = record[4]

auth_token='eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY1NDc1NDg1NCwiaWF0IjoxNjU0NzU0ODU0fQ.p6WAfLuC39cMk3XEF4LcU5iZy1rzbL0VTKVpTY7mRGQ'
headers = {'Authorization': f'Bearer {auth_token}'}
data = {'cccode' : cccode}

baseurl = f'http://{ip_server}:{port}/api/get-file'
baseurl_status = f'http://{ip_server}:{port}/api/move-file'

request = requests.post(baseurl, json=data, headers=headers)
# print(request.content)

zip = ZipFile(BytesIO(request.content))
zip.extractall("Files")

pattern = ['*.php','*.env','*.db','*.json']
path = 'Files'

for dirpath, dirnames, filenames in os.walk(path):

    if not filenames:
        continue
    for ext in pattern:
        files = fnmatch.filter(filenames, ext)
        if files:
            for file in files:
                Str ='{}/{}'.format(dirpath, file)
                folderpath = Str[17:100]
                fullpath = tenantPath+folderpath
                if os.path.exists(fullpath) :
                    os.remove(fullpath)
                shutil.move('Files/tenant_api/'+folderpath, fullpath, copy_function = shutil.copytree)
                if request.status_code  == 200:
                    r =requests.post(baseurl_status, json=data, headers=headers)
                    if r.status_code==200:
                        create_txt_path=f'{filename_date}.txt'
                        f = open('logs/'+create_txt_path, "a")
                        f.write(f'{date} - ({fullpath}), updated.\n')
                        f.close()
                    else:
                        create_txt_path=f'{filename_date}.txt'
                        f = open('logs/'+create_txt_path, "a")
                        f.write(f'{date} - Error update.\r\n')
                        f.close()
             
