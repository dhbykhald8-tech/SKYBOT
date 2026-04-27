import discord
from discord.ext import commands
from easy_pil import Editor, load_image_async
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# اسم الروم كما طلبت
WELCOME_CHANNEL_NAME = "ترحيب"
REQUIRED_ROLE_NAME = "فعاليات"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        # لاحظ هنا غيرنا الامتداد إلى .jpg ليتطابق مع ملفك
        image_path = "welcome_bg.jpg"
        
        if not os.path.exists(image_path):
            print(f"❌ خطأ: ملف {image_path} غير موجود!")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️")
            return

        try:
            # دمج صورة الشخص فوق صورتك الـ jpg
            background = Editor(image_path).resize((800, 450))
            avatar_image = await load_image_async(member.display_avatar.url)
            
            # جعل صورة الشخص دائرية
            avatar = Editor(avatar_image).resize((160, 160)).circle_clip()
            
            # وضعها في مكان الدائرة (x=320, y=45)
            background.paste(avatar, (320, 45))
            
            file = discord.File(fp=background.image_bytes, filename="welcome.png")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️", file=file)
            print(f"✅ تم إرسال الصورة بنجاح لـ {member.name}")
        except Exception as e:
            print(f"❌ خطأ في المعالجة: {e}")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️")

# --- نظام اللفل والألعاب (مختصر ونظيف) ---
user_xp = {}
@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if uid not in user_xp: user_xp[uid] = {'xp': 0, 'level': 1}
    user_xp[uid]['xp'] += 10
    if user_xp[uid]['xp'] >= (user_xp[uid]['level'] * 100):
        user_xp[uid]['level'] += 1
        await message.channel.send(f"🆙 كفو {message.author.mention}! لفل {user_xp[uid]['level']}!")

    if message.content == '-games':
        if not any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles):
            await message.channel.send(f"❌ لازم رتبة **({REQUIRED_ROLE_NAME})**")
            return
        await message.channel.send("🎮 **الألعاب:**\n`!level` | `!slots` | `!roll` | `!flip` | `!ball`")
    await bot.process_commands(message)

@bot.command()
async def level(ctx):
    d = user_xp.get(str(ctx.author.id), {'level': 1, 'xp': 0})
    await ctx.send(f"مستواك: {d['level']} | نقاطك: {d['xp']} XP")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
