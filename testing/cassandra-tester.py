import uuid
import time
import etcd
import yaml
import ast
import sys
from cassandra.cluster import Cluster


def return_cluster(etcd_client, index):
	node_dict = etcd_client.read('/cassandra').value
	node_dict = ast.literal_eval(node_dict)
	node = node_dict.keys()[index]
	instance = node_dict[node]
	port = 9042
	return {'host': str(instance['instance_host']), 'port': port}

#
# returns a list of all host ips
#
def return_cluster_hosts(etcd_client):
	nodelist = []
	node_dict = etcd_client.read('/cassandra').value
	node_dict = ast.literal_eval(node_dict)
	for key in node_dict.keys():
		nodelist.append(node_dict[key]['instance_host'])
	# return nodelist
	return ['54.202.3.58']
#
# connect to cluster, start session
#
data = yaml.load(open('config.yaml', 'r'))
etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))

sess = None
index = 0
while index < 6 and sess == None:
	try:

		connection_data = return_cluster_hosts(etcd_client)
		print '      trying '+str(connection_data)
		# cluster = Cluster([connection_data['host']], port = int(connection_data['port']))
		cluster = Cluster(connection_data)
		sess = cluster.connect()
	except Exception as failure:
		print '               failed '+str(failure)
		index+=1

assert sess is not None, 'sess is None'
print 'connection established'
sess.execute("CREATE KEYSPACE IF NOT EXISTS poopoo  WITH REPLICATION = {'class': 'NetworkTopologyStrategy', 'datacenter1' : 2}")
keyspace_name = 'poopoo'
sess.execute("CREATE TABLE IF NOT EXISTS poopoo.tests (test_id uuid PRIMARY KEY, test_name text)")

def num_records(table):
	events = sess.execute("SELECT * FROM "+keyspace_name+"."+str(table))
	return len(events)

#
# adding an event
#
def measure_insert_time(num_records):
	start_time = time.time()
	for i in range(0,num_records):
		session.execute("INSERT INTO events (id, title, type, properties) VALUES (%s, %s, %s, %s)",
		 (uuid.uuid1(),"blah","blah", "blah" ))  # right
	end_time = time.time()
	# delete useless events you just added
	session.execute('TRUNCATE events')
	completed_time = end_time-start_time
	print 'completed in '+str(completed_time)
	return completed_time

def measure_read_time(num_records):
	print 'not implemented yet'

#
# creates num records in table_name of keyspace
#
def populate_table(table_name, num):
	print 'populating tests table...'
	table = keyspace_name+'.'+table_name
	for i in range(0,num):
		sess.execute("INSERT INTO "+table+" (test_id, test_name) VALUES(%s, %s)", (uuid.uuid1(), 'blah'))
	print 'there are now '+str(num_records('tests')) + ' records!'


def generate_insert_testdata(trials, num_records):
	# print 'time elapsed...'+str(end_time-start_time)
	times = []
	for i in range(0, trials):
		times.append(measure_insert_time(num_records))
	return times


def test_insertions(outfile = 'cql-test.txt'):
	data = generate_insert_testdata(10, 50)
	with open(outfile, 'w') as output:
		for d in data:
			output.write(str(d)+'\n')
		output.close()
# test_insertions()

# print num_records("tests")
# populate_table('tests',100)


# 
# continuous read from table
# 
def continuous_read(keyspace, table):
	print 'started continuous read'
	while True:
		table_string = keyspace + '.' + table
		rows = sess.execute('SELECT * FROM '+table_string)
		print rows[0].test_name
		time.sleep(10)

if __name__ == "__main__":
    args = sys.argv
    print 'Welcome Master Liu'
    command = args[1]
    if command == 'test':
    	continuous_read("poopoo", "tests")
    if command == 'populate':
    	populate_table('tests', 100)
