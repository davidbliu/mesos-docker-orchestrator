import argparse
import atexit
import sys
import urlparse
import yaml
from flask import Flask, request, jsonify, render_template
import marathon
import urllib2
import etcd
import socket
import os
import shutil
import ast
import json
#
# copy config yaml file to this directory. should be included in volume
#
# shutil.copyfile('/opt/data/config.yaml', 'config.yaml')d
#
# import etcd registration tools from regisiter.py
#

#
# for storing events (TODO)
#
from stores import InMemoryStore, SyslogUdpStore


app = Flask(__name__)

# re-initialize later
events = None
event_store = None
data = None
marathon_client = None
def on_exit(marathon_client, callback_url):
	print 'exiting app.....'
	marathon_client.delete_event_subscription(callback_url)

#
# write latest data into config file
# set data here as well for /info path
#
@app.route('/reconfigure', methods=['POST'])
def reconfigure():
	global data
	global marathon_client
	data = request.form
	data = request.form['config_data']
	#
	# write that into config file
	#
	data = ast.literal_eval(data)

	print type(data)
	with open('config.yaml', 'w') as outfile:
		outfile.write(yaml.dump(data))
	#
	# register subscriber with marathon
	#
	# print 'creating event subscriber to marathon...'
	data = yaml.load(open('config.yaml', 'r'))
	
	# print 'this is data'
	# print data
	marathon_url = 'http://' + data['marathon']['host'] + ':' + str(data['marathon']['port'])
	print 'trying this marathon url: '+ str(marathon_url)
	callback_url = 'http://localhost:5000/callback' # testing locally
	host_address = os.environ.get('CONTAINER_HOST_ADDRESS')
	host_port = os.environ.get('CONTAINER_HOST_PORT')
	if host_address and host_port:
		callback_url = 'http://'+str(host_address)+':'+str(host_port)+'/callback'
	m = marathon.MarathonClient(marathon_url)
	m.create_event_subscription(callback_url)
	atexit.register(on_exit, m, callback_url)
	etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
	print 'successfully registered...app has started'
	return jsonify(result={"status": 200})

#
# notify when task created/destroyed
#
@app.route('/callback', methods=['GET', 'POST'])
def callback():
	# try:
	event = request.get_json()
	if event['eventType'] == "status_update_event":
		#
		# register/deregister logic goes here
		#
		status = event['taskStatus']
		host = event['host']
		taskId = event['taskId']
		appId = event['appID']

		
		
		#
		# register all running containers with etcd
		#
		import register as reg
		service_name = reg.decode_marathon_id(appId)['service']
		# 
		# status 1 means running 2 means killed
		print 'a '+str(service_name)+' container changed: status '+str(status)
		print 'reconfiguring etcd...'
		
		if int(status) == 1:
			print 'registering new container '+str(taskId)
			reg.register_new_container(taskId)
		else:
			print 'remove dead container '+str(taskId)
			reg.deregister_with_etcd(service_name, taskId)
		reg.clean_service(service_name)
		# reg.register_all()
		# print 'done'
	# except Exception as failure:
	#     print 'wut...something failed...'
	#     print failure
	return jsonify(result={"status": 200})

@app.route('/info', methods = ['GET', 'POST'])
def info():
	registered = {}
	#
	# loop through services
	#
	etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
	for service in data.keys():
		registered[service] = {}
		print 'trying this key '+str(service)
		try:
			full_instances_dict = etcd_client.read('/'+service).value
			full_instances_dict = ast.literal_eval(full_instances_dict)
			for instance in full_instances_dict.keys():
				registered[service][instance] = full_instances_dict[instance]
			print registered
		except Exception as failure:
			print failure
			print 'cannot read this key from etcd'
			# print registered

	# except:
	#     print 'wut wut'
	return render_template('etcd_view.html', registered = registered)

if __name__ == '__main__':

	data = None
	# host = 'localhost'
	host = socket.gethostbyname(socket.gethostname())
	print 'starting app on '+str(host)
	app.run(port=5000, host=host)