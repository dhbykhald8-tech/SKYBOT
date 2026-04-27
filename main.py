import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio

# إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

user_xp = {}
REQUIRED_ROLE_NAME = "فعاليات"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# --- كود لعبة الروليت (التحكم بالأزرار) ---

class RouletteView(View):
    def __init__(self, ctx):
        super().__init__(timeout=40)
        self.ctx = ctx
        self.players = []

    @discord.ui.button(label="انضمام (Join)", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("أنت موجود فعلاً في القائمة!", ephemeral=True)
        else:
            self.players.append(interaction.user)
            player_names = "\n".join([p.name for p in self.players])
            embed = discord.Embed(title="🎮 لعبة الروليت - تسجيل اللاعبين", description=f"المشاركين حالياً:\n{player_names}", color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=self)

@bot.command(name="roulette")
async def start_roulette(ctx):
    # فحص الرتبة
    has_role = any(role.name == REQUIRED_ROLE_NAME for role in ctx.author.roles)
    if not has_role:
        await ctx.send(f"❌ عفواً {ctx.author.mention}، لازم رتبة **({REQUIRED_ROLE_NAME})**")
        return

    view = RouletteView(ctx)
    embed = discord.Embed(title="🎮 فعاليات: لعبة الروليت", description="اضغط على الزر تحت عشان تشارك! لازم 4 لاعبين على الأقل.\nالوقت: 40 ثانية.", color=0x3498db)
    initial_msg = await ctx.send(embed=embed, view=view)

    await asyncio.sleep(40) # وقت الانتظار
    view.stop()

    if len(view.players) < 4:
        await ctx.send(f"❌ الغاء اللعبة! عدد المشاركين قليل ({len(view.players)}/4)")
        return

    active_players = view.players.copy()

    while len(active_players) > 1:
        chosen_one = random.choice(active_players)
        await ctx.send(f"🔄 جاري تدوير الروليت...\n🎯 السهم وقف عند: **{chosen_one.mention}**! أنت الآن تختار مين يطرد.")

        # صنع أزرار بأسماء اللاعبين الآخرين للطرد
        class KickView(View):
            def __init__(self, selector, current_players):
                super().__init__(timeout=20)
                self.selector = selector
                self.kicked_user = None
                for p in current_players:
                    if p != selector:
                        btn = Button(label=f"طرد {p.name}", style=discord.ButtonStyle.danger, custom_id=str(p.id))
                        btn.callback = self.make_callback(p)
                        self.add_item(btn)

            def make_callback(self, user):
                async def callback(interaction: discord.Interaction):
                    if interaction.user != self.selector:
                        await interaction.response.send_message("مو دورك تختار!", ephemeral=True)
                        return
                    self.kicked_user = user
                    self.stop()
                return callback

        k_view = KickView(chosen_one, active_players)
        kick_msg = await ctx.send(f"يا {chosen_one.mention}، اختر اللاعب اللي تبي تطرده من الأزرار تحت:", view=k_view)
        
        await k_view.wait()

        if k_view.kicked_user:
            active_players.remove(k_view.kicked_user)
            await ctx.send(f"🚫 تم طرد **{k_view.kicked_user.name}** من اللعبة!")
        else:
            # لو انتهى الوقت وما اختار، نطرد واحد عشوائي غير المختار
            others = [p for p in active_players if p != chosen_one]
            auto_kick = random.choice(others)
            active_players.remove(auto_kick)
            await ctx.send(f"⌛ انتهى الوقت! البوت طرد **{auto_kick.name}** عشوائياً.")

        if len(active_players) == 1:
            await ctx.send(f"🎊 مبروك الفوز يا **{active_players[0].mention}**! أنت الناجي الوحيد!")
            break

# --- الأوامر العادية (محدثة لتعمل مع bot.command) ---

@bot.event
async def on_message(message):
    if message.author.bot: return
    # نظام اللفل XP
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 مبروك {message.author.mention} لفل {user_xp[uid]['level']}!")
    
    await bot.process_commands(message)

@bot.command()
async def games(ctx):
    has_role = any(role.name == REQUIRED_ROLE_NAME for role in ctx.author.roles)
    if not has_role: return
    await ctx.send("🎮 الألعاب:\n`!roulette` - لعبة الروليت (4 أشخاص+)\n`!level` - لفلُك")

@bot.command()
async def level(ctx):
    uid = str(ctx.author.id)
    lvl = user_xp.get(uid, {'level': 1})['level']
    xp = user_xp.get(uid, {'xp': 0})['xp']
    await ctx.send(f"مستواك: {lvl} | نقاطك: {xp} XP")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
