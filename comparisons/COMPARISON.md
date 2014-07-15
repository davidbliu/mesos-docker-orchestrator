## Maestro
<img src='maestro.png' height=500></img>

## Mesos
<img src='mesos.png' height=500></img>

## Kubernetes
* __type of product: container cluster management__
	* declarative syntax for setting up containers
	* decouple applications from machines. dont care what machine application ends up on
	* sent job descriptions to master node, will spawn containers on work nodes
	* jobs described in "pods" (multiple containers per pod) for example web search frontend, datashard, data loader in one pod
	* labels -> tag pods with labels. (like services in maestro)
* __kubernetes elements__
	* pod. atomic unit for application. bunch of containers that work well together. could be 1 container, 5 containers. etc
	* replica controller : how many of your pods to keep up and running
	* like instances for your application in marathon
	* label: can make label queries (like service name for maestro, but can have many labels). like jquery selector
	* service:
	* labels for services -> services live behind load balancer (round robin)
* __service discovery: containers can access other labeled services__
	* labels act as selectors (label queries to pick a specific service) service containers live behind load balancer
	* other containers can access service through the load balancer (round robin)
	* ex: getenv('REDISSLAVE_SERVICE_PORT'), getenv('REDISMASTER_SERVICE_PORT'), etc...
	* ex from here: https://github.com/GoogleCloudPlatform/kubernetes/blob/master/examples/guestbook/README.md
	* what about containers talking directly to other containers (not round robin load balancer)? change load balancer. make your own
	* 43:43   https://www.youtube.com/watch?v=tsk0pWf4ipw
	* <img src='kubernetes-fig1.png' height=300></img>
* __benefits of using kubernetes?__
	* keep containers running
	* select out pods without having a sea of pods (dont have to worry about host machines)
	* benefits over marathon on mesos? idk

<img src='kubernetes.png' height=500></img>

## Helios
* job:  job name, a job version, the name of your Docker image, any environment variables you wish to pass to the running container, ports you wish to expose, and the command to run inside the container, if any.
* master: Helios masters are the servers that the Helios CLI and other tools talk to. They coordinate the deployment of your Docker containers onto Helios agents.
* agents: Helios agents, sometimes known as Helios hosts, are the machines on which the images you built eventually run. The masters tell agents to download jobs and run them.
* examples provided on their github page
	* basic deploy/undeploy
	* no service discovery example
	* not built in


## Other Technologies
* skydock
* fleet
* 
