import discord
from discord.ext import commands


TOKEN = 'MTQ5ODEzOTEyODAzNzExMzg1Ng.GmvzJ_.7Y9NZW84CUR2q2GKIZme_4gZQbKDjzXH33Udo'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hi(ctx):
    await ctx.send('Hello! Sky Bot is Online 🚀')

bot.run(TOKEN)