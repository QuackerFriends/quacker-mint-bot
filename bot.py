
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
@client.event
async def on_ready():
    global last_block

    print("=" * 40)
    print(f"✅ Logged in as {client.user}")
    print(f"📦 Starting from block {last_block}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Couldn't find Discord channel!")
        return

    print(f"✅ Found channel: #{channel.name}")

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

                    # Ignore non-Transfer events
                    if log["topics"][0].hex().lower() != TRANSFER_TOPIC.lower():
                        continue

                    from_addr = "0x" + log["topics"][1].hex()[-40:]
                    to_addr = "0x" + log["topics"][2].hex()[-40:]

                    # Only announce mints
                    if from_addr.lower() != ZERO.lower():
                        continue

                    token_id = int(log["topics"][3].hex(), 16)

                    embed = discord.Embed(
                        title=f"🦆 Quacker #{token_id} Minted!",
                        description="A new Quacker Friend has joined the flock!",
                        color=0xFFD54F
                    )

                    embed.add_field(
                        name="👤 Wallet",
                        value=f"`{to_addr}`",
                        inline=False
                    )

                    embed.add_field(
                        name="📈 Supply",
                        value=f"{token_id}/{MAX_SUPPLY}",
                        inline=False
                    )

                    embed.add_field(
                        name="🌊 OpenSea",
                        value=f"https://opensea.io/assets/base/{CONTRACT}/{token_id}",
                        inline=False
                    )

                    embed.add_field(
                        name="🔎 BaseScan",
                        value=f"https://basescan.org/token/{CONTRACT}?a={token_id}",
                        inline=False
                    )

                    await channel.send(embed=embed)

                    print(f"✅ Mint #{token_id}")

                last_block = latest

        except Exception as e:
            print("RPC Error:", e)

        await asyncio.sleep(2)

print("Starting Discord bot...")
client.run(DISCORD_TOKEN)
