import discord
from discord.ext import commands, tasks
import random
import json
import asyncio
import os
from datetime import datetime, timedelta

# إعدادات البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قاعدة البيانات
DATA_FILE = 'sky_system_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"users": {}, "marriages": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

def register_user(user_id):
    u_id = str(user_id)
    if u_id not in data["users"]:
        data["users"][u_id] = {"balance": 1000, "xp": 0, "level": 1, "partner": None}

# --- نظام اللفل والسكاي كوين التلقائي ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    register_user(message.author.id)
    u_id = str(message.author.id)
    
    # زيادة XP و 2 كوينز لكل رسالة
    data["users"][u_id]["xp"] += random.randint(5, 15)
    data["users"][u_id]["balance"] += 2
    
    # ارتقاء المستوى
    xp_needed = data["users"][u_id]["level"] * 200
    if data["users"][u_id]["xp"] >= xp_needed:
        data["users"][u_id]["level"] += 1
        data["users"][u_id]["xp"] = 0
        await message.channel.send(f"🆙 | مبروك {message.author.mention}! وصلت لفل **{data['users'][u_id]['level']}**")
    
    save_data(data)
    await bot.process_commands(message)

# --- نظام السرقة المطور (Steal) ---
@bot.command()
async def steal(ctx, member: discord.Member):
    register_user(ctx.author.id)
    u_id = str(ctx.author.id)
    
    # التحقق من الرصيد للمخاطرة
    if data["users"][u_id]["balance"] < 5000:
        return await ctx.send("❌ لازم يكون معك 5000 كوينز على الأقل عشان تخاطر!")

    if random.random() < 0.05: # نجاح 5%
        stolen_amt = random.randint(1000, 5000)
        data["users"][str(member.id)]["balance"] -= stolen_amt
        data["users"][u_id]["balance"] += stolen_amt
        await ctx.send(f"🥷 **عملية ناجحة!** سرقت {stolen_amt} سكاي كوينز من {member.display_name}")
    else:
        # عقوبة الفشل (غرامة 5000 + تايم آوت 3 دقائق)
        data["users"][u_id]["balance"] -= 5000
        try:
            await ctx.author.timeout(timedelta(minutes=3), reason="فشل في عملية سرقة")
            await ctx.send(f"🚨 **انصتّ!** فشلت السرقة. تم تغريمك **5000 كوينز** وطردك من الشات (تايم آوت) لمدة 3 دقائق!")
        except:
            await ctx.send(f"🚨 **فشلت السرقة!** تم تغريمك **5000 كوينز** (البوت يحتاج صلاحية Timeout لكتمك).")
    
    save_data(data)

# --- نظام الزواج (المهر 20k + شرط الأسبوع) ---
@bot.command()
async def marry(ctx, member: discord.Member):
    register_user(ctx.author.id)
    register_user(member.id)
    u_id, m_id = str(ctx.author.id), str(member.id)
    
    if data["users"][u_id]["balance"] < 20000:
        return await ctx.send("❌ المهر 20,000 كوينز، رصيدك ما يكفي!")

    view = discord.ui.View()
    btn = discord.ui.Button(label="موافقة 💍", style=discord.ButtonStyle.green)
    
    async def callback(interaction):
        if interaction.user != member: return
        data["users"][u_id]["balance"] -= 20000
        data["users"][m_id]["balance"] += 20000
        data["users"][u_id]["partner"], data["users"][m_id]["partner"] = m_id, u_id
        data["marriages"][f"{u_id}_{m_id}"] = datetime.now().isoformat()
        save_data(data)
        role = discord.utils.get(ctx.guild.roles, name="متزوج/ة")
        if role:
            await ctx.author.add_roles(role)
            await member.add_roles(role)
        await interaction.response.send_message(f"💍 مبروك الزواج! تم تحويل المهر {member.mention}")

    btn.callback = callback
    view.add_item(btn)
    await ctx.send(f"{member.mention}، تقبل الزواج من {ctx.author.mention}؟", view=view)

# --- أوامر الاقتصاد العامة ---
@bot.command(aliases=['coins', 'bal'])
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    register_user(member.id)
    await ctx.send(f"💰 رصيد {member.display_name}: **{data['users'][str(member.id)]['balance']}** سكاي كوينز.")

@bot.command()
async def top(ctx):
    sorted_users = sorted(data["users"].items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
    emb = discord.Embed(title="🏆 أغنى 10 في سكاي كوينز", color=0xffd700)
    for i, (uid, info) in enumerate(sorted_users, 1):
        u = bot.get_user(int(uid))
        name = u.name if u else f"عضو ({uid})"
        emb.add_field(name=f"{i}. {name}", value=f"{info['balance']} كوينز", inline=False)
    await ctx.send(embed=emb)
import discord
from discord.ext import commands
import os
import random

# إعدادات البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قائمة الألعاب الـ 20 (10 فردية و10 جماعية)
games_data = {
    "فردية 👤": [
        {"name": "لو خيروك", "desc": "يعطيك خيارين صعبين وعليك تختار"},
        {"name": "كت تويت", "desc": "تغريدات وأسئلة عشوائية ممتعة"},
        {"name": "تخمين الرقم", "desc": "البوت يختار رقم وأنت تحاول تعرفه"},
        {"name": "عواصم", "desc": "اختبر معلوماتك في عواصم الدول"},
        {"name": "أعلام", "desc": "يعطيك إيموجي علم ولازم تعرف الدولة"},
        {"name": "إكمال المثل", "desc": "مثل شعبي ناقص ولازم تكمله"},
        {"name": "حساب ذهني", "desc": "مسائل رياضيات سريعة للذكاء"},
        {"name": "صراحة", "desc": "سؤال صريح ومحرج لازم تجاوب عليه"},
        {"name": "ترتيب كلمات", "desc": "يعطيك كلمة ملخبطة ولازم ترتبها"},
        {"name": "أسئلة أنمي", "desc": "اختبر خبرتك في عالم الأنمي"}
    ],
    "جماعية 👥": [
        {"name": "فعالية السرعة", "desc": "أسرع واحد يكتب الكلمة يفوز"},
        {"name": "من فينا", "desc": "تصويت بين الأعضاء على صفة معينة"},
        {"name": "سجن الأعضاء", "desc": "تسجن عضو وتنتظر مين يفزع له"},
        {"name": "تحدي الرموز", "desc": "فك شفرات الإيموجي والرموز"},
        {"name": "نبات حيوان", "desc": "اللعبة الشهيرة بحرف عشوائي"},
        {"name": "إيجاد الإيموجي", "desc": "إيموجي ضايع وسط زحمة ولازم تطلعه"},
        {"name": "كشف الكذب", "desc": "عضو يقول 3 أشياء وواحد منها كذب"},
        {"name": "حرب العملات", "desc": "تحدي بين الأعضاء على رصيد الكوينز"},
        {"name": "طلب ارتباط", "desc": "فعالية زواج وهمي وتفاعل بالشات"},
        {"name": "قتال السيرفر", "desc": "تحدي قتالي (وهمي) بين عضوين"}
    ]
}

@bot.event
async def on_ready():
    print(f"🎮 قائمة الألعاب جاهزة للعمل | {bot.user.name}")

# أمر عرض قائمة الألعاب
@bot.command()
async def games(ctx):
    embed = discord.Embed(
        title="🎮 Sky Bot Games | قائمة ألعاب سكاي",
        description="استمتع بأفضل 20 لعبة فردية وجماعية داخل السيرفر!\nللبدء، اكتب اسم اللعبة بعد علامة **!**",
        color=discord.Color.blue()
    )
    
    # تنسيق الألعاب الفردية
    fardya = ""
    for game in games_data["فردية 👤"]:
        fardya += f"• **{game['name']}**\n"
    embed.add_field(name="👤 ألعاب فردية (10)", value=fardya, inline=True)

    # تنسيق الألعاب الجماعية
    jamaya = ""
    for game in games_data["جماعية 👥"]:
        jamaya += f"• **{game['name']}**\n"
    embed.add_field(name="👥 ألعاب جماعية (10)", value=jamaya, inline=True)

    embed.set_footer(text=f"طلب بواسطة: {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.set_image(url="https://i.imgur.com/example_image.png") # يمكنك وضع رابط صورة جمالية هنا
    
    await ctx.send(embed=embed)

# --- أمثلة تشغيل الألعاب (تقدر تضيف الأكواد لكل لعبة تحت) ---

@bot.command(name="")
async def choose_game(ctx):
    options = ["تآكل بصلة نية 🧅", "تسبح بثلج ❄️", "تنام بالشارع 🛣️", "تعطي كل كوينزك للي فوقك 💰"]
    q = f"{random.choice(options)} أو {random.choice(options)}؟"
    await ctx.send(f"🤔 **لو خيروك:**\n{q}")

@bot.command(name="سرعة")
async def speed_game(ctx):
    words = ["سكاي", "ديسكورد", "برمجة", "كوينز", "زواج", "سرقة"]
    word = random.choice(words)
    await ctx.send(f"⚡ أسرع واحد يكتب: **{word}**")
import discord
from discord.ext import commands
import json

# دالة لتحميل البيانات (تأكد أن اسم الملف هو نفس اسم ملفك الأساسي)
DATA_FILE = 'sky_system_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- كود كلمة السر والفلوس (منفصل) ---

@bot.command()
async def secret_code(ctx, code: str):
    # كلمة السر الخاصة بك
    SECRET = "SkyAdmin10M" 
    
    if code == SECRET:
        data = load_data()
        u_id = str(ctx.author.id)
        
        # التأكد من وجود المستخدم في البيانات
        if u_id not in data["users"]:
            data["users"][u_id] = {"balance": 0, "xp": 0, "level": 1}
            
        # إضافة الـ 10 مليون
        data["users"][u_id]["balance"] += 10000000
        save_data(data)
        
        await ctx.send(f"💰 **تم تفعيل الكود السري!** مبروك يا وحش، انضاف لحسابك 10,000,000 سكاي كوين.")
    else:
        await ctx.send("❌ كلمة السر غلط، لا تحاول تسرق البنك!")

@bot.command()
async def mycoins(ctx):
    data = load_data()
    u_id = str(ctx.author.id)
    
    if u_id in data["users"]:
        balance = data["users"][u_id]["balance"]
        await ctx.send(f"💳 رصيدك الحالي هو: **{balance:,}** سكاي كوينز.")
    else:
        await ctx.send("❌ ليس لديك حساب بنكي حالياً، تفاعل في الشات لفتح حساب!")
@bot.command()
async def marry(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("💍 منشن الشخص اللي تبي تتزوجه! مثال: `!marry @user` ")
    
    if member.id == ctx.author.id:
        return await ctx.send("😂 ما يصير تتزوج نفسك، دور لك أحد ثاني!")

    if member.bot:
        return await ctx.send("🤖 البوتات ما تتزوج، عندها شغل!")

    data = load_data()
    u_id = str(ctx.author.id)
    m_id = str(member.id)
    
    # التأكد من الرصيد (المهر 20 ألف)
    user_balance = data["users"].get(u_id, {}).get("balance", 0)
    if user_balance < 20000:
        return await ctx.send(f"❌ لازم يكون معك **20,000** كوينز للمهر! رصيدك الحالي: {user_balance:,}")

    # رسالة طلب الزواج مع الأزرار
    embed = discord.Embed(
        title="💍 طلب زواج جديد!",
        description=f"{ctx.author.mention} يبي يتزوجك يا {member.mention}!\n\n**المهر المحول:** 20,000 كوينز 💰",
        color=discord.Color.fuchsia()
    )
    
    class MarriageView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60) # الطلب ينتهي بعد دقيقة

        @discord.ui.button(label="أقبل 💍", style=discord.ButtonStyle.green)
        async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != member.id:
                return await interaction.response.send_message("الطلب مو لك! 🤫", ephemeral=True)
            
            # تنفيذ عملية الزواج ماليًا
            data["users"][u_id]["balance"] -= 20000
            if m_id not in data["users"]: data["users"][m_id] = {"balance": 0, "xp": 0, "level": 1}
            data["users"][m_id]["balance"] += 20000
            
            # تسجيل الزواج في الداتا
            data["users"][u_id]["married_to"] = m_id
            data["users"][m_id]["married_to"] = u_id
            save_data(data)
            
            await interaction.response.edit_message(content=f"🎉 مبروك! {ctx.author.mention} و {member.mention} صاروا متزوجين!", embed=None, view=None)

        @discord.ui.button(label="أرفض ❌", style=discord.ButtonStyle.red)
        async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != member.id:
                return await interaction.response.send_message("الطلب مو لك!", ephemeral=True)
            await interaction.response.edit_message(content=f"💔 {member.mention} رفض طلب الزواج.. خيرها بغيرها!", embed=None, view=None)

    await ctx.send(embed=embed, view=MarriageView())
# --- كود لعبة من فينا ---
@bot.command(name="")
async def who_is_it(ctx):
    questions = [
        "من فينا أكثر واحد ينام؟ 😴",
        "من فينا أكثر واحد يسحب على أخوياه؟ 🏃‍♂️",
        "من فينا الهامور اللي بيصير مليونير؟ 💰",
        "من فينا أكثر واحد يحب الأكل؟ 🍔",
        "من فينا اللي دايم يضيع في الألعاب؟ 🧩",
        "من فينا أكثر واحد يعصب وهو يلعب؟ 😡"
    ]
    import random
    question = random.choice(questions)
    
    embed = discord.Embed(
        title="🤔 من فينا؟",
        description=f"**{question}**\n\nمنشن الشخص اللي تحس إنه هو المقصود! 😂",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# --- كود لعبة لو خيروك ---
@bot.command(name="لو_خيروك")
async def this_or_that(ctx):
    choices = [
        "تاكل صرصور حي 🪳 ولا تشرب عصير بصل؟ 🧅",
        "تنام في غابة مسكونة 👻 ولا تسبح مع قروش؟ 🦈",
        "تصير غني بس وحيد 💰 ولا فقير ومعك أعز أخوياك؟ 🤝",
        "تلعب Resident Evil في الحقيقة 🧟 ولا تدخل عالم Jujutsu Kaisen؟ 🔥"
  
    choice = random.choice(choices)
    
    embed = discord.Embed(
        title="⚖️ لو خيروك..",
        description=f"**{choice}**",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
import asyncio
import random
from discord.ext import tasks

# قائمة الـ 100 سؤال (تقدر تزيدها أو تغيرها)
questions_list = [
    "ما هو أطول نهر في العالم؟",
    "من هو مؤلف مانجا ون بيس؟",
    "ما هي عاصمة اليابان؟",
    "كم عدد سجدات التلاوة في القرآن الكريم؟",
    "في أي عام انتهت الحرب العالمية الثانية؟",
    # ... أضف بقية الـ 100 سؤال هنا بنفس التنسيق
@tasks.loop(hours=1)
async def auto_question_task():
    # البوت بيبحث عن الروم بكل السيرفرات اللي هو فيها
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name="الشات-العام💬")
        
        if channel:
            # اختيار سؤال عشوائي
            question = random.choice(questions_list)
            
            embed = discord.Embed(
                title="❓ سؤال الساعة!",
                description=f"**{question}**\n\nأول واحد يجاوب صح له **2000 كوينز**! 💰",
                color=discord.Color.gold()
            )
            await channel.send(embed=embed)
            print(f"✅ تم إرسال السؤال في روم: {channel.name}")
            break # عشان يرسل في روم واحدة بس وما يكرر
import random
from discord.ext import tasks

# --- 1. قائمة الـ 100 سؤال (جهزت لك عينة وبإمكانك تكملتها) ---
questions_list = [
    "ما هي عاصمة الكويت؟", "من هو بطل أنمي ون بيس؟", "كم عدد قارات العالم؟", 
    "ما هو أسرع حيوان بري؟", "من فاز بكأس العالم 2022؟", "ما هي عاصمة السعودية؟",
    "ما هو لون غلاف مانجا Blue Lock المجلد الأول؟", "من هو مؤلف جوجوتسو كايسن؟",
    "ما هي عاصمة فرنسا؟", "كم عدد كواكب المجموعة الشمسية؟", "ما هو أثقل كوكب؟",
    "من هو الهداف التاريخي لكرة القدم؟", "ما هو اسم بطل Resident Evil 4؟",
    "كم عدد حلقات الجزء الأول من هوريميا؟", "من قتل غوجو في مانجا JJK؟"
    # أضف هنا بقية الأسئلة حتى تصل لـ 100...
]

# قائمة لحفظ الأسئلة اللي طلعت عشان ما تتكرر
asked_questions = []

# --- 2. نظام التوقيت التلقائي ---
@tasks.loop(hours=1)
async def auto_question_task():
    global asked_questions
    
    # ابحث عن الروم بالاسم (الشات-العام💬)
    target_channel = None
    for guild in bot.guilds:
        target_channel = discord.utils.get(guild.channels, name="الشات-العام💬")
        if target_channel:
            break

    if target_channel:
        # إذا خلصت كل الأسئلة، صفر القائمة
        if len(asked_questions) >= len(questions_list):
            asked_questions = []
            
        # اختيار سؤال لم يظهر من قبل
        available = [q for q in questions_list if q not in asked_questions]
        if not available: return # حماية في حال كانت القائمة فارغة
        
        question = random.choice(available)
        asked_questions.append(question)
        
        embed = discord.Embed(
            title="❓ سؤال الساعة التلقائي",
            description=f"**{question}**\n\nأول واحد يجاوب صح له **2000 كوينز**! 💰",
            color=discord.Color.from_rgb(255, 215, 0) # لون ذهبي
        )
        await target_channel.send(embed=embed)
        print(f"✅ أرسلت سؤال: {question}")

# --- 3. تشغيل الـ Task عند تشغيل البوت ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} متصل وراكب على نظام ويندوز 11!")
    if not auto_question_task.is_running():
        auto_question_task.start()

# تشغيل البوت بسحب التوكن من GitHub
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ خطأ: التوكن غير موجود في متغيرات البيئة!")
