
import os
from web3 import Web3

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Blockchain
RPC_URL = os.getenv("RPC_URL")

CONTRACT_ADDRESS = Web3.to_checksum_address(
    os.getenv("CONTRACT_ADDRESS")
)

MAX_SUPPLY = int(os.getenv("MAX_SUPPLY", "3000"))

# Discord Channel
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
