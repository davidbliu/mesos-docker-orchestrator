import ast
import launcher as launcher
import updater as updater
import replacer as replacer
import uuid 
import yaml

import pickle

from marathon import MarathonClient

data = yaml.load(open('mesos.yaml', 'r'))
etcd_host = data['etcd']['host']
marathon_host = data['marathon']['host']
marathon_port = data['marathon']['port']


class Director:
	def __init__(self, services = {}):
		self.services = services
	def clean(self):
		for key in self.services.keys():
			service = self.services[key]
			print 'cleaning '+str(service)
			service.remove_undeployed_groups()
	def find_labeled_group(self, service_name, labels):
		service = services.get(service_name)
		if not service:
			return None
		return service.labeled_groups.get(str(sorted(labels)))
	def flush_config(self, outfile):
		configuration = {}
		for key in self.services.keys():
			subdict = {}
			for lg_key in self.services[key].labeled_groups.keys():
				config = self.services[key].labeled_groups[lg_key].config
				subdict[lg_key] = config
			configuration[key] = subdict
		with open(outfile, 'w') as output_file:
			output_file.write(yaml.dump(configuration))


class Service:
	#
	# keeps track of labeled groups
	#
	def __init__(self, name):
		self.name = name
		self.labeled_groups = {}

	@property
	def name(self):
		"""Get the name of this entity."""
		return self.name

	def __repr__(self):
		return self.name

	def group_exists(self, labels):
		group = self.find_group(labels)
		if group:
			return True
		return False

	#
	# error if too many, create 1 if already, create new if none
	#
	def create_labeled_group(self, labels, config):
		labels = sorted(labels)
		existing_group = self.labeled_groups.get(str(labels))
		labeled_group = LabeledGroup(self, labels, config)
		if existing_group is None:
			# simple, deploy this onto marathon
			print 'no prior groups found, deploying onto marathon'
			labeled_group.deploy()
		else:
			# there is already one so you must replace it
			print 'replacing existing labeled group'
			print '     existing: '+str(existing_group)
			print '     new: '+str(labeled_group)
			# self.labeled_groups[str(labels)] = labeled_group
			# rolling update
			# replacer.rolling_replace(existing_group.encode_marathon_id, labeled_group)
			replacer.rolling_replace_group(existing_group, labeled_group)
		self.labeled_groups[str(labels)] = labeled_group
		return labeled_group

	def remove_undeployed_groups(self):
		for label in self.labeled_groups.keys():
			# print labels
			group = self.labeled_groups[label]
			if not group.is_deployed:
				print str(group)+' is not deployed. erasing...'
				self.labeled_groups.pop(label, None)
			else:
				print 'this group is deployed '+str(group)
	#
	# idk what this returns
	#
	def get_deployed_labeled_group_ids(self, labels):
		ids = []
		marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
		apps = marathon_client.list_apps()
		for app in apps:
			decoded = decode_marathon_id(app.id)
			if labels == decoded['labels'] and self.name == decoded['service']:
				# return app.id
				ids.append(app.id)
		return ids


class LabeledGroup:

	id_separator = 'D.L'

	def __init__(self, service, labels, config, image = 'default', version = 'asdf'):
		self.service = service
		self.labels = labels
		self.image = image
		self.config = config
		self.version = uuid.uuid4()
		self.deploy_ids = []

	def __repr__(self):
		return str(self.service) + ' labels ' + str(self.labels) + ' version '+str(self.version)

	#
	# returns marathon id for this labeled group
	#
	@property
	def encode_marathon_id(self):
		# start with service
		marathon_id_string = str(self.service)
		label_string = str(self.labels)[:-1][1:].replace("'", "-").replace(",", ".").replace(" ", "")
		version_string = str(self.version)
		marathon_id =  marathon_id_string + LabeledGroup.id_separator + label_string + LabeledGroup.id_separator + version_string + LabeledGroup.id_separator
		# print 'encoded: '+str(marathon_id)
		# print 'decoded: '+str(decode_marathon_id(marathon_id))
		return marathon_id
	#
	# makes api call to marathon to deploy this group
	#
	def deploy(self):
		# deploy_ids = launcher.launch(self.service.name, self.encode_marathon_id, self.config, self.labels)
		# print 'these are my deploy_ids'
		# print deploy_ids
		# self.deploy_ids = deploy_ids
		launcher.launch_group(self)
	#
	# returns true if my id is found in ANY app ids
	# will return true if you are multi-fixed-service and subset of all your apps are up
	#
	@property
	def is_deployed(self):
		marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
		apps = marathon_client.list_apps()
		my_encoded_id = self.encode_marathon_id
		for app in apps:
			if my_encoded_id in app.id:
				return True
		return False

	def clean_deploy_ids(self):
		marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
		apps = marathon_client.list_apps()
		app_ids = [x.id for x in apps]
		for deploy_id in self.deploy_ids:
			if not deploy_id in app_ids:
				print 'deploy_id is not in app id! '+str(deploy_id)
				# remove deploy id

	@property
	def get_marathon_app_id(self):
		marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
		apps = marathon_client.list_apps()
		my_encoded_id = self.encode_marathon_id
		for app in apps:
			if app.id == my_encoded_id:
				return app.id
		return None
	#
	# gets app id for the deployed app. used to replace this group
	#
	# @property
	# def get_deployed_id(self):
	# 	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	# 	apps = marathon_client.list_apps()
	# 	for app in apps:
	# 		decoded = decode_marathon_id(app.id)
	# 		if self.labels == decoded['labels'] and self.service.name == decoded['service']:
	# 			return app.id
	# 	return None

	# returns number of instances running. check marathon for this
	#
	def instances(self):
		return 0
# 
# gets a service and labels from marathon id
#
def decode_marathon_id(marathon_id):
	# split up id
	id_split = marathon_id.split(LabeledGroup.id_separator)
	service_name = str(id_split[0])
	labels = ast.literal_eval('['+id_split[1].replace("-", "'").replace(".", ",")+']')
	version = str(id_split[2])
	return {'service':service_name, 'labels':labels, 'version':version}