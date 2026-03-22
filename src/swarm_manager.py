import asyncio
from typing import Dict, List, Optional
import time
import logging

class SwarmManager:
    def __init__(self):
        self.nodes: Dict[str, 'NodeStatus'] = {}
        self.health_check_interval = 30  # seconds
        self.load_threshold = 0.8  # 80% capacity
        self.logger = logging.getLogger(__name__)

    class NodeStatus:
        def __init__(self, node_id: str, capacity: int):
            self.node_id = node_id
            self.capacity = capacity
            self.current_load = 0
            self.last_heartbeat = time.time()
            self.tasks: List[str] = []
            self.status = 'healthy'

    async def register_node(self, node_id: str, capacity: int) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = self.NodeStatus(node_id, capacity)
        self.logger.info(f'Node {node_id} registered with capacity {capacity}')

    async def heartbeat(self, node_id: str, current_load: int) -> None:
        """Update node heartbeat and load information"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.last_heartbeat = time.time()
            node.current_load = current_load

    async def monitor_health(self) -> None:
        """Monitor node health and handle failures"""
        while True:
            current_time = time.time()
            dead_nodes = []

            for node_id, node in self.nodes.items():
                if current_time - node.last_heartbeat > self.health_check_interval:
                    dead_nodes.append(node_id)
                    node.status = 'unreachable'
                    self.logger.warning(f'Node {node_id} is unreachable')

            # Handle dead nodes
            for node_id in dead_nodes:
                await self.rebalance_tasks(node_id)

            await asyncio.sleep(self.health_check_interval)

    async def rebalance_tasks(self, failed_node_id: str) -> None:
        """Redistribute tasks from failed node to healthy nodes"""
        if failed_node_id not in self.nodes:
            return

        failed_node = self.nodes[failed_node_id]
        tasks_to_redistribute = failed_node.tasks.copy()

        available_nodes = [
            node for node_id, node in self.nodes.items()
            if node.status == 'healthy' and 
            node.current_load / node.capacity < self.load_threshold
        ]

        if not available_nodes:
            self.logger.error('No available nodes for task redistribution')
            return

        # Simple round-robin redistribution
        for i, task_id in enumerate(tasks_to_redistribute):
            target_node = available_nodes[i % len(available_nodes)]
            target_node.tasks.append(task_id)
            self.logger.info(
                f'Task {task_id} redistributed from {failed_node_id} '
                f'to {target_node.node_id}'
            )

    async def get_node_status(self, node_id: str) -> Optional[dict]:
        """Get detailed status of a specific node"""
        if node_id not in self.nodes:
            return None

        node = self.nodes[node_id]
        return {
            'node_id': node.node_id,
            'capacity': node.capacity,
            'current_load': node.current_load,
            'load_percentage': (node.current_load / node.capacity) * 100,
            'status': node.status,
            'task_count': len(node.tasks),
            'last_heartbeat': node.last_heartbeat
        }

    async def get_swarm_health(self) -> dict:
        """Get overall swarm health metrics"""
        total_nodes = len(self.nodes)
        healthy_nodes = sum(1 for node in self.nodes.values() 
                           if node.status == 'healthy')
        total_capacity = sum(node.capacity for node in self.nodes.values())
        total_load = sum(node.current_load for node in self.nodes.values())

        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'total_capacity': total_capacity,
            'total_load': total_load,
            'swarm_load_percentage': 
                (total_load / total_capacity * 100) if total_capacity > 0 else 0
        }
