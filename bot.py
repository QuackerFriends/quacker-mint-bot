import os
import asyncio
import traceback

import discord
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# =====================
# CONFIG
# =====================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RPC_URL = os.getenv("RPC_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MAX_SUPPLY = int(os.getenv("MAX_SUPPLY"))

CONTRACT = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))

# =====================
# WEB3 SETUP
# =====================
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("RPC not connected")

print("Connected:", w3.is_connected())
print("Latest Block:", w3.eth.block_number)

ZERO = "0x0000000000000000000000000000000000000000"

TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

# =====================
# DISCORD SETUP
# =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_block = w3.eth.block_number


@client.event
async def on_ready():
    global last_block

    print("=" * 40)
    print(f"Logged in as {client.user}")
    print(f"Watching from block {last_block}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found")
        return

    print(f"Found channel: {channel.name}")

    while True:
        try:
            latest = w3.eth.block_number

            if latest > last_block:

                logs = w3.eth.get_logs({
                    "fromBlock": last_block + 1,
                    "toBlock": latest,
                    "address": CONTRACT
                })

                for log in logs:
                    try:
                        topics = log.get("topics", [])

                        if len(topics) < 3:
                            continue

                        if topics[0].hex().lower() != TRANSFER_TOPIC.lower():
                            continue

                        from_addr = "0x" + topics[1].hex()[-40:]
                        to_addr = "0x" + topics[2].hex()[-40:]

                        # mint only
                        if from_addr.lower() != ZERO.lower():
                            continue

                        token_id = int(topics[3].hex(), 16) if len(topics) >= 4 else None

                        embed = discord.Embed(
                            title=f"🦆 Quacker Minted #{token_id}",
                            color=0xFFD54F
                        )

                        embed.add_field(name="To", value=to_addr, inline=False)
                        embed.add_field(name="Supply", value=f"{token_id}/{MAX_SUPPLY}", inline=False)

                        await channel.send(embed=embed)

                        print("Mint detected:", token_id)

                    except Exception:
                        traceback.print_exc()

                last_block = latest

            await asyncio.sleep(3)

        except Exception:
            print("RPC error:")
            traceback.print_exc()
            await asyncio.sleep(5)


client.run(DISCORD_TOKEN)
