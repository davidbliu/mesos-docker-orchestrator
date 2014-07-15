## Centurion

## Maestro
![alt tag](maestro.png)
## Mesos
![alt tag](mesos.png)
## Kubernetes
* type of product: container cluster management
	* sent job descriptions to master node, will spawn containers on work nodes
	* jobs described in "pods" (multiple containers per pod) for example web search frontend, datashard, data loader in one pod
	* labels -> tag pods with labels. (like services in maestro)
* scheduler and workers
	* labels for services -> services live behind load balancer (round robin)
	* service discovery: containers can access other labeled services
	* labels act as selectors (label queries to pick a specific service) service containers live behind load balancer
	* other containers can access service through the load balancer (round robin)
	* what about containers talking directly to other containers (not round robin load balancer)? change load balancer. make your own
	* ![alt tag](kubernetes-fig1.png)
![alt tag](kubernetes.png)



## Other Technologies
* skydock
	* https://github.com/crosbymichael/skydock
	* records container health into DNS server skydns
	* services inside container can query
