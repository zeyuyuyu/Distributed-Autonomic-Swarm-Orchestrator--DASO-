import random
import time

class SwarmManager:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.node_loads = [0] * num_nodes
        self.task_queue = []

    def add_task(self, task):
        self.task_queue.append(task)
        self.balance_load()

    def balance_load(self):
        while self.task_queue:
            task = self.task_queue.pop(0)
            least_loaded_node = min(range(self.num_nodes), key=lambda i: self.node_loads[i])
            self.node_loads[least_loaded_node] += task.duration
            print(f'Assigned task to node {least_loaded_node}, new load: {self.node_loads[least_loaded_node]}')

    def simulate_task_execution(self):
        while True:
            for i in range(self.num_nodes):
                if self.node_loads[i] > 0:
                    self.node_loads[i] -= 1
                    print(f'Node {i} load reduced by 1, new load: {self.node_loads[i]}')
            time.sleep(1)
            self.balance_load()

class Task:
    def __init__(self, duration):
        self.duration = duration

# Example usage
swarm_manager = SwarmManager(num_nodes=5)
swarm_manager.add_task(Task(duration=5))
swarm_manager.add_task(Task(duration=3))
swarm_manager.add_task(Task(duration=7))
swarm_manager.simulate_task_execution()