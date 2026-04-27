import discord
from discord.ext import commands, tasks
import random, json, asyncio, time
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات (سكاي كوين) ---
def load_data():
    try:
        with open('users.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_qs():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

user_data = load_data()
all_questions = load_qs()
rob_cooldown = {}

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'xp': 0, 'level': 1}

# --- 1. قائمة الألعاب (الـ 20 لعبة والفعاليات) ---
@bot.command(name="games")
async def games_list(ctx):
    embed = discord.Embed(
        title="🎮 ترسانة ألعاب وفعاليات سكاي",
        description="هنا كل الألعاب اللي تقدر تجمع منها سكاي كوين وتفلها!",
        color=0x00ffcc
    )
    
    # ألعاب الحظ (القديمة)
    embed.add_field(name="🎰 ألعاب الحظ والكلاسيك", 
                    value="`!roulette` (روليت)\n`!adventure` (مغامرة)\n`!slots` (الأشكال)\n`!flip` (قرعة)\n`!dice` (نرد)", inline=True)
    
    # ألعاب السرعة (الجديدة)
    embed.add_field(name="🎯 ألعاب الذكاء والسرعة", 
                    value="`!math` (رياضيات)\n`!fast` (أسرع واحد)\n`!guess` (خمن الرقم)\n`!scramble` (فكك الكلمات)\n`!capitals` (عواصم)", inline=True)
    
    # الألعاب الجماعية (4 لاعبين وفوق)
    embed.add_field(name="⚔️ ألعاب جماعية (4+ لاعبين)", 
                    value="`!race` (سباق)\n`!war` (حرب)\n`!arena` (ساحة القتال)\n`!hunt` (صيد)\n`!mafia` (مافيا)", inline=False)
    
    # الفعاليات الكبرى
    embed.add_field(name="🌪️ المسابقات والأنظمة", 
                    value="`!تحدي` (الـ 2000 سؤال)\n`!سؤال` (100 عشوائي)\n`!rob` (سرقة الهوامير)\n`!top` (ترتيب الأغنياء)\n`!rank` (مستواك)", inline=False)
    
    embed.set_footer(text="استمتع في عالم سكاي!")
    await ctx.send(embed=embed)

# --- 2. نظام اللفل (فويس 20 XP وشات 10 XP) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id); check_u(uid)
    if message.channel.name == 'الشات-العام💬':
        user_data[uid]['xp'] += random.randint(5, 15)
        if user_data[uid]['xp'] >= user_data[uid]['level'] * 100:
            user_data[uid]['level'] += 1; user_data[uid]['xp'] = 0
            save_data(user_data)
    await bot.process_commands(message)

@tasks.loop(minutes=1)
async def voice_xp_loop():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if not member.bot:
                    uid = str(member.id); check_u(uid)
                    user_data[uid]['xp'] += 20
                    if user_data[uid]['xp'] >= user_data[uid]['level'] * 100:
                        user_data[uid]['level'] += 1; user_data[uid]['xp'] = 0
    save_data(user_data)

# --- 3. نظام السرقة الصارم (10% نجاح، 5000 غرامة، 3 دقايق منع) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    u_id = str(ctx.author.id); check_u(u_id)
    if u_id in rob_cooldown and time.time() < rob_cooldown[u_id]:
        rem = int(rob_cooldown[u_id] - time.time())
        return await ctx.send(f"🚫 انقفشت قبل شوي! انتظر {rem} ثانية عشان تسرق مرة ثانية.")
    
    if random.random() <= 0.10:
        amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += amt
        user_data[str(member.id)]['coins'] -= amt
        await ctx.send(f"🥷 **كفو!** سرقت {amt} سكاي كوين من {member.mention}")
    else:
        user_data[u_id]['coins'] -= 5000
        rob_cooldown[u_id] = time.time() + 180
        await ctx.send("👮 **انقفشت!** خسرت 5000 سكاي كوين وممنوع تسرق لـ 3 دقائق.")
    save_data(user_data)

# --- 4. نظام الزواج المتطور (أسبوع للقسمة) ---
@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id].get('partner'): return await ctx.send("أنت مو متزوج أصلاً!")
    
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() >= m_date + timedelta(days=7):
        p_id = user_data[u_id]['partner']
        total = (user_data[u_id]['coins'] + user_data[p_id]['coins']) // 2
        user_data[u_id]['coins'] = user_data[p_id]['coins'] = total
        await ctx.send(f"💔 تم الطلاق وتقسيم الثروة بالتساوي: {total} لكل طرف.")
    else:
        await ctx.send("⚠️ الطلاق متاح، بس تقسيم الفلوس ما يصير إلا بعد أسبوع زواج كامل!")
    
    p_id = user_data[u_id]['partner']
    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    save_data(user_data)

# --- 5. كلمة السر (10 مليون سكاي كوين) ---
@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id); check_u(uid)
    user_data[uid]['coins'] += 10000000; save_data(user_data)
    await ctx.send("🤫 شفرة الهامير تفعلت! مبروك الـ 10,000,000 سكاي كوين.")

# --- 6. التوب 10 ---
@bot.command()
async def top(ctx):
    sorted_u = sorted(user_data.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}> | `{d['coins']}` 🪙 | لفل `{d.get('level',1)}`" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 قائمة أغنى 10 في سكاي", description=lb, color=0xffd700))

# --- تشغيل البوت والمهام ---
@bot.event
async def on_ready():
    voice_xp_loop.start()
    print("SKYBOT IS READY AND STABLE!")

bot.run("TOKEN")
