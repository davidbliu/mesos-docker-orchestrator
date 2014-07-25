import os

#
# pluggable method
# 
def service_change(service, delta):
	print 'service has changed: '+str(service)[1:]
	if str(service)[1:] == os.environ.get('PROXY_SERVICE'):
		print 're-rendering old template'
		os.system('python -u render_template.py')
		os.system('haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid)')