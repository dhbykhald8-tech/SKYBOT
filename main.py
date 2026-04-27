import discord
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

user_xp = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    
    if user_id not in user_xp:
        user_xp[user_id] = {'xp': 0, 'level': 1}
    
    user_xp[user_id]['xp'] += 10
    xp = user_xp[user_id]['xp']
    lvl = user_xp[user_id]['level']
    
    if xp >= (lvl * 100):
        user_xp[user_id]['level'] += 1
        await message.channel.send(f'Congrats {message.author.mention}! You leveled up to level {lvl + 1} 🆙')

    # Commands

    if message.content == '!level':
        current_lvl = user_xp[user_id]['level']
        current_xp = user_xp[user_id]['xp']
        await message.channel.send(f'Your Level: {current_lvl} | XP: {current_xp}')

    if message.content == '!flip':
        result = random.choice(['Heads', 'Tails'])
        await message.channel.send(f'🪙 The coin landed on: **{result}**')

    if message.content.startswith('!guess'):
        number = random.randint(1, 10)
        await message.channel.send('I am thinking of a number between 1 and 10. Type your guess now!')
        
        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.isdigit()

        try:
            guess = await client.wait_for('message', check=check, timeout=15.0)
            if int(guess.content) == number:
                await message.channel.send(f'🎉 Correct! The number was {number}!')
            else:
                await message.channel.send(f'❌ Wrong! The number was {number}.')
        except:
            await message.channel.send('⌛ Time is up! You took too long to guess.')

token = os.getenv('DISCORD_TOKEN')
if token:
    client.run(token)
else:
    print("Error: No DISCORD_TOKEN found.")
