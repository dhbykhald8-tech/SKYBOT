import discord
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

token = os.getenv('DISCORD_TOKEN')

if token:
    client.run(token)
else:
    print("خطأ: لم يتم العثور على التوكن في إعدادات Railway!")
