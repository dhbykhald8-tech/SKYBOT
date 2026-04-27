import discord
from discord.ext import commands
from easy_pil import Editor, load_image_async
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

WELCOME_CHANNEL_NAME = "ترحيب"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        try:
            # رابط الصورة البنفسجية اللي تبيها (استخدمت رابط مباشر لضمان العمل)
            bg_url = "https://cdn.probot.io/banner/948c26f63f53096bca8fb151c869f00d.png"
            
            # تحميل الخلفية وصورة الشخص
            background = Editor(await load_image_async(bg_url)).resize((800, 450))
            avatar_image = await load_image_async(member.display_avatar.url)
            
            # صنع صورة الشخص دائرية
            avatar = Editor(avatar_image).resize((160, 160)).circle_clip()
            
            # دمجها في المكان الصح
            background.paste(avatar, (320, 45))
            
            file = discord.File(fp=background.image_bytes, filename="welcome.png")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️", file=file)
        except Exception as e:
            # لو فشل في الصورة يرسل نص (وهذا اللي صاير معاك)
            print(f"Error: {e}")
            await channel.send(f"حياك الله {member.mention} نورتنا! ✨☁️")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
