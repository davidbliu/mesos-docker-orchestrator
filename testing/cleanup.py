import yaml
from marathon import MarathonClient
import sys
import argparse
import requests
import json
#
# unecessary extra tasks to make up for my shortcomings sorry
#

data = yaml.load(open('config.yaml', 'r'))
marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))


#
# remove tasks that got stuck (staging i think)
def clean_tasks():
	tasks = marathon_client.list_tasks()
	for task in tasks:
		print 'task: '+str(task.app_id)
		print '\t'+str(task.started_at)+',  '+str(task.staged_at)

if __name__ == "__main__":
    print 'Welcome Master Liu'
    clean_tasks()