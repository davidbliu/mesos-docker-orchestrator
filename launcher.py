import yaml
from marathon import MarathonClient
import sys

#
# read data from config.yaml
#
data = yaml.load(open('config.yaml', 'r'))


def launch(service):
	print 'launching ' + service
	service_dict = data['services'][service]
	image = service_dict['image']
	try:
		ports = service_dict['ports'].values()
	except:
		ports = []
	instances = 1 if not service_dict.get('instances') else service_dict.get('instances')
	cpus = 0.3 if not service_dict.get('cpus') else service_dict.get('cpus')
	mem = 512 if not service_dict.get('mem') else service_dict.get('mem')
	#
	# env variables
	#
	env = {}
	env['ETCD_HOST_ADDRESS'] = data['etcd']['host']
	env['SERVICE_NAME'] = service
	# set up custom environment variables
	custom_env = service_dict.get('environment')
	if custom_env:
		for key in custom_env.keys():
			env[key] = custom_env[key]
	options = []
	constraints = []

	#
	# TODO add support for this
	#
	if service == "cassandra":
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		ports = []
		constraints = [["hostname", "UNIQUE"]]
	#
	# set up marathon client and launch container
	#
	marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))
	marathon_client.create_app(
		container = {
			"image" : str("docker:///"+image), 
			"options" : options
		},
		id = service,
		instances = str(instances),
		constraints = constraints,
		cpus = str(cpus),
		mem = str(mem),
		env = env,
		ports = ports #should be listed in order they appear in dockerfile
		
	)

if __name__ == "__main__":
    args = sys.argv
    print 'Welcome Master Liu'
    command = args[1]
    # try:
    launch(command)
    # except Exception as failure:
    	# print 'so sorry could not launch ' + command
    	# print failure