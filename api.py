
import requests
import os  
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import shutil 
from db import Database
import time
import fnmatch
import configparser
import platform
import socket
import zipfile

config = configparser.ConfigParser()
config.read(r'settings/config.txt') 

tenantPath =  config.get('tenant_config', 'tenant_path')
db = Database(f'{tenantPath}database/database.db')

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

#Telnet
def telnet2(ip, port):
	s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
	try:
		s.connect((ip , int(port)))
		s.shutdown(2)
		return True
	except:
		return False 

def fileupdater():
    result = telnet2(ip_server, int(port)) 
    if result:
        request = requests.post(baseurl, json=data, headers=headers)
        if zipfile.is_zipfile(BytesIO(request.content)):
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
                            updatePath = f'{Path().absolute()}/Files/tenant_api/{folderpath}'
                            # if os.path.exists(fullpath) :
                            #     os.remove(fullpath)
                            if platform.system() == 'Windows':
                                updatedsize = os.path.getsize(updatePath)
                                currentsize = os.path.getsize(fullpath)
                                if(updatedsize != currentsize):
                                    ispath = Path(fullpath)
                                    if ispath.exists() and ispath.is_dir():
                                        shutil.rmtree(ispath)
                                    # shutil.move('Files/tenant_api/'+folderpath, fullpath, copy_function = shutil.copytree)
                                    # os.replace(updatePath, fullpath)
                                    shutil.move(updatePath, fullpath)
                                    
                                    if request.status_code  == 200:
                                        r =requests.post(baseurl_status, json=data, headers=headers)
                                        if r.status_code==200:
                                            create_txt_path=f'{filename_date}.txt'
                                            f = open('logs/updaterLog'+create_txt_path, "a")
                                            f.write(f'{date} - ({fullpath}), updated.\n')
                                            f.close()
                                        else:
                                            create_txt_path=f'{filename_date}.txt'
                                            f = open('logs/updaterLog'+create_txt_path, "a")
                                            f.write(f'{date} - Error update.\r\n')
                                            f.close()
                            # For linux
                            else:
                                stat = os.stat(fullpath)
                                try:
                                    return stat.st_birthtime
                                except AttributeError:
                                    # We're probably on Linux. No easy way to get creation dates here,
                                    # so we'll settle for when its content was last modified.
                                    return stat.st_mtime
                            
                            

print(fileupdater())

             
