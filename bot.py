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
    raise Exception("Couldn't connect to RPC")

print("Connected:", w3.is_connected())
print("Latest Block:", w3.eth.block_number)

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

ZERO = "0x0000000000000000000000000000000000000000"

# TEST: replay mint #304
last_block = 47935918

# =====================
# DISCORD
# =====================

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    global last_block

    print("=" * 40)
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found!")
        return

    print(f"Found channel: {channel.name}")

    latest =  47977670 

    logs = w3.eth.get_logs({
        "fromBlock": latest,
        "toBlock": latest,
        "address": CONTRACT,
        "topics": [TRANSFER_TOPIC]
    })

    print(f"Found {len(logs)} transfer logs")

    for log in logs:

        topics = log["topics"]

        if len(topics) < 4:
            continue

        from_addr = "0x" + topics[1].hex()[-40:]
        to_addr = "0x" + topics[2].hex()[-40:]

        if from_addr.lower() != ZERO.lower():
            continue

        token_id = int(topics[3].hex(), 16)

        embed = discord.Embed(
            title=f"🦆 Quacker Friend #{token_id} Minted!",
            description="A new Quacker Friend has joined the flock! 🎉",
            color=0xFFD54F,
            url=f"https://opensea.io/assets/base/{CONTRACT}/{token_id}"
        )

        embed.set_image(
            url=f"https://box.quackerfriends.xyz/images/{token_id}.png"
        )

        embed.add_field(
            name="👤 Owner",
            value=f"`{to_addr}`",
            inline=False
        )

        embed.add_field(
            name="📈 Supply",
            value=f"{token_id}/{MAX_SUPPLY}",
            inline=True
        )

        embed.add_field(
            name="🌊 OpenSea",
            value=f"https://opensea.io/assets/base/{CONTRACT}/{token_id}",
            inline=False
        )

        embed.set_footer(
            text="Quacker Friends • Base"
        )

        await channel.send(embed=embed)

        print(f"Sent test embed for #{token_id}")

    print("✅ Test complete.")
    await client.close()


print("Starting Discord bot...")
client.run(DISCORD_TOKEN)
