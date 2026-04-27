import discord
from discord.ext import commands
from discord.ui import Button, View
from easy_pil import Editor, load_image_async, Font
import os
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_xp = {}
REQUIRED_ROLE_NAME = "فعاليات"
# تعديل اسم الروم إلى "ترحيب" فقط
WELCOME_CHANNEL_NAME = "ترحيب"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    # البحث عن القناة باسم "ترحيب"
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        try:
            bg_url = "https://wallpaperaccess.com/full/175910.jpg"
            background = Editor(await load_image_async(bg_url)).resize((800, 450))
            avatar = Editor(await load_image_async(member.display_avatar.url)).resize((200, 200)).circle_clip()
            background.paste(avatar, (300, 80))
            
            font_big = Font.poppins(size=50, variant="bold")
            font_small = Font.poppins(size=35, variant="regular")
            background.text((400, 300), "WELCOME", color="white", font=font_big, align="center")
            background.text((400, 370), f"{member.name}", color="white", font=font_small, align="center")
            
            file = discord.File(fp=background.image_bytes, filename="welcome.png")
            await channel.send(f"حياك الله {member.mention} نورتنا! ☁️✨", file=file)
        except:
            await channel.send(f"منور السيرفر يا {member.mention}!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 كفو {message.author.mention}! وصلت لفل {user_xp[uid]['level']}!")

    if message.content == '-games':
        if not any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles):
            await message.channel.send(f"❌ لازم رتبة **({REQUIRED_ROLE_NAME})**")
            return
        await message.channel.send("🎮 **الألعاب:**\n`!level` | `!slots` | `!fast` | `!roll` | `!flip` | `!ball` | `!roulette`")
    await bot.process_commands(message)

@bot.command()
async def level(ctx):
    d = user_xp.get(str(ctx.author.id), {'level': 1, 'xp': 0})
    await ctx.send(f"مستواك: {d['level']} | نقاطك: {d['xp']} XP")

@bot.command()
async def flip(ctx):
    await ctx.send(f"🪙 النتيجة: **{random.choice(['وجه (ملك)', 'كتابة'])}**")

@bot.command()
async def slots(ctx):
    res = [random.choice("🍎🍊🍇💎⭐") for _ in range(3)]
    msg = "🎉 فوز!" if len(set(res))==1 else "✨ حبتين!" if len(set(res))==2 else "❌ خسارة"
    await ctx.send(f"**[ {' | '.join(res)} ]**\n{msg}")

@bot.command()
async def roll(ctx): await ctx.send(f"🎲: {random.randint(1, 6)}")

@bot.command(name="ball")
async def ball(ctx):
    await ctx.send(f"🔮: {random.choice(['نعم', 'لا', 'ممكن جداً'])}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
