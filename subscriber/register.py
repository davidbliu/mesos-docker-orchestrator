import yaml
from marathon import MarathonClient
import sys
import etcd
import ast

data = yaml.load(open('config.yaml', 'r'))
marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))
etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
#
# Registers a container with etcd
#
def register_with_etcd(service, name, host, port_mapping):
  # throw an error if cannot connect to client?
  instance_dict = {'service_name': service,
           'instance_name': name,
           'instance_host': host,
           'port_mapping': port_mapping}
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

#
# erase all data in etcd and register just the tasks that are currently running
#
def register_all():
	print "registering all services"
	# delete all data 
	for service in data['services'].keys():
		print "    replacing " + service
		etcd_client.write('/'+service, {})
	# register currently running tasks
	tasks = marathon_client.list_tasks()
	for task in tasks:
		#
		# only register tasks that have already started
		#
		if task.started_at:
			service = task.app_id
			host = task.host
			name = task.id 
			port_mapping = {}
			if 'ports' in data['services'][service].keys():
				ports = data['services'][service]['ports'].values()
				ports.sort()
				port_names = []
				for port in ports:
					port_names.append(reverse_map(data['services'][service]['ports'], port))
				for index in range(0, len(port_names)):
					port_mapping[port_names[index]] = {}
					port_mapping[port_names[index]]["external"] = ('0.0.0.0', str(task.ports[index])+'/tcp')
					port_mapping[port_names[index]]["exposed"] = str(ports[index]) + '/tcp'
			print service
			print name
			print host
			print port_mapping
			register_with_etcd(service, name, host, port_mapping)
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