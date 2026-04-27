import discord
from discord.ext import commands, tasks
import random, json, asyncio, time
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام إدارة الأموال (سكاي كوين) ---
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

# --- نظام الجوائز (لفل فويس وشات) ---
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
                    user_data[uid]['xp'] += 20 # كسب لفل بالفويس
                    if user_data[uid]['xp'] >= user_data[uid]['level'] * 100:
                        user_data[uid]['level'] += 1; user_data[uid]['xp'] = 0
    save_data(user_data)

# --- نظام الزواج (تقسيم السكاي كوين بعد أسبوع) ---
@bot.command()
async def marry(ctx, member: discord.Member):
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['partner'] or user_data[p_id]['partner']:
        return await ctx.send("واحد منكم متزوج أصلاً!")
    user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
    user_data[u_id]['marry_date'] = user_data[p_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_data(user_data)
    await ctx.send(f"💍 مبروك! تم زواج {ctx.author.mention} و {member.mention}")

@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id]['partner']: return await ctx.send("أنت مو متزوج!")
    p_id = user_data[u_id]['partner']
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    
    if datetime.now() >= m_date + timedelta(days=7):
        total_coins = (user_data[u_id]['coins'] + user_data[p_id]['coins']) // 2
        user_data[u_id]['coins'] = user_data[p_id]['coins'] = total_coins
        await ctx.send(f"💔 تم الانفصال وتقسيم السكاي كوين بالتساوي: {total_coins}")
    else:
        await ctx.send("💔 تم الطلاق، بس مافيه تقسيم ثروة لأنكم ما كملتوا أسبوع.")
    
    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    save_data(user_data)

# --- نظام السرقة (تحدي السكاي كوين) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    u_id = str(ctx.author.id); check_u(u_id)
    if u_id in rob_cooldown and time.time() < rob_cooldown[u_id]:
        return await ctx.send(f"🚫 ممنوع السرقة! انتظر {int(rob_cooldown[u_id] - time.time())} ثانية.")
    
    if random.random() <= 0.10: # نجاح 10%
        amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += amt
        user_data[str(member.id)]['coins'] -= amt
        await ctx.send(f"🥷 كفو! سرقت {amt} سكاي كوين.")
    else:
        user_data[u_id]['coins'] -= 5000 # غرامة فشل
        rob_cooldown[u_id] = time.time() + 180
        await ctx.send("👮 انقفشت! غرامة 5000 ومنع 3 دقائق.")
    save_data(user_data)

# --- قائمة الألعاب والفعاليات ---
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 قائمة ألعاب سكاي كوين", color=0x00ffcc)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!slots` `!flip` `!dice`", inline=True)
    embed.add_field(name="🎯 ألعاب السرعة", value="`!math` `!fast` `!guess` `!scramble` `!capitals`", inline=True)
    embed.add_field(name="⚔️ ألعاب جماعية", value="`!race` `!war` `!arena` `!hunt` `!mafia`", inline=False)
    embed.add_field(name="🌪️ فعاليات مالية", value="`!bal` `!top` `!rob` `!sky10` `!pay`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid)
    await ctx.send(f"💰 رصيدك الحالي: `{user_data[uid]['coins']}` سكاي كوين.")

@bot.command()
async def top(ctx):
    sorted_u = sorted(user_data.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}> | `{d['coins']}` 🪙" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 أغنى 10 في سكاي", description=lb, color=0xffd700))

@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id); check_u(uid)
    user_data[uid]['coins'] += 10000000; save_data(user_data)
    await ctx.send("🤫 هكرت النظام! مبروك الـ 10 مليون سكاي كوين.")

@bot.event
async def on_ready():
    voice_xp_loop.start()
    print("SKYBOT IS READY")

bot.run(MTQ5ODEzOTEyODAzNzExMzg1Ng.GH3rfP.ADsDqlBzAOXgtNMWKPVBVKjko8q3BKZpUJyW-8)
