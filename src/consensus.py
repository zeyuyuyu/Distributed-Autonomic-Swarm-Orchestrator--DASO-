from typing import Dict, List, Optional
from dataclasses import dataclass
import time
import hashlib

@dataclass
class Vote:
    voter_id: str
    proposal_id: str
    timestamp: float
    weight: float
    signature: str

@dataclass 
class Proposal:
    id: str
    content: Dict
    timestamp: float
    status: str = 'pending'
    votes: List[Vote] = None

class ConsensusEngine:
    def __init__(self, min_quorum: float = 0.67):
        self.proposals: Dict[str, Proposal] = {}
        self.min_quorum = min_quorum
        self.validators: Dict[str, float] = {}
        
    def register_validator(self, validator_id: str, weight: float = 1.0) -> None:
        """Register a validator with an optional voting weight"""
        self.validators[validator_id] = weight
        
    def create_proposal(self, content: Dict) -> str:
        """Create a new proposal and return its ID"""
        proposal_id = hashlib.sha256(
            f"{content}{time.time()}".encode()
        ).hexdigest()
        
        self.proposals[proposal_id] = Proposal(
            id=proposal_id,
            content=content,
            timestamp=time.time(),
            votes=[]
        )
        return proposal_id

    def submit_vote(self, voter_id: str, proposal_id: str, signature: str) -> bool:
        """Submit a vote for a proposal"""
        if voter_id not in self.validators:
            raise ValueError("Invalid validator")
            
        if proposal_id not in self.proposals:
            raise ValueError("Invalid proposal")
            
        proposal = self.proposals[proposal_id]
        
        # Check if validator already voted
        if any(v.voter_id == voter_id for v in proposal.votes):
            return False
            
        vote = Vote(
            voter_id=voter_id,
            proposal_id=proposal_id,
            timestamp=time.time(),
            weight=self.validators[voter_id],
            signature=signature
        )
        
        proposal.votes.append(vote)
        self._check_consensus(proposal_id)
        return True
        
    def _check_consensus(self, proposal_id: str) -> None:
        """Check if consensus has been reached for a proposal"""
        proposal = self.proposals[proposal_id]
        
        total_weight = sum(self.validators.values())
        vote_weight = sum(vote.weight for vote in proposal.votes)
        
        if vote_weight / total_weight >= self.min_quorum:
            proposal.status = 'accepted'
        
    def get_proposal_status(self, proposal_id: str) -> Optional[str]:
        """Get the current status of a proposal"""
        if proposal_id not in self.proposals:
            return None
        return self.proposals[proposal_id].status

    def get_vote_weights(self, proposal_id: str) -> float:
        """Get the total vote weights for a proposal"""
        if proposal_id not in self.proposals:
            return 0.0
        return sum(v.weight for v in self.proposals[proposal_id].votes)

    def validate_signature(self, vote: Vote) -> bool:
        """Validate the cryptographic signature of a vote"""
        # TODO: Implement actual signature validation
        return True