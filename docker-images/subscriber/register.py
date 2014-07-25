import yaml
from marathon import MarathonClient
import sys
import etcd
import ast
# from Entities import *
data = yaml.load(open('config.yaml', 'r'))

marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))
etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
#
# Registers a container with etcd
#
def register_with_etcd(service, name, host, port_mapping, labels = []):
  # throw an error if cannot connect to client?
  instance_dict = {'service_name': service,
           'instance_name': name,
           'instance_host': host,
           'port_mapping': port_mapping, 
           'labels': labels}
  etcd_key = "/"+service
  try:
    old_dict = etcd_client.read(etcd_key).value
  except:
    new_dict = {}
    etcd_client.write(etcd_key, new_dict)
  full_instances_dict = etcd_client.read(etcd_key).value
  full_instances_dict = ast.literal_eval(full_instances_dict)
  full_instances_dict[name] = instance_dict
  etcd_client.write(etcd_key, full_instances_dict)

#
# remove a container from etcd
#
def deregister_with_etcd(service, name):
	etcd_key = "/"+service
	try:
		old_dict = etcd_client.read(etcd_key).value
	except:
		new_dict = {}
		etcd_client.write(etcd_key, new_dict)
	full_instances_dict = etcd_client.read(etcd_key).value
	full_instances_dict = ast.literal_eval(full_instances_dict)
	full_instances_dict.pop(name, None)
	etcd_client.write(etcd_key, full_instances_dict)


# def clean_all():
# 	for service in data.keys():
# 		clean_service(service)

#
# makes sure there are no tasks in etcd that do not correspond with tasks known by marathon
# basically syncing up, no actual task removal involved.
#
def clean_service(service, labels= []):
	service_tasks = marathon_client.list_tasks()
	service_task_names = map(lambda x: x.id, service_tasks)
	print service_task_names
	print 'those are the running services'
	#
	# loop through etcd instances, if name not in tasks, clean up
	#
	service_etcd_instances = ast.literal_eval(etcd_client.read('/'+str(service)).value)
	for instance_name in service_etcd_instances.keys():
		if instance_name not in service_task_names:
			print 'this instance was not in my list '+str(instance_name)
			deregister_with_etcd(service, instance_name)
	print 'done cleaning service '+str(service)
	
		# etcd_client.write('')

def get_task(taskId):
	all_tasks = marathon_client.list_tasks()
	this_task = None
	#
	# also cleans up tasks
	#
	for task in all_tasks:
		if task.id == taskId:
			this_task = task
	return this_task


def decode_marathon_id(marathon_id, id_separator = 'D.L'):
    # split up id
    id_split = marathon_id.split(id_separator)
    service_name = str(id_split[0])
    labels = ast.literal_eval('['+id_split[1].replace("-", "'").replace(".", ",")+']')
    version = str(id_split[2])
    return {'service':service_name, 'labels':labels, 'version':version}


def register_new_container(task_id):
	# load most recent data
	data = yaml.load(open('config.yaml', 'r'))

	task = get_task(task_id)
	if task.started_at:
		app_id = task.app_id
		app_data = decode_marathon_id(app_id)
		labels = app_data['labels']
		service = app_data['service']
		lg_key = str(sorted(labels))
		host = task.host
		name = task.id 
		port_mapping = {}
		if 'ports' in data[service][lg_key].keys():
			ports = data[service][lg_key]['ports'].values()
			ports.sort()
			port_names = []
			for port in ports:
				port_names.append(reverse_map(data[service][lg_key]['ports'], port))
			for index in range(0, len(port_names)):
				port_mapping[port_names[index]] = {}
				port_mapping[port_names[index]]["external"] = ('0.0.0.0', str(task.ports[index])+'/tcp')
				port_mapping[port_names[index]]["exposed"] = str(ports[index]) + '/tcp'
		print service
		print name
		print host
		print port_mapping
		register_with_etcd(service, name, host, port_mapping, labels)
	else:
		print 'task was staged but not started...'


#
# erase all data in etcd and register just the tasks that are currently running
#
def register_all():
	print "registering all services"
	# delete all data 
	for service in data.keys():
		print "    replacing " + service
		try:
			etcd_client.write('/'+service, {})
		except:
			print 'key is not there'
	# register currently running tasks
	tasks = marathon_client.list_tasks()
	for task in tasks:
		#
		# only register tasks that have already started
		#
		if task.started_at:
			service = task.app_id
			#
			# periods are delimiters, separate out service (first) and labels (everything following)
			# ex flask.banana.apple
			# service is flask, two labels banana and apple
			# @LABELS
			# TODO finalize delimiter
			#
			labels = []
			if '.' in service:
				separates = service.split('.')
				service = separates[0]
				separates.pop(0)
				for separate in separates:
					labels.append(separate)
			host = task.host
			name = task.id 
			port_mapping = {}
			if 'ports' in data[service].keys():
				ports = data[service]['ports'].values()
				ports.sort()
				port_names = []
				for port in ports:
					port_names.append(reverse_map(data[service]['ports'], port))
				for index in range(0, len(port_names)):
					port_mapping[port_names[index]] = {}
					port_mapping[port_names[index]]["external"] = ('0.0.0.0', str(task.ports[index])+'/tcp')
					port_mapping[port_names[index]]["exposed"] = str(ports[index]) + '/tcp'
			print service
			print name
			print host
			print port_mapping
			register_with_etcd(service, name, host, port_mapping, labels)
		else:
			print 'task was staged but not started...'


def reverse_map(d, value):
	for key in d.keys():
		if d[key] ==  value:
			return key
	return None


if __name__ == "__main__":
    args = sys.argv
    print 'Welcome Master Liu'
    command = args[1]
    if command == 'all':
    	register_all()