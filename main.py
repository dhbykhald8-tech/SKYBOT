import discord
from discord.ext import commands
import random, json, asyncio

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام حفظ البيانات (عشان فلوسك ما تضيع) ---
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
    if uid not in user_data: user_data[uid] = {'coins': 1000, 'partner': None}

# --- 1. القائمة الشاملة ---
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ترسانة ألعاب سكاي الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🧠 المسابقات", value="`!تحدي` (2000 سؤال) `!سؤال` (عشوائي) `!math`", inline=True)
    embed.add_field(name="💰 النظام المالي", value="`!bal` `!work` `!rob` `!marry` `!divorce`", inline=False)
    embed.set_footer(text="استمتع بالألعاب يا عذبي!")
    await ctx.send(embed=embed)

# --- 2. ألعاب المسابقات (الـ 2000 والأسئلة العشوائية) ---
@bot.command()
async def تحدي(ctx):
    global all_questions
    if not all_questions: return await ctx.send("🚨 خلصت الأسئلة!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    await ctx.send(f"🌪️ **سؤال التحدي:** {q_data['q']}")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 1000; save_data(user_data)
        await msg.reply(f"✅ صح! +1000 كوينز. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

@bot.command()
async def سؤال(ctx):
    qs = ["ما هو أسرع حيوان؟", "من هو ملك القراصنة؟", "كم عدد قارات العالم؟"]
    await ctx.send(f"❓ **سؤال عشوائي:** {random.choice(qs)}")

# --- 3. ألعاب الحظ (العملة، الروليت، المغامرة) ---
@bot.command()
async def flip(ctx, side: str):
    res = random.choice(['ملك', 'كتابة'])
    msg = "✅ فزت!" if side == res else "❌ خسرت!"
    await ctx.send(f"🪙 طلعت **{res}** | {msg}")

@bot.command()
async def roulette(ctx, amt: int):
    uid = str(ctx.author.id); check_u(uid)
    if user_data[uid]['coins'] < amt: return await ctx.send("رصيدك ناقص!")
    if random.random() > 0.6:
        user_data[uid]['coins'] += amt
        await ctx.send(f"🎰 كفو فزت بـ {amt*2}")
    else:
        user_data[uid]['coins'] -= amt
        await ctx.send("🎰 خسرت المراهنة!")
    save_data(user_data)

@bot.command()
async def adventure(ctx):
    uid = str(ctx.author.id); check_u(uid)
    res = random.randint(-300, 700)
    user_data[uid]['coins'] += res; save_data(user_data)
    await ctx.send(f"🤠 نتيجة مغامرتك: {res} كوينز")

# --- 4. الأنظمة الاجتماعية والمالية ---
@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid); await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']}")

@bot.command()
async def marry(ctx, m: discord.Member, amt: int):
    u, p = str(ctx.author.id), str(m.id)
    check_u(u); check_u(p)
    if user_data[u]['partner']: return await ctx.send("متزوج أصلاً!")
    user_data[u]['partner'], user_data[p]['partner'] = p, u
    user_data[u]['coins'] -= amt; user_data[p]['coins'] += amt
    save_data(user_data); await ctx.send(f"💍 مبروك الزواج لـ {ctx.author.mention} و {m.mention}")

@bot.command()
async def divorce(ctx):
    u = str(ctx.author.id); p = user_data[u].get('partner')
    if not p: return await ctx.send("مو متزوج!")
    user_data[u]['partner'] = user_data[p]['partner'] = None
    save_data(user_data); await ctx.send("💔 تم الانفصال")

bot.run("TOKEN")
import discord
from discord.ext import commands
import random, json, asyncio

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام حفظ البيانات (عشان فلوسك ما تضيع) ---
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
    if uid not in user_data: user_data[uid] = {'coins': 1000, 'partner': None}

# --- 1. القائمة الشاملة ---
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ترسانة ألعاب سكاي الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🧠 المسابقات", value="`!تحدي` (2000 سؤال) `!سؤال` (عشوائي) `!math`", inline=True)
    embed.add_field(name="💰 النظام المالي", value="`!bal` `!work` `!rob` `!marry` `!divorce`", inline=False)
    embed.set_footer(text="استمتع بالألعاب يا عذبي!")
    await ctx.send(embed=embed)

# --- 2. ألعاب المسابقات (الـ 2000 والأسئلة العشوائية) ---
@bot.command()
async def تحدي(ctx):
    global all_questions
    if not all_questions: return await ctx.send("🚨 خلصت الأسئلة!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    await ctx.send(f"🌪️ **سؤال التحدي:** {q_data['q']}")
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 1000; save_data(user_data)
        await msg.reply(f"✅ صح! +1000 كوينز. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

@bot.command()
async def سؤال(ctx):
    qs = ["ما هو أسرع حيوان؟", "من هو ملك القراصنة؟", "كم عدد قارات العالم؟"]
    await ctx.send(f"❓ **سؤال عشوائي:** {random.choice(qs)}")

# --- 3. ألعاب الحظ (العملة، الروليت، المغامرة) ---
@bot.command()
async def flip(ctx, side: str):
    res = random.choice(['ملك', 'كتابة'])
    msg = "✅ فزت!" if side == res else "❌ خسرت!"
    await ctx.send(f"🪙 طلعت **{res}** | {msg}")

@bot.command()
async def roulette(ctx, amt: int):
    uid = str(ctx.author.id); check_u(uid)
    if user_data[uid]['coins'] < amt: return await ctx.send("رصيدك ناقص!")
    if random.random() > 0.6:
        user_data[uid]['coins'] += amt
        await ctx.send(f"🎰 كفو فزت بـ {amt*2}")
    else:
        user_data[uid]['coins'] -= amt
        await ctx.send("🎰 خسرت المراهنة!")
    save_data(user_data)

@bot.command()
async def adventure(ctx):
    uid = str(ctx.author.id); check_u(uid)
    res = random.randint(-300, 700)
    user_data[uid]['coins'] += res; save_data(user_data)
    await ctx.send(f"🤠 نتيجة مغامرتك: {res} كوينز")

# --- 4. الأنظمة الاجتماعية والمالية ---
@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid); await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']}")

@bot.command()
async def marry(ctx, m: discord.Member, amt: int):
    u, p = str(ctx.author.id), str(m.id)
    check_u(u); check_u(p)
    if user_data[u]['partner']: return await ctx.send("متزوج أصلاً!")
    user_data[u]['partner'], user_data[p]['partner'] = p, u
    user_data[u]['coins'] -= amt; user_data[p]['coins'] += amt
    save_data(user_data); await ctx.send(f"💍 مبروك الزواج لـ {ctx.author.mention} و {m.mention}")

@bot.command()
async def divorce(ctx):
    u = str(ctx.author.id); p = user_data[u].get('partner')
    if not p: return await ctx.send("مو متزوج!")
    user_data[u]['partner'] = user_data[p]['partner'] = None
    save_data(user_data); await ctx.send("💔 تم الانفصال")

bot.run("TOKEN")
# --- 1. لعبة السلوتس (Slots) ---
@bot.command()
async def slots(ctx):
    items = ["🍎", "💎", "🎰", "🍀"]
    res = [random.choice(items) for _ in range(3)]
    await ctx.send(f"**[ {res[0]} | {res[1]} | {res[2]} ]**")
    uid = str(ctx.author.id); check_u(uid)
    if res[0] == res[1] == res[2]:
        user_data[uid]['coins'] += 2000; await ctx.send("🔥 كفووو! فزت بالجائزة الكبرى 2000 كوينز!")
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
        user_data[uid]['coins'] += 500; await ctx.send("✅ حبتين! فزت بـ 500 كوينز")
    save_data(user_data)

# --- 2. لعبة النرد (Dice) ---
@bot.command()
async def dice(ctx, guess: int):
    if guess < 1 or guess > 6: return await ctx.send("🎲 اختر رقم من 1 إلى 6!")
    roll = random.randint(1, 6)
    uid = str(ctx.author.id); check_u(uid)
    if guess == roll:
        user_data[uid]['coins'] += 1000; await ctx.send(f"🎲 النرد طلع {roll}.. مبروك فزت بـ 1000 كوينز!")
    else:
        await ctx.send(f"🎲 النرد طلع {roll}.. حظ أوفر المرة الجاية")
    save_data(user_data)

# --- 3. مسابقة الرياضيات السريعة (Math) ---
@bot.command()
async def math(ctx):
    n1, n2 = random.randint(1, 50), random.randint(1, 50)
    op = random.choice(['+', '-'])
    result = n1 + n2 if op == '+' else n1 - n2
    await ctx.send(f"🔢 أسرع واحد يحلها: **{n1} {op} {n2} = ؟**")
    def check(m): return m.channel == ctx.channel and m.content == str(result)
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 300; save_data(user_data)
        await msg.reply("✅ صح! أخذت 300 كوينز")
    except: await ctx.send(f"⏰ خلص الوقت، الإجابة كانت {result}")

# --- 4. نظام السرقة (Rob) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    u, t = str(ctx.author.id), str(member.id)
    check_u(u); check_u(t)
    if user_data[t]['coins'] < 500: return await ctx.send("ما يستاهل تسرقه، طفران!")
    if random.random() > 0.7:
        amt = random.randint(200, 600)
        user_data[u]['coins'] += amt; user_data[t]['coins'] -= amt
        await ctx.send(f"🥷 سرقت {amt} كوينز من {member.mention}!")
    else:
        user_data[u]['coins'] -= 400; await ctx.send("👮 انقفشت وتغرمت 400 كوينز!")
    save_data(user_data)

# --- 5. لوحة الشرف (Top) ---
@bot.command()
async def top(ctx):
    # ترتيب المستخدمين حسب الكوينز
    sorted_users = sorted(user_data.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    leaderboard = ""
    for i, (uid, data) in enumerate(sorted_users):
        leaderboard += f"**#{i+1}** | <@{uid}> - `{data['coins']}` 💰\n"
    embed = discord.Embed(title="🏆 قائمة أغنى 10 لاعبين", description=leaderboard, color=0xffd700)
    await ctx.send(embed=embed)
@bot.command()
async def marry(ctx, member: discord.Member, amt: int):
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)

    # شروط الزواج
    if member.bot: return await ctx.send("🤖 ما تقدر تتزوج بوت!")
    if member == ctx.author: return await ctx.send("👤 ما تقدر تتزوج نفسك!")
    if user_data[u_id].get('partner') or user_data[p_id].get('partner'):
        return await ctx.send("💍 واحد منكم متزوج أصلاً!")
    if user_data[u_id]['coins'] < amt or amt <= 0:
        return await ctx.send("💰 رصيدك ما يكفي للمهر!")

    # سحب المهر مؤقتاً (أمانة عند البوت)
    user_data[u_id]['coins'] -= amt
    save_data(user_data)

    await ctx.send(f"💍 {member.mention}، هل تقبل الزواج من {ctx.author.mention} بمهر قدره {amt} كوينز؟\n*(اكتب **أقبل** أو **أرفض** خلال 30 ثانية)*")

    def check(m):
        return m.author == member and m.channel == ctx.channel and m.content in ['أقبل', 'أرفض']

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        
        if msg.content == 'أقبل':
            # إتمام الزواج
            user_data[u_id]['partner'] = p_id
            user_data[p_id]['partner'] = u_id
            user_data[p_id]['coins'] += amt # تحويل المهر للزوجة
            
            # --- إضافة الرتبة أوتوماتيكياً (Auto Role) ---
            role = discord.utils.get(ctx.guild.roles, name="متزوجين")
            if role:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            
            save_data(user_data)
            await ctx.send(f"🎊 مبروك! تم الزواج وإعطاء رتبة **متزوجين**. تحول المهر {amt} لـ {member.mention}")
            
        else:
            # رفض الزواج وإرجاع المهر
            user_data[u_id]['coins'] += amt
            save_data(user_data)
            await ctx.send(f"💔 {member.mention} رفض الزواج، رجعت فلوسك يا {ctx.author.mention}")

    except asyncio.TimeoutError:
        # انتهى الوقت (إرجاع المهر)
        user_data[u_id]['coins'] += amt
        save_data(user_data)
        await ctx.send(f"⏰ انتهى الوقت وما رد الطرف الثاني، رجعت لك المهر {amt}")

# --- أمر الانفصال (لسحب الرتبة) ---
@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    p_id = user_data[u_id].get('partner')
    
    if not p_id: return await ctx.send("أنت مو متزوج!")
    
    user_data[u_id]['partner'] = None
    if p_id in user_data: user_data[p_id]['partner'] = None
    
    # سحب الرتبة أوتوماتيكياً
    role = discord.utils.get(ctx.guild.roles, name="متزوجين")
    if role:
        await ctx.author.remove_roles(role)
        partner_member = ctx.guild.get_member(int(p_id))
        if partner_member: await partner_member.remove_roles(role)
    
    save_data(user_data)
    await ctx.send("💔 تم الانفصال وسحب الرتبة.")
from datetime import datetime, timedelta

# --- تعديل في التحقق من المستخدم ---
def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'dowry': 0}

@bot.command()
async def marry(ctx, member: discord.Member, amt: int):
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)

    if user_data[u_id].get('partner') or user_data[p_id].get('partner'):
        return await ctx.send("💍 واحد منكم متزوج!")
    if user_data[u_id]['coins'] < amt or amt < 500:
        return await ctx.send("💰 المهر قليل أو رصيدك ما يكفي (أقل مهر 500)!")

    # سحب المهر وتخزينه كأمانة
    user_data[u_id]['coins'] -= amt
    save_data(user_data)

    await ctx.send(f"💍 {member.mention}، تقبل بـ {ctx.author.mention} مهر {amt}؟ (اكتب **أقبل**)")

    def check(m): return m.author == member and m.channel == ctx.channel and m.content == 'أقبل'

    try:
        await bot.wait_for('message', timeout=30.0, check=check)
        
        # تسجيل الزواج والتاريخ
        user_data[u_id]['partner'] = p_id
        user_data[p_id]['partner'] = u_id
        user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data[u_id]['dowry'] = amt # حفظ قيمة المهر
        
        role = discord.utils.get(ctx.guild.roles, name="متزوجين")
        if role:
            await ctx.author.add_roles(role)
            await member.add_roles(role)
            
        save_data(user_data)
        await ctx.send(f"🎊 مبروك! المهر {amt} مجمد عند البوت لمدة أسبوع. إذا استمر الزواج بيتحول للطرف الثاني!")

    except:
        user_data[u_id]['coins'] += amt
        save_data(user_data)
        await ctx.send("💔 الغي الزواج ورجعت الفلوس.")

@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id].get('partner'): return await ctx.send("أنت مو متزوج!")

    p_id = user_data[u_id]['partner']
    m_date = datetime.strptime(user_data[u_id].get('marry_date'), "%Y-%m-%d %H:%M:%S")
    dowry = user_data[u_id].get('dowry', 0)
    
    # حساب هل مر أسبوع؟
    if datetime.now() < m_date + timedelta(days=7):
        # عقاب الانفصال السريع: المهر يروح للبنك وما يرجع لأحد!
        await ctx.send(f"⚠️ **انفصال مبكر!** بما أنه لم يمر أسبوع على الزواج، المهر ({dowry} كوينز) راح يروح للبنك غرامة.")
    else:
        # إذا مر أسبوع، المهر يتحول للطرف الثاني (أو ينقسم)
        user_data[p_id]['coins'] += dowry
        await ctx.send(f"💔 تم الانفصال بعد أسبوع. تم تحويل المهر {dowry} كوينز لـ <@{p_id}>.")

    # مسح بيانات الزواج وسحب الرتبة
    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    user_data[u_id]['marry_date'] = None
    role = discord.utils.get(ctx.guild.roles, name="متزوجين")
    if role:
        await ctx.author.remove_roles(role)
        partner = ctx.guild.get_member(int(p_id))
        if partner: await partner.remove_roles(role)
        
    save_data(user_data)
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

# --- شرط الرتبة ---
async def is_allowed(ctx):
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role: return True
    await ctx.send("❌ هذا الأمر خاص بمسؤولي الـ **فعاليات** فقط!")
    return False

# --- القائمة الشاملة ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 موسوعة سكاي كوين للألعاب", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!slots` `!dice`", inline=True)
    embed.add_field(name="🌪️ المسابقات", value="`!تحدي` `!math` `!top`", inline=True)
    embed.add_field(name="💍 النظام الاجتماعي", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    embed.set_footer(text="نظام عملات سكاي كوين المطور")
    await ctx.send(embed=embed)

# --- نظام الـ 2000 سؤال (بدون تكرار) ---
@bot.command()
async def تحدي(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 بنك الأسئلة فارغ حالياً!")
    
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(embed=discord.Embed(title="🌪️ سؤال التحدي", description=f"**{q_data['q']}**", color=0x00ff00))
    
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=25.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 2000
        save_data(user_data)
        await msg.reply(f"✅ كفو! أخذت 2000 **سكاي كوين**. (باقي {len(all_questions)} سؤال)")
    except:
        await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

# --- نظام الزواج (أسبوع + مهر مجمد + رتبة) ---
@bot.command()
async def marry(ctx, member: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u_id, p_id = str(ctx.author.id), str(member.id)
    check_u(u_id); check_u(p_id)

    if user_data[u_id]['partner']: return await ctx.send("💍 أنت متزوج بالفعل!")
    if user_data[u_id]['coins'] < amt or amt < 500: return await ctx.send("💰 رصيدك لا يكفي للمهر (الأدنى 500 سكاي كوين)!")

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
            await ctx.send("🎊 مبروك! المهر مجمد لمدة أسبوع لضمان جدية الزواج.")
        else:
            user_data[u_id]['coins'] += amt
            save_data(user_data)
            await ctx.send("💔 تم رفض الطلب واستعادة المبلغ.")
    except:
        user_data[u_id]['coins'] += amt
        save_data(user_data); await ctx.send("⏰ انتهى الوقت.")

@bot.command()
async def divorce(ctx):
    u_id = str(ctx.author.id)
    if not user_data[u_id].get('partner'): return
    
    p_id = user_data[u_id]['partner']
    m_date = datetime.strptime(user_data[u_id]['marry_date'], "%Y-%m-%d %H:%M:%S")
    dowry = user_data[u_id].get('dowry', 0)

    if datetime.now() < m_date + timedelta(days=7):
        await ctx.send(f"⚠️ انفصال قبل الأسبوع! ضاعت الـ {dowry} **سكاي كوين** غرامة.")
    else:
        user_data[p_id]['coins'] += dowry
        await ctx.send(f"💔 تم الانفصال وتحويل المهر {dowry} للطرف الثاني.")

    user_data[u_id]['partner'] = user_data[p_id]['partner'] = None
    role = discord.utils.get(ctx.guild.roles, name="متزوجين")
    if role:
        await ctx.author.remove_roles(role)
        partner = ctx.guild.get_member(int(p_id))
        if partner: await partner.remove_roles(role)
    save_data(user_data)

# --- أوامر الرصيد والعمل ---
@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid)
    await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']} **سكاي كوين**")

@bot.command()
async def work(ctx):
    uid = str(ctx.author.id); check_u(uid)
    amt = random.randint(100, 300)
    user_data[uid]['coins'] += amt; save_data(user_data)
    await ctx.send(f"👷 ربحت {amt} **سكاي كوين**")

# --- لوحة الشرف ---
@bot.command()
async def top(ctx):
    sorted_u = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}>: {d['coins']} 🪙" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 هوامير سكاي كوين", description=lb, color=0xffd700))

bot.run("TOKEN")
