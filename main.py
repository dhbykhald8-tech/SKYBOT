import discord
from discord.ext import commands, tasks
import random, json, asyncio, time
from datetime import datetime, timedelta

# --- الإعدادات الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات (سكاي كوين) ---
def load_data():
    try:
        with open('users.json', 'r') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w') as f: json.dump(data, f, indent=4)

def load_qs():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

user_data = load_data()
all_questions = load_qs()
rob_cooldown = {}
daily_attempts = {}

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {
            'coins': 1000, 'partner': None, 'marry_date': None, 
            'dowry': 0, 'xp': 0, 'level': 1
        }

# --- 1. نظام اللفل المطور (فويس + شات) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    check_u(uid)
    
    # لفل الشات: يزيد XP مع كل رسالة في الشات العام
    if message.channel.name == 'الشات-العام💬':
        user_data[uid]['xp'] += random.randint(5, 15)
        needed = user_data[uid]['level'] * 100
        if user_data[uid]['xp'] >= needed:
            user_data[uid]['level'] += 1
            user_data[uid]['xp'] = 0
            save_data(user_data)
            await message.channel.send(f"🆙 كفو {message.author.mention}! ارتفع مستواك وصار لفل **{user_data[uid]['level']}** 🎉")

    await bot.process_commands(message)

# لفل الفويس: 20 XP كل دقيقة
@tasks.loop(minutes=1)
async def voice_leveling():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if not member.bot:
                    uid = str(member.id); check_u(uid)
                    user_data[uid]['xp'] += 20
                    needed = user_data[uid]['level'] * 100
                    if user_data[uid]['xp'] >= needed:
                        user_data[uid]['level'] += 1; user_data[uid]['xp'] = 0
    save_data(user_data)

# --- 2. نظام التوب (أغنى 10 بالسيرفر) ---
@bot.command(name="top")
async def top_ten(ctx):
    # ترتيب حسب الكوينز
    sorted_u = sorted(user_data.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    
    lb = ""
    emojis = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
    
    for i, (uid, d) in enumerate(sorted_u):
        lb += f"{emojis[i]} **#{i+1}** <@{uid}> \n 💰 `{d['coins']}` سكاي كوين | 🆙 لفل `{d.get('level', 1)}` \n\n"
    
    embed = discord.Embed(title="🏆 قائمة أغنى 10 أساطير في سكاي", description=lb, color=0xffd700)
    embed.set_footer(text="شد حيلك عشان تدخل القائمة!")
    await ctx.send(embed=embed)

# --- 3. نظام السرقة (10% نجاح + غرامة 5000 + منع 3 دقائق) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    u_id = str(ctx.author.id)
    check_u(u_id)
    
    if u_id in rob_cooldown and time.time() < rob_cooldown[u_id]:
        rem = int(rob_cooldown[u_id] - time.time())
        return await ctx.send(f"🚫 ممنوع تسرق الحين! انتظر {rem} ثانية.")

    if random.random() <= 0.10: # نسبة النجاح 10%
        amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += amt
        user_data[str(member.id)]['coins'] -= amt
        await ctx.send(f"🥷 **عملية ناجحة!** سرقت {amt} سكاي كوين من {member.mention}")
    else:
        user_data[u_id]['coins'] -= 5000
        rob_cooldown[u_id] = time.time() + 180 # منع 3 دقائق
        await ctx.send("👮 **انقفشت!** دفعوك مخالفة 5000 سكاي كوين وتم حظرك 3 دقائق.")
    save_data(user_data)

# --- 4. كلمة السر (10 مليون سكاي كوين) ---
@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id); check_u(uid)
    user_data[uid]['coins'] += 10000000
    save_data(user_data)
    await ctx.send("🤫 **تم تفعيل الشفرة!** مبروك الـ 10,000,000 سكاي كوين.")

# --- 5. نظام الزواج (أسبوع + تقسيم ثروة) ---
@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id].get('partner'): return
    
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() >= m_date + timedelta(days=7):
        p_id = user_data[u_id]['partner']
        total = (user_data[u_id]['coins'] + user_data[p_id]['coins']) // 2
        user_data[u_id]['coins'] = user_data[p_id]['coins'] = total
        await ctx.send(f"💔 تم الانفصال وتقسيم الثروة: {total} لكل طرف.")
    else:
        await ctx.send("⚠️ لازم يمر أسبوع على الزواج عشان تتقسم الثروة!")
    
    user_data[u_id]['partner'] = None # إنهاء الزواج
    save_data(user_data)

# --- تشغيل البوت والمهام التلقائية ---
@bot.event
async def on_ready():
    voice_leveling.start()
    print(f"Logged in as {bot.user.name}")

bot.run("YOUR_TOKEN")
