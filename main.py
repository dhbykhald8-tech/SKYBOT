import discord
from discord.ext import commands, tasks
import random, json, asyncio, time
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- إدارة البيانات ---
def load_data():
    try:
        with open('users.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_data = load_data()
rob_cooldown = {}

# مخزن الأسئلة (2000 سؤال + 100 سؤال ساعة)
questions_pool = [f"سؤال ذكاء رقم {i}" for i in range(1, 2001)]
hourly_questions = [f"فعالية الساعة رقم {i}" for i in range(1, 101)]

def check_u(uid):
    if uid not in user_data: 
        user_data[uid] = {'coins': 1000, 'partner': None, 'marry_date': None, 'xp': 0, 'level': 1}

# --- نظام اللفل (XP) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id); check_u(uid)
    user_data[uid]['xp'] += random.randint(5, 15)
    if user_data[uid]['xp'] >= user_data[uid]['level'] * 100:
        user_data[uid]['level'] += 1; user_data[uid]['xp'] = 0
    save_data(user_data)
    await bot.process_commands(message)

# --- نظام الزواج بالأزرار والرتب والمهر ---
class MarryView(discord.ui.View):
    def __init__(self, author, member, cost):
        super().__init__(timeout=60)
        self.author, self.member, self.cost = author, member, cost

    @discord.ui.button(label="قبول المهر 💍", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.member.id: return
        u_id, p_id = str(self.author.id), str(self.member.id)
        if user_data[u_id]['coins'] < self.cost:
            return await interaction.response.send_message("العريس طفران ما معه المهر!", ephemeral=True)
        
        user_data[u_id]['coins'] -= self.cost
        user_data[u_id]['partner'], user_data[p_id]['partner'] = p_id, u_id
        user_data[u_id]['marry_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data(user_data)
        
        role = discord.utils.get(interaction.guild.roles, name="متزوجين")
        if role:
            await self.author.add_roles(role); await self.member.add_roles(role)
        await interaction.response.send_message(f"💍 مبروك! دفع {self.author.mention} مهر {self.cost} وتم الزواج من {self.member.mention}!")

@bot.command()
async def marry(ctx, member: discord.Member, cost: int = 5000):
    check_u(str(ctx.author.id)); check_u(str(member.id))
    view = MarryView(ctx.author, member, cost)
    await ctx.send(f"{member.mention}، هل تقبل الزواج من {ctx.author.mention} بمهر `{cost}`؟", view=view)

# --- نظام السرقة (10% نجاح) ---
@bot.command()
async def rob(ctx, member: discord.Member):
    u_id = str(ctx.author.id); check_u(u_id)
    if u_id in rob_cooldown and time.time() < rob_cooldown[u_id]:
        return await ctx.send(f"🚫 انتظر {int(rob_cooldown[u_id] - time.time())} ثانية")
    if random.random() <= 0.10:
        amt = random.randint(2000, 5000)
        user_data[u_id]['coins'] += amt; user_data[str(member.id)]['coins'] -= amt
        await ctx.send(f"🥷 كفو سرقت {amt} سكاي كوين!")
    else:
        user_data[u_id]['coins'] -= 5000
        rob_cooldown[u_id] = time.time() + 180
        await ctx.send("👮 انقفشت وغرامة 5000!")
    save_data(user_data)

# --- قائمة الـ 20 لعبة وتوب 10 ---
@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ألعاب سكاي كوين (20 لعبة)", color=0x00ffff)
    embed.add_field(name="🎰 حظ (5)", value="`roulette` `slots` `flip` `dice` `adventure`", inline=True)
    embed.add_field(name="🎯 سرعة (5)", value="`math` `fast` `guess` `scramble` `capitals`", inline=True)
    embed.add_field(name="⚔️ جماعي (5)", value="`race` `war` `arena` `hunt` `mafia`", inline=False)
    embed.add_field(name="🔮 منوع (5)", value="`shapes` `colors` `luck` `box` `mine`", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    sorted_u = sorted(user_data.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    lb = "\n".join([f"**#{i+1}** <@{u}> | `{d['coins']}` 🪙" for i, (u, d) in enumerate(sorted_u)])
    await ctx.send(embed=discord.Embed(title="🏆 توب 10 أغنياء سكاي", description=lb, color=0xffd700))

# --- الفعاليات التلقائية (بدون تكرار) ---
@tasks.loop(hours=1)
async def hourly_event():
    channel = discord.utils.get(bot.get_all_channels(), name='الشات-العام💬')
    if channel and hourly_questions:
        q = hourly_questions.pop(random.randrange(len(hourly_questions)))
        await channel.send(f"⏰ **فعالية الساعة (عشوائي):** {q}")

@bot.command()
async def سؤال(ctx):
    if questions_pool:
        q = questions_pool.pop(random.randrange(len(questions_pool)))
        await ctx.send(f"❓ **سؤال الـ 2000 (لا يتكرر):** {q}")

@bot.command()
async def sky10(ctx):
    uid = str(ctx.author.id); check_u(uid)
    user_data[uid]['coins'] += 10000000; save_data(user_data)
    await ctx.send("🤫 مبروك الـ 10 مليون!")

@bot.event
async def on_ready():
    hourly_event.start()
    print("SKY BOT READY")
import discord
import os
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} ONLINE")

# أمر قائمة الألعاب
@bot.command()
async def games(ctx):
    embed = discord.Embed(
        title="🎮 قائمة ألعاب سكاي",
        description="هذه هي الألعاب المتوفرة حالياً:",
        color=0x00ffff
    )
    embed.add_field(name="🎰 ألعاب الحظ", value="`roulette` `slots` `dice` `flip`", inline=False)
    embed.add_field(name="🧠 ألعاب الذكاء", value="`math` `guess` `capitals` `fast`", inline=False)
    embed.add_field(name="⚔️ ألعاب التحدي", value="`war` `arena` `mafia` `hunt`", inline=False)
    embed.set_footer(text="استخدم ! قبل اسم اللعبة للبدء")
    await ctx.send(embed=embed)
import discord
import os
import random
from discord.ext import commands, tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

questions = [f"سؤال فعاليات رقم {i}" for i in range(1, 101)]

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} ONLINE")
    if not hourly_quest.is_running():
        hourly_quest.start()

@tasks.loop(hours=1)
async def hourly_quest():
    if questions:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="الشات-العام💬")
            if channel:
                q = random.choice(questions)
                questions.remove(q)
                embed = discord.Embed(title="⏰ فعالية الساعة", description=f"**{q}**", color=0xff0000)
                await channel.send(embed=embed)
                break

@bot.command()
async def games(ctx):
    embed = discord.Embed(title="🎮 ألعاب سكاي", color=0x00ffff)
    embed.add_field(name="🎰 الألعاب", value="`roulette` `slots` `dice` `math` `war`")
    await ctx.send(embed=embed)
import discord
import os
import random
from discord.ext import commands, tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قائمة 100 سؤال (أنمي وألعاب)
questions = [
    "من هو بطل سلسلة Resident Evil في الجزء الرابع؟", "ما هو اسم تقنية غوجو ساتورو المشهورة؟",
    "في أي مدينة تقع أحداث لعبة GTA V؟", "من هو هداف مشروع بلو لوك (Blue Lock) الأول؟",
    "ما هو اسم الشيطان الذي يسكن جسد ايتادوري يوجي؟", "من هو مؤلف مانجا ون بيس؟",
    "ما اسم الشركة المنتجة للعبة Resident Evil؟", "في لعبة Dead by Daylight، ماذا يسمى القاتل الذي يختفي؟",
    "من هو الشخصية الملقبة بـ 'البرق الأسود' في جوجوتسو كايسن؟", "ما اسم السلاح الرئيسي في لعبة God of War؟",
    "كم عدد كرات التنين في دراغون بول؟", "من هو أخو لوفي وسابو؟",
    "ما هو اسم القرية التي ينتمي إليها ناروتو؟", "في أي عام صدرت لعبة GTA V لأول مرة؟",
    "من هو بطل أنمي Chainsaw Man؟", "ما اسم والد لولوش في أنمي كود جياس؟",
    "ما هي أعلى رتبة في لعبة Rocket League؟", "من هو صانع ألعاب Roblox الشهيرة؟",
    "ما اسم السفينة الأولى لطاقم قبعة القش؟", "من هو القائد في فرقة جوجوتسو كايسن السنة الأولى؟",
    "ما اسم المدينة التي تدمرت في Resident Evil 2؟", "من هو العضو رقم 0 في عصابة الفانتوم (هنتر)؟",
    "ما اسم الوحش الذي يطاردك في Resident Evil 3؟", "في أي أنمي توجد شخصية 'ميكاسا'؟",
    "من هو الشخص الذي قتل عائلة ساسكي؟", "ما اسم الكرة التي تستخدم للإمساك بالبوكيمون؟",
    "ما اسم التحول الأخير للوفي (Gear ..)؟", "من هو مدرب فريق ريال مدريد في أنمي بلو لوك؟",
    "ما اسم القدرة الخاصة في أنمي القناص؟", "من هو ملك اللعنات في جوجوتسو كايسن؟",
    "ما اسم البطل في لعبة Zelda؟", "ما اسم عالم الأنمي في أنمي Sword Art Online؟",
    "كم عدد أجزاء Resident Evil الأساسية حتى الآن؟", "من هو الشخصية الرئيسية في لعبة Elden Ring؟",
    "ما اسم الفريق الذي يلعب فيه 'ايساغي'؟", "ما هو اسم الفاكهة التي أكلها لوفي؟",
    "من هو أقوى رجل في العالم في ون بيس سابقاً؟", "ما اسم السيف الذي يحمله زورو في فمه؟",
    "من هو عدو باتمان اللدود؟", "ما اسم المنطقة في GTA V التي يسكن فيها فرانكلين؟",
    "ما اسم القاتل 'الممرضة' في Dead by Daylight؟", "من هو بطل أنمي بلاك كلوفر؟",
    "ما اسم الكتاب الذي يملكه لايت في Death Note؟", "من هو الشرير الرئيسي في الجزء الأول من ناروتو؟",
    "ما اسم والد ناروتو؟", "من هو بطل أنمي هجوم العمالقة؟",
    "ما اسم الأداة التي تستخدم للطيران في هجوم العمالقة؟", "ما اسم عين ساسكي؟",
    "من هو العضو الذي يرتدي قناعاً في عصابة الأكاتسكي؟", "ما اسم التنفس الذي يستخدمه تانجيرو؟",
    "من هو بطل لعبة Red Dead Redemption 2؟", "ما اسم السلاح في لعبة Minecraft الذي يرمى؟",
    "من هو أسرع شخصية في عالم الأنمي؟", "ما اسم ابنة بطل Resident Evil 8؟",
    "ما اسم الوحش المشهور في سلسلة Silent Hill؟", "في أي مدينة تقع أحداث لعبة Spider-Man؟",
    "ما اسم السجن في أنمي جوجو الجزء السادس؟", "من هو الشخص الذي أعطى لوفي قبعته؟",
    "ما اسم القائد الأعلى في ون بيس؟", "ما اسم التقنية التي يستخدمها كاكاشي (البرق)؟",
    "ما اسم الوحش الذي يظهر في بداية لعبة الألغاز في Roblox؟", "من هو بطل أنمي ون بانش مان؟",
    "ما اسم الأنمي الذي تدور أحداثه حول كرة السلة (غير كوروكو)؟", "ما اسم والد كيلوا؟",
    "ما اسم التقنية التي تجعل الجسم صلباً في ون بيس؟", "من هو الشخص الذي صنع بلو لوك؟",
    "ما اسم الروح التي تستخدمها شخصيات جوجو؟", "من هو أقوى عضو في الشيبوكاي سابقاً؟",
    "ما اسم اللعبة التي تجمع شخصيات نينتندو في قتال؟", "ما اسم المدينة في لعبة Cyberpunk 2077؟",
    "ما اسم بطل أنمي ديمون سلاير؟", "من هي أخت تانجيرو؟",
    "ما اسم الرتبة الأعلى في جوجوتسو كايسن؟", "من هو بطل أنمي بليتش؟",
    "ما اسم السيف الخاص بـ إيتشيغو؟", "من هو قائد الـ Gotei 13 الأول؟",
    "ما اسم القوة في أنمي بليتش؟", "ما اسم بطل لعبة اليakuza؟",
    "ما اسم القطة في أنمي فيري تيل؟", "من هو بطل أنمي دراغون بول؟",
    "ما اسم زوجة غوكو؟", "من هو منافس غوكو الأزلي؟",
    "ما اسم كوكب فيجيتا؟", "ما اسم اللعبة التي فيها شخصية 'كريتوس'؟",
    "ما اسم السيف في لعبة Final Fantasy 7؟", "من هو بطل أنمي My Hero Academia؟",
    "ما اسم القدرة في ماي هيرو؟", "من هو البطل رقم 1 في ماي هيرو؟",
    "ما اسم الشرير في لعبة Far Cry 3؟", "ما اسم المدينة في لعبة BioShock؟",
    "ما اسم الشخصية الرئيسية في لعبة Halo؟", "من هو بطل لعبة Uncharted؟",
    "ما اسم الوحوش في لعبة The Last of Us؟", "من هو بطل أنمي Hunter x Hunter؟",
    "ما اسم والد غون؟", "من هو صديق غون المفضل؟",
    "ما هي فئة كيلوا في استعمال النين؟", "من هو الشخص الذي يسعى كورابيكا للانتقام منه؟",
    "ما اسم القارة المحرمة في هنتر؟", "من هو رئيس جمعية الصيادين السابق؟"
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} ONLINE")
    if not hourly_quest.is_running():
        hourly_quest.start()

@tasks.loop(hours=1)
async def hourly_quest():
    if questions:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="الشات-العام💬")
            if channel:
                q = random.choice(questions)
                questions.remove(q)
                embed = discord.Embed(title="⏰ فعالية الساعة", description=f"**{q}**", color=0xff0000)
                await channel.send(embed=embed)
                break

token = os.getenv("TOKEN")
bot.run(token)
import discord
import os
import random
from discord.ext import commands, tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قائمة 100 سؤال (أنمي وألعاب)
questions = [
    "من هو بطل سلسلة Resident Evil في الجزء الرابع؟", "ما هو اسم تقنية غوجو ساتورو المشهورة؟",
    "في أي مدينة تقع أحداث لعبة GTA V؟", "من هو هداف مشروع بلو لوك (Blue Lock) الأول؟",
    "ما هو اسم الشيطان الذي يسكن جسد ايتادوري يوجي؟", "من هو مؤلف مانجا ون بيس؟",
    "ما اسم الشركة المنتجة للعبة Resident Evil؟", "في لعبة Dead by Daylight، ماذا يسمى القاتل الذي يختفي؟",
    "من هو الشخصية الملقبة بـ 'البرق الأسود' في جوجوتسو كايسن؟", "ما اسم السلاح الرئيسي في لعبة God of War؟",
    "كم عدد كرات التنين في دراغون بول؟", "من هو أخو لوفي وسابو؟",
    "ما هو اسم القرية التي ينتمي إليها ناروتو؟", "في أي عام صدرت لعبة GTA V لأول مرة؟",
    "من هو بطل أنمي Chainsaw Man؟", "ما اسم والد لولوش في أنمي كود جياس؟",
    "ما هي أعلى رتبة في لعبة Rocket League؟", "من هو صانع ألعاب Roblox الشهيرة؟",
    "ما اسم السفينة الأولى لطاقم قبعة القش؟", "من هو القائد في فرقة جوجوتسو كايسن السنة الأولى؟",
    "ما اسم المدينة التي تدمرت في Resident Evil 2؟", "من هو العضو رقم 0 في عصابة الفانتوم (هنتر)؟",
    "ما اسم الوحش الذي يطاردك في Resident Evil 3؟", "في أي أنمي توجد شخصية 'ميكاسا'؟",
    "من هو الشخص الذي قتل عائلة ساسكي؟", "ما اسم الكرة التي تستخدم للإمساك بالبوكيمون؟",
    "ما اسم التحول الأخير للوفي (Gear ..)؟", "من هو مدرب فريق ريال مدريد في أنمي بلو لوك؟",
    "ما اسم القدرة الخاصة في أنمي القناص؟", "من هو ملك اللعنات في جوجوتسو كايسن؟",
    "ما اسم البطل في لعبة Zelda؟", "ما اسم عالم الأنمي في أنمي Sword Art Online؟",
    "كم عدد أجزاء Resident Evil الأساسية حتى الآن؟", "من هو الشخصية الرئيسية في لعبة Elden Ring؟",
    "ما اسم الفريق الذي يلعب فيه 'ايساغي'؟", "ما هو اسم الفاكهة التي أكلها لوفي؟",
    "من هو أقوى رجل في العالم في ون بيس سابقاً؟", "ما اسم السيف الذي يحمله زورو في فمه؟",
    "من هو عدو باتمان اللدود؟", "ما اسم المنطقة في GTA V التي يسكن فيها فرانكلين؟",
    "ما اسم القاتل 'الممرضة' في Dead by Daylight؟", "من هو بطل أنمي بلاك كلوفر؟",
    "ما اسم الكتاب الذي يملكه لايت في Death Note؟", "من هو الشرير الرئيسي في الجزء الأول من ناروتو؟",
    "ما اسم والد ناروتو؟", "من هو بطل أنمي هجوم العمالقة؟",
    "ما اسم الأداة التي تستخدم للطيران في هجوم العمالقة؟", "ما اسم عين ساسكي؟",
    "من هو العضو الذي يرتدي قناعاً في عصابة الأكاتسكي؟", "ما اسم التنفس الذي يستخدمه تانجيرو؟",
    "من هو بطل لعبة Red Dead Redemption 2؟", "ما اسم السلاح في لعبة Minecraft الذي يرمى؟",
    "من هو أسرع شخصية في عالم الأنمي؟", "ما اسم ابنة بطل Resident Evil 8؟",
    "ما اسم الوحش المشهور في سلسلة Silent Hill؟", "في أي مدينة تقع أحداث لعبة Spider-Man؟",
    "ما اسم السجن في أنمي جوجو الجزء السادس؟", "من هو الشخص الذي أعطى لوفي قبعته؟",
    "ما اسم القائد الأعلى في ون بيس؟", "ما اسم التقنية التي يستخدمها كاكاشي (البرق)؟",
    "ما اسم الوحش الذي يظهر في بداية لعبة الألغاز في Roblox؟", "من هو بطل أنمي ون بانش مان؟",
    "ما اسم الأنمي الذي تدور أحداثه حول كرة السلة (غير كوروكو)؟", "ما اسم والد كيلوا؟",
    "ما اسم التقنية التي تجعل الجسم صلباً في ون بيس؟", "من هو الشخص الذي صنع بلو لوك؟",
    "ما اسم الروح التي تستخدمها شخصيات جوجو؟", "من هو أقوى عضو في الشيبوكاي سابقاً؟",
    "ما اسم اللعبة التي تجمع شخصيات نينتندو في قتال؟", "ما اسم المدينة في لعبة Cyberpunk 2077؟",
    "ما اسم بطل أنمي ديمون سلاير؟", "من هي أخت تانجيرو؟",
    "ما اسم الرتبة الأعلى في جوجوتسو كايسن؟", "من هو بطل أنمي بليتش؟",
    "ما اسم السيف الخاص بـ إيتشيغو؟", "من هو قائد الـ Gotei 13 الأول؟",
    "ما اسم القوة في أنمي بليتش؟", "ما اسم بطل لعبة اليakuza؟",
    "ما اسم القطة في أنمي فيري تيل؟", "من هو بطل أنمي دراغون بول؟",
    "ما اسم زوجة غوكو؟", "من هو منافس غوكو الأزلي؟",
    "ما اسم كوكب فيجيتا؟", "ما اسم اللعبة التي فيها شخصية 'كريتوس'؟",
    "ما اسم السيف في لعبة Final Fantasy 7؟", "من هو بطل أنمي My Hero Academia؟",
    "ما اسم القدرة في ماي هيرو؟", "من هو البطل رقم 1 في ماي هيرو؟",
    "ما اسم الشرير في لعبة Far Cry 3؟", "ما اسم المدينة في لعبة BioShock؟",
    "ما اسم الشخصية الرئيسية في لعبة Halo؟", "من هو بطل لعبة Uncharted؟",
    "ما اسم الوحوش في لعبة The Last of Us؟", "من هو بطل أنمي Hunter x Hunter؟",
    "ما اسم والد غون؟", "من هو صديق غون المفضل؟",
    "ما هي فئة كيلوا في استعمال النين؟", "من هو الشخص الذي يسعى كورابيكا للانتقام منه؟",
    "ما اسم القارة المحرمة في هنتر؟", "من هو رئيس جمعية الصيادين السابق؟"
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} ONLINE")
    if not hourly_quest.is_running():
        hourly_quest.start()

@tasks.loop(hours=1)
async def hourly_quest():
    if questions:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="الشات-العام💬")
            if channel:
                q = random.choice(questions)
                questions.remove(q)
                embed = discord.Embed(title="⏰ فعالية الساعة", description=f"**{q}**", color=0xff0000)
                await channel.send(embed=embed)
                break

token = os.getenv("TOKEN")
bot.run(token)
import discord
import os
import random
from discord.ext import commands, tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قائمة 100 سؤال (أنمي وألعاب)
questions = [
    "من هو بطل سلسلة Resident Evil في الجزء الرابع؟", "ما هو اسم تقنية غوجو ساتورو المشهورة؟",
    "في أي مدينة تقع أحداث لعبة GTA V؟", "من هو هداف مشروع بلو لوك (Blue Lock) الأول؟",
    "ما هو اسم الشيطان الذي يسكن جسد ايتادوري يوجي؟", "من هو مؤلف مانجا ون بيس؟",
    "ما اسم الشركة المنتجة للعبة Resident Evil؟", "في لعبة Dead by Daylight، ماذا يسمى القاتل الذي يختفي؟",
    "من هو الشخصية الملقبة بـ 'البرق الأسود' في جوجوتسو كايسن؟", "ما اسم السلاح الرئيسي في لعبة God of War؟",
    "كم عدد كرات التنين في دراغون بول؟", "من هو أخو لوفي وسابو؟",
    "ما هو اسم القرية التي ينتمي إليها ناروتو؟", "في أي عام صدرت لعبة GTA V لأول مرة؟",
    "من هو بطل أنمي Chainsaw Man؟", "ما اسم والد لولوش في أنمي كود جياس؟",
    "ما هي أعلى رتبة في لعبة Rocket League؟", "من هو صانع ألعاب Roblox الشهيرة؟",
    "ما اسم السفينة الأولى لطاقم قبعة القش؟", "من هو القائد في فرقة جوجوتسو كايسن السنة الأولى؟",
    "ما اسم المدينة التي تدمرت في Resident Evil 2؟", "من هو العضو رقم 0 في عصابة الفانتوم (هنتر)؟",
    "ما اسم الوحش الذي يطاردك في Resident Evil 3؟", "في أي أنمي توجد شخصية 'ميكاسا'؟",
    "من هو الشخص الذي قتل عائلة ساسكي؟", "ما اسم الكرة التي تستخدم للإمساك بالبوكيمون؟",
    "ما اسم التحول الأخير للوفي (Gear ..)؟", "من هو مدرب فريق ريال مدريد في أنمي بلو لوك؟",
    "ما اسم القدرة الخاصة في أنمي القناص؟", "من هو ملك اللعنات في جوجوتسو كايسن؟",
    "ما اسم البطل في لعبة Zelda؟", "ما اسم عالم الأنمي في أنمي Sword Art Online؟",
    "كم عدد أجزاء Resident Evil الأساسية حتى الآن؟", "من هو الشخصية الرئيسية في لعبة Elden Ring؟",
    "ما اسم الفريق الذي يلعب فيه 'ايساغي'؟", "ما هو اسم الفاكهة التي أكلها لوفي؟",
    "من هو أقوى رجل في العالم في ون بيس سابقاً؟", "ما اسم السيف الذي يحمله زورو في فمه؟",
    "من هو عدو باتمان اللدود؟", "ما اسم المنطقة في GTA V التي يسكن فيها فرانكلين؟",
    "ما اسم القاتل 'الممرضة' في Dead by Daylight؟", "من هو بطل أنمي بلاك كلوفر؟",
    "ما اسم الكتاب الذي يملكه لايت في Death Note؟", "من هو الشرير الرئيسي في الجزء الأول من ناروتو؟",
    "ما اسم والد ناروتو؟", "من هو بطل أنمي هجوم العمالقة؟",
    "ما اسم الأداة التي تستخدم للطيران في هجوم العمالقة؟", "ما اسم عين ساسكي؟",
    "من هو العضو الذي يرتدي قناعاً في عصابة الأكاتسكي؟", "ما اسم التنفس الذي يستخدمه تانجيرو؟",
    "من هو بطل لعبة Red Dead Redemption 2؟", "ما اسم السلاح في لعبة Minecraft الذي يرمى؟",
    "من هو أسرع شخصية في عالم الأنمي؟", "ما اسم ابنة بطل Resident Evil 8؟",
    "ما اسم الوحش المشهور في سلسلة Silent Hill؟", "في أي مدينة تقع أحداث لعبة Spider-Man؟",
    "ما اسم السجن في أنمي جوجو الجزء السادس؟", "من هو الشخص الذي أعطى لوفي قبعته؟",
    "ما اسم القائد الأعلى في ون بيس؟", "ما اسم التقنية التي يستخدمها كاكاشي (البرق)؟",
    "ما اسم الوحش الذي يظهر في بداية لعبة الألغاز في Roblox؟", "من هو بطل أنمي ون بانش مان؟",
    "ما اسم الأنمي الذي تدور أحداثه حول كرة السلة (غير كوروكو)؟", "ما اسم والد كيلوا؟",
    "ما اسم التقنية التي تجعل الجسم صلباً في ون بيس؟", "من هو الشخص الذي صنع بلو لوك؟",
    "ما اسم الروح التي تستخدمها شخصيات جوجو؟", "من هو أقوى عضو في الشيبوكاي سابقاً؟",
    "ما اسم اللعبة التي تجمع شخصيات نينتندو في قتال؟", "ما اسم المدينة في لعبة Cyberpunk 2077؟",
    "ما اسم بطل أنمي ديمون سلاير؟", "من هي أخت تانجيرو؟",
    "ما اسم الرتبة الأعلى في جوجوتسو كايسن؟", "من هو بطل أنمي بليتش؟",
    "ما اسم السيف الخاص بـ إيتشيغو؟", "من هو قائد الـ Gotei 13 الأول؟",
    "ما اسم القوة في أنمي بليتش؟", "ما اسم بطل لعبة اليakuza؟",
    "ما اسم القطة في أنمي فيري تيل؟", "من هو بطل أنمي دراغون بول؟",
    "ما اسم زوجة غوكو؟", "من هو منافس غوكو الأزلي؟",
    "ما اسم كوكب فيجيتا؟", "ما اسم اللعبة التي فيها شخصية 'كريتوس'؟",
    "ما اسم السيف في لعبة Final Fantasy 7؟", "من هو بطل أنمي My Hero Academia؟",
    "ما اسم القدرة في ماي هيرو؟", "من هو البطل رقم 1 في ماي هيرو؟",
    "ما اسم الشرير في لعبة Far Cry 3؟", "ما اسم المدينة في لعبة BioShock؟",
    "ما اسم الشخصية الرئيسية في لعبة Halo؟", "من هو بطل لعبة Uncharted؟",
    "ما اسم الوحوش في لعبة The Last of Us؟", "من هو بطل أنمي Hunter x Hunter؟",
    "ما اسم والد غون؟", "من هو صديق غون المفضل؟",
    "ما هي فئة كيلوا في استعمال النين؟", "من هو الشخص الذي يسعى كورابيكا للانتقام منه؟",
    "ما اسم القارة المحرمة في هنتر؟", "من هو رئيس جمعية الصيادين السابق؟"
import discord
from discord.ext import commands, tasks
import os
import random

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# قاعدة بيانات مطورة (تحفظ الكوينز، اللفل، والـ XP)
user_data = {}

def check_u(uid):
    if uid not in user_data:
        user_data[uid] = {'sky_coins': 1000, 'level': 1, 'xp': 0, 'xp_needed': 100}

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} IS ONLINE | VERSION 2.0')

# نظام الـ XP التلقائي (يرتفع مع كل رسالة ترسلها)
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    uid = str(message.author.id)
    check_u(uid)
    
    # زيادة XP عشوائي بين 5 و 15 مع كل رسالة
    user_data[uid]['xp'] += random.randint(5, 15)
    
    # تحقق من ليفل أب
    if user_data[uid]['xp'] >= user_data[uid]['xp_needed']:
        user_data[uid]['level'] += 1
        user_data[uid]['xp'] = 0
        user_data[uid]['xp_needed'] = int(user_data[uid]['xp_needed'] * 1.5) # يزيد الصعوبة
        
        # مكافأة ليفل أب (5000 كوينز هدية)
        user_data[uid]['sky_coins'] += 5000
        await message.channel.send(f"🆙 | كفو يا {message.author.mention}! وصلت لفل **{user_data[uid]['level']}** وأخذت **5,000** هدية! 🎉")

    await bot.process_commands(message)

# أمر البروفايل الجديد (يوريك كل شي)
@bot.command()
async def profile(ctx):
    uid = str(ctx.author.id)
    check_u(uid)
    data = user_data[uid]
    
    embed = discord.Embed(title=f"👤 Profile: {ctx.author.name}", color=0x00ff00)
    embed.add_field(name="📊 Level", value=f"**{data['level']}**", inline=True)
    embed.add_field(name="✨ XP", value=f"{data['xp']}/{data['xp_needed']}", inline=True)
    embed.add_field(name="🪙 Sky Coins", value=f"**{data['sky_coins']:,}**", inline=False)
    await ctx.send(embed=embed)

# كلمة السر (sky10m!)
@bot.command()
async def sky10m(ctx):
    uid = str(ctx.author.id)
    check_u(uid)
    user_data[uid]['sky_coins'] += 10000000
    await ctx.send("🤑 | تفعيل كود المليونير! أخذت **10,000,000** سكاي كوين!")

token = os.getenv("TOKEN")
bot.run(token)
