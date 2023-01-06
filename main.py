import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

from dotenv import load_dotenv, find_dotenv
from datetime import datetime as dt
from datetime import timedelta
from asyncio import sleep
import os
import json

import game_informer

files = {
	'data': 'data.json', 
	'channels': 'channels.json',
	'games': 'games.json',
}

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

@bot.event
async def setup_hook():
	bot_loop.start()
	bot_loop_delete_message.start()

@bot.event
async def on_ready():
	for key, file_name in files.items():
		if not os.path.exists(file_name):
			with open(file_name, 'w', encoding='utf-8') as file:
				file.write('{}')
		
		try:
			with open(file_name, 'r', encoding='utf-8') as file:
				test = json.load(file)
		except:
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
					'everyone': str(False),
					'games': {},
				}

			json.dump(channels, file, ensure_ascii=False, indent=4)	

	print('Database loaded!')

	try:
		synced = await bot.tree.sync()
		print(f'All is right. Synced {len(synced)} commands')
	except Exception as e:
		print(e)

@bot.event
async def on_guild_join(guild):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		if channels.get(str(guild.id)) == None:
			channels[str(guild.id)] = {
				'channel': str(None),
				'status': str(False),
				'everyone': str(False),
				'games': {},
			}

		json.dump(channels, file, ensure_ascii=False, indent=4)


@tasks.loop(minutes=5.0, reconnect=True)
async def bot_loop_delete_message():
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for guild in bot.guilds:
		check = channels[str(guild.id)]
		if len(check['games']) != 0:
			for key, game in check['games'].items():
				if game['deleted'] != 'True':
					timenow = dt.utcnow() + timedelta(seconds=(3600*3))
					date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
					if date_end < timenow:
						channel = bot.get_channel(int(check['channel']))
						messsage = await channel.fetch_message(game['message_id'])
						await messsage.delete()

						check['games'][str(key)] = {
							'date_end': str(game['date_end']),
							'message_id': str(game['message_id']),
							'deleted': str(True),
						}

						with open(files['channels'], 'w', encoding='utf-8') as file:
							channels[str(guild.id)] = {
								'channel': str(check['channel']),
								'status': str(check['status']),
								'everyone': str(check['everyone']),
								'games': check['games'],
							}

							json.dump(channels, file, ensure_ascii=False, indent=4)
						


@tasks.loop(minutes=10.0, reconnect=True)
async def bot_loop():
	game_informer.check_new_games()

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['games'], 'r', encoding='utf-8') as file:
		games = json.load(file)

	for guild in bot.guilds:
		check = channels[str(guild.id)]
		if check['channel'] != 'None' and check['status'] != 'False':
			channel = bot.get_channel(int(check['channel']))
			for key, game in games.items():
				if key not in check['games']:
					if game['expired'] == 'False' and game['started'] == 'True':
						embed = discord.Embed()
						embed.title = game['title']
						embed.colour = discord.Color.green()
						embed.timestamp = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
						price = game['price']
						embed.add_field(name = f'Цена игры ({price})', value = game['description'], inline = False)
						embed.set_image(url=game['image'])
						embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
						embed.set_footer(text='Акция заканчивается')
						
						button = discord.ui.View()
						button.add_item(discord.ui.Button(
							label = 'Ссылка на раздачу',
							style = discord.ButtonStyle.success,
							url = game['url'],
							emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
							disabled = False,
						))
						content = '@everyone' if channels[str(guild.id)]['everyone'] == 'True' else '@here'
						
						timenow = dt.utcnow() + timedelta(seconds=(3600*3))
						date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
						time_delta = (date_end - timenow).total_seconds()

						message = await channel.send(
							content = content, 
							embed = embed, 
							allowed_mentions = discord.AllowedMentions.all(), 
							view = button,
							#delete_after = 60.0,
						)

						#print(message)

						games = channels[str(guild.id)]['games']
						games[str(game['id'])] = {
							'date_end': str(date_end),
							'message_id': str(message.id),
							'deleted': str(False),
						}

						with open(files['channels'], 'w', encoding='utf-8') as file:
							channels[str(guild.id)] = {
								'channel': str(channels[str(guild.id)]['channel']),
								'status': str(channels[str(guild.id)]['status']),
								'everyone': str(channels[str(guild.id)]['everyone']),
								'games': games,
							}

							json.dump(channels, file, ensure_ascii=False, indent=4)

# class Test_Button(discord.ui.View):
# 	def __init__(self):
# 		super().__init__(timeout=None)
# 	# @discord.ui.button(label="Link to the Game", style=discord.ButtonStyle.link, url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline')
# 	# async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
# 	# 	await interaction.response.send_message(content = 'Hello World')


@bot.tree.command(name='test_script')
@app_commands.checks.has_permissions(administrator=True)
async def test_script(interaction: discord.Interaction):
	with open(files['games'], 'r', encoding='utf-8') as file:
		games = json.load(file)

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for key, game in games.items():
		if game['expired'] == 'False' and game['started'] == 'True':
			embed = discord.Embed()
			embed.title = game['title']
			embed.colour = discord.Color.green()
			#embed.url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline'
			embed.timestamp = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
			price = game['price']
			embed.add_field(name = f'Цена игры ({price})', value = game['description'], inline = False)
			embed.set_image(url=game['image'])
			embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
			embed.set_footer(text='Акция заканчивается')
			
			button = discord.ui.View()
			button.add_item(discord.ui.Button(
				label = 'Ссылка на раздачу',
				style = discord.ButtonStyle.success,
				url = game['url'],
				emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
				disabled = False,
			))

			await interaction.response.send_message(content='@everyone', 
				embed = embed, 
				allowed_mentions = discord.AllowedMentions.all(), 
				view = button,
				delete_after = 10.0,
			)
			# embed.title = 'Eximius: Seize the Frontline'
			# embed.colour = discord.Color.green()
			# #embed.url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline'
			# embed.timestamp = dt.now()
			# embed.add_field(name = 'Цена игры (549 рублей)', value = 'EXIMIUS — это сочетание шутера от первого лица и стратегии в мире времени, основанное на командных захватах. Игра отличается многопользовательским геймплеем 5 на 5 игроков, причём каждая команда состоит из одного офицера и одного командира.', inline = False)
			# embed.set_image(url='https://cdn1.epicgames.com/offer/1c943de0163f4f0982f34dc0fc37dce9/EGS_EximiusSeizetheFrontline_AmmoboxStudios_S11_2560x1440-afd78f58327ae2bf5ae3e6f38ea0b6b3')
			# embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
			# embed.set_footer(text='Акция заканчивается')
			
			# button = Test_Button()
			# button.add_item(discord.ui.Button(
			# 	label = 'Ссылка на раздачу',
			# 	style = discord.ButtonStyle.success,
			# 	url = 'https://store.epicgames.com/en/p/eximius-seize-the-frontline',
			# 	emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
			# 	disabled = False,
			# ))

			# await interaction.response.send_message(content='@everyone', 
			# 	embed = embed, 
			# 	allowed_mentions = discord.AllowedMentions.all(), 
			# 	view = button,
			# )

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
@app_commands.checks.has_permissions(manage_channels=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(interaction.guild_id)] = {
			'channel': str(channel.id),
			'status': str(channels[str(interaction.guild_id)]['status']),
			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
			'games': channels[str(interaction.guild_id)]['games'],
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'Thanks {interaction.user.mention}. New channel is setup!', ephemeral=True)

@bot.tree.command(name='change_everyone')
@app_commands.checks.has_permissions(manage_channels=True)
async def change_everyone(interaction: discord.Interaction):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	everyone = str(channels[str(interaction.guild_id)]['everyone'])

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(interaction.guild_id)] = {
			'channel': str(channels[str(interaction.guild_id)]['channel']),
			'status': str(channels[str(interaction.guild_id)]['status']),
			'everyone': str(True) if everyone == 'False' else str(False),
			'games': channels[str(interaction.guild_id)]['games'],
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	if everyone == 'True':
		await interaction.response.send_message(f'Thanks {interaction.user.mention}. Everyone is OFF now!', ephemeral=True)
	else:
		await interaction.response.send_message(f'Thanks {interaction.user.mention}. Everyone is ON now!', ephemeral=True)

@bot.tree.command(name='start_bot')
@app_commands.checks.has_permissions(manage_channels=True)
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
			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
			'games': channels[str(interaction.guild_id)]['games'],
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was started!', ephemeral=True)


@bot.tree.command(name='stop_bot')
@app_commands.checks.has_permissions(manage_channels=True)
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
			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
			'games': channels[str(interaction.guild_id)]['games'],
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was stoped!', ephemeral=True)

@set_channel.error
async def set_channel_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@start_bot.error
async def start_bot_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@stop_bot.error
async def stop_bot_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@change_everyone.error
async def change_everyone_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@test_script.error
async def test_script_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.MissingPermissions):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

load_dotenv(find_dotenv())

bot.run(os.getenv('TOKEN'))