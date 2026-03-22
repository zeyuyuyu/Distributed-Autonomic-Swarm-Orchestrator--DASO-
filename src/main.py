import os
import asyncio
from daso.core.swarm import SwarmManager
from daso.protocols.consensus import ConsensusProtocol

async def main():
    # Initialize the SwarmManager
    swarm_manager = SwarmManager()

    # Start the ConsensusProtocol
    consensus_protocol = ConsensusProtocol(swarm_manager)
    await consensus_protocol.start()

    # Run the main event loop
    await asyncio.Event().wait()

if __name__ == "__main__":
    main()