from time import sleep
import ray
import asyncio
import torch
import random
import pprint
# Import placement group APIs.
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group
)

bundle1 = {"GPU": 0.25, "CPU": 1}
tot_cpus = 15
tot_gpus = 3
ray.init(num_gpus=tot_gpus, num_cpus=tot_cpus, address="auto", _redis_password='123')

@ray.remote(num_cpus=bundle1['CPU'], num_gpus=bundle1['GPU'])
class AsyncActor():
    def __init__(self, actor_id):
        self.id = actor_id

    async def rollout(self, parameters, batch_size=4):
        sleep_sec = random.randint(0, 10)
        await asyncio.sleep(sleep_sec) # Network, I/O task here
        value = torch.randn(batch_size, 1)
        input = torch.randn(batch_size, 2)
        return {
            "input": input,
            "value": value,
            "actor_id": self.id,
        }

pg_cnt = min(int(tot_gpus/bundle1['GPU']), int(tot_cpus/bundle1['CPU']))

pgs = [placement_group(bundle1, strategy="STRICT_PACK") for _ in range(pg_cnt)]
# Wait until placement group is created.
ray.get([pg.ready() for pg in pgs])
for pg in pgs:
    print(placement_group_table(pg))

# You can look at placement group states using this API.
print(placement_group_table(pg))

actors = [AsyncActor.options(placement_group=pg).remote() for pg in pgs]

# Get a list of the IP addresses of the nodes that have joined the cluster.
epoch = 5
batch_size = 4
bunch_size = 2
parameters = {"conv1x1": 1}
data_ids = [actor.rollout.remote(parameters, batch_size) for actor in actors]
for i in range(epoch):
    pprint(f"collection start - {epoch}")
    done_ids = [ray.wait(data_ids) for _ in range(bunch_size)]
    batch_data = [ray.get(done_id) for done_id in done_ids]
    pprint(f"collection end - {epoch}")
    for bd in batch_data:
        print(bd['input'])
    pprint(f"training start - {epoch}")
    # pushing to the replay buffer
    # training...
    sleep(3)
    pprint(f"training end - {epoch}")
    data_ids.extend([actors[bd['actor_id']].rollout.remote(parameters, batch_size) for bd in batch_data])
