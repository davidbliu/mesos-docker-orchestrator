## guestutils functions

guestutils have the same method signatures as maestro's guestutils
* label queries
  * get_node_list can take an optional parameter labels=[label1,label2...]
  * will find nodes whose labels are a superset or specified list of labels
  * same output format as get_nodes_list without labels parameter

## recieving updates

containers can watch keys in etcd for chances with watcher.py. to watch keys, set WATCHES environment variable.
* for example to watch cassandra and ingestor WATCHES=cassandra,ingestor
* pluggable methods in watch_methods.py
