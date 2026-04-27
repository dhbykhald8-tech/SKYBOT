import discord
from discord.ext import commands
import random, json, asyncio
from datetime import datetime, timedelta

# --- الإعدادات الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات ---
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

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'dowry': 0}

# --- شرط الروم والرتبة (تأكد من اسم الرتبة والروم في سيرفرك) ---
async def is_allowed(ctx):
    if ctx.channel.name != 'الشات-العام💬': return False
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات**!")
        return False
    return True

# --- الأوامر ---

@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 قائمة ألعاب سكاي كوين", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🌪️ المسابقات", value="`!تحدي` `!math` `!top`", inline=True)
    embed.add_field(name="💍 النظام الاجتماعي", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="تحدي")
async def tahadi(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 الأسئلة خلصت!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    await ctx.send(f"🌪️ **سؤال التحدي:** {q_data['q']}")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 2000; save_data(user_data)
        await msg.reply(f"✅ صح! +2000 **سكاي كوين**. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

@bot.command(name="marry")
async def marry_cmd(ctx, member: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['coins'] < amt or amt < 500: return await ctx.send("💰 رصيدك لا يكفي للمهر!")
    user_data[u_id]['coins'] -= amt
    user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
    user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_data[u_id]['dowry'] = amt
    save_data(user_data)
    await ctx.send(f"💍 تم الزواج! المهر ({amt}) **سكاي كوين** مجمد لمدة أسبوع.")

@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid)
    await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']} **سكاي كوين**")

@bot.command()
async def top(ctx):
    if not await is_allowed(ctx): return
    sorted_u = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}>: {d['coins']} 🪙" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 هوامير سكاي كوين", description=lb, color=0xffd700))

# --- تشغيل البوت ---
bot.run("YOUR_TOKEN_HERE")
import discord
from discord.ext import commands
import random, json, asyncio
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات ---
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

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'dowry': 0}

# --- نظام التحقق ---
async def is_allowed(ctx):
    if ctx.channel.name != 'الشات-العام💬': return False
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات**!")
        return False
    return True

# --- 1. القائمة الشاملة ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 ترسانة سكاي كوين الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🌪️ مسابقات", value="`!تحدي` `!math` `!top`", inline=True)
    embed.add_field(name="💍 النظام الاجتماعي", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    embed.set_footer(text="جميع الحقوق لبوت سكاي")
    await ctx.send(embed=embed)

# --- 2. نظام التحدي (2000 سؤال) ---
@bot.command(name="تحدي")
async def tahadi(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 الأسئلة خلصت!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(f"🌪️ **سؤال التحدي:** {q_data['q']}")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 2000; save_data(user_data)
        await msg.reply(f"✅ صح! +2000 **سكاي كوين**. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

# --- 3. نظام الزواج (أسبوع + رتبة) ---
@bot.command(name="marry")
async def marry_cmd(ctx, member: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['partner'] or user_data[p_id]['partner']: return await ctx.send("💍 واحد منكم متزوج!")
    if user_data[u_id]['coins'] < amt: return await ctx.send("💰 رصيدك لا يكفي للمهر!")

    user_data[u_id]['coins'] -= amt
    save_data(user_data)
    await ctx.send(f"💍 {member.mention}، تقبل بـ {ctx.author.mention} مهر {amt} **سكاي كوين**؟ (أقبل/أرفض)")

    def check(m): return m.author == member and m.content in ['أقبل', 'أرفض']
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        if msg.content == 'أقبل':
            user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
            user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_data[u_id]['dowry'] = amt
            role = discord.utils.get(ctx.guild.roles, name="متزوجين")
            if role:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            save_data(user_data)
            await ctx.send("🎊 مبروك! تم الزواج وإعطاء الرتبة. المهر مجمد لمدة أسبوع.")
        else:
            user_data[u_id]['coins'] += amt; save_data(user_data)
            await ctx.send("💔 رفض الطلب.")
    except:
        user_data[u_id]['coins'] += amt; save_data(user_data)
        await ctx.send("⏰ انتهى الوقت.")

@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id].get('partner'): return
    p_id = user_data[u_id]['partner']
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    dowry = user_data[u_id].get('dowry', 0)

    if datetime.now() >= m_date + timedelta(days=7):
        user_data[p_id]['coins'] += dowry
        await ctx.send(f"💔 طلاق بعد أسبوع. تم تحويل المهر {dowry} للطرف الثاني.")
    else:
        await ctx.send(f"⚠️ طلاق مبكر! ضاع المهر {dowry} **سكاي كوين**.")

    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    role = discord.utils.get(ctx.guild.roles, name="متزوجين")
    if role:
        await ctx.author.remove_roles(role)
        p_mem = ctx.guild.get_member(int(p_id))
        if p_mem: await p_mem.remove_roles(role)
    save_data(user_data)

# --- 4. الرصيد ولوحة الشرف ---
@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid)
    await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']} **سكاي كوين**")

@bot.command()
async def top(ctx):
    if not await is_allowed(ctx): return
    sorted_u = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}>: {d['coins']} 🪙" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 هوامير سكاي كوين", description=lb, color=0xffd700))

# --- 5. ألعاب الحظ (مثال) ---
@bot.command()
async def roulette(ctx, amt: int):
    if not await is_allowed(ctx): return
    uid = str(ctx.author.id); check_u(uid)
    if user_data[uid]['coins'] < amt: return await ctx.send("رصيدك ناقص!")
    if random.random() > 0.6:
        user_data[uid]['coins'] += amt
        await ctx.send(f"🎰 فزت بـ {amt*2} **سكاي كوين**")
    else:
        user_data[uid]['coins'] -= amt
        await ctx.send("🎰 خسرت!")
    save_data(user_data)

bot.run("TOKEN")
import discord
from discord.ext import commands
import random, json, asyncio
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات ---
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

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'dowry': 0}

# --- نظام التحقق (الروم والرتبة) ---
async def is_allowed(ctx):
    if ctx.channel.name != 'الشات-العام💬': return False
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات**!")
        return False
    return True

# --- 1. القائمة الشاملة (محدثة) ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 ترسانة سكاي كوين الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🌪️ مسابقات وذكاء", value="`!تحدي` (2000 سؤال) `!سؤال` (عشوائي) `!math` `!top`", inline=True)
    embed.add_field(name="💍 النظام الاجتماعي", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    embed.set_footer(text="نظام عملات سكاي كوين - النسخة الكاملة")
    await ctx.send(embed=embed)

# --- 2. الأسئلة العشوائية (الجديد) ---
@bot.command(name="سؤال")
async def random_q(ctx):
    if not await is_allowed(ctx): return
    questions_list = [
        "من هو الشخصية الرئيسية في أنمي ون بيس؟",
        "ما هو أسرع حيوان في العالم؟",
        "كم عدد أجزاء لعبة ريزيدنت إيفل الأساسية؟",
        "ما هي عاصمة اليابان؟",
        "من هو الهداف التاريخي لدوري أبطال أوروبا؟",
        "ماهي أقوى قدرة في أنمي جوجوتسو كايسن؟",
        "من هو مؤسس شركة مايكروسوفت؟"
    ]
    q = random.choice(questions_list)
    await ctx.send(f"❓ **سؤال عشوائي للدردشة:**\n> {q}")

# --- 3. نظام التحدي (الـ 2000 سؤال) ---
@bot.command(name="تحدي")
async def tahadi(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 بنك الأسئلة فارغ!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(f"🌪️ **سؤال التحدي السريع:**\n**{q_data['q']}**")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 2000; save_data(user_data)
        await msg.reply(f"✅ كفو! أخذت 2000 **سكاي كوين**. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ انتهى الوقت! الإجابة: {q_data['a']}")

# --- 4. نظام الزواج المطور (أسبوع + رتبة) ---
@bot.command(name="marry")
async def marry_cmd(ctx, member: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['partner']: return await ctx.send("💍 أنت متزوج بالفعل!")
    if user_data[u_id]['coins'] < amt: return await ctx.send("💰 رصيدك لا يكفي للمهر!")

    user_data[u_id]['coins'] -= amt
    save_data(user_data)
    await ctx.send(f"💍 {member.mention}، هل تقبل بـ {ctx.author.mention} مهر {amt} **سكاي كوين**؟ (أقبل/أرفض)")

    def check(m): return m.author == member and m.content in ['أقبل', 'أرفض']
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        if msg.content == 'أقبل':
            user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
            user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_data[u_id]['dowry'] = amt
            role = discord.utils.get(ctx.guild.roles, name="متزوجين")
            if role:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            save_data(user_data)
            await ctx.send("🎊 مبروك الزواج! تم إعطاء الرتبة والمهر مجمد لمدة أسبوع.")
        else:
            user_data[u_id]['coins'] += amt; save_data(user_data)
            await ctx.send("💔 تم رفض الطلب واستعادة المبلغ.")
    except:
        user_data[u_id]['coins'] += amt; save_data(user_data)
        await ctx.send("⏰ انتهى الوقت.")

# --- (باقي الأوامر: bal, top, work, rob, roulette, divorce...) ---

bot.run("TOKEN")
import discord
from discord.ext import commands
import random, json, asyncio
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات ---
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

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'dowry': 0}

# --- نظام التحقق (الروم والرتبة) ---
async def is_allowed(ctx):
    if ctx.channel.name != 'الشات-العام💬': return False
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات**!")
        return False
    return True

# --- 1. القائمة الشاملة (محدثة) ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 ترسانة سكاي كوين الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🌪️ مسابقات وذكاء", value="`!تحدي` (2000 سؤال) `!سؤال` (عشوائي) `!math` `!top`", inline=True)
    embed.add_field(name="💍 النظام الاجتماعي", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    embed.set_footer(text="نظام عملات سكاي كوين - النسخة الكاملة")
    await ctx.send(embed=embed)

# --- 2. الأسئلة العشوائية (الجديد) ---
@bot.command(name="سؤال")
async def random_q(ctx):
    if not await is_allowed(ctx): return
    questions_list = [
        "من هو الشخصية الرئيسية في أنمي ون بيس؟",
        "ما هو أسرع حيوان في العالم؟",
        "كم عدد أجزاء لعبة ريزيدنت إيفل الأساسية؟",
        "ما هي عاصمة اليابان؟",
        "من هو الهداف التاريخي لدوري أبطال أوروبا؟",
        "ماهي أقوى قدرة في أنمي جوجوتسو كايسن؟",
        "من هو مؤسس شركة مايكروسوفت؟"
    ]
    q = random.choice(questions_list)
    await ctx.send(f"❓ **سؤال عشوائي للدردشة:**\n> {q}")

# --- 3. نظام التحدي (الـ 2000 سؤال) ---
@bot.command(name="تحدي")
async def tahadi(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 بنك الأسئلة فارغ!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(f"🌪️ **سؤال التحدي السريع:**\n**{q_data['q']}**")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 2000; save_data(user_data)
        await msg.reply(f"✅ كفو! أخذت 2000 **سكاي كوين**. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ انتهى الوقت! الإجابة: {q_data['a']}")

# --- 4. نظام الزواج المطور (أسبوع + رتبة) ---
@bot.command(name="marry")
async def marry_cmd(ctx, member: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)
    if user_data[u_id]['partner']: return await ctx.send("💍 أنت متزوج بالفعل!")
    if user_data[u_id]['coins'] < amt: return await ctx.send("💰 رصيدك لا يكفي للمهر!")

    user_data[u_id]['coins'] -= amt
    save_data(user_data)
    await ctx.send(f"💍 {member.mention}، هل تقبل بـ {ctx.author.mention} مهر {amt} **سكاي كوين**؟ (أقبل/أرفض)")

    def check(m): return m.author == member and m.content in ['أقبل', 'أرفض']
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        if msg.content == 'أقبل':
            user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
            user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_data[u_id]['dowry'] = amt
            role = discord.utils.get(ctx.guild.roles, name="متزوجين")
            if role:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            save_data(user_data)
            await ctx.send("🎊 مبروك الزواج! تم إعطاء الرتبة والمهر مجمد لمدة أسبوع.")
        else:
            user_data[u_id]['coins'] += amt; save_data(user_data)
            await ctx.send("💔 تم رفض الطلب واستعادة المبلغ.")
    except:
        user_data[u_id]['coins'] += amt; save_data(user_data)
        await ctx.send("⏰ انتهى الوقت.")

# --- (باقي الأوامر: bal, top, work, rob, roulette, divorce...) ---

bot.run("TOKEN")
import time # تأكد من وجود هذا السطر فوق مع الـ imports

# --- نظام تبريد المحاولات والسرقة ---
rob_cooldown = {} # لحفظ وقت العقوبة (5 دقايق)
daily_attempts = {} # لحفظ عدد محاولات اليوم

@bot.command()
async def rob(ctx, member: discord.Member):
    if not await is_allowed(ctx): return
    
    u_id = str(ctx.author.id)
    t_id = str(member.id)
    check_u(u_id); check_u(t_id)

    # 1. التحقق من عقوبة الـ 5 دقائق
    if u_id in rob_cooldown:
        remaining = rob_cooldown[u_id] - time.time()
        if remaining > 0:
            return await ctx.send(f"🚫 أنت محظور من السرقة حالياً! انتظر {int(remaining/60)} دقيقة و {int(remaining%60)} ثانية.")

    # 2. التحقق من عدد المحاولات اليومية (مرتين باليوم)
    today = datetime.now().strftime("%Y-%m-%d")
    if u_id not in daily_attempts or daily_attempts[u_id]['date'] != today:
        daily_attempts[u_id] = {'count': 0, 'date': today}
    
    if daily_attempts[u_id]['count'] >= 2:
        return await ctx.send("❌ خلصت محاولاتك اليوم! مسموح لك تسرق مرتين بس في اليوم.")

    # 3. شروط عامة
    if member == ctx.author: return await ctx.send("تسرق نفسك؟")
    if user_data[t_id]['coins'] < 5000: return await ctx.send("المستهدف طفران ما يغطي حتى قيمة المخالفة!")

    # احتساب المحاولة
    daily_attempts[u_id]['count'] += 1

    # 4. تنفيذ السرقة (نسبة النجاح 10%)
    if random.random() <= 0.10: 
        # نجحت السرقة
        stolen_amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += stolen_amt
        user_data[t_id]['coins'] -= stolen_amt
        save_data(user_data)
        await ctx.send(f"🥷 **عملية ناجحة!** سرقت {stolen_amt} سكاي كوين من {member.mention} وهربت!")
    else:
        # فشلت السرقة (العقوبات)
        fine = 5000
        user_data[u_id]['coins'] -= fine
        # وضع عقوبة منع الكتابة للأمر لمدة 5 دقائق
        rob_cooldown[u_id] = time.time() + 300 
        save_data(user_data)
        await ctx.send(f"👮 **انقفشت!** دفعوك مخالفة {fine} سكاي كوين وتم حظرك من السرقة لمدة 5 دقائق.")

# أضف هذا الجزء داخل دالة check_u أو تحتها
def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {
            'coins': 1000, 
            'partner': None, 
            'marry_date': None, 
            'dowry': 0,
            'xp': 0,      # نظام الخبرة
            'level': 1    # نظام اللفل
        }

# دالة لزيادة اللفل مع كل رسالة في الشات العام
@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.name == 'الشات-العام💬':
        uid = str(message.author.id)
        check_u(uid)
        
        # زيادة الخبرة (XP)
        user_data[uid]['xp'] += random.randint(5, 15)
        
        # حساب اللفل (كل لفل يحتاج خبرة أكثر)
        xp_needed = user_data[uid]['level'] * 100
        if user_data[uid]['xp'] >= xp_needed:
            user_data[uid]['level'] += 1
            user_data[uid]['xp'] = 0
            save_data(user_data)
            await message.channel.send(f"🆙 كفو يا {message.author.mention}! لفلك ارتفع وصار **{user_data[uid]['level']}**! 🎉")

    await bot.process_commands(message) # ضروري عشان الأوامر ما تتعطل
