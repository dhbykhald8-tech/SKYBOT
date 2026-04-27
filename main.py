import discord
from discord.ext import commands
import os
import random
import json
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = "data.json"
jail_list = {} # قائمة السجن المؤقتة

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
    save_data(user_data)
    await bot.process_commands(message)

# --- نظام السرقة والسجن ---
@bot.command()
async def steal(ctx, member: discord.Member):
    uid, target_id = str(ctx.author.id), str(member.id)
    
    if member == ctx.author: return await ctx.send("❌ تسرق نفسك؟")
    if member.bot: return await ctx.send("❌ البوت مفلس ما عنده شيء!")
    
    # فحص السجن
    if uid in jail_list:
        if datetime.now() < jail_list[uid]:
            rem = (jail_list[uid] - datetime.now()).seconds
            return await ctx.send(f"🚫 أنت في السجن! باقي لك `{rem}` ثانية.")

    if user_data.get(target_id, {}).get('coins', 0) < 100:
        return await ctx.send("❌ هذا العضو طفران، خله يجمع أول!")

    # نسبة النجاح 5%
    if random.random() < 0.05:
        stolen = int(user_data[target_id]['coins'] * 0.10)
        user_data[uid]['coins'] += stolen
        user_data[target_id]['coins'] -= stolen
        save_data(user_data)
        await ctx.send(f"🥷 **كفووو!** سرقت من {member.mention} مبلغ `{stolen}` كوينز!")
    else:
        # فشل وسجن لمدة 3 دقائق
        jail_list[uid] = datetime.now() + timedelta(minutes=3)
        fine = 50
        user_data[uid]['coins'] = max(0, user_data[uid]['coins'] - fine)
        save_data(user_data)
        await ctx.send(f"👮 **صادوك!** انقذفت بالسجن 3 دقائق وتغرمت `{fine}` كوينز.")

# --- باقي الأوامر ---
@bot.command(aliases=['bal', 'فلوس'])
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = user_data.get(str(member.id), {'coins': 0})
    await ctx.send(f"💰 رصيد **{member.display_name}**: `{data['coins']}` كوينز")

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
    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(uid))
            leaderboard += f"**#{i}** | {user.name} - `{data['coins']}` 💰\n"
        except: continue
    embed = discord.Embed(title="🏆 أغنى 10 في سكاي", description=leaderboard, color=0xFFD700)
    await ctx.send(embed=embed)

@bot.command()
async def marry(ctx, member: discord.Member):
    if member == ctx.author: return
    view = discord.ui.View()
    async def accept(interaction):
        if interaction.user != member: return
        await interaction.response.edit_message(content=f"💍 **مبروك! {ctx.author.mention} و {member.mention} تزوجوا!** 🎉", view=None)
    b1 = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green)
    b1.callback = accept
    view.add_item(b1)
    await ctx.send(f"💍 {member.mention}، هل تقبل الزواج من {ctx.author.mention}؟", view=view)

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
