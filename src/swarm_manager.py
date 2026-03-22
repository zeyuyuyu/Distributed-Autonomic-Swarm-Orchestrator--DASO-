import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Lock

@dataclass
class NodeStatus:
    last_heartbeat: float
    load: float
    tasks_running: int
    healthy: bool

class SwarmManager:
    def __init__(self, heartbeat_timeout: float = 30.0):
        self.nodes: Dict[str, NodeStatus] = {}
        self.node_lock = Lock()
        self.heartbeat_timeout = heartbeat_timeout
        self.logger = logging.getLogger(__name__)

    def register_node(self, node_id: str) -> bool:
        with self.node_lock:
            if node_id in self.nodes:
                return False
            self.nodes[node_id] = NodeStatus(
                last_heartbeat=time.time(),
                load=0.0,
                tasks_running=0,
                healthy=True
            )
            self.logger.info(f'Node {node_id} registered successfully')
            return True

    def update_heartbeat(self, node_id: str, load: float, tasks: int) -> None:
        with self.node_lock:
            if node_id not in self.nodes:
                self.logger.warning(f'Received heartbeat from unknown node {node_id}')
                return
            
            self.nodes[node_id] = NodeStatus(
                last_heartbeat=time.time(),
                load=load,
                tasks_running=tasks,
                healthy=True
            )

    def check_node_health(self) -> List[str]:
        unhealthy_nodes = []
        current_time = time.time()
        
        with self.node_lock:
            for node_id, status in self.nodes.items():
                if current_time - status.last_heartbeat > self.heartbeat_timeout:
                    status.healthy = False
                    unhealthy_nodes.append(node_id)
                    self.logger.warning(f'Node {node_id} appears to be unhealthy')
        
        return unhealthy_nodes

    def get_best_node(self) -> Optional[str]:
        with self.node_lock:
            available_nodes = [
                (node_id, status) for node_id, status in self.nodes.items()
                if status.healthy and status.load < 0.8  # 80% load threshold
            ]
            
            if not available_nodes:
                return None
            
            # Sort by load and number of tasks
            available_nodes.sort(key=lambda x: (x[1].load, x[1].tasks_running))
            return available_nodes[0][0]

    def remove_node(self, node_id: str) -> bool:
        with self.node_lock:
            if node_id not in self.nodes:
                return False
            del self.nodes[node_id]
            self.logger.info(f'Node {node_id} removed from swarm')
            return True

    def get_swarm_stats(self) -> Dict:
        with self.node_lock:
            total_nodes = len(self.nodes)
            healthy_nodes = sum(1 for status in self.nodes.values() if status.healthy)
            total_tasks = sum(status.tasks_running for status in self.nodes.values())
            avg_load = sum(status.load for status in self.nodes.values()) / total_nodes if total_nodes > 0 else 0

            return {
                'total_nodes': total_nodes,
                'healthy_nodes': healthy_nodes,
                'total_tasks': total_tasks,
                'average_load': avg_load
            }
