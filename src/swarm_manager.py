# src/swarm_manager.py
import random
import time
from typing import List

from .consensus import reach_consensus

class SwarmManager:
    def __init__(self, num_nodes: int, heartbeat_interval: float = 5.0):
        self.num_nodes = num_nodes
        self.heartbeat_interval = heartbeat_interval
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.healthy_nodes = self.nodes.copy()

    def start(self):
        while True:
            self.monitor_nodes()
            self.heal_swarm()
            time.sleep(self.heartbeat_interval)

    def monitor_nodes(self):
        for node in self.nodes:
            if node.is_healthy():
                continue
            if node.check_health():
                self.healthy_nodes.append(node)
            else:
                self.healthy_nodes.remove(node)

    def heal_swarm(self):
        if len(self.healthy_nodes) < self.num_nodes:
            print(f'Swarm health is degraded. Healthy nodes: {len(self.healthy_nodes)}/{self.num_nodes}')
            self.redistribute_workload()
            self.spawn_new_nodes()

    def redistribute_workload(self):
        # Reach consensus on workload distribution among healthy nodes
        workload_distribution = reach_consensus(self.healthy_nodes)
        for node, tasks in workload_distribution.items():
            node.assign_tasks(tasks)

    def spawn_new_nodes(self):
        # Spawn new nodes to replace unhealthy ones
        new_nodes = [Node(len(self.nodes) + i) for i in range(self.num_nodes - len(self.healthy_nodes))]
        self.nodes.extend(new_nodes)
        self.healthy_nodes.extend(new_nodes)

class Node:
    def __init__(self, id: int):
        self.id = id
        self.tasks = []
        self.health = random.randint(0, 100)

    def is_healthy(self) -> bool:
        return self.health >= 50

    def check_health(self) -> bool:
        # Simulate node health check
        self.health = random.randint(0, 100)
        return self.is_healthy()

    def assign_tasks(self, tasks: List[str]):
        self.tasks = tasks
