
import os
import asyncio

import discord
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RPC_URL = os.getenv("RPC_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MAX_SUPPLY = int(os.getenv("MAX_SUPPLY"))

CONTRACT = Web3.to_checksum_address(
    os.getenv("CONTRACT_ADDRESS")
)

w3 = Web3(Web3.HTTPProvider(RPC_URL))

ZERO = "0x0000000000000000000000000000000000000000"

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

intents = discord.Intents.default()

client = discord.Client(intents=intents)

last_block = w3.eth.block_number
