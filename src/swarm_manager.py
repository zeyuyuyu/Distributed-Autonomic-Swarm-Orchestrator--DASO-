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
    health_score: float

class SwarmManager:
    def __init__(self, heartbeat_timeout: float = 30.0):
        self.nodes: Dict[str, NodeStatus] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)

    def register_node(self, node_id: str) -> bool:
        with self.lock:
            if node_id in self.nodes:
                return False
            self.nodes[node_id] = NodeStatus(
                last_heartbeat=time.time(),
                load=0.0,
                tasks_running=0,
                health_score=1.0
            )
            self.logger.info(f'Node {node_id} registered successfully')
            return True

    def update_heartbeat(self, node_id: str, load: float, tasks: int) -> None:
        with self.lock:
            if node_id not in self.nodes:
                return
            
            node = self.nodes[node_id]
            node.last_heartbeat = time.time()
            node.load = load
            node.tasks_running = tasks
            
            # Update health score based on load and responsiveness
            time_since_last = time.time() - node.last_heartbeat
            load_factor = 1.0 - (load / 100.0)
            time_factor = 1.0 - (time_since_last / self.heartbeat_timeout)
            node.health_score = (load_factor + time_factor) / 2.0

    def get_best_node(self) -> Optional[str]:
        with self.lock:
            best_node = None
            best_score = -1.0

            current_time = time.time()
            for node_id, status in self.nodes.items():
                # Skip nodes that haven't sent heartbeat recently
                if current_time - status.last_heartbeat > self.heartbeat_timeout:
                    continue

                if status.health_score > best_score:
                    best_score = status.health_score
                    best_node = node_id

            return best_node

    def remove_node(self, node_id: str) -> bool:
        with self.lock:
            if node_id not in self.nodes:
                return False
            del self.nodes[node_id]
            self.logger.info(f'Node {node_id} removed from swarm')
            return True

    def get_unhealthy_nodes(self) -> List[str]:
        with self.lock:
            current_time = time.time()
            return [
                node_id for node_id, status in self.nodes.items()
                if (current_time - status.last_heartbeat > self.heartbeat_timeout) or
                   (status.health_score < 0.3)
            ]

    def get_swarm_stats(self) -> Dict:
        with self.lock:
            total_nodes = len(self.nodes)
            active_nodes = sum(1 for status in self.nodes.values() 
                             if time.time() - status.last_heartbeat <= self.heartbeat_timeout)
            total_tasks = sum(status.tasks_running for status in self.nodes.values())
            avg_load = sum(status.load for status in self.nodes.values()) / total_nodes if total_nodes > 0 else 0

            return {
                'total_nodes': total_nodes,
                'active_nodes': active_nodes,
                'total_tasks': total_tasks,
                'average_load': avg_load,
                'health_scores': {
                    node_id: status.health_score 
                    for node_id, status in self.nodes.items()
                }
            }
