import ConfigParser
import sqlite3
import requests
import json
import xml.etree.ElementTree as xmlModule
from requests.auth import HTTPBasicAuth
from pushover import init, Client


def saveBuild(build):
	db = sqlite3.connect('buildsdb')
	cursor = db.cursor()
	# Create table if required
	cursor.execute("CREATE TABLE IF NOT EXISTS BUILDS(buildId INTEGER, buildNum INTEGER, status TEXT, startDate TEXT, href TEXT, webUrl TEXT)")
	db.commit()
	cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS BUILDSBK ON BUILDS(buildId)")
	db.commit()
	# Insert build
	cursor.execute("""INSERT OR IGNORE INTO BUILDS VALUES (?,?,?,?,?,?)""",(build[0],build[1],build[2],build[3],build[4],build[5]))
	db.commit()
	db.close()

def isBuildInDB(ID):
	result = True
	db = sqlite3.connect('buildsdb')
	cursor = db.cursor()
	cursor.execute('SELECT 1 FROM BUILDS WHERE buildId=?',(ID,))
	if cursor.fetchone() == None:
		result = False
	db.close()
	return result

def pushMessage(Devices,Message,Title=None,Priority=None,URL=None):
	for device in Devices:
		if Priority == 'Blocker':
			device.send_message(Message, url=URL, title=Title, priority=2, expire=3600, retry=60)
		elif Priority == 'Normal':
			device.send_message(Message, url=URL, title=Title, priority=0)
		else:
			device.send_message(Message, url=URL, title=Title, priority=-1)


# Parse config file
config = ConfigParser.ConfigParser()
config.read('settings.cfg')

g_message_title = config.get('General','message_title')

tc_username = config.get('TeamCity','username')
tc_password = config.get('TeamCity','password')
tc_server = config.get('TeamCity','server')
tc_build_type_ids = json.loads(config.get('TeamCity','build_type_ids'))

pushover_app_token = config.get('Pushover','api_token')
devices_key_list = json.loads(config.get('Pushover','user_keys'))

#Register Devices
devices = []
for key in devices_key_list:
	devices.append(Client(key, api_token=pushover_app_token))

#Scrape Teamcity
for tc_build_type in tc_build_type_ids:
	builds = requests.get(tc_server+'/httpAuth/app/rest/buildTypes/id:'+tc_build_type+'/builds', auth=HTTPBasicAuth(tc_username, tc_password), verify=False)

	if builds.status_code != requests.codes.ok:
		print('TeamCity is not responding. Error code is '+str(builds.status_code)+'. Requested URL is '+builds.url)
		pushMessage(devices,'TeamCity is not responding. Error code is '+str(builds.status_code),Title=g_message_title,Priority='Blocker',URL=builds.url)
	else:
		print('Start parsing '+builds.url)
		root = xmlModule.fromstring(builds.text)
		buldslist = []
		for build in root.iter('build'):
			if not isBuildInDB(build.get('id')):
				#We got a new build
				print(build.get('status') + 'Build #'+build.get('number')+': '+build.get('webUrl'))
				if build.get('status')=='SUCCESS':
					#Send Push Message for Success
					pushMessage(devices,'Test Run is Successful. Build number is '+build.get('number'),Title=g_message_title)
				else:
					#Send Push Message for Failure
					pushMessage(devices,'Test Run is Failorious. Build number is '+build.get('number'),Title=g_message_title,Priority='Blocker',URL=build.get('webUrl'))

			saveBuild([build.get('id'),build.get('number'),build.get('status'),build.get('startDate'),build.get('href'),build.get('webUrl')])
		print('Done')

