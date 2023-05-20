#!/usr/env/python3 

import re
import os
import ssl
import filecmp
import smtplib
import requests
from difflib import Differ
from datetime import datetime
from datetime import timedelta

#Setting variables for date
date = datetime.today()
yday = date - timedelta(days=1)
yesterday = f'{yday.day:02d}'
day = f'{date.day:02d}'
month = f'{date.month:02d}'
year = datetime.now().year
year_month = str(year) + '/' + str(month)

#Setting variables for the scripts files it writes to
cwd = os.path.realpath(__file__)
new_cwd = cwd.replace(os.path.basename(__file__), "")
file = new_cwd + 'articles{}-{}-{}.txt'.format(month, day, year)
yesterdays_file = new_cwd + 'articles{}-{}-{}.txt'.format(month, yesterday, year)
error = new_cwd + "error.log"

#Checking for gmailpass environment variable
try:
	os.environ['gmailpass']
except:
	with open(error, 'a') as f:
		f.write(f'[{datetime.now()}]: Gmail App Password environment variable not found. Please set an env variable called "gmailpass' + '\n')
	f.close()
	exit()

#If first time running
first_time = ""
if (not os.path.exists(file)) and (not os.path.exists(yesterdays_file)):
	first_time = True
	with open(file, 'w') as f:
		pass
	f.close()

#Setting SMTP using TLS settings
smtp_server = 'smtp.gmail.com'
password = os.environ['gmailpass']
port = 587
sender = ""
receiver = ""

#Writing to error file if Sender/Reciever variables are null
if not (sender and receiver):
	with open(error, 'a') as f:
		f.write(f'[{datetime.now()}]: Neither the sender/receiver variables are set. Please edit the script and enter the email for the address that will send & the address that will receive the RSS email on line 50 and 51.' + '\n')
	f.close()
	exit()
	 
if not ( sender or receiver):
	if not sender:
		with open(error, 'a') as f:
			f.write(f'[{datetime.now()}]: Sender variable is not set. Please edit the script and enter the email for the address that will send the RSS email on line 50.' + '\n')
		f.close()
	elif not receiver:
		with open(error, 'a') as f:
			f.write(f'[{datetime.now()}]: Receiver variable is not set. Please edit the script and enter the email for the address that will receive the RSS email on line 51.' + '\n')
		f.close()
	exit()
				
#Create secure SSL context
context = ssl.create_default_context()

#Setting list of RSS feeds
feeds = [
	'https://krebsonsecurity.com/feed/', 
	'https://feeds.feedburner.com/TheHackersNews?format=html', 
	'https://cybersecurity.att.com/site/blog-all-rss',
	'https://www.techrepublic.com/rssfeeds/topic/security/?feedType=rssfeeds',
	'https://tacsecurity.com/feed/',
	'https://www.exploitone.com/feed/',
	'https://thecyberexpress.com/feed/'
	]

#If current day's file doesn't exist, rename previous days list to today's date and then continue
if os.path.exists(file):
	file1 = new_cwd + 'articles{}-{}-{}.1.txt'.format(month, day, year)
else:
	os.rename(yesterdays_file, file)
	file1 = new_cwd + 'articles{}-{}-{}.1.txt'.format(month, day, year)

#Function to pull RSS HTML page, and parse for <link> tag and write to new file to compare differences
def utd(url):
	x = requests.get(url)
	links = re.findall('<link>[a-zA-Z0-9].*?<', x.text)
	rep = [sub.replace('<link>', "").replace('<', "") for sub in links]
	for link in rep:
		with open(file1, 'a+') as f:
				f.write(link + '\n')
		f.close()

#For RSS feed in list		
for feed in feeds:
	utd(feed)

#Compare the temp file with original list of URL's. If different, send latest URL's. 
if filecmp.cmp(file1, file) is True: 
	os.remove(file1)
else:
	with open (file) as f:
		file1_lines = f.readlines()
	f.close()
	with open (file1) as f:
		file2_lines = f.readlines()
	f.close()
	d = Differ()
	difference = (list(d.compare(file2_lines, file1_lines)))
	rep = [sub.replace('- ', "").strip() for sub in difference]
	new = []
	for line in reversed(list(rep)):
		with open(file, 'r') as f:
			if line in f.read():
				pass
			else:
				new.append(''.join(line).strip())
		if "+" in line:
			new.remove(line)
	try:
		server = smtplib.SMTP(smtp_server, port)
		server.ehlo()
		server.starttls(context=context)
		server.ehlo()
		server.login(sender, password)
		message = f'Subject: Latest Security Articles' + ('\n' * 2) + 'Here are the latest security articles from the past hour: ' + ('\n' * 2) + "{}".format(new) + ('\n') + 'Delivered via PySS'
		if first_time == True: 
			pass
		else:
			if new == []:
				pass
			else:
				server.sendmail(sender, receiver, message.replace('[', "").replace(']', "").replace("'", "").replace(',', ('\n' * 2)).strip())
	except Exception as e:
		with open(error, 'a') as f:
			f.write(f'[{datetime.now()}]: {e}' + '\n')
		f.close()
	finally:
		server.quit()
	os.remove(file)
	os.rename(file1, file)
