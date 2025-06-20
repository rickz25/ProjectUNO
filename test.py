import configparser 
import subprocess
import os
import logging
import threading


config = configparser.ConfigParser()
config.read(r'settings/config.txt') 

tenantPath =  config.get('tenant_config', 'tenant_path')
c1='php artisan config:cache'
c2='php artisan config:clear'
c3='php artisan cache:clear'
c4='php artisan route:cache'

command = f"cd {tenantPath} && {c1} && {c2} && {c3} && {c4}"
run_command = f"cd {tenantPath} && php artisan schedule:run"

# def hasPHP():
#     try:
#         subprocess.run(['php', '-v'], stderr= subprocess.STDOUT)
#         return True
#     except:
#         return False
# hasPHP()


# process = subprocess.Popen(run_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# errors = process.stdout.read()

# print(errors)






exit_code = os.system(run_command)
if exit_code == 1:
    print('Something went wrong')
else:
    print('Working')


# 

# print(isinstance(int(tenantPath), int))

# if tenantPath == "":
#     print('empty')

# else:
#     print('not')

# os.chdir(tenantPath)
# os.startfile("schedule.bat")

# os.system(f'cmd /c "cd {tenantPath} && php artisan schedule:run"')

# c1='php artisan config:cache'
# c2='php artisan config:clear'
# c3='php artisan cache:clear'
# c4='php artisan route:cache'

# exit_code = os.system(f'cmd /c "cd {tenantPath} && {c1} && {c2} && {c3} && {c4}"')

# proc = subprocess.Popen(f"cd {tenantPath} && php artisan schedule:run", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# out, err = proc.communicate()
# if err==None:
#     print('no error')
# else:
#     print('with error')

# if exit_code == 0:
#     print('Working')
# else:
#    print('Something went wrong')

# Create and configure logger
# logging.basicConfig(filename="Logs/uno_log/logs.log",
#                     format='%(asctime)s %(message)s',
#                     filemode='w')

# # logging.config.fileConfig('temp.conf')
 
# # create logger
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
 
# # 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')


