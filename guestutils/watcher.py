import etcd
import os
import ast
import time
import threading
import sys
etcd_host_address = os.environ['ETCD_HOST_ADDRESS'] 
# etcd_host_address = '54.189.223.174'
client = etcd.Client(host=etcd_host_address, port=4001, read_timeout = sys.maxint)


val = client.read('/ingestor').value
val = ast.literal_eval(val)
# print val

#
# watches key, gets delta
# TODO doesn't support watching labels. ingestor label=[testing] doesn't work
#
# 
def watch_key(service, labels=[]):
#
# watch a key in etcd
#
	watch_key = '/'+str(service)
	#
	# store previous value 
	#
	prev_dict = ast.literal_eval(client.read(watch_key).value)
	previous_value = len(prev_dict.keys())
	print 'previous value was '+str(previous_value)
	current_value = previous_value
	current_dict = prev_dict
	print 'started watching key '+ watch_key
	for event in client.eternal_watch(watch_key):
		#
		# number of nodes has changed...
		# node removed:
		# node added:
		# container shouldn't know anything else?
		# how to restart cassandra? replace nodes one at a time?
		#
		current_dictionary = ast.literal_eval(client.read(watch_key).value)
		curr = len(current_dictionary.keys())
		if curr != 0:
			previous_value = current_value
			current_value = curr
			prev_dict = current_dict
			current_dict = current_dictionary
			delta = current_value - previous_value
			# print 'prev is '+str(previous_value)+' curr is '+str(current_value)+' delta is '+str(delta)
			service_change(watch_key, delta)
			
#
# user defined function, pluggable
# what procedure to invoke when services you depend on change
#			
def service_change(service, delta):
	try:
		import watch_methods 
		print 'running custom watch method'
		watch_methods.service_change(service, delta)
	except:
		print 'not implemented yet. service was '+str(service)+', delta was '+str(delta)


class ThreadClass(threading.Thread):
	service = None
	def set_service(self, service):
		self.service = service
	def run(self):
		service = self.service
		watch_key(service)
#
# spawns multiple threads to watch multiple keys
#
def watch_keys(service_list):
	for service in service_list:
		t=ThreadClass()
		t.set_service(service)
		t.daemon=True
		t.start()

keys = os.environ.get('WATCHES')
my_keys = keys.split(',')
watch_keys(my_keys)
# watch_key(os.environ.get('WATCHES'))
#
# keep threads alive
#
while True:
	time.sleep(60)