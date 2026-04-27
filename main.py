import discord
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Dictionary to store user levels and XP
user_xp = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    
    # Initialize user data if not exists
    if user_id not in user_xp:
        user_xp[user_id] = {'xp': 0, 'level': 1}
    
    # Add XP for each message
    user_xp[user_id]['xp'] += 10
    
    # Level up logic
    xp = user_xp[user_id]['xp']
    lvl = user_xp[user_id]['level']
    
    if xp >= (lvl * 100):
        user_xp[user_id]['level'] += 1
        await message.channel.send(f'Congrats {message.author.mention}! You leveled up to level {lvl + 1} 🆙')

    # Command to check level
    if message.content == '!level':
        current_lvl = user_xp[user_id]['level']
        current_xp = user_xp[user_id]['xp']
        await message.channel.send(f'Your Level: {current_lvl} | XP: {current_xp}')

token = os.getenv('DISCORD_TOKEN')
if token:
    client.run(token)
else:
    print("Error: No DISCORD_TOKEN found in environment variables.")
