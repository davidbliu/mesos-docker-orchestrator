import requests
import time
import us
import random
import argparse

import Queue
import threading
import urllib2
import datetime
import thread
#
# start sending traffic 
#

address = 'localhost'
amount = 100000

states = us.states
state_names = []
for state in states.STATES:
	state_names.append(state.name)
print state_names

global_good = 1
global_bad = 1

class ThreadClass(threading.Thread):
  def run(self):
    print 'sending traffic to '+str(address)
    result = blast_data(address, amount)
    # print result
    # print 'was the result of this thread'
    self.result = result

    with open('results.txt', 'a') as result_file:
    	result_file.write(str(result)+'\n')
    # global_good+=result[0]
    # global_bad+=result[1]
    
def blast_data(address, amount):
	ind = 0
	good = 1
	bad = 1
	while ind < amount:
		index = random.randint(0,49)
		ingestor_address = 'http://'+address
		r = requests.post(ingestor_address, data={'data': state_names[index]})
		# print r
		# print type(r)
		if r.ok:
			good += 1
		else:
			bad += 1
		rate = float(float(good)/float(bad+good))
		print 'good: '+str(good)+', bad: '+str(bad)+', rate: '+str(rate)
		time.sleep(.5)
		ind+=1
	return (good, bad, rate)

def dummy(asdf):
	try:
		print 'hi'
	except:
		print 'bad'
def threaded_blast(address):
	print 'starting this'
	for index in range(0,2):
		t=ThreadClass()
		t.daemon=True
		t.start()
		# print 'thread finished and the result was '+str(t.result)
		# t.result = 

if __name__ == "__main__":
    print 'Welcome Master Liu'
    parser = argparse.ArgumentParser(description='Docker Orchestrator Scheduler')
    parser.add_argument('-addr', '--address', required=True, help='procedure')
    args = parser.parse_args()
    global address
    address = args.address
    threaded_blast(str(address))
    while True:
    	time.sleep(60)
    	print str(float(global_good/global_bad))