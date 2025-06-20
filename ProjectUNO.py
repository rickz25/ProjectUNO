from tkinter import *
from PIL import ImageTk
from tkinter import messagebox
from tkinter.font import Font
from db import Database
import subprocess, platform
import socket
import schedule
import time
import threading
import requests
import os  
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import shutil 
import configparser 
import fnmatch
import logging
from PIL import Image
import psutil
import zipfile

# kill process when double run the program
process_to_kill = "ProjectUNO.exe"

# get PID of the current process
my_pid = os.getpid()

# iterate through all running processes
for p in psutil.process_iter():
	try:
		# if it's process we're looking for...
		if p.name() == process_to_kill:
			# and if the process has a different PID than the current process, kill it
			if not p.pid == my_pid:
				p.terminate()
	except psutil.AccessDenied:
		continue


# Create and configure logger
logging.basicConfig(filename="Logs/unoLog/logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#global variable
schedule_start_process = True

# set colours
bg_color = "#f24f00"
fg_color = "#2A1C06"
title_color = "white"
fg_color_result = "#CBCFCB"
fg_color_text = "#686C68"

config = configparser.ConfigParser()
config.read(r'settings/config.txt') 
tenantPath =  config.get('tenant_config', 'tenant_path')
isExist = os.path.isdir(tenantPath)
if not isExist:
	messagebox.showerror('Error', 'Tenant path not found!')
db = Database(f'{tenantPath}database/database.db')

scheduleStart =  config.get('tenant_config', 'schedule_start')
schedule_updater =  config.get('tenant_config', 'schedule_updater')
schedule_setting =  config.get('tenant_config', 'schedule_setting')

if scheduleStart == "":
    scheduleStart=5
else:
   scheduleStart = int(scheduleStart)
	
if schedule_updater == "":
    schedule_updater=1
else:
    schedule_updater = int(schedule_updater)

if schedule_setting == "":
    schedule_setting=1
else:
    schedule_setting = int(schedule_setting)

#Manual send
def manual_upload():
	try:
		c1='php artisan config:cache'
		c2='php artisan config:clear'
		c3='php artisan cache:clear'
		c4='php artisan route:cache'
		command = f"cd {tenantPath} && {c1} && {c2} && {c3} && {c4}"
		run_command = f"cd {tenantPath} && php artisan schedule:run"

		isExist = os.path.isdir(tenantPath)
		if isExist:
			process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			output, errors = process.communicate()

			time.sleep(10)  # wait for the cache to clear
			
			if errors==None:
				messagebox.showinfo('Success', 'Clear Cache Successful!')
				proc = subprocess.Popen(run_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
				out, err = proc.communicate()
				if err==None:
					messagebox.showinfo('Success', 'Started manually!')
				else:
					messagebox.showerror('Error', err)
					raise ValueError(err)
			else:
				messagebox.showerror('Error', errors)
				raise ValueError(errors)
		else:
			messagebox.showerror('Error', 'Tenant path not found!')
	except ValueError as ve:
		logger.exception("Exception occurred: %s", str(ve))
		messagebox.showinfo('Error', str(ve))
		
#Auto clear cache
def auto_clear_cache():
	try:
		c1='php artisan config:cache'
		c2='php artisan config:clear'
		c3='php artisan cache:clear'
		c4='php artisan route:cache'
 	
		process = subprocess.Popen(f"cd {tenantPath} && {c1} && {c2} && {c3} && {c4}", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		output, errors = process.communicate()
		
		if errors==None:
			proc = subprocess.Popen(f"cd {tenantPath} && php artisan schedule:run", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			out, err = proc.communicate()
			if err==None:
				print('cleared')
			else:
				messagebox.showerror('Error', err)
				raise ValueError(errors)
		else:
			messagebox.showerror('Error', "Error on clear cache, please check the PHP Path.")
			raise ValueError(errors)
	except ValueError as ve:
		logger.exception("Exception occurred: %s", str(ve))

#schedule start
def schedule_start():
	try:
		process = subprocess.Popen(f"cd {tenantPath} && php artisan schedule:run", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		output, error = process.communicate()
		if error==None:
			print('started')
		else:
			messagebox.showerror('Error', "Error started, please check the PHP Path.")
			raise ValueError("Error started.")
	except ValueError as ve:
		logger.exception("Exception occurred: %s", str(ve))

#schedule interrupt
def schedule_stop():
	try:
		process = subprocess.Popen(f"cd {tenantPath} && php artisan schedule:interrupt", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		output, error = process.communicate()
	except ValueError as ve:
		logger.exception("Exception occurred: %s", str(ve))

#Ping
def ping2(host):
    """
    Returns True if host responds to a ping request
    """
    # Ping parameters as function of OS
    ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 4"
    args = "ping " + " " + ping_str + " " + host
    need_sh = False if  platform.system().lower()=="windows" else True

    # Ping
    return subprocess.call(args, shell=need_sh) == 0
	

#Telnet
def telnet2(ip, port):
	s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
	try:
		s.connect((ip , int(port)))
		s.shutdown(2)
		return True
	except:
		return False 


### API REQUEST
def fileUpdater():
	try:
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

		#set global schedule_start_process to false
		global schedule_start_process
		schedule_start_process = False

		#stop the schedule first before update the file
		# schedule_stop()

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
								if platform.system() == 'Windows':
									updatedsize = os.path.getsize(updatePath)
									currentsize = os.path.getsize(fullpath)
									if updatedsize != currentsize:
										ispath = Path(fullpath)
										if ispath.exists() and ispath.is_dir():
											shutil.rmtree(ispath)
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
		#set global schedule_start_process to true
		schedule_start_process = True

	except Exception as e:
   		logger.error('Error at %s', 'Updater', exc_info=e)

def clear_widgets(frame):
	# select all frame widgets and delete them
	for widget in frame.winfo_children():
		widget.destroy()

def update(cccode,ip_server,pos_vendor_code, port):
	if cccode == '' or ip_server == '' or pos_vendor_code == '' or port == '':
		messagebox.showerror('Required Fields', 'Please include all fields')
		return
	return db.update(1, cccode, ip_server, pos_vendor_code, port)

def load_frame1():
	clear_widgets(frame2)
	clear_widgets(frame3)
	# stack frame 1 above frame 2
	frame1.tkraise()
	# prevent widgets from modifying the frame
	frame1.pack_propagate(False)

	# create label widget for instructions
	# Label(frame1, text="",fg=title_color,font=titleFont,borderwidth=1,bg=bg_color).grid(row=0, column=1, pady=10,sticky=W)

	#get record
	status = db.getStatus()
	print(status[3])

	current_date = StringVar()
	# sending_text = StringVar()
	Label(frame1, text='Current Date:', font=labelFont, fg=fg_color, bg=bg_color,anchor="w", justify=LEFT).grid(row=2, column=0,padx=10,pady=10,sticky=W)
	Label(frame1,font=normalFont, fg=fg_color_result, textvariable=current_date, bg=bg_color, borderwidth=1).grid(row=2, column=1,sticky=W)
	current_date.set(status[3])

	sending_text = Label(frame1, font=labelFont, fg="#CBCFCB", pady=10, bg=bg_color)
	sending_text.grid(row=3, column=1, sticky=W)

	#Green=0, Orange=1, Red=2
	Label(frame1, text='Sending:', font=labelFont, fg=fg_color, pady=10, bg=bg_color,anchor="w", justify=LEFT).grid(row=3, column=0,padx=10,sticky=W)
	if status[1]==0:
		logo_img = ImageTk.PhotoImage(file="assets/icon/red.png")
		logo_widget = Label(frame1, image=logo_img, bg=bg_color)
		logo_widget.image = logo_img
		logo_widget.grid(row=3, column=1,sticky=W)
		sending_text.config(text='Not Sending',padx=35)
	if status[1]==1:
		logo_img = ImageTk.PhotoImage(file="assets/icon/green.png")
		logo_widget = Label(frame1, image=logo_img, bg=bg_color)
		logo_widget.image = logo_img
		logo_widget.grid(row=3, column=1,sticky=W)
		sending_text.config(text='Sending',padx=35)
	if status[2] ==0 and status[1]==1 :
		logo_img = ImageTk.PhotoImage(file="assets/icon/orange.png")
		logo_widget = Label(frame1, image=logo_img, bg=bg_color)
		logo_widget.image = logo_img
		logo_widget.grid(row=3, column=1,sticky=W)
		sending_text.config(text='Waiting',padx=35)
	

	connection = StringVar()
	Label(frame1, text='Connection:', font=labelFont, fg=fg_color, pady=10, bg=bg_color,anchor="w", justify=LEFT).grid(row=4, column=0,padx=10,sticky=W)
	conn = Label(frame1, fg=fg_color_result,font=normalFont,textvariable=connection,borderwidth=1, bg=bg_color)
	conn.grid(row=4, column=1,sticky=W)

	if status[1]==1:
		connection.set('Online')
		conn.config(fg="#166A09")
	else:
		connection.set('Offline')
		conn.config(fg="#892907")
	
	# create button widget
	Button(frame1, text='Other Settings',font=buttonFont, width=12, bg="#999999", highlightthickness=0, bd=0, fg="white", cursor="hand2", command=lambda:load_frame2()).grid(row=5, column=0, pady=10,sticky=W, padx=7)
	Button(frame1, text='Test Connection',font=buttonFont, width=12, bg="#999999", highlightthickness=0, bd=0, fg="white", cursor="hand2", command=lambda:load_frame3()).grid(row=5, column=1, pady=10, padx=0,sticky=W)
	Button(frame1, text='Manual Upload',font=buttonFont, width=12, bg="#999999", highlightthickness=0, bd=0, fg="white", cursor="hand2", command=lambda:manual_upload()).grid(row=5, column=1, pady=1,padx=119,sticky=W)

	# log_img = ImageTk.PhotoImage(file="assets/icon/bottom_logo.png")
	# log_widget = Label(frame1, image=log_img, bg=bg_color)
	# log_widget.image = log_img
	# log_widget.grid(row=7, column=0)

def load_frame2():
	clear_widgets(frame1)
	# stack frame 2 above frame 1
	frame2.tkraise()

	Label(frame2, text="Other Settings",fg=title_color,font=titleFont,borderwidth=1, relief="groove",bg=bg_color).grid(row=0, column=0, pady=10,sticky=W, padx=10)

	# CCCODE
	cccode = StringVar()
	Label(frame2, text='CCCODE:', font=labelFont, fg=fg_color, pady=10, bg=bg_color).grid(row=2, column=0, sticky=W,padx=10)
	Entry(frame2, width=20,font=normalFont, fg=fg_color_text, textvariable=cccode).grid(row=2, column=1, sticky=W,padx=10)
	# POS VENDOR CODE
	pos_vendor_code = StringVar()
	Label(frame2, text='POS VENDOR CODE:', font=labelFont, fg=fg_color, pady=10, bg=bg_color).grid(row=3, column=0, sticky=W,padx=10)
	Entry(frame2, width=20,font=normalFont, fg=fg_color_text, textvariable=pos_vendor_code).grid(row=3, column=1, sticky=W,padx=10)
	# Autopoll IP Server
	ip_server = StringVar()
	Label(frame2, text='AUTOPOLL IP SERVER:', font=labelFont, fg=fg_color, pady=10, bg=bg_color).grid(row=4, column=0, sticky=W,padx=10)
	Entry(frame2, width=20,font=normalFont, fg=fg_color_text, textvariable=ip_server, show="*").grid(row=4, column=1, sticky=W,padx=10)
	# Port
	port = StringVar()
	Label(frame2, text='PORT:', font=labelFont, fg=fg_color, pady=10, bg=bg_color).grid(row=5, column=0, sticky=W,padx=10)
	Entry(frame2, textvariable=port, fg=fg_color_text, width=20,font=normalFont ).grid(row=5, column=1, sticky=W,padx=10)

	#Set record from database
	record = db.fetchSetting()
	cccode.set(record[1])
	ip_server.set(record[3])
	pos_vendor_code.set(record[2])
	port.set(record[4])

	# 'back' button widget
	Button(frame2,text="<< Back",font=buttonFont,bg="#999999",fg="white",cursor="hand2", width=9, activebackground="#badee2", highlightthickness=0, bd=0,activeforeground="black",command=lambda:load_frame1()).grid(row=7, column=1,sticky=W,padx=10)
	Button(frame2,text="Update",font=buttonFont,bg="#999999",fg="white",cursor="hand2", width=9, activebackground="#badee2", highlightthickness=0, bd=0,activeforeground="black",command=lambda:update(cccode.get(), ip_server.get(),pos_vendor_code.get(),port.get())).grid(row=7, column=1,sticky='W',padx=110)
 
 
def load_frame3():
	clear_widgets(frame1)
	# stack frame 2 above frame 1
	frame3.tkraise()

	#get record
	conn = db.fetchSetting()

	Label(frame3, text="Test Connection",fg=title_color,font=titleFont,borderwidth=1, relief="groove",bg=bg_color).grid(row=0, column=0, pady=15,sticky=W,padx=10)

	def ping():
		con = db.fetchSetting()
		result = ping2(con[3])
		if result==True:
			pingText.config(text=f"{con[3]} is up!")
		else:
			pingText.config(text=f"{con[3]} is down!")
	
	def telnet():
		con = db.fetchSetting()
		result = telnet2(con[3], con[4])
		if result==True:
			telnetText.config(text='Connected...')
		else:
			telnetText.config(text='Not Connected...')
	

	# ping
	Label(frame3, text='PING Autopoll IP Server:', font=labelFont, fg=fg_color, pady=10,bg=bg_color).grid(row=2, column=0, sticky=W,padx=10)
	Button(frame3,text="Check",font=buttonFont,bg="#999999",fg="white",cursor="hand2",width=8,activebackground="#badee2", highlightthickness=0, bd=0, activeforeground="black",command=lambda:ping()).grid(row=2, column=1,sticky=W)
	pingText=Label(frame3, fg=fg_color_result,font=normalFont, bg=bg_color,width=20)
	pingText.grid(row=3, column=1,sticky=W)
	# Telnet
	Label(frame3, text='Telnet:', font=labelFont, fg=fg_color, pady=10,bg=bg_color).grid(row=4, column=0, sticky=W,padx=10)
	Button(frame3,text="Check",font=buttonFont,bg="#999999",fg="white",cursor="hand2",width=8,activebackground="#badee2", highlightthickness=0, bd=0, activeforeground="black",command=lambda:telnet()).grid(row=4, column=1,sticky=W)
	telnetText = Label(frame3,font=normalFont, fg=fg_color_result, bg=bg_color, width=20)
	telnetText.grid(row=5, column=1,sticky=W)

	Button(frame3,text="<< Back",font=buttonFont,bg="#999999",fg="white",cursor="hand2",width=8,activebackground="#badee2", highlightthickness=0, bd=0, activeforeground="black",command=lambda:load_frame1()).grid(row=6, column=1,pady=20, sticky=W)
 

# initiallize app with basic settings
root = Tk()
root.title('')
root.iconbitmap('assets/icon/settings.ico')
root.eval("tk::PlaceWindow . center")
root.configure(background=bg_color)
root.geometry('460x265')

image = Image.open("assets/icon/bottom_logo.png")
 
# Resize the image using resize() method
resize_image = image.resize((90, 25))
img = ImageTk.PhotoImage(resize_image)
# create label and add resize image
label1 = Label(root, image=img,bg=bg_color)
label1.image = img
label1.grid(row=1, column=0,pady=1, padx=10, sticky=W)

version = Label(root, text='v2.3.2',bg=bg_color,fg="white")
version.grid(row=1, column=1,sticky='e')

# place app in the center of the screen (alternative approach to root.eval())
# x = root.winfo_screenwidth() // 2
# y = int(root.winfo_screenheight() * 0.1)
# root.geometry('500x600+' + str(x) + '+' + str(y))

# load custom fonts
titleFont = Font(
	family="arial",
	size=12,
	weight="bold"
)
buttonFont = Font(
	family="arial",
	size=11,
	
)
labelFont = Font(
	family="arial",
	size=11,
	
)
resultFont = Font(
	family="arial",
	size=12,
	
)
normalFont = Font(
	family="arial",
	size=12,
	
)

# create a frame widgets
frame1 = Frame(root, bg=bg_color,relief= 'sunken')
frame2 = Frame(root, bg=bg_color)
frame3 = Frame(root,bg=bg_color)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# place frame widgets in window
for frame in (frame1, frame2, frame3):
	frame.grid(row=0, column=0, padx= 25)
	
	

# load the first frame
load_frame1()


##Schedule cron job
# schedule.every(2).seconds.do(load_frame1)
try:
	schedule.every(schedule_setting).minutes.do(load_frame1)
	schedule.every(schedule_updater).minutes.do(fileUpdater)
	if schedule_start_process:
		schedule.every(scheduleStart).seconds.do(schedule_start)
		schedule.every(1).hour.do(auto_clear_cache)

	def check_schedule():
		while True:
			schedule.run_pending()
			time.sleep(1)

	threading.Thread(target=check_schedule, daemon=True).start()
except Exception as e:
   logger.error('Error at %s', 'Scheduler', exc_info=e)

logging.getLogger('schedule').setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# def minimizeWindow():
#     root.withdraw()
#     root.overrideredirect(False)
#     root.iconify()

# def disable_event():
#     pass

# root.resizable(False, False)
# root.protocol("WM_DELETE_WINDOW", minimizeWindow)

# run app
root.mainloop()