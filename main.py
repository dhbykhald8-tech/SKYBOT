import discord
from discord.ext import commands
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

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
    save_data(user_data)
    await bot.process_commands(message)

@bot.command(aliases=['فلوس', 'coins', 'bal'])
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = user_data.get(str(member.id), {'coins': 0})
    await ctx.send(f"💰 رصيد **{member.display_name}**: `{data['coins']}` سكاي كوينز")

@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id)
    user_data[uid]['coins'] += 10000000
    save_data(user_data)
    await ctx.send(f"💰 **مبروك!** تم إضافة 10 مليون سكاي كوينز لرصيدك!")
    try: await ctx.message.delete()
    except: pass

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    reward = random.randint(500, 1000)
    user_data[uid]['coins'] += reward
    save_data(user_data)
    await ctx.send(f"💸 أخذت راتبك اليومي بقيمة **{reward}**!")

@bot.command()
async def top(ctx):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    lb = ""
    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            u = await bot.fetch_user(int(uid))
            lb += f"**#{i}** | {u.name} - `{data['coins']}` 💰\n"
        except: continue
    await ctx.send(embed=discord.Embed(title="🏆 أغنى 10 في سكاي", description=lb, color=0xFFD700))

@bot.command()
async def steal(ctx, member: discord.Member):
    uid, tid = str(ctx.author.id), str(member.id)
    if member == ctx.author or member.bot: return
    if random.random() < 0.05:
        amt = int(user_data[tid]['coins'] * 0.10)
        user_data[uid]['coins'] += amt
        user_data[tid]['coins'] -= amt
        await ctx.send(f"🥷 سرقت `{amt}` من {member.mention}!")
    else:
        user_data[uid]['coins'] = max(0, user_data[uid]['coins'] - 50)
        await ctx.send(f"👮 صادوك وتغرمت 50 كوينز!")
    save_data(user_data)

@bot.command()
async def marry(ctx, member: discord.Member):
    if member == ctx.author: return
    view = discord.ui.View()
    async def acc(interaction):
        if interaction.user != member: return
        await interaction.response.edit_message(content=f"💍 **مبروك! {ctx.author.mention} و {member.mention} تزوجوا!** 🎉", view=None)
    btn = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green)
    btn.callback = acc
    view.add_item(btn)
    await ctx.send(f"💍 {member.mention}، هل تقبل الزواج من {ctx.author.mention}؟", view=view)

token = os.getenv('DISCORD_TOKEN')
bot.run(token)

@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id)
    if uid not in user_data:
        user_data[uid] = {'coins': 0, 'xp': 0, 'level': 1}
    user_data[uid]['coins'] += 10000000
    save_data(user_data)
    await ctx.send(f"💰 **مبروك يا عذبي!** تم إضافة 10 مليون سكاي كوينز لرصيدك!")
    try: await ctx.message.delete()
    except: pass
