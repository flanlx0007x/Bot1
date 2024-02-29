import discord
from discord.ext import commands
from discord import app_commands
import datetime
import time
import json
import youtube_dl
from keep_alive import keep_alive
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

TOKEN = "MTE2NTQ0MzExMTQ1NjA3OTkyMw.GbsSxP.mOd9OKRCT4ST5wcl8OusSI2Hedm3W80MY8WSig"
try:
    with open("server_data.json", "r") as file:
        server_data = json.load(file)
except FileNotFoundError:
    server_data = {}


def save_server_data():
    with open("server_data.json", "w") as file:
        json.dump(server_data, file)


@bot.event
async def on_ready():
    print("Bot: ready")
    synced = await bot.tree.sync()
    print(f"{len(synced)} command")
    await bot.change_presence(activity=discord.Game(name="Playing with Python"))
server_data = {}


@bot.tree.command(name='set_welcome_room', description='เป็นการsetค่าห้องสำหรับต้อนรับสมาชิก')
async def set_welcome_room(ctx, channel: discord.TextChannel):
    if ctx.guild.id not in server_data:
        server_data[ctx.guild.id] = {"welcome_channel": None, "remove_member_channel": None}

    server_data[ctx.guild.id]["welcome_channel"] = channel.id
    await ctx.response.send_message(f"Welcome messages will now be sent to {channel.mention}!")


@bot.tree.command(name='set_removemeber_room', description='เป็นการsetค่าห้องสำหรับแจ้งลาออกของสมาชิก')
async def set_removemeber_room(ctx, channel: discord.TextChannel):
    if ctx.guild.id not in server_data:
        server_data[ctx.guild.id] = {"welcome_channel": None, "remove_member_channel": None}

    server_data[ctx.guild.id]["remove_member_channel"] = channel.id
    await ctx.response.send_message(f"removemeber will now be sent to {channel.mention}!")


@bot.event
async def on_disconnect():
    save_server_data()




@bot.event
async def on_member_join(member):
    if member.guild.id in server_data and server_data[member.guild.id]["welcome_channel"] is not None:
        channel = bot.get_channel(server_data[member.guild.id]["welcome_channel"])

        # ตรวจสอบว่ามีการตั้งค่า welcome_settings หรือไม่
        if "welcome_settings" in server_data[member.guild.id]:
            welcome_settings = server_data[member.guild.id]["welcome_settings"]
            if "welcome_text" in welcome_settings:
                welcome_text = welcome_settings["welcome_text"]
            else:
                welcome_text = "Welcome to the server, {member.mention}!"
            if "description_text" in welcome_settings:
                description_text = welcome_settings["description_text"]
            else:
                description_text = "Welcome to our server!"
        else:
            welcome_text = "Welcome to the server, {member.mention}!"
            description_text = "Welcome to our server!"

        embed = discord.Embed(title=welcome_text.format(member=member),
                              description=description_text.format(member=member),
                              color=0x66FFFF)
        embed.set_image(url="https://media.tenor.com/cF12xp3X7RYAAAAM/universe-galaxy.gif")
        await channel.send(embed=embed)


@bot.tree.command(name='set_welcome_settings', description='เป็นการsetค่าสำหรับการต้อนรับสมาชิก')
async def set_welcome_settings(ctx, setting_type: str, *, new_value: str):
    if ctx.guild.id not in server_data:
        server_data[ctx.guild.id] = {"welcome_channel": None, "welcome_settings": {}}

    # ตรวจสอบว่า setting_type เป็น "welcome_text" หรือ "description_text" หรือไม่
    if setting_type.lower() == "title":
        server_data[ctx.guild.id]["welcome_settings"]["title"] = new_value
        await ctx.response.send_message(f"Welcome text has been updated to: {new_value}")
    elif setting_type.lower() == "description":
        server_data[ctx.guild.id]["welcome_settings"]["description"] = new_value
        await ctx.response.send_message(f"Description text has been updated to: {new_value}")
    else:
        await ctx.response.send_message("Invalid setting type. Please use 'title' or 'description'.")

    save_server_data()
@bot.event
async def on_member_remove(member):
    if member.guild.id in server_data and server_data[member.guild.id]["remove_member_channel"] is not None:
        channel = bot.get_channel(server_data[member.guild.id]["remove_member_channel"])
        text = f"Goodbye, {member.mention}!"
        embed = discord.Embed(title='Goodbye!',
                              description=text,
                              color=0xFF0000)
        embed.set_image(url="https://media.tenor.com/mE8G6htsZzAAAAAM/garou-opm.gif")
        await channel.send(embed=embed)


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")


@bot.tree.command(name='hello', description='เป็นการตอบกลับ')
async def treecommand(interaction):
    await interaction.response.send_message("ไงครับ ผมคือบอทดิส")


@bot.tree.command(name='nickname', description='เปลี่ยนชื่อของคุณเท่านั้น')
async def change_nickname(ctx, *, new_nickname: str):
    try:
        await ctx.user.edit(nick=new_nickname)
        await ctx.send(f"เปลี่ยนชื่อของ {member.mention} เป็น {new_nickname} แล้ว!")
    except discord.Forbidden:
        await ctx.response.send_message("ไม่สามารถเปลี่ยนชื่อได้ เนื่องจากข้อจำกัดสิทธิ์!")
    except discord.HTTPException:
        await ctx.response.send_message("เกิดข้อผิดพลาดในการดำเนินการ กรุณาลองใหม่ภายหลัง!")


USER_MESSAGES = {}


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    current_time = time.time()

    if message.author.id in USER_MESSAGES:
        time_difference = current_time - USER_MESSAGES[message.author.id][-1]
        if time_difference < 0.25:
            await message.delete()
            await message.channel.send(f"{message.author.mention} ห้ามสแปม!")

    if message.author.id not in USER_MESSAGES:
        USER_MESSAGES[message.author.id] = [current_time]
    else:
        USER_MESSAGES[message.author.id].append(current_time)

    await bot.process_commands(message)  # ประมวลผลคำสั่งทั่วไป


@bot.tree.command(name='name')
@app_commands.describe(name='ชื่ออะไร')
async def namecommand(interaction, name: str):
    await interaction.response.send_message(f"Hello {name}")


# ข้อมูล key และการตรวจสอบความถูกต้องของ key
VALID_KEYS = ["key1", "key2", "key3"]


def check_key(key):
    async def predicate(ctx):
        if key in VALID_KEYS:
            return True
        else:
            await ctx.send("Key ไม่ถูกต้อง")
            return False

    return commands.check(predicate)


VALID_KEYS = "1Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473"


def check_key(key):
    async def predicate(ctx):
        if key in VALID_KEYS:
            return True
        else:
            await ctx.send("Key ไม่ถูกต้อง")
            return False

    return commands.check(predicate)


@bot.tree.command(name='create_channels', description='เพิ่มห้องในหมวดหมู่ที่กำหนด')
async def create_channels(interaction, key: str, channel_name_or_id: str, channel_type: str, number_of_channels: int,
                          category_name_or_id: str = None):
    if key not in VALID_KEYS:
        await interaction.response.send_message("Key ไม่ถูกต้อง")
        return

    guild = interaction.guild
    category = None

    if category_name_or_id:

        if category_name_or_id.isdigit():
            category = discord.utils.get(guild.categories, id=int(category_name_or_id))
        else:
            category = discord.utils.get(guild.categories, name=category_name_or_id)

        if not category:
            await interaction.response.send_message(f"ไม่พบหมวดหมู่ชื่อหรือ ID '{category_name_or_id}' ในเซิร์ฟเวอร์")
            return

    for i in range(number_of_channels):
        if category:
            if channel_type.lower() == 'voice':
                new_channel = await guild.create_voice_channel(name=f"{channel_name_or_id}", category=category)
            else:
                new_channel = await guild.create_text_channel(name=f"{channel_name_or_id}", category=category)
        else:
            if channel_type.lower() == 'voice':
                new_channel = await guild.create_voice_channel(name=f"{channel_name_or_id}")
            else:
                new_channel = await guild.create_text_channel(name=f"{channel_name_or_id}")

    if category:
        await interaction.response.send_message(
            f'เพิ่มห้องแชท {number_of_channels} ห้อง ชื่อ `{channel_name_or_id}` ประเภท `{channel_type}` ในหมวดหมู่ `{category.name}` เรียบร้อยแล้ว!')
    else:
        await interaction.response.send_message(
            f'เพิ่มห้องแชท {number_of_channels} ห้อง ชื่อ `{channel_name_or_id}` ประเภท `{channel_type}` เรียบร้อยแล้ว!')


@bot.tree.command(name='move', description='ย้ายสมาชิกไปยังห้องคุยอื่นๆ')
async def move_member(interaction, key: str, target_member: discord.Member, destination_channel: discord.VoiceChannel):
    if key not in VALID_KEYS:
        await interaction.response.send_message("Key ไม่ถูกต้อง")
        return
    if target_member.guild != interaction.guild:
        await interaction.response.send_message("เป้าหมายต้องอยู่ในเซิร์ฟเวอร์เดียวกันกับบอท")
        return

    # ย้ายสมาชิกไปยังห้องที่เลือก
    await target_member.move_to(destination_channel)
    await interaction.response.send_message(f"ย้าย {target_member.mention} ไปยังห้อง {destination_channel.name} แล้ว!")


@bot.tree.command(name='dm_key', description='ส่ง Key ไปยังผู้ใช้ที่กำหนด')
async def dm_key(interaction):
    # ตรวจสอบว่าผู้ใช้เป็นเพียงคุณและเพื่อนเท่านั้น
    allowed_user_ids = [862571604751810602, 1044945204827918466]
    if interaction.user.id not in allowed_user_ids:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
        return

    key = "1Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473123tzuchi2473123123123tzuchi24731231231231231Willberich123123123123tzuchi2473"  # สร้าง Key ตามที่คุณต้องการ

    # ส่งข้อความพร้อมกับ Key ไปยังผู้ใช้ที่กำหนดผ่าน DM
    for user_id in allowed_user_ids:
        user = await bot.fetch_user(user_id)
        if user:
            await user.send(f"นี่คือ Key ของคุณ: ```{key}```")


USER_MESSAGES = {}

# เปลี่ยนเป็นเวลาที่คุณต้องการ (หน่วยเป็นวินาที)
TIME_THRESHOLD = 2


@bot.event
async def on_message(message):
    # ตรวจสอบว่าข้อความเป็นของบอทหรือไม่
    if message.author == bot.user:
        return

    # เก็บเวลาข้อความ
    current_time = time.time()

    # ตรวจสอบว่าสมาชิกมียศ "สแปม" หรือไม่
    spam_role = discord.utils.get(message.guild.roles, name="สแปม")
    if spam_role and spam_role in message.author.roles:
        # ลบข้อความทันที
        await message.delete()
        # ข้อความเตือนสมาชิก

    # เพิ่มข้อความลงในรายการของสมาชิก
    if message.author.id not in USER_MESSAGES:
        USER_MESSAGES[message.author.id] = [current_time]
    else:
        USER_MESSAGES[message.author.id].append(current_time)

    await bot.process_commands(message)  # ประมวลผลคำสั่งอื่นๆ


@bot.tree.command(name='createrole', description='สร้างยศใหม่')
async def create_role(ctx, role_name: str, color_hex: str = None):
    guild = ctx.guild
    if discord.utils.get(guild.roles, name=role_name):
        await ctx.send(f"ยศชื่อ '{role_name}' มีอยู่แล้ว!")
        return

    if color_hex is None:
        color = discord.Color.default()
    else:

        color_hex = color_hex.lstrip('#')
        color = discord.Color(int(color_hex, 16))

    await guild.create_role(name=role_name, color=color)
    await ctx.channel.send(f"สร้างยศชื่อ '{role_name}' เรียบร้อยแล้ว!")

song_database = {}
@bot.command(name='addsong', description='เพิ่มเพลงเข้าสู่ฐานข้อมูล')
async def addsong(ctx: commands.Context, song_name: str, song_url: str):
    song_database[song_name] = song_url
    await ctx.send(f"เพลง '{song_name}' ถูกเพิ่มลงในฐานข้อมูลแล้ว!")


@bot.command(name='play', description='เล่นเพลง')
async def play(ctx: commands.Context, song_name: str):
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        voice_client = await voice_channel.connect()

        # เล่นเพลงจาก URL ในฐานข้อมูล
        if song_name in song_database:
            voice_client.play(discord.FFmpegPCMAudio(song_database[song_name]))
        else:
            await ctx.send("เพลงนี้ไม่มีในฐานข้อมูล!")
    else:
        await ctx.send("คุณต้องอยู่ในช่องเสียงก่อน!")

@bot.command(name='stop', description='หยุดเพลง')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("เพลงถูกหยุดแล้ว!")
    else:
        await ctx.send("ไม่มีเพลงที่กำลังเล่นอยู่ในขณะนี้!")

@bot.tree.command(name='test_welcome', description='เป็นการทดสอบการต้อนรับสมาชิกใหม่')
async def test_welcome(ctx):
    # สร้างสมาชิกสมมติ
    member = ctx.user
    guild = ctx.guild
    if guild.id in server_data and server_data[guild.id]["welcome_channel"] is not None:
        channel = bot.get_channel(server_data[guild.id]["welcome_channel"])

        # ตรวจสอบว่ามีการตั้งค่า welcome_settings หรือไม่
        if "welcome_settings" in server_data[guild.id]:
            welcome_settings = server_data[guild.id]["welcome_settings"]
            if "welcome_text" in welcome_settings:
                welcome_text = welcome_settings["welcome_text"]
            else:
                welcome_text = "Welcome to the server, {member.mention}!"
            if "description_text" in welcome_settings:
                description_text = welcome_settings["description_text"]
            else:
                description_text = "Welcome to our server!"
        else:
            welcome_text = "Welcome to the server, {member.mention}!"
            description_text = "Welcome to our server!"

        embed = discord.Embed(title=welcome_text.format(member=member),
                              description=description_text.format(member=member),
                              color=0x66FFFF)
        embed.set_image(url="https://media.tenor.com/cF12xp3X7RYAAAAM/universe-galaxy.gif")
        await channel.send(embed=embed)
    else:
        await ctx.response.send_message("Please set the welcome channel first using the set_welcome_channel command.")

@bot.tree.command(name='deleteroom', description='ลบห้อง')
async def delete_room(interaction, key: str, room_name: str, quantity: int = 1):
    if key not in VALID_KEYS:
        await interaction.response.send_message("Key ไม่ถูกต้อง")
        return
    voice_channels = [channel for channel in interaction.guild.channels if
                      isinstance(channel, discord.VoiceChannel) and channel.name == room_name]
    text_channels = [channel for channel in interaction.guild.channels if
                     isinstance(channel, discord.TextChannel) and channel.name == room_name]

    rooms = voice_channels + text_channels

    if not rooms:
        await interaction.response.send_message(
            f"ไม่พบห้องที่ชื่อ '{room_name}' ที่เป็น Voice Channel หรือ Text Channel")
        return

    # นับจำนวนห้องที่พบ
    num_rooms_found = len(rooms)

    if num_rooms_found < quantity:
        await interaction.response.send_message(
            f"พบห้องที่ชื่อ '{room_name}' ที่เป็น Voice Channel หรือ Text Channel เพียง {num_rooms_found} ห้องเท่านั้น")
        return

    # สร้างเซ็ตของห้องที่พบซ้ำกัน
    duplicate_rooms = set()

    # ลบห้องตามจำนวนที่กำหนด
    i = 0
    while i < min(quantity, num_rooms_found):
        room = rooms[i]
        if room not in duplicate_rooms:
            await room.delete()
            duplicate_rooms.add(room)
            i += 1
        else:
            del rooms[i]
            num_rooms_found -= 1

    await interaction.response.send_message(
        f"ลบห้อง '{room_name}' จำนวน {min(quantity, num_rooms_found)} ห้องเรียบร้อยแล้ว!")


@bot.tree.command(name='slow_mode', description='เป็นการปรับจำกัดเวลาห้อง')
async def slowmod(interaction, key: str, channel: discord.TextChannel, time_seconds: int):
    if key not in VALID_KEYS:
        await interaction.response.send_message("Key ไม่ถูกต้อง")
        return

    # ตั้งค่า slow mode ในห้อง
    await channel.edit(slowmode_delay=time_seconds)
    await interaction.response.send_message(f"ตั้งค่า slow mode ในห้อง {channel.name} เป็น {time_seconds} วินาที")


@bot.tree.command(name='assignrole', description='ให้ยศให้สมาชิก')
async def assign_role(ctx, member: discord.Member, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"ไม่พบยศที่ชื่อ '{role_name}'")
        return

    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"ให้ยศ '{role_name}' ให้ {member.display_name} เรียบร้อยแล้ว!")
    except discord.Forbidden:
        await interaction.response.send_message("ไม่สามารถให้ยศได้ เนื่องจากสิทธิ์ไม่เพียงพอ")


@bot.tree.command(name='help', description='เป็นการช่วยหาคำสั่งทั้งหมด')
async def helpcommand(interaction):
    embed = discord.Embed(title='Help command',
                          description='Bot help command',
                          color=0x66FFFF,
                          timestamp=datetime.datetime.utcnow())

    # ตัวอย่างเพิ่มคำสั่งใน Embed
    embed.add_field(name='```/hello```', value='คำสั่งทักทาย', inline=False)
    embed.add_field(name='```/set_welcome_room```', value='คำสั่งตั้งค่าห้องต้อนรับ', inline=False)
    embed.add_field(name='```set_removemeber_room```', value='คำสั่งตั้งค่าห้องต้อนรับ', inline=False)
    embed.add_field(name='```/nickname```', value='คำสั่งตั้งชื่อเล่น', inline=False)
    embed.add_field(name='```/name```', value='พิมชื่อเล่นๆ', inline=False)
    embed.add_field(name='```/create_channels```', value='สร้างห้องแต่ต้องมีkeyน่ะ', inline=False)
    embed.add_field(name='```/dm_key```', value='เอาkeyแต่ล็อคIDน่ะจะ', inline=False)
    embed.add_field(name='```/createrole```', value='สร้างยศ', inline=False)
    embed.add_field(name='```/deleteroom```', value='ลบห้อง', inline=False)
    embed.add_field(name='```/assignrole```', value='ใส่ยศให้เอง', inline=False)

    await interaction.response.send_message(embed=embed)

keep_alive()
bot.run(TOKEN)
