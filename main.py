import discord
import os
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

user_xp = {}

# اسم الرتبة المسموح لها باللعب
REQUIRED_ROLE_NAME = "فعاليات"

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in user_xp:
        user_xp[user_id] = {'xp': 0, 'level': 1}
    
    user_xp[user_id]['xp'] += 10
    xp = user_xp[user_id]['xp']
    lvl = user_xp[user_id]['level']
    
    if xp >= (lvl * 100):
        user_xp[user_id]['level'] += 1
        await message.channel.send(f'مبروك {message.author.mention}! ارتفع مستواك إلى لفل {lvl + 1} 🆙')

    # قائمة الأوامر اللي تبدأ بـ ! أو - (الألعاب)
    game_commands = ['!slots', '!fast', '!roll', '!flip', '!guess', '!rps', '!8ball', '-games']
    
    # فحص إذا كانت الرسالة عبارة عن أمر لعبة
    is_game_command = any(message.content.startswith(cmd) for cmd in game_commands)

    if is_game_command:
        # فحص إذا كان الشخص عنده رتبة "فعاليات"
        has_role = any(role.name == REQUIRED_ROLE_NAME for role in message.author.roles)
        
        if not has_role:
            await message.channel.send(f"❌ عفواً {message.author.mention}، لازم يكون معك رتبة **({REQUIRED_ROLE_NAME})** عشان تقدر تلعب!")
            return

    # --- الألعاب وفعاليات البوت ---

    if message.content == '-games':
        help_text = (
            "🎮 **قائمة ألعاب سكاي بوت:**\n"
            "`!level` - لمعرفة لفلك ونقاطك\n"
            "`!slots` - لعبة آلة الحظ (الفواكه)\n"
            "`!fast` - اختبار سرعة الكتابة\n"
            "`!roll` - رمي النرد\n"
            "`!flip` - رمي العملة\n"
            "`!guess` - تخمين الرقم\n"
            "`!rps` - حجر ورقة مقص\n"
            "`!8ball` - اسأل الكرة السحرية"
        )
        await message.channel.send(help_text)

    if message.content == '!level':
        await message.channel.send(f'مستواك الحالي: {user_xp[user_id]["level"]} | نقاطك: {user_xp[user_id]["xp"]} XP')

    if message.content == '!slots':
        emojis = "🍎🍊🍇💎⭐"
        a, b, c = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        res = f"**[ {a} | {b} | {c} ]**\n"
        if a == b == c: await message.channel.send(f"{res} 🎉 كفوووو! فزت بالجائزة الكبرى!")
        elif a == b or b == c or a == c: await message.channel.send(f"{res} ✨ قريبة! حبتين متشابهة.")
        else: await message.channel.send(f"{res} ❌ حظ أوفر المرة الجاية.")

    if message.content == '!fast':
        words = ["كويت", "برمجة", "ديسكورد", "سرعة", "لعبة", "تطوير", "سريع", "فائز"]
        target = random.choice(words)
        await message.channel.send(f"اكتب الكلمة التالية بأسرع ما يمكن: **{target}**")
        def check(m): return m.author == message.author and m.channel == message.channel and m.content == target
        try:
            await client.wait_for('message', check=check, timeout=8.0)
            await message.channel.send(f"⚡ وحش يا {message.author.mention}! كتبتها بالوقت المناسب!")
        except asyncio.TimeoutError:
            await message.channel.send(f"⏰ انتهى الوقت! الكلمة كانت: **{target}**")

    if message.content == '!roll':
        await message.channel.send(f"🎲 طلع لك الرقم: **{random.randint(1, 6)}**")

    if message.content == '!flip':
        res = random.choice(['وجه (ملك)', 'كتابة'])
        await message.channel.send(f"🪙 النتيجة هي: **{res}**")

    if message.content.startswith('!guess'):
        num = random.randint(1, 10)
        await message.channel.send("خمن رقم بين 1 و 10:")
        def check_guess(m): return m.author == message.author and m.channel == message.channel and m.content.isdigit()
        try:
            g = await client.wait_for('message', check=check_guess, timeout=10.0)
            if int(g.content) == num: await message.channel.send(f"✅ صح! الرقم هو {num}")
            else: await message.channel.send(f"❌ خطأ، الرقم كان {num}")
        except: await message.channel.send("⌛ تأخرت بالتخمين!")

    if message.content.startswith('!rps'):
        options = ["حجر", "ورقة", "مقص"]
        bot_choice = random.choice(options)
        user_choice = message.content.split()[-1] if len(message.content.split()) > 1 else None
        if user_choice not in options:
            await message.channel.send("طريقة اللعب: `!rps حجر` أو `!rps ورقة` أو `!rps مقص`")
        else:
            if user_choice == bot_choice: result = "تعادل! 🤝"
            elif (user_choice == "حجر" and bot_choice == "مقص") or \
                 (user_choice == "ورقة" and bot_choice == "حجر") or \
                 (user_choice == "مقص" and bot_choice == "ورقة"):
                result = "فزت علي! 🎉"
            else: result = "أنا فزت! 🤖"
            await message.channel.send(f"أنا اخترت **{bot_choice}**. {result}")

    if message.content.startswith('!8ball'):
        responses = ["نعم بالتأكيد", "لا أظن ذلك", "ممكن", "اسأل لاحقاً", "من المستحيل", "طبعاً"]
        await message.channel.send(f"🔮 الكرة السحرية تقول: **{random.choice(responses)}**")

token = os.getenv('DISCORD_TOKEN')
client.run(token)
