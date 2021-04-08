import ray
import time

ray.init(address="auto",  _redis_password='123')

@ray.remote
def f():
    time.sleep(0.01)
    return ray._private.services.get_node_ip_address()

# Get a list of the IP addresses of the nodes that have joined the cluster.
ip_list = set(ray.get([f.remote() for _ in range(1000)]))
print(ip_list)