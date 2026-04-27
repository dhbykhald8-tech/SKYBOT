import discord
from discord.ext import commands, tasks
import random, json, asyncio, time
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def load_data():
    try:
        with open('users.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_data = load_data()
rob_cooldown = {}

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'xp': 0, 'level': 1}

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

@bot.command()
async def marry(ctx, member: discord.Member):
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['partner'] or user_data[p_id]['partner']:
        return await ctx.send("واحد منكم متزوج!")
    user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
    user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_data(user_data)
    await ctx.send(f"💍 مبروك الزواج! {ctx.author.mention} و {member.mention}")

@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id]['partner']: return
    p_id = user_data[u_id]['partner']
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() >= m_date + timedelta(days=7):
        total = (user_data[u_id]['coins'] + user_data[p_id]['coins']) // 2
        user_data[u_id]['coins'] = user_data[p_id]['coins'] = total
        await ctx.send(f"💔 طلاق وتقسيم ثروة بالتساوي: {total}")
    else:
        await ctx.send("💔 طلاق بدون تقسيم (المدة أقل من أسبوع).")
    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    save_data(user_data)

@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ألعاب سكاي", color=0x00ffcc)
    embed.add_field(name="💰 اقتصاد", value="`!bal` `!top` `!rob` `!sky10`")
    embed.add_field(name="🎰 حظ", value="`!roulette` `!adventure` `!slots` `!flip` `!dice`")
    await ctx.send(embed=embed)

@bot.command()
async def rob(ctx, member: discord.Member):
    u_id = str(ctx.author.id); check_u(u_id)
    if u_id in rob_cooldown and time.time() < rob_cooldown[u_id]:
        return await ctx.send(f"🚫 انتظر {int(rob_cooldown[u_id] - time.time())} ثانية!")
    if random.random() <= 0.10:
        amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += amt
        user_data[str(member.id)]['coins'] -= amt
        await ctx.send(f"🥷 سرقت {amt} سكاي كوين.")
    else:
        user_data[u_id]['coins'] -= 5000
        rob_cooldown[u_id] = time.time() + 180
        await ctx.send("👮 انقفشت! غرامة 5000 ومنع 3 دقائق.")
    save_data(user_data)

@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id); check_u(uid)
    user_data[uid]['coins'] += 10000000; save_data(user_data)
    await ctx.send("🤫 مبروك الـ 10 مليون!")

@bot.event
async def on_ready():
    voice_xp_loop.start()
    print("READY")

# استبدل الكود بالأسفل بالتوكن حقك (تأكد من وجود علامات التنصيص "")
bot.run("MTQ5ODEzOTEyODAzNzExMzg1Ng.GH3rfP.ADsDqlBzAOXgtNMWKPVBVKjko8q3BKZpUJyW-8")
