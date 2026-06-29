import os
import asyncio

import discord
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RPC_URL = os.getenv("RPC_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

CONTRACT = Web3.to_checksum_address(
    os.getenv("CONTRACT_ADDRESS")
)

w3 = Web3(Web3.HTTPProvider(RPC_URL))

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

ZERO = "0x0000000000000000000000000000000000000000"

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found")
        await client.close()
        return

    TEST_BLOCK = 47935919

    print(f"Testing block {TEST_BLOCK}")

    logs = w3.eth.get_logs({
        "fromBlock": TEST_BLOCK,
        "toBlock": TEST_BLOCK,
        "address": CONTRACT
    })

    print(f"Logs found: {len(logs)}")

    for log in logs:
        print(log)

        topics = log["topics"]

        if len(topics) < 4:
            continue

        if topics[0].hex().lower() != TRANSFER_TOPIC.lower():
            continue

        from_addr = "0x" + topics[1].hex()[-40:]

        if from_addr.lower() != ZERO.lower():
            continue

        token_id = int(topics[3].hex(), 16)

        await channel.send(f"✅ TEST SUCCESS! Mint #{token_id}")

        print("Mint detected:", token_id)

    print("Finished test.")
    await client.close()


client.run(DISCORD_TOKEN)
