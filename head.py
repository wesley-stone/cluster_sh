import ray
import asyncio
import torch
import time


@ray.remote(num_cpus=5, num_gpus=1)
class AsyncActor():
    def __init__(self):
        pass

    async def rollout(self):
        print("start")
        await asyncio.sleep(1) # Network, I/O task here
        value = torch.randn(8)
        return value
        print("end")

"""
def f():
    time.sleep(0.01)
    return ray._private.services.get_node_ip_address(), ray._private.service.get_node_port
"""

ray.init(address="auto",  _redis_password='123')
actor = AsyncActor.options(max_concurrency=2).remote()

# Get a list of the IP addresses of the nodes that have joined the cluster.
for i in range(10):
    results = ray.get([actor.rollout.remote() for _ in range(5)])
    for j in range(5):
        print(results[j])