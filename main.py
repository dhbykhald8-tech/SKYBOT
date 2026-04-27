import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_xp = {}
REQUIRED_ROLE_NAME = "فعاليات"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# --- كود لعبة الروليت ---
class RouletteView(View):
    def __init__(self):
        super().__init__(timeout=40)
        self.players = []

    @discord.ui.button(label="انضمام (Join)", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("أنت موجود فعلاً!", ephemeral=True)
        else:
            self.players.append(interaction.user)
            names = "\n".join([p.name for p in self.players])
            embed = discord.Embed(title="🎮 تسجيل اللاعبين", description=f"المشاركين:\n{names}", color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=self)

# --- نظام اللفل وامر القائمة ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 مبروك {message.author.mention} لفل {user_xp[uid]['level']}!")

    # امر عرض الالعاب
    if message.content == '-games':
        has_role = any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles)
        if not has_role:
            await message.channel.send(f"❌ لازم رتبة **({REQUIRED_ROLE_NAME})** عشان تشوف وتلعب!")
            return
            
        help_text = (
            "🎮 **قائمة ألعاب سكاي بوت:**\n"
            "`!roulette` - لعبة الروليت (4 لاعبين فأكثر)\n"
            "`!level` - معرفة لفلُك\n"
            "`!slots` - آلة الحظ\n"
            "`!fast` - سرعة الكتابة\n"
            "`!roll` - رمي النرد\n"
            "`!flip` - ملك أو كتابة\n"
            "`!guess` - تخمين الرقم\n"
            "`!rps` - حجر ورقة مقص\n"
            "`!8ball` - الكرة السحرية"
        )
        await message.channel.send(help_text)

    await bot.process_commands(message)

# --- تعريف الأوامر ! ---

@bot.command()
async def roulette(ctx):
    has_role = any(role.name == REQUIRED_ROLE_NAME for role in ctx.author.roles)
    if not has_role: return

    view = RouletteView()
    embed = discord.Embed(title="🎮 لعبة الروليت", description="اضغط Join للمشاركة! (نحتاج 4 لاعبين)\nالوقت: 40 ثانية.", color=0x3498db)
    await ctx.send(embed=embed, view=view)

    await asyncio.sleep(40)
    view.stop()

    if len(view.players) < 4:
        await ctx.send("❌ ألغيت اللعبة، العدد غير كافي.")
        return

    active = view.players.copy()
    while len(active) > 1:
        chosen = random.choice(active)
        await ctx.send(f"🎯 السهم عند: {chosen.mention}! اختر من تطرد.")

        class KickV(View):
            def __init__(self, selector, p_list):
                super().__init__(timeout=20)
                self.sel, self.kicked, self.p_list = selector, None, p_list
                for p in p_list:
                    if p != selector:
                        btn = Button(label=f"طرد {p.name}", style=discord.ButtonStyle.danger)
                        btn.callback = self.create_cb(p)
                        self.add_item(btn)
            def create_cb(self, user):
                async def cb(i: discord.Interaction):
                    if i.user != self.sel: return
                    self.kicked = user
                    self.stop()
                return cb

        kv = KickV(chosen, active)
        await ctx.send("اختر الهدف:", view=kv)
        await kv.wait()

        target = kv.kicked if kv.kicked else random.choice([p for p in active if p != chosen])
        active.remove(target)
        await ctx.send(f"🚫 تم طرد {target.name}!")

    await ctx.send(f"🎊 الفائز هو {active[0].mention}!")

@bot.command()
async def level(ctx):
    uid = str(ctx.author.id)
    d = user_xp.get(uid, {'level': 1, 'xp': 0})
    await ctx.send(f"لفلُك: {d['level']} | نقاطك: {d['xp']}")

@bot.command()
async def slots(ctx):
    e = "🍎🍊🍇💎⭐"
    a, b, c = random.choice(e), random.choice(e), random.choice(e)
    res = f"**[ {a} | {b} | {c} ]**"
    msg = "🎉 فزت!" if a==b==c else "✨ حبتين!" if a==b or b==c or a==c else "❌ خسرت"
    await ctx.send(f"{res}\n{msg}")

@bot.command()
async def fast(ctx):
    target = random.choice(["كويت", "برمجة", "سرعة", "سكاي"])
    await ctx.send(f"اكتب: **{target}**")
    def check(m): return m.author == ctx.author and m.content == target
    try:
        await bot.wait_for('message', check=check, timeout=8.0)
        await ctx.send("⚡ وحش!")
    except: await ctx.send("⏰ انتهى الوقت")

@bot.command()
async def roll(ctx): await ctx.send(f"🎲: {random.randint(1, 6)}")

@bot.command()
async def flip(ctx): await ctx.send(f"🪙: {random.choice(['وجه', 'كتابة'])}")

@bot.command()
async def guess(ctx):
    n = random.randint(1, 10)
    await ctx.send("خمن (1-10):")
    def c(m): return m.author == ctx.author and m.content.isdigit()
    try:
        g = await bot.wait_for('message', check=c, timeout=10)
        await ctx.send("✅ صح" if int(g.content)==n else f"❌ خطأ، كان {n}")
    except: await ctx.send("⌛ انتهى الوقت")

@bot.command()
async def rps(ctx, choice: str):
    bot_c = random.choice(["حجر", "ورقة", "مقص"])
    if choice == bot_c: res = "تعادل"
    elif (choice=="حجر" and bot_c=="مقص") or (choice=="ورقة" and bot_c=="حجر") or (choice=="مقص" and bot_c=="ورقة"): res = "فزت"
    else: res = "خسرت"
    await ctx.send(f"أنا {bot_c}، {res}!")

@bot.command()
async def 8ball(ctx): await ctx.send(f"🔮: {random.choice(['نعم', 'لا', 'ممكن'])}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
