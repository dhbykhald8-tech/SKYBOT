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
@bot.command(name="mycoins")
async def mycoins(ctx):
    data = load_data()
    u_id = str(ctx.author.id)
    balance = data.get("users", {}).get(u_id, {}).get("balance", 0)
    await ctx.reply(f"💰 رصيدك الحالي هو: **{balance:,}** سكاي كوينز")

class MarryView(discord.ui.View):
    def __init__(self, author, target):
        super().__init__(timeout=60)
        self.author = author
        self.target = target

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("❌ الطلب مو لك!", ephemeral=True)
        
        data = load_data()
        u_id, t_id = str(self.author.id), str(self.target.id)
        
        # التأكد من وجود بيانات المستخدمين
        if u_id not in data["users"]: data["users"][u_id] = {"balance": 0, "married_to": None}
        if t_id not in data["users"]: data["users"][t_id] = {"balance": 0, "married_to": None}
        
        data["users"][u_id]["married_to"] = t_id
        data["users"][t_id]["married_to"] = u_id
        data["users"][u_id]["balance"] -= 20000 
        save_data(data)
        await interaction.response.edit_message(content=f"💖 مبروك! {self.author.mention} و {self.target.mention} تزوجوا! 💍", view=None)

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("❌ مو أنت المقصود!", ephemeral=True)
        await interaction.response.edit_message(content=f"💔 تم رفض طلب الزواج..", view=None)

@bot.command(name="marry")
async def marry(ctx, member: discord.Member):
    if member == ctx.author: return await ctx.reply("ما يصير تتزوج نفسك 😂")
    
    data = load_data()
    u_id = str(ctx.author.id)
    balance = data.get("users", {}).get(u_id, {}).get("balance", 0)

    if balance < 20000:
        await ctx.reply(f"❌ لازم مهر 20,000! رصيدك الحالي: {balance:,}")
        return

    view = MarryView(ctx.author, member)
    await ctx.send(f"💍 {ctx.author.mention} يطلب الزواج من {member.mention}!\nهل تقبلين؟", view=view)

@bot.command(name="انفصال")
async def divorce(ctx):
    data = load_data()
    u_id = str(ctx.author.id)
    if u_id in data["users"] and data["users"][u_id].get("married_to"):
        t_id = data["users"][u_id]["married_to"]
        data["users"][u_id]["married_to"] = None
        if t_id in data["users"]: data["users"][t_id]["married_to"] = None
        save_data(data)
        await ctx.reply("💔 تم الانفصال بنجاح!")
    else:
        await ctx.reply("أنت عزوبي أصلاً!")
# --- محرك الألعاب واللفلات (حطه في بداية الملف) ---
game_config = {"current_q": None}
questions = {
    "من هو بطل Resident Evil 4؟": "ليون",
    "ما اسم الشيطان داخل إيتادوري؟": "سوكونا",
    "من هو الوميض الأصفر في ناروتو؟": "ميناتو"
}

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # زيادة XP مع كل رسالة عشان يرتفع اللفل
    update_data_with_xp(message.author.id, 2)

    # التحقق من إجابة اللعبة
    global game_config
    if game_config["current_q"] in questions:
        if message.content.strip() == questions[game_config["current_q"]]:
            is_up, lvl = update_data_with_xp(message.author.id, 30, 2000)
            await message.reply(f"✅ صح! فزت بـ 2000 كوينز و 30 XP.")
            if is_up: await message.send(f"🎊 مبروك! وصلت لفل **{lvl}**")
            game_config["current_q"] = None
            return

    await bot.process_commands(message)

@bot.command(name="سؤال")
async def start_game(ctx):
    game_config["current_q"] = random.choice(list(questions.keys()))
    await ctx.send(f"❓ **سؤال اللعبة:**\n{game_config['current_q']}")

@bot.command(name="profile")
async def show_profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user = data["users"].get(str(member.id), {"balance": 0, "level": 1, "xp": 0})
    embed = discord.Embed(title=f"👤 ملف {member.display_name}", color=0x3498db)
    embed.add_field(name="🆙 المستوى", value=user.get("level", 1), inline=True)
    embed.add_field(name="✨ الـ XP", value=f"{user.get('xp', 0)}/100", inline=True)
    embed.add_field(name="💰 الرصيد", value=f"{user.get('balance', 0):,}", inline=False)
    await ctx.reply(embed=embed)

@bot.command(name="steal")
async def steal(ctx, member: discord.Member):
    if member == ctx.author:
        return await ctx.reply("تبوق نفسك؟ صرنا في GTA؟ 😂")
        
    data = load_data()
    u_id = str(ctx.author.id)
    t_id = str(member.id)
    
    if u_id not in data["users"]: data["users"][u_id] = {"balance": 0}
    if t_id not in data["users"]: data["users"][t_id] = {"balance": 0}

    # نسبة النجاح 20% والفشل 80%
    if random.randint(1, 100) <= 20:
        stolen = random.randint(20000, 50000)
        data["users"][u_id]["balance"] += stolen
        data["users"][t_id]["balance"] -= stolen
        save_data(data)
        await ctx.reply(f"🎯 **عملية ناجحة!** سرقت **{stolen}** كوينز من {member.mention}!")
    else:
        penalty = 50000# الغرامة
        current_bal = data["users"][u_id].get("balance", 0)
        
        if current_bal < penalty:
            try:
                # كتم 5 دقائق (أنت أضفت timedelta فوق في سطر 7)
                await ctx.author.timeout(timedelta(minutes=5), reason="طفران ويبي يسرق")
                await ctx.reply(f"🚨 انصدت وأنت طفران! تم كتمك **5 دقائق** عشان تتربى. 🤐")
            except:
                await ctx.reply(f"🚨 انصدت وما عندك فلوس، بس ما قدرت أكتمك!")
        else:
            data["users"][u_id]["balance"] -= penalty
            save_data(data)
            await ctx.reply(f"🚨 **انقفطت!** حاول يسرق وانصاد، ودفع غرامة **{penalty}** كوينز.")
# 1. إعداد الأسئلة
game_questions = {
    "من هو بطل Resident Evil 4؟": "ليون",
    "ما اسم الشيطان داخل إيتادوري؟": "سوكونا",
    "ما هو اللقب الذي يطلق على ميناتو؟": "الوميض الأصفر",
    "كم مهر الزواج في هذا البوت؟": "20000"
}
active_question = None

# 2. دالة تحديث اللفل والـ XP (بدقة)
def add_user_xp(user_id, xp_amount, money_reward=0):
    data = load_data()
    u_id = str(user_id)
    if u_id not in data["users"]:
        data["users"][u_id] = {"balance": 0, "married_to": None, "xp": 0, "level": 1}
    
    # التأكد من وجود الخانات عشان ما يكرش
    user = data["users"][u_id]
    user["xp"] = user.get("xp", 0) + xp_amount
    user["balance"] = user.get("balance", 0) + money_reward
    
    # نظام اللفل: كل 100 XP يرفع لفل
    leveled_up = False
    current_xp = user["xp"]
    current_lvl = user.get("level", 1)
    
    if current_xp >= 100:
        user["xp"] = current_xp - 100
        user["level"] = current_lvl + 1
        leveled_up = True
    
    save_data(data)
    return leveled_up, user["level"]
# --- نظام اللفل والتشغيل الموحد ---

@bot.event
async def on_ready():
    # هذي تطبع في Railway إن البوت اشتغل تمام
    print(f"✅ {bot.user} متصل وشغال.. نظام اللفل جاهز!")

@bot.event
async def on_message(message):
    # عشان البوت ما يرد على نفسه ويكرر
    if message.author == bot.user:
        return
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # --- نظام اللفل ---
    data = load_data()
    u_id = str(message.author.id)
    if u_id not in data["users"]:
        data["users"][u_id] = {"balance": 0, "xp": 0, "level": 1}
    
    user = data["users"][u_id]
    user["xp"] = user.get("xp", 0) + 5
    
    if user["xp"] >= 100:
        user["xp"] = 0
        user["level"] = user.get("level", 1) + 1
        await message.channel.send(f"🆙 كفو {message.author.mention}! وصلت لفل **{user['level']}**")
    
    save_data(data)
    # --- نهاية اللفل ---

    await bot.process_commands(message)

# هذا الجزء لازم يكون بآخر الملف وبدون أي فراغات قبله
token = os.getenv("TOKEN")
if token:
    bot.run(token)
