import yaml
import requests
import json
#
# send a post request with config_test.yaml as the config_data attribute
#
config_data = yaml.load(open('config_test.yaml', 'r'))
# print config_datad

payload = {'config_data': json.dumps(config_data)}
r = requests.post("http://localhost:5000/reconfigure", data={'config_data':json.dumps(config_data)})