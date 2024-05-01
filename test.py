import configparser 
import subprocess
import os


config = configparser.ConfigParser()
config.read(r'settings/config.txt') 

tenantPath =  config.get('tenant_config', 'tenant_path')

# print(isinstance(int(tenantPath), int))

# if tenantPath == "":
#     print('empty')

# else:
#     print('not')

# os.chdir(tenantPath)
# os.startfile("schedule.bat")

# os.system(f'cmd /c "cd {tenantPath} && php artisan schedule:run"')

c1='php artisan config:cache'
c2='php artisan config:clear'
c3='php artisan cache:clear'
c4='php artisan route:cache'

# exit_code = os.system(f'cmd /c "cd {tenantPath} && {c1} && {c2} && {c3} && {c4}"')

proc = subprocess.Popen(f"cd {tenantPath} && php artisan schedule:run", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
out, err = proc.communicate()
if err==None:
    print('no error')
else:
    print('with error')

# if exit_code == 0:
#     print('Working')
# else:
#    print('Something went wrong')
