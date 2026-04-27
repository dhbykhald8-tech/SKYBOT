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

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 مبروك {message.author.mention} لفل {user_xp[uid]['level']}!")

    if message.content == '-games':
        has_role = any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles)
        if not has_role:
            await message.channel.send(f"❌ لازم رتبة **({REQUIRED_ROLE_NAME})**")
            return
            
        help_text = (
            "🎮 **قائمة ألعاب سكاي بوت:**\n"
            "`!roulette` - لعبة الروليت (4+)\n"
            "`!level` - لفلُك\n"
            "`!slots` - آلة الحظ\n"
            "`!fast` - سرعة الكتابة\n"
            "`!roll` - رمي النرد\n"
            "`!flip` - ملك أو كتابة\n"
            "`!guess` - تخمين الرقم\n"
            "`!rps` - حجر ورقة مقص\n"
            "`!ball` - الكرة السحرية"
        )
        await message.channel.send(help_text)
    await bot.process_commands(message)

@bot.command()
async def roulette(ctx):
    has_role = any(role.name == REQUIRED_ROLE_NAME for role in ctx.author.roles)
    if not has_role: return
    view = RouletteView()
    await ctx.send(embed=discord.Embed(title="🎮 لعبة الروليت", description="اضغط Join! (نحتاج 4 لاعبين)\nالوقت: 40 ثانية."), view=view)
    await asyncio.sleep(40)
    if len(view.players) < 4:
        await ctx.send("❌ عدد غير كافي.")
        return
    active = view.players.copy()
    while len(active) > 1:
        chosen = random.choice(active)
        await ctx.send(f"🎯 الدور عند: {chosen.mention}")
        class KickV(View):
            def __init__(self, selector, p_list):
                super().__init__(timeout=20)
                self.sel, self.kicked = selector, None
                for p in p_list:
                    if p != selector:
                        btn = Button(label=f"طرد {p.name}", style=discord.ButtonStyle.danger)
                        btn.callback = self.make_cb(p)
                        self.add_item(btn)
            def make_cb(self, user):
                async def cb(i: discord.Interaction):
                    if i.user != self.sel: return
                    self.kicked = user
                    self.stop()
                return cb
        kv = KickV(chosen, active)
        await ctx.send("اختر من تطرد:", view=kv)
        await kv.wait()
        target = kv.kicked if kv.kicked else random.choice([p for p in active if p != chosen])
        active.remove(target)
        await ctx.send(f"🚫 طرد {target.name}")
    await ctx.send(f"🎊 الفائز: {active[0].mention}")

@bot.command()
async def level(ctx):
    d = user_xp.get(str(ctx.author.id), {'level': 1, 'xp': 0})
    await ctx.send(f"لفلُك: {d['level']} | نقاطك: {d['xp']}")

@bot.command()
async def slots(ctx):
    res = [random.choice("🍎🍊🍇💎⭐") for _ in range(3)]
    await ctx.send(f"**[ {' | '.join(res)} ]**\n{'🎉 فوز!' if res[0]==res[1]==res[2] else '✨ حبتين!' if len(set(res))<3 else '❌ خسارة'}")

@bot.command()
async def fast(ctx):
    t = random.choice(["كويت", "برمجة", "سكاي"])
    await ctx.send(f"اكتب: **{t}**")
    try:
        await bot.wait_for('message', check=lambda m: m.author==ctx.author and m.content==t, timeout=8)
        await ctx.send("⚡ وحش!")
    except: await ctx.send("⌛ انتهى الوقت")

@bot.command()
async def roll(ctx): await ctx.send(f"🎲: {random.randint(1, 6)}")

@bot.command()
async def flip(ctx): await ctx.send(f"🪙: {random.choice(['وجه', 'كتابة'])}")

@bot.command()
async def guess(ctx):
    n = random.randint(1, 10)
    await ctx.send("خمن (1-10):")
    try:
        g = await bot.wait_for('message', check=lambda m: m.author==ctx.author and m.content.isdigit(), timeout=10)
        await ctx.send("✅ صح" if int(g.content)==n else f"❌ خطأ، كان {n}")
    except: await ctx.send("⌛ وقت")

@bot.command()
async def rps(ctx, choice: str):
    bot_c = random.choice(["حجر", "ورقة", "مقص"])
    res = "تعادل" if choice==bot_c else "فزت" if (choice=="حجر" and bot_c=="مقص") or (choice=="ورقة" and bot_c=="حجر") or (choice=="مقص" and bot_c=="ورقة") else "خسرت"
    await ctx.send(f"أنا {bot_c}، {res}!")

@bot.command(name="ball")
async def ball(ctx):
    await ctx.send(f"🔮: {random.choice(['نعم', 'لا', 'ممكن'])}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)

