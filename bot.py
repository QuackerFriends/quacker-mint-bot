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

CONTRACT = Web3.to_checksum_address(
    os.getenv("CONTRACT_ADDRESS")
)

# =====================
# WEB3
# =====================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("RPC not connected!")

print("Connected:", w3.is_connected())
print("Latest Block:", w3.eth.block_number)

ZERO = "0x0000000000000000000000000000000000000000"

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

# =====================
# DISCORD
# =====================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_block = 47935918


@client.event
async def on_ready():
    global last_block

    print("=" * 40)
    print(f"Logged in as {client.user}")
    print(f"Watching from block {last_block}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Couldn't find Discord channel.")
        return

    print(f"Found channel: {channel.name}")

    while True:

        try:

            latest = w3.eth.block_number

            if latest > last_block:

                for block in range(last_block + 1, latest + 1):

                    print(f"Checking block {block}")

                    try:

                        logs = w3.eth.get_logs({
                            "fromBlock": block,
                            "toBlock": block,
                            "address": CONTRACT,
                            "topics": [TRANSFER_TOPIC]
                        })

                    except Exception as e:
                        print("RPC Error:", e)
                        continue

                    print(f"Found {len(logs)} logs")

                    for log in logs:

                        try:

                            topics = log["topics"]

                            if len(topics) < 4:
                                continue

                            from_addr = "0x" + topics[1].hex()[-40:]
                            to_addr = "0x" + topics[2].hex()[-40:]

                            if from_addr.lower() != ZERO.lower():
                                continue

                            token_id = int(topics[3].hex(), 16)

                            print(f"Mint detected #{token_id}")

                            embed = discord.Embed(
                                title=f"🦆 Quacker #{token_id} Minted!",
                                description="A new Quacker Friend has joined the flock!",
                                color=0xFFD54F
                            )

                            embed.add_field(
                                name="Wallet",
                                value=f"`{to_addr}`",
                                inline=False
                            )

                            embed.add_field(
                                name="Supply",
                                value=f"{token_id}/{MAX_SUPPLY}",
                                inline=False
                            )

                            embed.add_field(
                                name="OpenSea",
                                value=f"https://opensea.io/assets/base/{CONTRACT}/{token_id}",
                                inline=False
                            )

                            embed.add_field(
                                name="BaseScan",
                                value=f"https://basescan.org/token/{CONTRACT}?a={token_id}",
                                inline=False
                            )

                            await channel.send(embed=embed)

                        except Exception:
                            traceback.print_exc()

                last_block = latest

            await asyncio.sleep(2)

        except Exception:
            traceback.print_exc()
            await asyncio.sleep(5)


print("Starting Discord bot...")
client.run(DISCORD_TOKEN)
