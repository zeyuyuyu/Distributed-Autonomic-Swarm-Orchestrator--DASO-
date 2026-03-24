#!/usr/bin/env python3

from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum
import hashlib
import time

class MessageType(Enum):
    PRE_PREPARE = 'pre-prepare'
    PREPARE = 'prepare'
    COMMIT = 'commit'
    REPLY = 'reply'

@dataclass
class ConsensusMessage:
    msg_type: MessageType
    view_num: int
    seq_num: int
    digest: str
    node_id: str
    timestamp: float
    signature: str = ''

class PBFTConsensus:
    def __init__(self, node_id: str, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.f = (total_nodes - 1) // 3  # Max Byzantine nodes tolerated
        self.view_num = 0
        self.seq_num = 0
        self.prepared_msgs: Dict[int, Set[ConsensusMessage]] = {}
        self.committed_msgs: Dict[int, Set[ConsensusMessage]] = {}
        
    def _calculate_digest(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _verify_signature(self, msg: ConsensusMessage) -> bool:
        # TODO: Implement actual signature verification
        return True

    def start_consensus(self, data: str) -> bool:
        """Initiates consensus process for given data"""
        digest = self._calculate_digest(data)
        
        # Create pre-prepare message
        pre_prepare = ConsensusMessage(
            msg_type=MessageType.PRE_PREPARE,
            view_num=self.view_num,
            seq_num=self.seq_num,
            digest=digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        
        return self.handle_pre_prepare(pre_prepare)

    def handle_pre_prepare(self, msg: ConsensusMessage) -> bool:
        if not self._verify_signature(msg):
            return False
            
        if msg.seq_num not in self.prepared_msgs:
            self.prepared_msgs[msg.seq_num] = set()
            
        self.prepared_msgs[msg.seq_num].add(msg)
        
        # Send prepare message
        prepare = ConsensusMessage(
            msg_type=MessageType.PREPARE,
            view_num=msg.view_num,
            seq_num=msg.seq_num,
            digest=msg.digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        
        return self.handle_prepare(prepare)

    def handle_prepare(self, msg: ConsensusMessage) -> bool:
        if not self._verify_signature(msg):
            return False
            
        if msg.seq_num not in self.prepared_msgs:
            self.prepared_msgs[msg.seq_num] = set()
            
        self.prepared_msgs[msg.seq_num].add(msg)
        
        # Check if we have 2f+1 prepare messages
        prepares = len([m for m in self.prepared_msgs[msg.seq_num] 
                       if m.msg_type == MessageType.PREPARE])
                       
        if prepares >= 2 * self.f + 1:
            # Send commit message
            commit = ConsensusMessage(
                msg_type=MessageType.COMMIT,
                view_num=msg.view_num,
                seq_num=msg.seq_num,
                digest=msg.digest,
                node_id=self.node_id,
                timestamp=time.time()
            )
            return self.handle_commit(commit)
            
        return True

    def handle_commit(self, msg: ConsensusMessage) -> bool:
        if not self._verify_signature(msg):
            return False
            
        if msg.seq_num not in self.committed_msgs:
            self.committed_msgs[msg.seq_num] = set()
            
        self.committed_msgs[msg.seq_num].add(msg)
        
        # Check if we have 2f+1 commit messages
        commits = len([m for m in self.committed_msgs[msg.seq_num]
                      if m.msg_type == MessageType.COMMIT])
                      
        if commits >= 2 * self.f + 1:
            # Consensus achieved!
            self.seq_num += 1
            return True
            
        return True

    def get_committed_messages(self) -> List[ConsensusMessage]:
        """Returns list of all committed messages in order"""
        committed = []
        for seq in sorted(self.committed_msgs.keys()):
            commits = [m for m in self.committed_msgs[seq]
                      if m.msg_type == MessageType.COMMIT]
            if len(commits) >= 2 * self.f + 1:
                committed.append(commits[0])
        return committed