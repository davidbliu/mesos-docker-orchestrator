from fabric.api import *
from fabric_ec2 import EC2TagManager
import re
def ec2_instances():
    """ Set up the Fabric env.roledefs, using the correct roles for the given environment
    """
    #
    # CHANGE TAG BASED ON MASTER OR SLAVE
    # TODO command line input for tag
    #
    # tags = EC2TagManager('AKIAJJMIYCLPCYO7RHKA', 'UEXDegNSvhTAnrYns2IGloTb/vwL4jeYzOW27vvq',
    #     regions=['us-west-2'],
    #     common_tags={'Name': 'slave'})
    # return tags.get_instances()
    tags = EC2TagManager('awskey', 'secret',
        regions=['us-west-2'])
    return tags.get_instances()

print 'these are ec2_instances'
print ec2_instances()
for instance in ec2_instances():
	print instance

env.user = 'ubuntu'
env.hosts = ec2_instances()
env.key_filename = [
    '/home/david/helloworld.pem'
]

@parallel
def mesos():
	print("Executing on %(host)s as %(user)s" % env)
	sudo('export DEBIAN_FRONTEND=noninteractive')
	sudo('apt-get -y update')
	sudo('apt-get -y install curl') 
	sudo('apt-get -y install git') 
	sudo('apt-get -y install python-setuptools') 
	sudo('apt-get -y install python-pip') 
	sudo('apt-get -y install python-dev')
	sudo('apt-get -y install python-protobuf')
	sudo('apt-get -y install openjdk-6-jdk')

	#
	# install docker stuff
	#
	sudo('apt-get -y install docker.io')
	sudo('ln -sf /usr/bin/docker.io /usr/local/bin/docker')
	sudo("sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io")

	#
	# install mesos
	#
	sudo('curl -fL http://downloads.mesosphere.io/master/ubuntu/14.04/mesos_0.19.0~ubuntu14.04%2B1_amd64.deb -o /tmp/mesos.deb')
	sudo('dpkg -i /tmp/mesos.deb')
	sudo('mkdir -p /etc/mesos-master')
	sudo('echo in_memory | sudo dd of=/etc/mesos-master/registry')
	sudo('curl -fL http://downloads.mesosphere.io/master/ubuntu/14.04/mesos-0.19.0_rc2-py2.7-linux-x86_64.egg -o /tmp/mesos.egg')
	sudo('easy_install /tmp/mesos.egg')

@parallel
def deimos():
	#
	# configure to use custom deimos
	#
	with settings(warn_only=True):
		sudo('git clone https://github.com/davidbliu/deimos')
	with cd('deimos'):
		run('sudo python setup.py install')

@parallel
def slave():
	#
	# get public ip
	#
	ip = sudo("curl -s 'http://checkip.dyndns.org'") 
	r = re.compile(r'.*\<body>Current IP Address:\s(.*)\</body>.*')
	final_ip = r.match(ip).group(1)
	print str(final_ip)+' that was my final ip'
	#
	# start the slave node
	#
	execution_string = 'mesos-slave --master=zk://54.188.87.91:2181/mesos --containerizer_path=/usr/local/bin/deimos --isolation=external --hostname='+final_ip+' start'
	print execution_string
	sudo("pkill -f 'mesos-slave'")
	sudo(execution_string)

@parallel
def master():
	#
	# setup zookeeper
	#
	sudo('apt-get -y install zookeeperd')
	sudo('echo 1 | sudo dd of=/var/lib/zookeeper/myid')
	#
	# install marathon
	#
	sudo('curl -fL http://downloads.mesosphere.io/marathon/marathon_0.5.0-xcon2_noarch.deb -o /tmp/marathon.deb')
	sudo('dpkg -i /tmp/marathon.deb')
	#
	# start master
	#
	sudo('initctl reload-configuration')
	sudo('start zookeeper || sudo restart zookeeper')
	sudo('start mesos-master || sudo restart mesos-master')
	sudo('start marathon || sudo restart marathon')

@parallel
def cache_images():
	sudo('docker pull 54.189.193.228:5000/flask')
	sudo('docker pull 54.189.193.228:5000/haproxy')
	sudo('docker pull 54.189.193.228:5000/cassandra-processor-s')
	sudo('docker pull davidbliu/kafka_processor_nossh')
	sudo('docker pull davidbliu/zookeeper_processor')
	



@parallel
def slave_main():
	mesos()
	deimos()
	slave()

@parallel
def master_main():
	mesos()
	master()
