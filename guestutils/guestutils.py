import os
import etcd
import docker
import ast
import time
import socket
# TODO replace hardcoded address
etcd_host_address = os.environ['ETCD_HOST_ADDRESS'] 
client = etcd.Client(host=etcd_host_address, port=4001)
"""
assumes that these env variables are passed into container.
SERVICE_NAME: the friendly name of the service the container is an instance of. Note that it is possible to have multiple clusters of the same kind of application by giving them distinct friendly names.
CONTAINER_NAME: the friendly name of the instance, which is also used as the name of the container itself. This will also be the visible hostname from inside the container.
CONTAINER_HOST_ADDRESS: the external IP address of the host of the container. This can be used as the "advertised" address when services use dynamic service discovery techniques.
"""

#
# Wait for etcd config
#

def get_environment_name():
	# returns the name of the environment as defined in the description file. Could be useful to namespace information inside ZooKeeper for example.
	return 'default'
def get_service_name():
	# returns the friendly name of the service the container is a member of.
	return os.environ['SERVICE_NAME']
def get_container_name():
	# returns the friendly name of the container itself.
	return os.environ['CONTAINER_NAME']
def get_container_host_address():
	# returns the IP address or hostname of the host of the container. Useful if your application needs to advertise itself to some service discovery system.
	return os.environ['CONTAINER_HOST_ADDRESS']
	service = get_service_name()
	all_service_instances = client.read('/' + service).value
	return all_service_instances[get_container_name()]

def get_container_internal_address():
	# returns the IP address assigned to the container itself by Docker (its private IP address).
	# host_ip = get_container_host_address()
	# print 'this is the modifIED VERSION'
	# dockerclient = docker.Client(base_url = "tcp://"+host_ip+":4243", 
	# 	version = '1.10', 
	# 	timeout=10)
	# details =  dockerclient.inspect_container(get_container_name())
	# return str(details['NetworkSettings']['IPAddress'])
	return socket.gethostbyname(socket.gethostname())
def get_port(name, default = 'default_port'):
	# will return the exposed (internal) port number of a given named port for the current container instance. This is useful to set configuration parameters for example.
	# 'port_mapping': {'rpc': {'external': ('0.0.0.0', '9160/tcp'), 'exposed': '9160/tcp'}, 'storage': {'external': ('0.0.0.0', '7000/tcp'), 'exposed': '7000/tcp'}
	if default != 'default_port':
		return get_specific_exposed_port(get_service_name(), get_container_name(), name, default)
	return get_specific_exposed_port(get_service_name(), get_container_name(), name)
def get_node_list(service, ports=[], minimum=1, labels = []):
	# It takes in a service name and an optional list of port names and returns the list of IP addresses/hostname of the containers of that service. For each port specified, in order, it will append :<port number> to each host with the external port number. For example, if you want to return the list of ZooKeeper endpoints with their client ports:
	# get_node_list('zookeeper', ports=['client']) -> ['c414.ore1.domain.com:2181', 'c415.ore1.domain.com:2181']
	nodes = []
	all_service_instances = client.read('/' + service).value
	all_service_instances = ast.literal_eval(all_service_instances)

	for key in all_service_instances.keys():
		instance = all_service_instances[key]
		#
		# only proceed if the labels are correct
		# @LABELS
		#
		fits_query=True
		for label in labels:
			if label not in instance['labels']:
				fits_query = False
		if fits_query:
			node = instance['instance_host']
			portlist = ""
			for port in ports:
				p = get_specific_port(instance['service_name'], instance['instance_name'], port)
				p = ":" + p
				portlist = portlist + p
			nodes.append(str(node + portlist))
	return nodes
def get_specific_host(service, container):
	# which can be used to return the hostname or IP address of a specific container from a given service, and
	all_service_instances = client.read('/' + service).value
	all_service_instances = ast.literal_eval(all_service_instances)
	try:
		return all_service_instances[container]['instance_host']
	except: 
		return None
def get_specific_port(service, container, port, default='default'):
	# to retrieve the external port number of a specific named port of a given container.
	all_service_instances = client.read('/'+service).value
	all_service_instances = ast.literal_eval(all_service_instances)
	my_instance = all_service_instances[container]
	port_mappings = my_instance['port_mapping']
	port_mapping = port_mappings.get(port)
	if port_mapping is None:
		return default
	return port_mapping['external'][1].replace('/tcp', '')
def get_specific_exposed_port(service, container, port, default='default'):
	# to retrieve the exposed (internal) port number of a specific named port of a given container.
	all_service_instances = client.read('/'+service).value
	all_service_instances = ast.literal_eval(all_service_instances)
	print all_service_instances.keys()
	my_instance = all_service_instances[container]
	port_mappings = my_instance['port_mapping']
	port_mapping = port_mappings.get(port)
	if port_mapping is None:
		return default
	return port_mapping['exposed'].replace('/tcp', '')

def test_all():
	try:
		print 'get_environment_name():'
		print get_environment_name()
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_service_name():'
		print get_service_name()
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_container_name():'
		print get_container_name()
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_container_host_address():'
		print get_container_host_address()
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_container_internal_address():'
		print get_container_internal_address()
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_port(name, default = default_port):'
		print get_port('storage', 1234)
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_node_list(service, ports=[], minimum=1):'
		print get_node_list('cassandra', ports = ['storage', 'transport', 'rpc'])
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'
	try:
		print 'get_specific_host(service, container):'
		print get_specific_host('cassandra', 'cassandra2')
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_specific_port(service, container, port, default'
		print get_specific_port('cassandra', 'cassandra2', 'storage', 1234)
		print get_specific_port('cassandra', 'cassandra2', 'storage')
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'

	try:
		print 'get_specific_exposed_port(service, container, port, defaul'
		print get_specific_exposed_port('cassandra', 'cassandra2', 'storage', 1234)
		print get_specific_exposed_port('cassandra', 'cassandra2', 'storage')
	except Exception, e:
		print e.__doc__
		print e.message
		print 'failed'