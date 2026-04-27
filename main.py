import discord
from discord.ext import commands
import os
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# رتبة الفعاليات (تأكد أن الاسم مطابق لسيرفرك)
REQUIRED_ROLE_NAME = "فعاليات"
user_xp = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Sky Bot is ready for Games and XP!')

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # نظام اللفل والـ XP
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 كفو {message.author.mention}! وصلت لفل **{user_xp[uid]['level']}**!")

    # قائمة الألعاب
    if message.content == '-games':
        if not any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles):
            await message.channel.send(f"❌ عفواً، لازم رتبة **({REQUIRED_ROLE_NAME})** للعب!")
            return
        await message.channel.send("🎮 **الألعاب المتاحة:**\n`!level` | `!slots` | `!roll` | `!flip` | `!ball`")
    
    await bot.process_commands(message)

@bot.command()
async def level(ctx):
    d = user_xp.get(str(ctx.author.id), {'level': 1, 'xp': 0})
    await ctx.send(f"📊 مستواك: **{d['level']}** | نقاطك: **{d['xp']} XP**")

@bot.command()
async def flip(ctx):
    await ctx.send(f"🪙 النتيجة: **{random.choice(['ملك', 'كتابة'])}**")

@bot.command()
async def roll(ctx):
    await ctx.send(f"🎲 الرقم: **{random.randint(1, 6)}**")

@bot.command()
async def slots(ctx):
    res = [random.choice("🍎💎⭐") for _ in range(3)]
    msg = "🎉 كفو فزت!" if len(set(res)) == 1 else "❌ حظ أوفر"
    await ctx.send(f"**[ {' | '.join(res)} ]**\n{msg}")

@bot.command(name="ball")
async def ball(ctx):
    await ctx.send(f"🔮 الكرة تقول: **{random.choice(['نعم', 'لا', 'ممكن', 'أكيد'])}**")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
