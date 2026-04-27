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
