import yaml
from marathon import MarathonClient
import sys

#
# read data from config.yaml
#
data = yaml.load(open('config.yaml', 'r'))


def update(service, instances = 1):
	#
	# set up marathon client and launch container
	#
	print 'updating ' + service
	image_string = 'docker:///' + data['services'][service]['image']
	print image_string
	marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))
	app = marathon_client.get_app(service)
	#
	# set up options for cassandra
	#
	options = []
	if service == "cassandra":
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		# ports = []
		# constraints = [["hostname", "UNIQUE"]]
	marathon_client.update_app(
		service,
		app,
		instances = instances,
		container = {
			"image" : image_string, 
			"options" : options
		}
	)
if __name__ == "__main__":
    args = sys.argv
    print 'Welcome Master Liu'
    command = args[1]
    amount = args[2]
    update(command, int(amount))

