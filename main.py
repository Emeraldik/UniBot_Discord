import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

from dotenv import load_dotenv, find_dotenv
from datetime import datetime as dt
from pytz import timezone

import os
import json

import game_informer

files = {
	'users': 'users.json', 
	'channels': 'channels.json',
	'games': 'games.json',
}

users = {
	'303498186708746240',
}

ownerID = 303498186708746240

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

		with open(files['users'], 'r', encoding='utf-8') as file:
			data = json.load(file)

		with open(files['users'], 'w', encoding='utf-8') as file:
			for member in guild.members:
				if not member.bot:
					if not str(guild.id) in data:
						data_members[str(member.id)] = {
							'name': str(member.name),
							'has_permissions': str(True) if ((str(member.id) in users) or (member.id == ownerID)) else str(False),  
						}
					elif not str(member.id) in data[str(guild.id)]:
						data_members[str(member.id)] = {
							'name': str(member.name),
							'has_permissions': str(True) if ((str(member.id) in users) or (member.id == ownerID)) else str(False),  
						}
					else:
						data_members = data[str(guild.id)]

			data[str(guild.id)] = data_members

			json.dump(data, file, ensure_ascii=False, indent=4)
		
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			if not str(guild.id) in channels:
				channels[str(guild.id)] = {
					'channel': str(0),
					'status': str(False),
					'role': str(0),
					'need_delete': str(False),
					'games': {},
				}

			json.dump(channels, file, ensure_ascii=False, indent=4)	

	print('Database loaded!')

	try:
		synced = await bot.tree.sync()
		print(f'All is right. Synced {len(synced)} commands')
	except Exception as e:
		print(e)

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} servers ({len(bot.users)} users)',
	))

@bot.event
async def on_guild_join(guild):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		if not str(guild.id) in channels:
			channels[str(guild.id)] = {
				'channel': str(0),
				'status': str(False),
				'role': str(0),
				'need_delete': str(False),
				'games': {},
			}

		json.dump(channels, file, ensure_ascii=False, indent=4)

	data_members = {}

	with open(files['users'], 'r', encoding='utf-8') as file:
		data = json.load(file)

	with open(files['users'], 'w', encoding='utf-8') as file:
		for member in guild.members:
			if not member.bot:
				if not str(guild.id) in data:
					data_members[str(member.id)] = {
						'name': str(member.name),
						'has_permissions': str(True) if ((str(member.id) in users) or (member.id == ownerID)) else str(False),  
					}
				elif not str(member.id) in data[str(guild.id)]:
					data_members[str(member.id)] = {
						'name': str(member.name),
						'has_permissions': str(True) if ((str(member.id) in users) or (member.id == ownerID)) else str(False),  
					}
				else:
					data_members = data[str(guild.id)]

		data[str(guild.id)] = data_members

		json.dump(data, file, ensure_ascii=False, indent=4)

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} servers ({len(bot.users)} users)',
	))

@bot.event
async def on_guild_remove(guild):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(guild.id)] = {
			'channel': channels[str(guild.id)]['channel'],
			'status': str(False),
			'role': channels[str(guild.id)]['role'],
			'need_delete': channels[str(guild.id)]['need_delete'],
			'games': channels[str(guild.id)]['games'],
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)
	
	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} servers ({len(bot.users)} users)',
	))

@bot.event
async def on_member_join(member):
	with open(files['users'], 'r', encoding='utf-8') as file:
		data = json.load(file)

	with open(files['users'], 'w', encoding='utf-8') as file:
		data_members = data[str(member.guild.id)]
		if not str(member.id) in data_members:
			data_members[str(member.id)] = {
				'name': str(member.name),
				'has_permissions': str(True) if ((str(member.id) in users) or (member.id == ownerID)) else str(False),  
			}
			data[str(member.guild.id)] = data_members

		json.dump(data, file, ensure_ascii=False, indent=4)

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} servers ({len(bot.users)} users)',
	))

@bot.event
async def on_member_remove(member):
	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} servers ({len(bot.users)} users)',
	))

@bot.event
async def on_user_update(before, after):
	with open(files['users'], 'r', encoding='utf-8') as file:
		data = json.load(file)

	with open(files['users'], 'w', encoding='utf-8') as file:
		for key, guild in data.items():
			if str(before.id) in guild:
				guild[str(before.id)] = {
					'name': str(after.name),
					'has_permissions': str(True) if ((str(before.id) in users) or (before.id == ownerID)) else str(False),  
				}
	
		json.dump(data, file, ensure_ascii=False, indent=4)

@tasks.loop(minutes=10.0, reconnect=True)
async def bot_loop_delete_message():
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['games'], 'r', encoding='utf-8') as file:
		games = json.load(file)

	for guild in bot.guilds:
		check = channels[str(guild.id)]
		if len(check['games']) != 0:
			for key, game in check['games'].items():
				if game['deleted'] != 'True':
					timenow = dt.utcnow()
					date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
					if date_end < timenow:
						channel = bot.get_channel(int(game['channel_id']))
						try:
							message = await channel.fetch_message(game['message_id'])
						except Exception as e:
							pass
						else:
							if check['need_delete'] == 'True':
								await message.delete()
							else:
								GM = games[key]

								embed = discord.Embed()
								embed.title = GM['title']
								embed.colour = discord.Color.green()
								utc = timezone('UTC')
								time = dt.strptime(GM['date_end'], "%Y-%m-%d %H:%M:%S")
								time = utc.localize(time)
								embed.timestamp = time
								price = GM['price']
								embed.add_field(name = f'Цена игры ({price})', value = GM['description'], inline = False)
								embed.set_image(url=GM['image'])
								embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
								embed.set_footer(text='Акция закончилась')
								
								label = '(Не для RU аккаунта)' if GM['key'] == 'not_ru' else ''

								button = discord.ui.View()
								button.add_item(discord.ui.Button(
									label = f'Ссылка на раздачу {label}',
									style = discord.ButtonStyle.success,
									url = GM['url'],
									emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
									disabled = True,
								))

								await message.edit(
									embed = embed,
									view = button,
								)

								check['games'][str(key)] = {
									'date_end': str(game['date_end']),
									'message_id': str(game['message_id']),
									'channel_id': str(game['channel_id']),
									'deleted': str(True),
									'game_info': game['game_info'],
								}

								channels[str(guild.id)] = {
									'channel': str(check['channel']),
									'status': str(check['status']),
									'role': str(check['role']),
									'need_delete': str(check['need_delete']),
									'games': check['games'],
								}

	with open(files['channels'], 'w', encoding='utf-8') as file:
		json.dump(channels, file, ensure_ascii=False, indent=4)
						
@tasks.loop(seconds=30.0, reconnect=True)
async def bot_loop():
	game_informer.check_games()

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['games'], 'r', encoding='utf-8') as file:
		games = json.load(file)

	for guild in bot.guilds:
		check = channels[str(guild.id)]
		if check['channel'] != 'None' and check['status'] != 'False':
			channel = bot.get_channel(int(check['channel']))
			if channel == None:
				continue
			for key, game in games.items():
				if key not in check['games']:
					if game['expired'] == 'False' and game['started'] == 'True':
						utc = timezone('UTC')
						date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
						date_for_json = date_end
						date_end = utc.localize(date_end)

						embed = discord.Embed()
						embed.title = game['title']
						embed.colour = discord.Color.green()
						embed.timestamp = date_end
						price = game['price']
						embed.add_field(name = f'Цена игры ({price})', value = game['description'], inline = False)
						embed.set_image(url=game['image'])
						embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
						embed.set_footer(text='Акция заканчивается')
						
						label = '(Не для RU аккаунта)' if game['key'] == 'not_ru' else ''

						button = discord.ui.View()
						button.add_item(discord.ui.Button(
							label = f'Ссылка на раздачу {label}',
							style = discord.ButtonStyle.success,
							url = game['url'],
							emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
							disabled = False,
						))
						
						content = ''

						if guild.get_role(int(check['role'])) != None:
							content = guild.get_role(int(check['role'])).mention if guild.get_role(int(check['role'])).name != '@everyone' else '@everyone'
						
						message = await channel.send(
							content = content, 
							embed = embed, 
							allowed_mentions = discord.AllowedMentions.all(), 
							view = button,
						)

						game_json = {
		                    'title': str(game['title']),
		                    'description': str(game['description']),
		                    'url': str(game['url']),
		                    'price': str(game['price']),
		                    'key': str(game['key']),
						}

						games_channel = channels[str(guild.id)]['games']
						games_channel[str(game['id'])] = {
							'date_end': str(date_for_json),
							'message_id': str(message.id),
							'channel_id': str(check['channel']),
							'deleted': str(False),
							'game_info': game_json,
						}

						channels[str(guild.id)] = {
							'channel': str(check['channel']),
							'status': str(check['status']),
							'role': str(check['role']),
							'need_delete': str(check['need_delete']),
							'games': games_channel,
						}

	with open(files['channels'], 'w', encoding='utf-8') as file:
		json.dump(channels, file, ensure_ascii=False, indent=4)

def is_owner():
	def predicate(interaction: discord.Interaction) -> bool:
		return interaction.user.id == ownerID
	return app_commands.check(predicate)

def in_list_users():
	def predicate(interaction: discord.Interaction) -> bool:
		with open(files['users'], 'r', encoding='utf-8') as file:
			data = json.load(file)
		return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False
	return app_commands.check(predicate)

def has_channel_permissions():
	def predicate(interaction: discord.Interaction) -> bool:
		if interaction.user.id == ownerID:
			return True

		if interaction.user.guild_permissions.manage_channels:
			return True

		with open(files['users'], 'r', encoding='utf-8') as file:
			data = json.load(file)
		return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False
		
	return app_commands.check(predicate)

@bot.tree.command(name='dev_test')
@app_commands.guild_only()
@is_owner()
async def dev_test(interaction: discord.Interaction):
	with open(files['games'], 'r', encoding='utf-8') as file:
		games = json.load(file)

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for key, game in games.items():
		if game['expired'] == 'False' and game['started'] == 'True':
			embed = discord.Embed()
			embed.title = game['title']
			embed.colour = discord.Color.green()
			utc = timezone('UTC')
			time = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
			time = utc.localize(time)
			embed.timestamp = time
			price = game['price']
			embed.add_field(name = f'Цена игры ({price})', value = game['description'], inline = False)
			embed.set_image(url=game['image'])
			embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
			embed.set_footer(text='Акция закончилась')
			
			button = discord.ui.View()
			button.add_item(discord.ui.Button(
				label = 'Ссылка на раздачу',
				style = discord.ButtonStyle.success,
				url = game['url'],
				emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
				disabled = False,
			))

			await interaction.response.send_message(
				content='', 
				embed = embed, 
				allowed_mentions = discord.AllowedMentions.all(), 
				view = button,
				delete_after = 10.0,
			)

async def embedSettignsMenu(interaction: discord.Interaction):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)
		
	guild = channels[str(interaction.guild.id)]
	
	channel_name = 'No channel'
	if bot.get_channel(int(guild['channel'])) != None:
		channel_name = bot.get_channel(int(guild['channel'])).name
	
	role_name = 'No role'
	
	if interaction.guild.get_role(int(guild['role'])) != None:
		role_name = interaction.guild.get_role(int(guild['role'])).name
	
	delete_edit_name = 'Now message will be Delete' if guild['need_delete'] == 'True' else 'Now message will be Edit'
	start_stop_name = 'Bot Started' if guild['status'] == 'True' else 'Bot Stoped'

	embed = discord.Embed()
	embed.title = f'Settings of Bot'
	embed.add_field(name = f'Current channel', value = channel_name, inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True) # Empty Field
	embed.add_field(name = f'Current role', value = role_name, inline = True)
	embed.add_field(name = f'Delete/Edit setting', value = delete_edit_name, inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True) # Empty Field
	embed.add_field(name = f'Bot Status', value = start_stop_name, inline = True)
	embed.set_author(name = interaction.user.name, icon_url = interaction.user.display_avatar.url)
	embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
	embed.colour = discord.Color.green()
	embed.timestamp = dt.now(timezone('UTC'))

	return embed

class _SubmitModal(discord.ui.Modal, title = 'Submit for reset settings: write \'SUBMIT\''):
	check = discord.ui.TextInput(
		label = 'Submit reset',
		style = discord.TextStyle.short,
		placeholder = 'SUBMIT',
		required = False,
	)

	async def on_submit(self, interaction: discord.Interaction):
		if self.check.value != 'SUBMIT': 
			for btn in self.view.children:
				if btn.custom_id != '_return':
					btn.disabled = True

			await interaction.response.edit_message(
				content = 'Settings don\'t reset!',
			 	view = self.view
			)
			return

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild.id)] = {
				'channel': str(0),
				'status': str(False),
				'role': str(0),
				'need_delete': str(False),
				'games': channels[str(interaction.guild.id)]['games'],
			}

			json.dump(channels, file, ensure_ascii=False, indent=4)

		for btn in self.view.children:
			if btn.custom_id != '_return':
				btn.disabled = True

		await interaction.response.edit_message(
			content = 'Settings reset!',
		 	view = self.view
		)

class _ResetMenu(discord.ui.View):
	def __init__(self):
		super().__init__(timeout = None)

	@discord.ui.button(
		style = discord.ButtonStyle.success,
		label = 'Confirm',
	)
	async def confirm_callback(self, interaction: discord.Interaction, button):
		submit = _SubmitModal()
		submit.view = self
		await interaction.response.send_modal(submit)

class _ReturnButton(discord.ui.Button):
	def __init__(self, view):
		self.menu = view
		super().__init__(
			label = 'Return to settings menu',
			style = discord.ButtonStyle.danger,
			custom_id = '_return',
		)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.edit_message(content = '', embed = await embedSettignsMenu(interaction), view = self.menu)

class _ChannelSettingsMenu(discord.ui.View):
	async def update_message(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		channel = channels[str(interaction.guild.id)]['channel']

		channel_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label = text.name,
					value = str(text.id)
				) for text in interaction.guild.text_channels
			],
			placeholder = f'Choose the channel',
		)

		channel_name = 'No channel'
		if bot.get_channel(int(channel)) != None:
			channel_name = bot.get_channel(int(channel)).name
		self.last_channel = channel_name
		embed = discord.Embed()
		embed.title = f'Settings of Channel'
		embed.add_field(name = f'Current channel for {interaction.guild.name} channel', value = self.last_channel, inline = False)
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		embed.colour = discord.Color.green()
		embed.timestamp = dt.now(timezone('UTC'))

		async def select_callback(interaction: discord.Interaction):
			channel_new = bot.get_channel(int(channel_select.values[0]))
			if channel_new == None:
				await interaction.response.send_message('Channel doesn\'t exists', ephemeral = True)
				return

			# if channel_name == channel_new.name:
			# 	return

			embed.clear_fields()
			embed.add_field(name = f'Current channel for {interaction.guild.name} channel', value = channel_new.name, inline = False)
			embed.add_field(name = f'Last channel', value = self.last_channel, inline = False)
			self.last_channel = channel_new.name
			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)] = {
					'channel': str(channel_new.id),
					'status': str(channels[str(interaction.guild_id)]['status']),
					'role': str(channels[str(interaction.guild_id)]['role']),
					'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
					'games': channels[str(interaction.guild_id)]['games'],
				}

				json.dump(channels, file, ensure_ascii=False, indent=4)

			await interaction.response.edit_message(embed = embed, view = self)
	
		channel_select.callback = select_callback

		self.add_item(channel_select)
		self.add_item(_ReturnButton(self.menu))
		await interaction.response.edit_message(embed = embed, view = self)

class _RoleSettingsMenu(discord.ui.View):
	async def update_message(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		role = channels[str(interaction.guild.id)]['role']

		role_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label = role_.name,
					value = str(role_.id)
				) for role_ in interaction.guild.roles if (not role_.is_bot_managed())
			] + [
				discord.SelectOption(
					label = 'None',
					value = '0'
				),
			],
			placeholder = f'Choose the role',
		)

		role_name = 'No role'
		if interaction.guild.get_role(int(role)) != None:
			role_name = interaction.guild.get_role(int(role)).name
		self.last_role = role_name
		embed = discord.Embed()
		embed.title = f'Settings of Role'
		embed.add_field(name = f'Current role for {interaction.guild.name} channel', value = self.last_role, inline = False)
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		embed.colour = discord.Color.green()
		embed.timestamp = dt.now(timezone('UTC'))

		async def select_callback(interaction: discord.Interaction):
			role_new = interaction.guild.get_role(int(role_select.values[0])) if (role_select.values[0] != '0') else '0'
			if role_new == None:
				await interaction.response.send_message('Role doesn\'t exists', ephemeral = True)
				return

			if role_new == '0':
				role_new_name = 'No role'
			else:
				role_new_name = role_new.name

			# if self.last_role == role_new_name:
			# 	return

			embed.clear_fields()
			embed.add_field(name = f'Current role for {interaction.guild.name} channel', value = role_new_name, inline = False)
			embed.add_field(name = f'Last role', value = self.last_role, inline = False)
			self.last_role = role_new_name
			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)] = {
					'channel': str(channels[str(interaction.guild_id)]['channel']),
					'status': str(channels[str(interaction.guild_id)]['status']),
					'role': str(role_new.id) if role_new != '0' else '0',
					'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
					'games': channels[str(interaction.guild_id)]['games'],
				}

				json.dump(channels, file, ensure_ascii=False, indent=4)

			await interaction.response.edit_message(embed = embed, view = self)
	
		role_select.callback = select_callback

		self.add_item(role_select)
		self.add_item(_ReturnButton(self.menu))
		await interaction.response.edit_message(embed = embed, view = self)

class _StatusSettingsButton(discord.ui.Button):
	def __init__(self, view, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		self.menu = view
		self.interaction = interaction
		super().__init__(
			label = 'Start Bot' if channels[str(self.interaction.guild_id)]['status'] == 'False' else 'Stop Bot',
			style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)]['status'] == 'False' else discord.ButtonStyle.danger,
			row = 1,
		)

	async def callback(self, interaction: discord.Interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild_id)] = {
				'channel': str(channels[str(interaction.guild_id)]['channel']),
				'status': str(True) if channels[str(interaction.guild_id)]['status'] == 'False' else str(False),
				'role': str(channels[str(interaction.guild_id)]['role']),
				'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
				'games': channels[str(interaction.guild_id)]['games'],
			}

			json.dump(channels, file, ensure_ascii=False, indent=4)

		self.menu.remove_item(self)
		self.label = 'Start Bot' if channels[str(interaction.guild_id)]['status'] == 'False' else 'Stop Bot'
		self.style = style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)]['status'] == 'False' else discord.ButtonStyle.danger
		self.menu.add_item(self)
		await interaction.response.edit_message(content = '', embed = await embedSettignsMenu(interaction), view = self.menu)

class _SettingsMenu(discord.ui.View):
	def __init__(self):
		super().__init__(timeout = None)

	async def update_message(self, interaction: discord.Interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		embed = await embedSettignsMenu(interaction)
		await interaction.response.edit_message(content = '', embed = embed, view = self)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = 'Setup Channel',
		row = 1,
	)
	async def channel_settings(self, interaction: discord.Interaction, button):
		check_channels = [text.id for text in interaction.guild.text_channels]
		if len(check_channels) == 0:
			await interaction.response.send_message('No text channels in this guild', ephemeral = True)
			return

		channel_menu = _ChannelSettingsMenu()
		channel_menu.menu = self
		await channel_menu.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.secondary,
		label = 'Change Delete/Edit setting',
		row = 0,
	)
	async def need_delete_settings(self, interaction: discord.Interaction, button):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild_id)] = {
				'channel': str(channels[str(interaction.guild_id)]['channel']),
				'status': str(channels[str(interaction.guild_id)]['status']),
				'role': str(channels[str(interaction.guild_id)]['role']),
				'need_delete': str(True) if channels[str(interaction.guild_id)]['need_delete'] == 'False' else str(False),
				'games': channels[str(interaction.guild_id)]['games'],
			}

			json.dump(channels, file, ensure_ascii=False, indent=4)

		await self.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = 'Choose role',
		row = 0,
	)
	async def everyone_settings(self, interaction: discord.Interaction, button):
		check_roles = [role_.id for role_ in interaction.guild.roles]
		if len(check_roles) == 0:
			await interaction.response.send_message('No roles in this guild', ephemeral = True)
			return

		role_menu = _RoleSettingsMenu()
		role_menu.menu = self
		await role_menu.update_message(interaction)
		# with open(files['channels'], 'r', encoding='utf-8') as file:
		# 	channels = json.load(file)

		# with open(files['channels'], 'w', encoding='utf-8') as file:
		# 	channels[str(interaction.guild_id)] = {
		# 		'channel': str(channels[str(interaction.guild_id)]['channel']),
		# 		'status': str(channels[str(interaction.guild_id)]['status']),
		# 		'role': '@everyone' if channels[str(interaction.guild_id)]['role'] == 'None' else 'None',
		# 		'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
		# 		'games': channels[str(interaction.guild_id)]['games'],
		# 	}

		# 	json.dump(channels, file, ensure_ascii=False, indent=4)
		
		# await self.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.danger,
		label = 'Reset Settings',
		row = 1,
	)
	async def reset_settings(self, interaction: discord.Interaction, button):
		view = _ResetMenu()
		view.guild = interaction.guild
		_return = _ReturnButton(self)
		view.add_item(_return)
		await interaction.response.edit_message(
			content = 'You really want reset all settings for bot on this server?',
			embed = None,
			view = view
		)

@bot.tree.command(name='settings')
@app_commands.guild_only()
@has_channel_permissions()
async def settings(interaction: discord.Interaction):
	view = _SettingsMenu()
	embed = await embedSettignsMenu(interaction)
	view.embed = embed
	view.interaction = interaction
	view.add_item(_StatusSettingsButton(view, interaction))
	await interaction.response.send_message(embed = embed, view = view, ephemeral = True)

class _ChangeMessageModal(discord.ui.Modal):
	def __init__(self, game, embed, message, game_id):
		self.game = game
		self.embed = embed
		self.message = message
		self.game_id = game_id
		super().__init__(title = 'Message Editor')

	async def on_submit(self, interaction: discord.Interaction):
		options = self.game
		for _input in self.children:
			if str(self.game[_input.custom_id]) != str(_input.value):
				if _input.custom_id == 'key':
					if _input.value != 'ru':
						if _input.value != 'not_ru':
							await interaction.response.send_message(content = 'You change \'key\', but it\'s  not \'ru\' or \'not_ru\'', ephemeral = True)
							return
				options[str(_input.custom_id)] = str(_input.value)
		
		self.embed.title = options['title']
		price = options['price']
		self.embed.set_field_at(0, name = f'Цена игры ({price})', value = options['description'], inline = False)

		label = '(Не для RU аккаунта)' if options['key'] == 'not_ru' else ''

		view = discord.ui.View()
		view.add_item(discord.ui.Button(
			label = f'Ссылка на раздачу {label}',
			style = discord.ButtonStyle.success,
			url = options['url'],
			emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
			disabled = False,
		))

		button_confirm = discord.ui.Button(
			label = f'Apply changes',
			style = discord.ButtonStyle.success,
			disabled = False,
		)
		async def button_confirm_callback(interaction: discord.Interaction):
			with open(files['channels'], 'r', encoding='utf-8') as file:
				channels = json.load(file)

			games = channels[str(interaction.guild.id)]['games']
			games[str(self.game_id)]['game_info'] = options

			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild.id)] = {
					'channel': channels[str(interaction.guild.id)]['channel'],
					'status': channels[str(interaction.guild.id)]['status'],
					'role': channels[str(interaction.guild.id)]['role'],
					'need_delete': channels[str(interaction.guild.id)]['need_delete'],
					'games': games,
				}

				json.dump(channels, file, ensure_ascii=False, indent=4)

			view.clear_items()
			view.add_item(discord.ui.Button(
				label = f'Ссылка на раздачу {label}',
				style = discord.ButtonStyle.success,
				url = options['url'],
				emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
				disabled = False,
			))

			await self.message.edit(embed = self.embed, view = view)
			await interaction.response.edit_message(
				content = 'Message was edited',
				view = None,
				embed = None
			)

		button_confirm.callback = button_confirm_callback

		button_cancel = discord.ui.Button(
			label = f'Discard changes',
			style = discord.ButtonStyle.danger,
			disabled = False,
		)

		async def button_cancel_callback(interaction: discord.Interaction):
			await interaction.response.edit_message(
				content = 'Message edit was discard',
				view = None,
				embed = None
			)
		button_cancel.callback = button_cancel_callback

		view.add_item(button_confirm)
		view.add_item(button_cancel)

		await interaction.response.edit_message(
			content = 'How it will be view',
			view = view,
			embed = self.embed,
		)

class _SubmitMessageModal(discord.ui.Modal, title = 'Submit for delete message: write \'SUBMIT\''):
	check = discord.ui.TextInput(
		label = 'Submit reset',
		style = discord.TextStyle.short,
		placeholder = 'SUBMIT',
		required = False,
	)

	async def on_submit(self, interaction: discord.Interaction):
		if self.check.value != 'SUBMIT': 
			await interaction.response.edit_message(
				content = 'Message don\'t deleted!',
				embed = None,
				view = None,
			)
			return

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		games = channels[str(interaction.guild.id)]['games']
		games[str(self.game_id)]['deleted'] = str(True)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild.id)] = {
				'channel': channels[str(interaction.guild.id)]['channel'],
				'status': channels[str(interaction.guild.id)]['status'],
				'role': channels[str(interaction.guild.id)]['role'],
				'need_delete': channels[str(interaction.guild.id)]['need_delete'],
				'games': games,
			}

			json.dump(channels, file, ensure_ascii=False, indent=4)

		await self.message.delete()

		await interaction.response.edit_message(
			content = 'Message was deleted!',
			embed = None,
			view = None,
		)

@bot.tree.command(name='fix_message')
@app_commands.guild_only()
@has_channel_permissions()
async def fix_message(interaction: discord.Interaction):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	games = channels[str(interaction.guild.id)]['games']
	def select_channel():
		channel_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label =	message['game_info']['title'],
					value = str(key),
				) for key, message in games.items() if message['deleted'] != 'True'
			],
			placeholder = f'Choose the message, what you want change',
		)
		async def select_callback(interaction: discord.Interaction):
			channel = bot.get_channel(int(channels[str(interaction.guild.id)]['games'][str(channel_select.values[0])]['channel_id']))
			try:
				message = await channel.fetch_message(int(channels[str(interaction.guild.id)]['games'][str(channel_select.values[0])]['message_id']))
			except Exception as e:
				await interaction.response.send_message(content = 'Message is not exists', ephemeral = True)
			else:
				embed = message.embeds[0]
				game = channels[str(interaction.guild.id)]['games'][str(channel_select.values[0])]['game_info']
				game_id = str(channel_select.values[0])

				label = '(Не для RU аккаунта)' if game['key'] == 'not_ru' else ''
				
				view = discord.ui.View()
				view.add_item(discord.ui.Button(
					label = f'Ссылка на раздачу {label}',
					style = discord.ButtonStyle.success,
					url = game['url'],
					emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
					disabled = False,
				))

				button_change = discord.ui.Button(
					label = f'Change message',
					style = discord.ButtonStyle.primary,
					disabled = False,
				)

				async def button_change_callback(interaction: discord.Interaction):
					modal = _ChangeMessageModal(game, embed, message, game_id)
					labels = {
						'title': 'Title of Game',
	                    'description': 'Description of Game',
	                    'url': 'URL of Game',
	                    'price': 'Price of Game',
	                    'key': 'Key of Game : JUST \'ru\' or \'not_ru\'',
					}
					for key, value in game.items():
						check = discord.ui.TextInput(
							label = labels[str(key)],
							style = discord.TextStyle.short if key != 'description' else discord.TextStyle.long,
							default = str(value),
							required = True,
							custom_id = str(key)
						)
						try:
							modal.add_item(check)
						except Exception as e:
							pass
					await interaction.response.send_modal(modal)

				button_change.callback = button_change_callback

				button_delete = discord.ui.Button(
					label = f'Delete message',
					style = discord.ButtonStyle.danger,
					disabled = False,
				)

				async def button_delete_callback(interaction: discord.Interaction):
					modal = _SubmitMessageModal()
					modal.game_id = game_id
					modal.game = game
					modal.message = message
					await interaction.response.send_modal(modal)

				button_delete.callback = button_delete_callback

				view.add_item(button_change)
				view.add_item(button_delete)

				await interaction.response.edit_message(
					content = 'How it view now', 
					embed = embed, 
					view = view,
				)

		channel_select.callback = select_callback
		return channel_select

	options_check = [key for key, message in games.items() if message['deleted'] != 'True']
	if len(options_check) == 0:
		await interaction.response.send_message('There are no messages with an existing giveaway', ephemeral = True)
		return

	view = discord.ui.View()
	view.add_item(select_channel())
	await interaction.response.send_message(view = view, ephemeral = True)


@bot.tree.command(name='send_to_channel')
@app_commands.guild_only()
@in_list_users()
async def send_to_channel(interaction: discord.Interaction, user: discord.Member):
	channels = interaction.guild.voice_channels
	view = discord.ui.View()
	def select_channel():
		channel_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label = voice.name,
					value = str(voice.id)
				) for voice in channels
			],
			placeholder = f'Choose the channel, where you want send {user.name}',
		)
		async def select_callback(interaction: discord.Interaction):
			if user.voice == None:
				await interaction.response.send_message(
					content=f'Sorry, {user.name} must be in the voice channel',
					ephemeral=True
				)
				return

			channel = bot.get_channel(int(channel_select.values[0]))
			await user.move_to(channel)
			await interaction.response.send_message(
				content = f'{user.name} will be sent to **{channel.name}** channel.', 
				ephemeral = True,
			)
		
		channel_select.callback = select_callback
		return channel_select

	def button_all_members():
		button = discord.ui.Button(
			style = discord.ButtonStyle.success,
			label = 'Check members in all channel',
			emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
		)
		async def btn_callback(interaction: discord.Interaction):
			embed = discord.Embed()
			for channel in channels:
				members = [str(m.name) for m in channel.members]
				embed.add_field(
					name = f'{channel.name} : ({len(members)} users)',
					value = ', '.join(members) if len(members) != 0 else '---',
					inline = False,
				)
			await interaction.response.send_message(embed = embed, ephemeral = True)
		button.callback = btn_callback
		return button
	
	view.add_item(select_channel())
	view.add_item(button_all_members())

	await interaction.response.send_message(
		view = view, 
		ephemeral=True,
	)

# @bot.tree.command(name='set_channel')
# @app_commands.describe(channel = 'Set up a channel where new messages from the bot will be sent')
# @app_commands.checks.has_permissions(manage_channels=True)
# @app_commands.guild_only()
# async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	with open(files['channels'], 'w', encoding='utf-8') as file:
# 		channels[str(interaction.guild_id)] = {
# 			'channel': str(channel.id),
# 			'status': str(channels[str(interaction.guild_id)]['status']),
# 			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
# 			'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
# 			'games': channels[str(interaction.guild_id)]['games'],
# 		}

# 		json.dump(channels, file, ensure_ascii=False, indent=4)

# 	await interaction.response.send_message(f'Thanks {interaction.user.mention}. New channel is setup!', ephemeral=True)

# @bot.tree.command(name='set_everyone')
# @app_commands.describe(boolean = 'True - message will send with @everyone | False : without @everyone')
# @app_commands.checks.has_permissions(manage_channels=True)
# @app_commands.guild_only()
# async def set_everyone(interaction: discord.Interaction, boolean: bool):
# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	with open(files['channels'], 'w', encoding='utf-8') as file:
# 		channels[str(interaction.guild_id)] = {
# 			'channel': str(channels[str(interaction.guild_id)]['channel']),
# 			'status': str(channels[str(interaction.guild_id)]['status']),
# 			'everyone': str(boolean),
# 			'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
# 			'games': channels[str(interaction.guild_id)]['games'],
# 		}

# 		json.dump(channels, file, ensure_ascii=False, indent=4)

# 	if str(boolean) == 'True':
# 		await interaction.response.send_message(f'Thanks {interaction.user.mention}. Everyone is ON now!', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'Thanks {interaction.user.mention}. Everyone is OFF now!', ephemeral=True)

# @bot.tree.command(name='need_delete')
# @app_commands.describe(boolean = 'True - messages will be deleted when it expires | False : messages will be changed when it expires')
# @app_commands.checks.has_permissions(manage_channels=True)
# @app_commands.guild_only()
# async def need_delete(interaction: discord.Interaction, boolean: bool):
# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	with open(files['channels'], 'w', encoding='utf-8') as file:
# 		channels[str(interaction.guild_id)] = {
# 			'channel': str(channels[str(interaction.guild_id)]['channel']),
# 			'status': str(channels[str(interaction.guild_id)]['status']),
# 			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
# 			'need_delete': str(boolean),
# 			'games': channels[str(interaction.guild_id)]['games'],
# 		}

# 		json.dump(channels, file, ensure_ascii=False, indent=4)

# 	if str(boolean) == 'True':
# 		await interaction.response.send_message(f'Thanks {interaction.user.mention}. The messages will be deleted when it expires!', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'Thanks {interaction.user.mention}. The messages will be changed when it expires!', ephemeral=True)

# @bot.tree.command(name='start_bot')
# @app_commands.checks.has_permissions(manage_channels=True)
# @app_commands.guild_only()
# async def start_bot(interaction: discord.Interaction):
# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	if channels[str(interaction.guild_id)]['channel'] == 'None':
# 		await interaction.response.send_message(f'Error {interaction.user.mention}. Need setup channel!', ephemeral=True)
# 		return

# 	if channels[str(interaction.guild_id)]['status'] == 'True':
# 		await interaction.response.send_message(f'Error {interaction.user.mention}. Bot didn\'t stop!', ephemeral=True)
# 		return

# 	with open(files['channels'], 'w', encoding='utf-8') as file:
# 		channels[str(interaction.guild_id)] = {
# 			'channel': str(channels[str(interaction.guild_id)]['channel']),
# 			'status': str(True),
# 			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
# 			'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
# 			'games': channels[str(interaction.guild_id)]['games'],
# 		}

# 		json.dump(channels, file, ensure_ascii=False, indent=4)

# 	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was started!', ephemeral=True)

# @bot.tree.command(name='stop_bot')
# @app_commands.checks.has_permissions(manage_channels=True)
# @app_commands.guild_only()
# async def stop_bot(interaction: discord.Interaction):
# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	if channels[str(interaction.guild_id)]['status'] == 'False':
# 		await interaction.response.send_message(f'Error {interaction.user.mention}. Bot didn\'t start!', ephemeral=True)
# 		return

# 	with open(files['channels'], 'w', encoding='utf-8') as file:
# 		channels[str(interaction.guild_id)] = {
# 			'channel': str(channels[str(interaction.guild_id)]['channel']),
# 			'status': str(False),
# 			'everyone': str(channels[str(interaction.guild_id)]['everyone']),
# 			'need_delete': str(channels[str(interaction.guild_id)]['need_delete']),
# 			'games': channels[str(interaction.guild_id)]['games'],
# 		}

# 		json.dump(channels, file, ensure_ascii=False, indent=4)

# 	await interaction.response.send_message(f'All ready {interaction.user.mention}! Bot was stoped!', ephemeral=True)

@bot.tree.command(name='give_permissions')
@app_commands.guild_only()
@app_commands.describe(boolean = 'True - give permissions | False : take permissions')
@is_owner()
async def give_permissions(interaction: discord.Interaction, user: discord.Member, boolean: bool):
	with open(files['users'], 'r', encoding='utf-8') as file:
		data = json.load(file)

	with open(files['users'], 'w', encoding='utf-8') as file:
		check = data[str(interaction.guild_id)]
		check[str(user.id)] = {
			'name': str(check[str(user.id)]['name']),
			'has_permissions': str(boolean),
		}
		data[str(interaction.guild_id)] = check

		json.dump(data, file, ensure_ascii=False, indent=4)

	await interaction.response.send_message(content = f'All ready! {interaction.user.mention}! {user.name} now has a new status : {boolean}.', ephemeral = True)

# @set_channel.error
# async def set_channel_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

# @start_bot.error
# async def start_bot_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

# @stop_bot.error
# async def stop_bot_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

# @set_everyone.error
# async def set_everyone_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

# @need_delete.error
# async def need_delete_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@dev_test.error
async def dev_test_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@give_permissions.error
async def give_permissions_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@send_to_channel.error
async def send_to_channel_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

# @reset_settings.error
# async def reset_settings_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@settings.error
async def settings_error(interaction: discord.Interaction, error):
	print(error)
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@fix_message.error
async def fix_message_error(interaction: discord.Interaction, error):
	#print(error)
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)


load_dotenv(find_dotenv())

bot.run(os.environ['TOKEN'])