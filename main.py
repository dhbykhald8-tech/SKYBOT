import discord
from discord.ext import commands
import os
import random
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_data()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if uid not in user_data:
        user_data[uid] = {'coins': 100, 'xp': 0, 'level': 1}
    
    user_data[uid]['xp'] += 5
    user_data[uid]['coins'] += 2
    
    if user_data[uid]['xp'] >= (user_data[uid]['level'] * 100):
        user_data[uid]['level'] += 1
        await message.channel.send(f"🆙 كفو {message.author.mention}! لفل **{user_data[uid]['level']}**")
    
    save_data(user_data)
    await bot.process_commands(message)

@bot.command(aliases=['bal', 'فلوس'])
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = user_data.get(str(member.id), {'coins': 0})
    await ctx.send(f"💰 رصيد **{member.display_name}**: `{data['coins']}` سكاي كوينز")

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    reward = random.randint(500, 1000)
    user_data[uid]['coins'] += reward
    save_data(user_data)
    await ctx.send(f"💸 أخذت راتبك اليومي بقيمة **{reward}**! رصيدك: `{user_data[uid]['coins']}`")

@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    uid1, uid2 = str(ctx.author.id), str(member.id)
    if amount <= 0 or user_data.get(uid1, {}).get('coins', 0) < amount:
        return await ctx.send("❌ رصيدك ما يكفي!")
    if uid2 not in user_data: user_data[uid2] = {'coins': 0, 'xp': 0, 'level': 1}
    user_data[uid1]['coins'] -= amount
    user_data[uid2]['coins'] += amount
    save_data(user_data)
    await ctx.send(f"✅ تم تحويل `{amount}` عملة إلى {member.mention}")

@bot.command()
async def top(ctx):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(uid))
            leaderboard += f"**#{i}** | {user.name} - `{data['coins']}` 💰\n"
        except: continue
    embed = discord.Embed(title="🏆 أغنى 10 في سكاي", description=leaderboard or "لا يوجد بيانات", color=0xFFD700)
    await ctx.send(embed=embed)

@bot.command()
async def marry(ctx, member: discord.Member):
    if member == ctx.author: return await ctx.send("❌ ما يصير تتزوج نفسك!")
    view = discord.ui.View()
    async def accept(interaction):
        if interaction.user != member: return
        await interaction.response.edit_message(content=f"💍 **مبروك! {ctx.author.mention} و {member.mention} تزوجوا!** 🎉", view=None)
    async def decline(interaction):
        if interaction.user != member: return
        await interaction.response.edit_message(content=f"💔 للاسف {member.mention} رفض الزواج..", view=None)
    
    b1, b2 = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green), discord.ui.Button(label="رفض ❌", style=discord.ButtonStyle.red)
    b1.callback, b2.callback = accept, decline
    view.add_item(b1); view.add_item(b2)
    await ctx.send(f"💍 {member.mention}، هل تقبل الزواج من {ctx.author.mention}؟", view=view)

@bot.command()
async def slots(ctx):
    uid = str(ctx.author.id)
    if user_data[uid]['coins'] < 50: return await ctx.send("❌ لازم عندك 50 عملة!")
    user_data[uid]['coins'] -= 50
    res = [random.choice(["🍎", "💎", "⭐"]) for _ in range(3)]
    if len(set(res)) == 1:
        user_data[uid]['coins'] += 500
        msg = "🎉 فوز! 500 عملة"
    else: msg = "❌ خسارة"
    save_data(user_data)
    await ctx.send(f"**[ {' | '.join(res)} ]**\n{msg}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
