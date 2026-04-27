import discord
from discord.ext import commands, tasks
import os
import random
import json

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
DATA_FILE = "data.json"
CHAT_ROOM_NAME = "الشات-العام💬" # تأكد من مطابقة الاسم تماماً

# متغيرات النظام
current_q = {"q": "", "a": ""}
questions_pool = []

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

user_data = load_data()

# --- 100 سؤال منوعة ---
ALL_QUESTIONS = [
    # قيمنق وبيسي
    {"q": "ما هو اختصار وحدة المعالجة المركزية؟", "a": "CPU"},
    {"q": "بطل لعبة God of War؟", "a": "كريتوس"},
    {"q": "أشهر كرت شاشة اقتصادي من انفيديا؟", "a": "GTX 1660"},
    {"q": "لعبة شوتر وبناء مشهورة؟", "a": "فورتنايت"},
    {"q": "اختصار ذاكرة الوصول العشوائي؟", "a": "RAM"},
    {"q": "بطل لعبة Uncharted؟", "a": "نيثان دريك"},
    {"q": "لعبة رعب في مدينة راكون سيتي؟", "a": "Resident Evil"},
    {"q": "شركة صنعت جهاز بلايستيشن؟", "a": "سوني"},
    {"q": "لعبة كرة قدم بالسيارات؟", "a": "روكيت ليغ"},
    {"q": "أعلى دقة وضوح حالياً في الشاشات؟", "a": "8K"},
    {"q": "نظام تشغيل أغلب أجهزة البيسي؟", "a": "ويندوز"},
    {"q": "لعبة مشهورة عالمها من المكعبات؟", "a": "ماينكرافت"},
    {"q": "ماذا يرمز اختصار GPU؟", "a": "كرت الشاشة"},
    {"q": "بطلة لعبة Tomb Raider؟", "a": "لارا كروفت"},
    {"q": "برنامج تواصل أساسي للقيمرز؟", "a": "ديسكورد"},
    {"q": "لعبة شوتر تكتيكية من شركة Riot؟", "a": "فالورانت"},
    {"q": "أداة تستخدم لتبريد المعالج؟", "a": "مبرد"},
    {"q": "ما هو محرك ألعاب شركة Epic؟", "a": "Unreal Engine"},
    {"q": "لعبة فازت بلعبة العام 2023؟", "a": "Baldur's Gate 3"},
    {"q": "أول جهاز من نينتندو؟", "a": "NES"},

    # أفلام ومسلسلات
    {"q": "مسلسل بطله ريك غرايمز والزومبي؟", "a": "The Walking Dead"},
    {"q": "ممثل دور الجوكر في Dark Knight؟", "a": "هيث ليدجر"},
    {"q": "مسلسل كوري فيه ألعاب موت؟", "a": "Squid Game"},
    {"q": "بطل أفلام Mission Impossible؟", "a": "توم كروز"},
    {"q": "مسلسل صراع العروش؟", "a": "Game of Thrones"},
    {"q": "فيلم أحلام من إخراج نولان؟", "a": "Inception"},
    {"q": "مسلسل عصابة تسرق البنك؟", "a": "La Casa de Papel"},
    {"q": "بطل مسلسل بريزون بريك؟", "a": "مايكل سكوفيلد"},
    {"q": "فيلم الكائنات الزرقاء؟", "a": "Avatar"},
    {"q": "أول فيلم في عالم مارفل؟", "a": "Iron Man"},
    {"q": "مسلسل كيميائي يطبخ مخدرات؟", "a": "Breaking Bad"},
    {"q": "الغابة التي عاش فيها ماوكلي؟", "a": "سيوني"},
    {"q": "فيلم الدمية تشاكي؟", "a": "Child's Play"},
    {"q": "مخرج فيلم تايتانيك؟", "a": "جيمس كاميرون"},
    {"q": "مسلسل قوى خارقة في الثمانينات؟", "a": "Stranger Things"},
    {"q": "بطل أفلام جون ويك؟", "a": "كيانو ريفز"},
    {"q": "مدرسة هاري بوتر؟", "a": "هوجوورتس"},
    {"q": "فيلم ديناصورات في حديقة؟", "a": "Jurassic Park"},
    {"q": "أنمي صبي يريد ملك القراصنة؟", "a": "One Piece"},
    {"q": "عدو باتمان اللدود؟", "a": "الجوكر"},

    # كيمياء وعلوم
    {"q": "الرمز الكيميائي للماء؟", "a": "H2O"},
    {"q": "الرمز الكيميائي للذهب؟", "a": "Au"},
    {"q": "الرمز الكيميائي للأكسجين؟", "a": "O2"},
    {"q": "أخف عنصر كيميائي؟", "a": "الهيدروجين"},
    {"q": "الرمز الكيميائي لملح الطعام؟", "a": "NaCl"},
    {"q": "الكوكب الأحمر؟", "a": "المريخ"},
    {"q": "أقرب كوكب للشمس؟", "a": "عطارد"},
    {"q": "أكبر كوكب؟", "a": "المشتري"},
    {"q": "الغاز الذي نتنفسه؟", "a": "الأكسجين"},
    {"q": "معدن سائل؟", "a": "الزئبق"},
    {"q": "الرمز الكيميائي للحديد؟", "a": "Fe"},
    {"q": "الرمز الكيميائي للفضة؟", "a": "Ag"},
    {"q": "مادة صلبة من الكربون؟", "a": "الألماس"},
    {"q": "القوة التي تسحب للأرض؟", "a": "الجاذبية"},
    {"q": "وحدة قياس التيار؟", "a": "الأمبير"},
    {"q": "غاز الضحك؟", "a": "أكسيد النيتروز"},
    {"q": "الطبقة التي تحمي الأرض؟", "a": "الأوزون"},
    {"q": "أسرع شيء في الكون؟", "a": "الضوء"},
    {"q": "جهاز رؤية النجوم؟", "a": "تلسكوب"},
    {"q": "درجة غليان الماء؟", "a": "100"},

    # عامة
    {"q": "عاصمة الكويت؟", "a": "الكويت"},
    {"q": "عاصمة السعودية؟", "a": "الالرياض"},
    {"q": "مخترع المصباح؟", "a": "اديسون"},
    {"q": "عدد أركان الإسلام؟", "a": "5"},
    {"q": "أطول نهر؟", "a": "النيل"},
    {"q": "أكبر قارة؟", "a": "آسيا"},
    {"q": "قلوب الأخطبوط؟", "a": "3"},
    {"q": "عملة الكويت؟", "a": "دينار"},
    {"q": "أكبر دولة مساحة؟", "a": "روسيا"},
    {"q": "مكتشف أمريكا؟", "a": "كولومبوس"},
    {"q": "أيام السنة البسيطة؟", "a": "365"},
    {"q": "عاصمة فرنسا؟", "a": "باريس"},
    {"q": "أصغر دولة؟", "a": "الفاتيكان"},
    {"q": "لغة البرازيل؟", "a": "البرتغالية"},
    {"q": "سفينة الصحراء؟", "a": "الجمل"},
    {"q": "أعلى قمة جبل؟", "a": "إفرست"},
    {"q": "أسنان الإنسان البالغ؟", "a": "32"},
    {"q": "لون الزمرد؟", "a": "أخضر"},
    {"q": "مخترع الهاتف؟", "a": "غراهام بيل"},
    {"q": "أكبر المحيطات؟", "a": "الهادي"},

    # أنمي
    {"q": "بطل دراغون بول؟", "a": "غوكو"},
    {"q": "بطل نارتو؟", "a": "نارتو"},
    {"q": "أنمي مفكرة الموت؟", "a": "Death Note"},
    {"q": "بطل هجوم العمالقة؟", "a": "إيرين"},
    {"q": "صديق لوفي السياف؟", "a": "زورو"},
    {"q": "كرات التنين عددها؟", "a": "7"},
    {"q": "أنمي قاتل الشياطين؟", "a": "Demon Slayer"},
    {"q": "عين اليوتشيها؟", "a": "شارينقان"},
    {"q": "صديق كيلوا؟", "a": "غون"},
    {"q": "وحش نارتو؟", "a": "كوراما"},
    {"q": "لقب لوفي؟", "a": "قبعة القش"},
    {"q": "أذكى شخصية في ديث نوت؟", "a": "إل"},
    {"q": "والد لوفي؟", "a": "دراغون"},
    {"q": "قرية نارتو؟", "a": "كونوها"},
    {"q": "ملك اللعنات؟", "a": "سوكونا"},
    {"q": "بطل بليتش؟", "a": "إيتشيغو"},
    {"q": "قائد الفرقة الأولى في بليتش؟", "a": "ياماموتو"},
    {"q": "بطل فينلاند ساغا؟", "a": "ثورفين"},
    {"q": "مدرب نارتو؟", "a": "ككاشي"},
    {"q": "شقيق إيس ولوفي؟", "a": "سابو"}
]

@bot.event
async def on_ready():
    print(f'Sky Bot is online as {bot.user}')
    auto_event.start()

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    
    if uid not in user_data: 
        user_data[uid] = {'coins': 100, 'xp': 0, 'level': 1, 'partner': None}
    
    # تحديد الحساب (مشترك أو فردي)
    target_id = uid
    if user_data[uid].get('partner'):
        p_id = user_data[uid]['partner']
        target_id = uid if int(uid) < int(p_id) else p_id

    # نظام الأسئلة
    global current_q
    if current_q["a"] and message.channel.name == CHAT_ROOM_NAME:
        if message.content.strip().lower() == current_q["a"].lower():
            user_data[target_id]['coins'] += 2000
            save_data(user_data)
            await message.reply("✅ كفو! إجابة صحيحة، أخذت 2000 كوينز للحساب! 💰")
            current_q = {"q": "", "a": ""}

    # ربح تلقائي
    user_data[target_id]['coins'] += 2
    user_data[uid]['xp'] += 5
    save_data(user_data)
    await bot.process_commands(message)

# --- الفعالية التلقائية كل ساعة ---
@tasks.loop(hours=1)
async def auto_event():
    channel = discord.utils.get(bot.get_all_channels(), name=CHAT_ROOM_NAME)
    if not channel: return
    
    global current_q, questions_pool
    if not questions_pool:
        questions_pool = ALL_QUESTIONS.copy()
        random.shuffle(questions_pool)

    current_q = questions_pool.pop()
    embed = discord.Embed(title="🎮 فعالية سكاي المنوعة", 
                          description=f"**السؤال:** {current_q['q']}\n\nأسرع واحد يجاوب ياخذ **2000 كوينز**!", 
                          color=0x3498db)
    await channel.send(embed=embed)

# --- أوامر الزواج والحساب المشترك ---
@bot.command()
async def marry(ctx, member: discord.Member, amount: int):
    uid, mid = str(ctx.author.id), str(member.id)
    if user_data[uid]['coins'] < amount: return await ctx.send("❌ ما عندك المهر!")
    if user_data[uid].get('partner') or user_data[mid].get('partner'): return await ctx.send("أحدكم متزوج!")

    view = discord.ui.View()
    async def confirm(i):
        if i.user != member: return
        user_data[uid]['partner'], user_data[mid]['partner'] = mid, uid
        user_data[uid]['coins'] -= amount
        user_data[mid]['coins'] += amount
        
        # دمج الأرصدة
        main = uid if int(uid) < int(mid) else mid
        other = mid if main == uid else uid
        user_data[main]['coins'] += user_data[other]['coins']
        user_data[other]['coins'] = 0
        save_data(user_data)
        await i.response.edit_message(content=f"💍 مبروك الزواج والحساب المشترك! المهر: {amount}", view=None)

    btn = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green)
    btn.callback = confirm
    view.add_item(btn)
    await ctx.send(f"💍 {member.mention}، يقدم لك {ctx.author.mention} مهر {amount}.. موافقة؟", view=view)

@bot.command()
async def divorce(ctx):
    uid = str(ctx.author.id)
    if not user_data[uid].get('partner'): return
    pid = user_data[uid]['partner']
    main = uid if int(uid) < int(pid) else pid
    half = user_data[main]['coins'] // 2
    user_data[uid]['coins'], user_data[pid]['coins'] = half, half
    user_data[uid]['partner'], user_data[pid]['partner'] = None, None
    save_data(user_data)
    await ctx.send("💔 تم الانفصال وتقسيم الحساب بالنص.")

# --- أوامر أساسية ---
@bot.command(aliases=['bal', 'فلوس'])
async def balance(ctx, member: discord.Member = None):
    m = member or ctx.author
    uid = str(m.id)
    if user_data.get(uid, {}).get('partner'):
        p = user_data[uid]['partner']
        main = uid if int(uid) < int(p) else p
        await ctx.send(f"👪 حساب عائلة **{m.display_name}**: `{user_data[main]['coins']}` كوينز")
    else:
        await ctx.send(f"💰 رصيد **{m.display_name}**: `{user_data.get(uid, {'coins':0})['coins']}`")

@bot.command()
async def sky10(ctx):
    user_data[str(ctx.author.id)]['coins'] += 10000000
    save_data(user_data)
    await ctx.send("💰 تم إضافة 10 مليون عملة!")
    try: await ctx.message.delete()
    except: pass

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
# --- أمر الزواج مع إعطاء الرتبة ---
@bot.command()
async def marry(ctx, member: discord.Member, amount: int):
    uid, mid = str(ctx.author.id), str(member.id)
    if user_data[uid]['coins'] < amount: return await ctx.send("❌ ما عندك المهر!")
    if user_data[uid].get('partner') or user_data[mid].get('partner'): return await ctx.send("أحدكم متزوج!")

    view = discord.ui.View()
    async def confirm(i):
        if i.user != member: return
        
        # تنفيذ الزواج في البيانات
        user_data[uid]['partner'], user_data[mid]['partner'] = mid, uid
        user_data[uid]['coins'] -= amount
        user_data[mid]['coins'] += amount
        
        # دمج الأرصدة
        main = uid if int(uid) < int(mid) else mid
        other = mid if main == uid else uid
        user_data[main]['coins'] += user_data[other]['coins']
        user_data[other]['coins'] = 0
        save_data(user_data)

        # --- إعطاء الرتبة تلقائياً ---
        role = discord.utils.get(ctx.guild.roles, name="متزوج")
        if role:
            try:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            except:
                print("تأكد أن رتبة البوت أعلى من رتبة متزوج")

        await i.response.edit_message(content=f"💍 مبروك الزواج والحساب المشترك! المهر: {amount}\nتم إعطاؤكم رتبة **{role.name if role else 'متزوج'}**! 🎉", view=None)

    btn = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green)
    btn.callback = confirm
    view.add_item(btn)
    await ctx.send(f"💍 {member.mention}، يقدم لك {ctx.author.mention} مهر {amount}.. موافقة؟", view=view)

# --- أمر الانفصال مع سحب الرتبة ---
@bot.command()
async def divorce(ctx):
    uid = str(ctx.author.id)
    if not user_data[uid].get('partner'): return
    pid = user_data[uid]['partner']
    
    # سحب الرتبة عند الانفصال
    role = discord.utils.get(ctx.guild.roles, name="متزوج")
    if role:
        try:
            member_partner = ctx.guild.get_member(int(pid))
            await ctx.author.remove_roles(role)
            if member_partner: await member_partner.remove_roles(role)
        except:
            pass

    main = uid if int(uid) < int(pid) else pid
    half = user_data[main]['coins'] // 2
    user_data[uid]['coins'], user_data[pid]['coins'] = half, half
    user_data[uid]['partner'], user_data[pid]['partner'] = None, None
    save_data(user_data)
    await ctx.send("💔 تم الانفصال.. سحبنا رتبة متزوج وقسمنا الحساب بالنص.")
import time # أضف هذا السطر في أعلى الكود مع المكتبات

# --- تحديث أمر الزواج (إضافة تاريخ الزواج) ---
@bot.command()
async def marry(ctx, member: discord.Member, amount: int):
    uid, mid = str(ctx.author.id), str(member.id)
    if user_data[uid]['coins'] < amount: return await ctx.send("❌ ما عندك المهر!")
    if user_data[uid].get('partner') or user_data[mid].get('partner'): return await ctx.send("أحدكم متزوج!")

    view = discord.ui.View()
    async def confirm(i):
        if i.user != member: return
        
        # تسجيل البيانات وتاريخ الزواج (بالثواني)
        user_data[uid]['partner'], user_data[mid]['partner'] = mid, uid
        user_data[uid]['m_date'] = time.time() # تاريخ الزواج
        user_data[mid]['m_date'] = time.time()
        
        user_data[uid]['coins'] -= amount
        user_data[mid]['coins'] += amount
        
        main = uid if int(uid) < int(mid) else mid
        other = mid if main == uid else uid
        user_data[main]['coins'] += user_data[other]['coins']
        user_data[other]['coins'] = 0
        save_data(user_data)

        role = discord.utils.get(ctx.guild.roles, name="متزوج")
        if role:
            try:
                await ctx.author.add_roles(role)
                await member.add_roles(role)
            except: pass

        await i.response.edit_message(content=f"💍 مبروك! تم الزواج بنجاح.\n⚠️ تنبيه: لا يمكن تقسيم الأموال عند الانفصال إلا بعد مرور **7 أيام**!", view=None)

    btn = discord.ui.Button(label="موافقة ✅", style=discord.ButtonStyle.green)
    btn.callback = confirm
    view.add_item(btn)
    await ctx.send(f"💍 {member.mention}، هل تقبل الزواج من {ctx.author.mention} بمهر {amount}؟", view=view)

# --- تحديث أمر الانفصال (شرط الأسبوع) ---
@bot.command()
async def divorce(ctx):
    uid = str(ctx.author.id)
    if not user_data[uid].get('partner'): return await ctx.send("أنت لست متزوجاً!")
    
    pid = user_data[uid]['partner']
    m_date = user_data[uid].get('m_date', 0)
    current_time = time.time()
    
    # حساب الثواني في أسبوع (7 أيام * 24 ساعة * 60 دقيقة * 60 ثانية)
    week_in_seconds = 7 * 24 * 60 * 60
    
    if current_time - m_date < week_in_seconds:
        remaining = week_in_seconds - (current_time - m_date)
        days = int(remaining // (24 * 3600))
        hours = int((remaining % (24 * 3600)) // 3600)
        return await ctx.send(f"❌ **عذراً!** لا يمكنك الانفصال وتقسيم الثروة إلا بعد مرور أسبوع على الزواج.\nباقي لكم: `{days} يوم و {hours} ساعة`.")

    # إذا مر أسبوع، يتم الانفصال الطبيعي
    role = discord.utils.get(ctx.guild.roles, name="متزوج")
    if role:
        try:
            member_partner = ctx.guild.get_member(int(pid))
            await ctx.author.remove_roles(role)
            if member_partner: await member_partner.remove_roles(role)
        except: pass

    main = uid if int(uid) < int(pid) else pid
    half = user_data[main]['coins'] // 2
    user_data[uid]['coins'], user_data[pid]['coins'] = half, half
    user_data[uid]['partner'], user_data[pid]['partner'] = None, None
    user_data[uid]['m_date'], user_data[pid]['m_date'] = 0, 0
    
    save_data(user_data)
    await ctx.send("💔 بعد صمود دام أكثر من أسبوع.. تم الانفصال وتقسيم الحساب بالنصف.")
@tasks.loop(minutes=60)
async def auto_event():
    channel = discord.utils.get(bot.get_all_channels(), name="الشات-العام💬")
    if not channel: return
    
    global current_q, questions_pool
    if not questions_pool:
        questions_pool = ALL_QUESTIONS.copy()
        random.shuffle(questions_pool)

    current_q = questions_pool.pop()
    await channel.send(embed=discord.Embed(title="🎮 سؤال الفعالية", description=f"**{current_q['q']}**", color=0x3498db))

@bot.event
async def on_ready():
    if not auto_event.is_running():
        auto_event.start()
@bot.command(aliases=['games', 'العاب'])
async def help_cmd(ctx):
    await ctx.send("🎮 ألعاب البوت: \n1. فعاليات كل ساعة \n2. نظام الزواج \n3. نظام السرقة")
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ألعاب Sky Bot", color=0x3498db)
    embed.add_field(name="💍 الزواج", value="`!marry @user [المهر]`\nنظام الحساب المشترك والرتب", inline=False)
    embed.add_field(name="💔 الانفصال", value="`!divorce` \n(شرط مرور أسبوع للتقسيم)", inline=False)
    embed.add_field(name="💰 البنك", value="`!bal` أو `!balance`", inline=False)
    embed.add_field(name="🧠 الفعاليات", value="سؤال آلي كل ساعة بـ 2000 كوينز", inline=False)
    await ctx.send(embed=embed)
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ألعاب سكاي بوت", color=0x3498db)
    embed.add_field(name="💍 نظام الزواج", value="`!marry @user [المهر]`\nنظام الحساب المشترك والرتب", inline=False)
    embed.add_field(name="💔 الانفصال", value="`!divorce` \n(شرط مرور أسبوع للتقسيم)", inline=False)
    embed.add_field(name="💰 البنك", value="`!bal` أو `!balance` \nلرؤية رصيدك أو رصيد العائلة", inline=False)
    embed.add_field(name="🧠 الفعاليات", value="سؤال آلي كل ساعة بـ 2000 كوينز", inline=False)
    await ctx.send(embed=embed)
import discord
from discord.ext import commands
import random, json, asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 قائمة ألعاب سكاي", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ", value="`!roulette` `!adventure` `!flip` `!dice` `!slots`", inline=False)
    embed.add_field(name="🧠 مسابقات", value="`!تحدي` (سؤال لا يتكرر) `!math` `!guess`", inline=False)
    embed.add_field(name="💰 أنظمة", value="`!marry` `!divorce` `!bal` `!work` `!rob`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def تحدي(ctx):
    global all_questions
    if not all_questions: return await ctx.send("🚨 الأسئلة خلصت! كلم المطور.")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(embed=discord.Embed(title="🌪️ تحدي سكاي", description=f"**السؤال:** {q_data['q']}", color=0x00ff00))
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 1000; save_data(user_data)
        await msg.reply(f"✅ صح! +1000 كوينز. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

@bot.command()
async def marry(ctx, m: discord.Member, amt: int):
    u, p = str(ctx.author.id), str(m.id)
    check_u(u); check_u(p)
    if user_data[u]['partner'] or amt < 500: return await ctx.send("خطأ في الطلب")
    user_data[u]['partner'], user_data[p]['partner'] = p, u
    user_data[u]['coins'] -= amt; user_data[p]['coins'] += amt
    save_data(user_data); await ctx.send("💍 تم الزواج")

@bot.command()
async def divorce(ctx):
    u = str(ctx.author.id); p = user_data[u].get('partner')
    if not p: return
    user_data[u]['partner'] = user_data[p]['partner'] = None
    save_data(user_data); await ctx.send("💔 تم الانفصال")

@bot.command()
async def bal(ctx):
    u = str(ctx.author.id); check_u(u); await ctx.send(f"💰 رصيدك: {user_data[u]['coins']}")

@bot.command()
async def roulette(ctx, amt: int):
    u = str(ctx.author.id); check_u(u)
    if user_data[u]['coins'] < amt: return
    if random.random() > 0.6: user_data[u]['coins'] += amt
    else: user_data[u]['coins'] -= amt
    save_data(user_data); await ctx.send("🎰 تم")

@bot.command()
async def adventure(ctx):
    u = str(ctx.author.id); check_u(u)
    res = random.randint(-200, 500)
    user_data[u]['coins'] += res; save_data(user_data)
    await ctx.send(f"🤠 نتيجة المغامرة: {res}")

@bot.command()
async def work(ctx):
    u = str(ctx.author.id); check_u(u)
    amt = random.randint(50, 150); user_data[u]['coins'] += amt
    save_data(user_data); await ctx.send(f"👷 ربحت {amt}")

bot.run("TOKEN")
import discord
from discord.ext import commands
import random, json, asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام البيانات ---
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

# --- نظام التحقق (الروم والرتبة) ---
async def is_allowed(ctx):
    if ctx.channel.name != 'الشات-العام💬': return False
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات** وفي **الشات العام**!")
        return False
    return True

# --- 1. القائمة الشاملة ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 موسوعة ألعاب سكاي الكبرى", color=0x3498db)
    embed.add_field(name="🎰 ألعاب الحظ والمخاطرة", value="`!roulette` `!adventure` `!flip` `!dice` `!slots` `!rob`", inline=False)
    embed.add_field(name="🌪️ مسابقات ذكاء", value="`!تحدي` (2000 سؤال) `!math` `!guess`", inline=False)
    embed.add_field(name="💰 النظام المالي", value="`!marry` `!divorce` `!bal` `!work`", inline=False)
    await ctx.send(embed=embed)

# --- 2. لعبة الـ 2000 سؤال (تحدي) ---
@bot.command()
async def تحدي(ctx):
    if not await is_allowed(ctx): return
    global all_questions
    if not all_questions: return await ctx.send("🚨 الأسئلة خلصت!")
    q_data = random.choice(all_questions)
    all_questions.remove(q_data)
    with open('questions.json', 'w', encoding='utf-8') as f: json.dump(all_questions, f, indent=4)
    
    await ctx.send(embed=discord.Embed(title="🌪️ سؤال التحدي", description=q_data['q'], color=0x00ff00))
    def check(m): return m.channel == ctx.channel and m.content.strip() == q_data['a']
    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        uid = str(msg.author.id); check_u(uid)
        user_data[uid]['coins'] += 1000; save_data(user_data)
        await msg.reply(f"✅ كفو! +1000 كوينز. (باقي {len(all_questions)} سؤال)")
    except: await ctx.send(f"⏰ وقت! الإجابة: {q_data['a']}")

# --- 3. ألعاب الحظ (الروليت، المغامرة، إلخ) ---
@bot.command()
async def roulette(ctx, amt: int):
    if not await is_allowed(ctx): return
    uid = str(ctx.author.id); check_u(uid)
    if user_data[uid]['coins'] < amt: return await ctx.send("رصيدك ما يكفي!")
    if random.random() > 0.6: 
        user_data[uid]['coins'] += amt
        await ctx.send(f"🎰 كفو! دبلت مبلغك لـ {amt*2}")
    else:
        user_data[uid]['coins'] -= amt
        await ctx.send("🎰 للأسف خسرت المراهنة")
    save_data(user_data)

@bot.command()
async def adventure(ctx):
    if not await is_allowed(ctx): return
    uid = str(ctx.author.id); check_u(uid)
    res = random.choice([("كنز أسطوري!", 1000), ("فخ مميت!", -500), ("رحلة عادية", 50)])
    user_data[uid]['coins'] += res[1]; save_data(user_data)
    await ctx.send(f"🤠 {res[0]} | الربح/الخسارة: {res[1]}")

@bot.command()
async def work(ctx):
    if not await is_allowed(ctx): return
    uid = str(ctx.author.id); check_u(uid)
    amt = random.randint(100, 300)
    user_data[uid]['coins'] += amt; save_data(user_data)
    await ctx.send(f"👷 اشتغلت بجد وربحت {amt} كوينز")

# --- (أنظمة الزواج والبنك) ---
@bot.command()
async def bal(ctx):
    uid = str(ctx.author.id); check_u(uid); await ctx.send(f"💰 رصيدك: {user_data[uid]['coins']}")

@bot.command()
async def marry(ctx, m: discord.Member, amt: int):
    if not await is_allowed(ctx): return
    u, p = str(ctx.author.id), str(m.id)
    check_u(u); check_u(p)
    if user_data[u]['partner']: return await ctx.send("أنت متزوج!")
    user_data[u]['partner'], user_data[p]['partner'] = p, u
    user_data[u]['coins'] -= amt; user_data[p]['coins'] += amt
    save_data(user_data); await ctx.send(f"💍 مبروك الزواج لـ {ctx.author.mention} و {m.mention}")

bot.run("YOUR_TOKEN")
import discord
from discord.ext import commands
import random, json, asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام البيانات ---
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
        user_data[uid] = {'coins': 1000, 'partner': None, 'last_daily': ""}

# --- نظام التحقق الجديد (مرن أكثر) ---
async def is_allowed(ctx):
    # إذا تبي تحصر الروم بالاسم، تأكد إنه مطابق 100%
    allowed_rooms = ['الشات-العام💬', 'الشات-العام'] 
    if ctx.channel.name not in allowed_rooms: return False
    
    role = discord.utils.get(ctx.author.roles, name="فعاليات")
    if role is None:
        await ctx.send("❌ لازم رتبة **فعاليات**!")
        return False
    return True

# --- 1. القائمة المحدثة ---
@bot.command()
async def games(ctx):
    if not await is_allowed(ctx): return
    embed = discord.Embed(title="🎮 ترسانة ألعاب سكاي", color=0x3498db)
    embed.add_field(name="🎰 الحظ", value="`!roulette` `!adventure` `!flip` `!slots`", inline=True)
    embed.add_field(name="🌪️ المسابقات", value="`!تحدي` `!top` (الأغنى)", inline=True)
    embed.add_field(name="💰 النظام المالي", value="`!bal` `!daily` `!rob` `!marry`", inline=False)
    await ctx.send(embed=embed)

# --- 2. لوحة الشرف (Top 10) ---
@bot.command()
async def top(ctx):
    if not await is_allowed(ctx): return
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    leaderboard = "\n".join([f"**#{i+1}** <@{uid}>: {data['coins']} 💰" for i, (uid, data) in enumerate(sorted_users)])
    embed = discord.Embed(title="🏆 أغنى 10 في السيرفر", description=leaderboard, color=0xffd700)
    await ctx.send(embed=embed)

# --- 3. نظام السرقة (Rob) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    if not await is_allowed(ctx): return
    u, t = str(ctx.author.id), str(member.id)
    check_u(u); check_u(t)
    if user_data[t]['coins'] < 500: return await ctx.send("المستهدف طفران، ما يسوى تسرقه!")
    
    if random.random() > 0.7: # نسبة النجاح 30%
        stolen = random.randint(100, 500)
        user_data[u]['coins'] += stolen
        user_data[t]['coins'] -= stolen
        await ctx.send(f"🥷 كفو! سرقت من {member.mention} مبلغ {stolen} كوينز")
    else:
        fine = 300
        user_data[u]['coins'] -= fine
        await ctx.send(f"👮 انقفشت! دفعوك غرامة {fine} كوينز لـ {member.mention}")
    save_data(user_data)

# --- 4. الهدية اليومية (Daily) ---
@bot.command()
async def daily(ctx):
    if not await is_allowed(ctx): return
    uid = str(ctx.author.id); check_u(uid)
    # ملاحظة: هذا نظام بسيط، للتطوير نحتاج مكتبة datetime
    amt = 500
    user_data[uid]['coins'] += amt
    save_data(user_data)
    await ctx.send(f"🎁 أخذت هديتك اليومية {amt} كوينز!")

# --- (أضف باقي الأوامر السابقة هنا: تحدي، روليت، زواج) ---

bot.run("YOUR_TOKEN")
