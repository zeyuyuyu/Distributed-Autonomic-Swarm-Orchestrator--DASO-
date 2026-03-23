import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class SwarmNode:
    id: str
    ip: str
    port: int
    load: float = 0.0
    last_heartbeat: float = 0.0
    status: str = 'healthy'

class SwarmManager:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.health_check_interval = 10  # seconds
        self.heartbeat_timeout = 30  # seconds

    async def register_node(self, node_id: str, ip: str, port: int) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            ip=ip,
            port=port,
            last_heartbeat=time.time()
        )
        print(f'Node {node_id} registered at {ip}:{port}')

    async def heartbeat(self, node_id: str, load: float) -> None:
        """Update node heartbeat and load information"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            self.nodes[node_id].load = load
            self.nodes[node_id].status = 'healthy'

    async def remove_node(self, node_id: str) -> None:
        """Remove a node from the swarm"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f'Node {node_id} removed from swarm')

    def get_optimal_node(self) -> Optional[SwarmNode]:
        """Get the node with lowest load for task assignment"""
        healthy_nodes = [n for n in self.nodes.values() 
                        if n.status == 'healthy']
        if not healthy_nodes:
            return None
        return min(healthy_nodes, key=lambda x: x.load)

    async def health_monitor(self) -> None:
        """Monitor node health and remove dead nodes"""
        while True:
            current_time = time.time()
            dead_nodes = []

            for node_id, node in self.nodes.items():
                time_since_heartbeat = current_time - node.last_heartbeat
                
                if time_since_heartbeat > self.heartbeat_timeout:
                    node.status = 'dead'
                    dead_nodes.append(node_id)
                elif time_since_heartbeat > self.health_check_interval:
                    node.status = 'warning'

            # Remove dead nodes
            for node_id in dead_nodes:
                await self.remove_node(node_id)

            await asyncio.sleep(self.health_check_interval)

    def get_swarm_status(self) -> Dict:
        """Get overall swarm status and statistics"""
        total_nodes = len(self.nodes)
        healthy_nodes = len([n for n in self.nodes.values() 
                           if n.status == 'healthy'])
        warning_nodes = len([n for n in self.nodes.values() 
                           if n.status == 'warning'])
        dead_nodes = len([n for n in self.nodes.values() 
                         if n.status == 'dead'])
        avg_load = sum(n.load for n in self.nodes.values()) / total_nodes \
                   if total_nodes > 0 else 0

        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'warning_nodes': warning_nodes,
            'dead_nodes': dead_nodes,
            'average_load': avg_load
        }

    async def start(self) -> None:
        """Start the swarm manager"""
        print('Starting Swarm Manager...')
        await self.health_monitor()
