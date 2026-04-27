import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# قفل الرتبة (تأكد إن اسم الرتبة صح عندك)
REQUIRED_ROLE_NAME = "فعاليات"
# اسم القناة اللي بيرسل فيها ترحيب عادي
WELCOME_CHANNEL_NAME = "ترحيب"

# نظام النقاط (في الذاكرة)
user_xp = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# --- ترحيب كتابي فقط (بدون صور) ---
@bot.event
async def on_member_join(member):
    # البحث عن القناة
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"حياك الله يا {member.mention} نورتنا! منور السيرفر يا بطل! ✨☁️")

# --- نظام اللفل والفعاليات ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # زيادة XP عند كل رسالة
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    
    # فحص إذا ارتفع اللفل
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 كفو يا {message.author.mention}! ارتفع ليفلك وصار **{user_xp[uid]['level']}**!")

    # عرض قائمة الألعاب (قفل الرتبة)
    if message.content == '-games':
        has_role = any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles)
        if not has_role:
            await message.channel.send(f"❌ عفواً {message.author.mention}، لازم رتبة **({REQUIRED_ROLE_NAME})** عشان تلعب!")
            return
            
        help_text = (
            "🎮 **قائمة ألعاب سكاي بوت المتاحة للرتبة:**\n"
            "`!level` - لفلُك ونقاطك\n"
            "`!slots` - آلة الحظ (فواكه)\n"
            "`!fast` - تحدي الكتابة\n"
            "`!roll` - ارمِ النرد\n"
            "`!flip` - ملك أو كتابة\n"
            "`!ball` - الكرة السحرية"
        )
        await message.channel.send(help_text)
    
    await bot.process_commands(message)

# --- أوامر الألعاب بالردود العربية ---

@bot.command()
async def level(ctx):
    uid = str(ctx.author.id)
    d = user_xp.get(uid, {'level': 1, 'xp': 0})
    await ctx.send(f"مستواك: **{d['level']}** | نقاطك: **{d['xp']} XP**")

@bot.command()
async def flip(ctx):
    res = random.choice(['وجه (ملك)', 'كتابة'])
    await ctx.send(f"🪙 النتيجة: **{res}**")

@bot.command()
async def slots(ctx):
    icons = "🍎🍊🍇💎⭐"
    res = [random.choice(icons) for _ in range(3)]
    result_text = "🎉 مبروك! فوز!" if len(set(res))==1 else "✨ كفو! حبتين!" if len(set(res))==2 else "❌ خسارة"
    await ctx.send(f"**[ {' | '.join(res)} ]**\n{result_text}")

@bot.command()
async def fast(ctx):
    words = ["كويت", "برمجة", "سكاي", "سرعة", "طور"]
    t = random.choice(words)
    await ctx.send(f"اكتب بسرعة الكلمة هذي: **{t}**")
    try:
        await bot.wait_for('message', check=lambda m: m.author==ctx.author and m.content==t, timeout=8)
        await ctx.send("⚡ وحش! كتبتها بالوقت!")
    except: await ctx.send(f"⌛ وقت، كانت الكلمة: {t}")

@bot.command()
async def roll(ctx): await ctx.send(f"🎲 الرقم هو: **{random.randint(1, 6)}**")

@bot.command(name="ball")
async def ball(ctx):
    ans = ["نعم", "لا", "ممكن", "اسأل لاحقاً"]
    await ctx.send(f"🔮 الكرة تقول: **{random.choice(ans)}**")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
