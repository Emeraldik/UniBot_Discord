import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

from dotenv import load_dotenv, find_dotenv
from datetime import datetime as dt
from asyncio import sleep
import os
import json

files = {
	'data': 'data.json', 
	'channels': 'channels.json'
}

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

@bot.event
async def setup_hook():
	bot_loop.start()

@bot.event
async def on_ready():
	for key, file_name in files.items():
		if not os.path.exists(file_name):
			with open(file_name, 'w', encoding='utf-8') as file:
				file.write('{}')

	print(f'Discord Bot {bot.user} is ready!')
	for guild in bot.guilds:
		data_members = {}
		with open(files['data'], 'r', encoding='utf-8') as file:
			data = json.load(file)

		with open(files['data'], 'w', encoding='utf-8') as file:
			for member in guild.members:
				if not member.bot:
					data_members[str(member.id)] = {
						'name': str(member.name),
						'avatar': str(member.display_avatar),
						'joined': str(member.joined_at),
					}
			data[str(guild.id)] = data_members

			json.dump(data, file, ensure_ascii=False, indent=4)
		
			#print(f'{member.name} {member.id} {member.joined_at}')
			

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			if channels.get(str(guild.id)) == None:
				channels[str(guild.id)] = {
					'channel': str(None),
					'status': str(False),
				}

			json.dump(channels, file, ensure_ascii=False, indent=4)	

	print('Database loaded!')

	try:
		synced = await bot.tree.sync()
		print(f'All is right. Synced {len(synced)} commands')
	except Exception as e:
		print(e)


@tasks.loop(seconds=10.0)
async def bot_loop():
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for guild in bot.guilds:
		check = channels[str(guild.id)]
		if check['channel'] != 'None' and check['status'] != 'False':
			channel = bot.get_channel(int(check['channel']))
			await channel.send('Hello, it\'s test!')

@bot.tree.command(name='test_script')
async def test_script(interaction: discord.Interaction):
	embed = discord.Embed()
	embed.title = title = 'Акция в Epic Games Store'
	embed.colour = discord.Color.green()
	#embed.url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline'
	embed.timestamp = dt.utcnow()
	embed.add_field(name = 'Eximius: Seize the Frontline', value = 'EXIMIUS — это сочетание шутера от первого лица и стратегии в мире времени, основанное на командных захватах. Игра отличается многопользовательским геймплеем 5 на 5 игроков, причём каждая команда состоит из одного офицера и одного командира.', inline = False)
	embed.set_image(url='https://cdn1.epicgames.com/offer/1c943de0163f4f0982f34dc0fc37dce9/EGS_EximiusSeizetheFrontline_AmmoboxStudios_S11_2560x1440-afd78f58327ae2bf5ae3e6f38ea0b6b3')
	embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
	embed.set_footer(text='Акция заканчивается')
	
	# button = discord.ui.Button()
	# button.label = 'Ссылка на раздачу'
	# button.url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline'
	# button.disabled = False

	await interaction.response.send_message(content='@everyone', 
		embed = embed, 
		allowed_mentions = discord.AllowedMentions.all(), 
		#view = discord.ui.View().add_item(button)
	)

# @bot_loop.before_loop
# async def wait__when_ready():
#     await bot.wait_until_ready()

# @bot.event
# async def on_message(message):
# 	await bot.process_commands(message)

# 	if message.author == bot.user: 
# 		return

	#print(f'New message by {message.author.name} : {message}')
	# await message.channel.typing()
	# await sleep(1)
	# await message.reply(content = f'Thanks for you message, {message.author.mention}', mention_author=False)

# @bot.command()
# @commands.has_permissions(manage_channels=True)
# async def set_channel(ctx, channel: discord.TextChannel):
	
# 	print(ctx.channel.name)
# 	await ctx.send('New channel is setup!')

# @set_channel.error
# async def error(ctx, error):
# 	if isinstance(error, commands.MissingRequiredArgument):
# 		print('Something went wrong...')

@bot.tree.command(name='set_channel')
@app_commands.describe(channel = 'What\'s new channel?')
@commands.has_permissions(manage_channels = True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(interaction.guild_id)] = {
			'channel': str(channel.id),
			'status': str(channels[str(interaction.guild_id)]['status']),
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'Thanks {interaction.user.mention}. New channel is setup!', ephemeral=True)

@bot.tree.command(name='start_bot')
@commands.has_permissions(manage_channels = True)
async def start_bot(interaction: discord.Interaction):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	if channels[str(interaction.guild_id)]['channel'] == 'None':
		await interaction.response.send_message(f'Error {interaction.user.mention}. Need setup channel!', ephemeral=True)
		return

	if channels[str(interaction.guild_id)]['status'] == 'True':
		await interaction.response.send_message(f'Error {interaction.user.mention}. Bot didn\'t stop!', ephemeral=True)
		return

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(interaction.guild_id)] = {
			'channel': str(channels[str(interaction.guild_id)]['channel']),
			'status': str(True),
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was started!', ephemeral=True)


@bot.tree.command(name='stop_bot')
@commands.has_permissions(manage_channels = True)
async def stop_bot(interaction: discord.Interaction):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	if channels[str(interaction.guild_id)]['status'] == 'False':
		await interaction.response.send_message(f'Error {interaction.user.mention}. Bot didn\'t start!', ephemeral=True)
		return

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(interaction.guild_id)] = {
			'channel': str(channels[str(interaction.guild_id)]['channel']),
			'status': str(False),
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was stoped!', ephemeral=True)

@set_channel.error
async def new_channel_error(interaction: discord.Interaction, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await interaction.response.send_message(f'{interaction.user.mention} You missing argument', ephemeral=True)		
	elif isinstance(error, commands.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)
	elif isinstance(error, commands.ChannelNotFound):
		await interaction.response.send_message(f'{interaction.user.mention} This channel doesn\'t exists', ephemeral=True)

@start_bot.error
async def start_bot_error(interaction: discord.Interaction, error):
	if isinstance(error, commands.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@stop_bot.error
async def stop_bot_error(interaction: discord.Interaction, error):
	if isinstance(error, commands.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)
	

load_dotenv(find_dotenv())

bot.run(os.getenv('TOKEN'))