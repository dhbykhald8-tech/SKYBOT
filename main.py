import discord
from discord.ext import commands
from easy_pil import Editor, load_image_async
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# اسم الروم كما طلبت
WELCOME_CHANNEL_NAME = "ترحيب"
REQUIRED_ROLE_NAME = "فعاليات"
user_xp = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        try:
            # 1. فتح صورتك البنفسجية (تأكد ان اسمها welcome_bg.png في GitHub)
            background = Editor("welcome_bg.png").resize((800, 450))
            avatar_image = await load_image_async(member.display_avatar.url)
            
            # 2. جعل صورة الشخص دائرية (قياس 160)
            avatar = Editor(avatar_image).resize((160, 160)).circle_clip()
            
            # 3. دمج صورة الشخص (الإحداثيات معدلة لتكون في منتصف الدائرة)
            background.paste(avatar, (320, 45))
            
            file = discord.File(fp=background.image_bytes, filename="welcome.png")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️", file=file)
        except Exception as e:
            print(f"Error: {e}")
            await channel.send(f"منور السيرفر يا {member.mention}! ✨☁️")

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
        await message.channel.send("🎮 **الألعاب:**\n`!level` | `!slots` | `!fast` | `!roll` | `!flip` | `!ball`")
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

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
