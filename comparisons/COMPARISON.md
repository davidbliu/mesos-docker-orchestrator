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
	* service discovery: containers can access other labeled services by accessing the load balancer address for that service (see figure below)
![alt tag](kubernetes-fig1.png)
![alt tag](kubernetes.png)



## Other Technologies
* skydock
	* https://github.com/crosbymichael/skydock
	* records container health into DNS server skydns
	* services inside container can query
