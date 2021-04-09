import ray
import asyncio
import torch
# Import placement group APIs.
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group
)


@ray.remote(num_cpus=5, num_gpus=1)
class AsyncActor():
    def __init__(self):
        pass

    async def rollout(self):
        print("start")
        await asyncio.sleep(1) # Network, I/O task here
        value = torch.randn(8)
        print("end")
        return {
            "value": value,
            "": 0
            }

bundle1 = {"GPU": 1}
bundle2 = {"CPU": 5}

pg = placement_group([bundle1, bundle2], strategy="STRICT_PACK")
# Wait until placement group is created.
ray.get(pg.ready())

# You can also use ray.wait.
ready, unready = ray.wait([pg.ready()], timeout=0)

# You can look at placement group states using this API.
print(placement_group_table(pg))

ray.init(address="auto", _redis_password='123')
actor = AsyncActor.options(max_concurrency=2).remote()

# Get a list of the IP addresses of the nodes that have joined the cluster.
for i in range(10):
    results = ray.get([actor.rollout.remote() for _ in range(5)])
    for j in range(5):
        print(results[j])