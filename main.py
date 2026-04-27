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
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} IS ONLINE!")

bot.run("MTQ5ODEzOTEyODAzNzExMzg1Ng.GV5xER.lCtKXFA5ufKew9ElUx0PBCj_1SoREnVn43mDB0")
