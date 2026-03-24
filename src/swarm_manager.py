import random
import time

class SwarmManager:
    def __init__(self, swarm_size, heartbeat_interval):
        self.swarm_size = swarm_size
        self.heartbeat_interval = heartbeat_interval
        self.swarm = []
        self.last_heartbeat = {}

    def add_node(self, node):
        self.swarm.append(node)
        self.last_heartbeat[node] = time.time()

    def remove_node(self, node):
        self.swarm.remove(node)
        del self.last_heartbeat[node]

    def monitor_swarm(self):
        while True:
            for node in self.swarm:
                if time.time() - self.last_heartbeat[node] > self.heartbeat_interval:
                    self.remove_node(node)
                    self.add_node(self._spawn_new_node())
                    print(f'Detected failed node {node}, respawned new node.')
            time.sleep(self.heartbeat_interval)

    def _spawn_new_node(self):
        # Implement logic to spawn a new node, e.g., via cloud provisioning
        new_node = f'node_{random.randint(1, 1000)}'
        return new_node
