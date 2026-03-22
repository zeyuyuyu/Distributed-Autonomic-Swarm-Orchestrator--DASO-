import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
import queue

@dataclass
class SwarmNode:
    id: str
    capacity: int
    current_load: int
    status: str
    last_heartbeat: float

class SwarmManager:
    def __init__(self, min_nodes: int = 3, max_nodes: int = 10):
        self.nodes: Dict[str, SwarmNode] = {}
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.load_threshold = 0.8  # 80% capacity threshold
        self.scaling_lock = threading.Lock()
        self.task_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)
        
    def register_node(self, node_id: str, capacity: int) -> bool:
        if node_id not in self.nodes:
            self.nodes[node_id] = SwarmNode(
                id=node_id,
                capacity=capacity,
                current_load=0,
                status='active',
                last_heartbeat=time.time()
            )
            self.logger.info(f'Node {node_id} registered with capacity {capacity}')
            return True
        return False

    def deregister_node(self, node_id: str) -> bool:
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.logger.info(f'Node {node_id} deregistered')
            return True
        return False

    def update_node_load(self, node_id: str, load: int) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].current_load = load
            self.nodes[node_id].last_heartbeat = time.time()
            self._check_scaling_needs()

    def get_available_node(self) -> Optional[str]:
        available_nodes = [
            node for node in self.nodes.values()
            if node.status == 'active' and 
            node.current_load < (node.capacity * self.load_threshold)
        ]
        
        if available_nodes:
            return min(available_nodes, 
                      key=lambda x: x.current_load / x.capacity).id
        return None

    def _check_scaling_needs(self) -> None:
        with self.scaling_lock:
            total_capacity = sum(node.capacity for node in self.nodes.values())
            total_load = sum(node.current_load for node in self.nodes.values())
            
            if total_capacity == 0:
                return

            utilization = total_load / total_capacity
            
            if utilization > self.load_threshold and len(self.nodes) < self.max_nodes:
                self._scale_up()
            elif utilization < (self.load_threshold * 0.5) and len(self.nodes) > self.min_nodes:
                self._scale_down()

    def _scale_up(self) -> None:
        self.logger.info('Initiating scale up operation')
        # Implementation would integrate with cloud provider API
        # to provision new nodes

    def _scale_down(self) -> None:
        self.logger.info('Initiating scale down operation')
        if len(self.nodes) <= self.min_nodes:
            return
            
        # Find least utilized node
        least_utilized = min(
            self.nodes.values(),
            key=lambda x: x.current_load / x.capacity
        )
        
        # Only remove if load can be redistributed
        if least_utilized.current_load == 0:
            self.deregister_node(least_utilized.id)

    def health_check(self) -> Dict[str, List[str]]:
        unhealthy_nodes = []
        healthy_nodes = []
        current_time = time.time()
        
        for node_id, node in self.nodes.items():
            if current_time - node.last_heartbeat > 30:  # 30 second timeout
                node.status = 'inactive'
                unhealthy_nodes.append(node_id)
            else:
                healthy_nodes.append(node_id)
                
        return {
            'healthy': healthy_nodes,
            'unhealthy': unhealthy_nodes
        }

    def get_swarm_metrics(self) -> Dict:
        total_capacity = sum(node.capacity for node in self.nodes.values())
        total_load = sum(node.current_load for node in self.nodes.values())
        
        return {
            'node_count': len(self.nodes),
            'total_capacity': total_capacity,
            'total_load': total_load,
            'utilization': total_load / total_capacity if total_capacity > 0 else 0
        }