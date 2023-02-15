import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

from dotenv import load_dotenv, find_dotenv
from datetime import datetime as dt
from pytz import timezone

import os
import json
import asyncio
from deepdiff import DeepDiff

import backup
import epic_informer
import steam_informer

from language import language, LANG
from log_main import logger

load_dotenv(find_dotenv())

files = {
	#'users': 'users.json', 
	'channels': 'channels.json',
	'epic_games': 'epic_games.json',
	'steam' : 'steam.json'
}

thumbnails = {
	'epic_games' : 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images',
	'steam' : 'https://soft-list.ru/wp-content/uploads/2021/07/steam.png',
}

ownerID = os.environ['ownerID']

users = {
	ownerID,
}

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command = None)

@bot.event
async def setup_hook():
	bot_loop_backup.start()
	bot_loop_send_message.start()
	bot_loop_delete_message.start()
	bot_loop_edit_message.start()

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

	logger.debug(f'Discord Bot {bot.user} is ready!')
	
	for guild in bot.guilds:
		# data_members = {}

		# with open(files['users'], 'r', encoding='utf-8') as file:
		# 	data = json.load(file)

		# with open(files['users'], 'w', encoding='utf-8') as file:
		# 	for member in guild.members:
		# 		if not member.bot:
		# 			if not str(guild.id) in data:
		# 				data_members[str(member.id)] = {
		# 					'name': str(member.name),
		# 					'has_permissions': str(True) if ((str(member.id) in users) or (str(member.id) == ownerID)) else str(False),  
		# 				}
		# 			elif not str(member.id) in data[str(guild.id)]:
		# 				data_members[str(member.id)] = {
		# 					'name': str(member.name),
		# 					'has_permissions': str(True) if ((str(member.id) in users) or (str(member.id) == ownerID)) else str(False),  
		# 				}
		# 			else:
		# 				data_members = data[str(guild.id)]

		# 	data[str(guild.id)] = data_members

		# 	json.dump(data, file, ensure_ascii=False, indent=4)
		
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			if not str(guild.id) in channels:
				channels[str(guild.id)] = {
					'admin_settings' : {
						'roles' : [],
						'users' : []
					}
				}	
				for parser in thumbnails.keys():
					channels[str(guild.id)].update({parser : {}})
					channels[str(guild.id)][parser].update({
						'channel': str(0),
						'anounce_publish' : str(False),
						'status': str(False),
						'role': str(0),
						'message_after': str(None),
						'games': {},
					})

				logger.debug(f'Bot joined to new guild in offline : {guild.name}')

			json.dump(channels, file, ensure_ascii=False, indent=4)	

	logger.debug('Database loaded!')

	try:
		synced = await bot.tree.sync()
		logger.debug(f'All is right. Synced {len(synced)} commands')
	except Exception as e:
		print(e)

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} {language[LANG]["precense_servers"][str(len(bot.guilds) % 10)]} ({len(bot.users)} {language[LANG]["precense_users"]})',
	))

@bot.event
async def on_guild_join(guild):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		if not str(guild.id) in channels:
			channels[str(guild.id)] = {
				'admin_settings' : {
					'roles' : [],
					'users' : []
				}
			}
			for parser in thumbnails.keys():
				channels[str(guild.id)].update({parser : {}})
				channels[str(guild.id)][parser].update({
					'channel': str(0),
					'anounce_publish' : str(False),
					'status': str(False),
					'role': str(0),
					'message_after': str(None),
					'games': {},
				})

		json.dump(channels, file, ensure_ascii=False, indent=4)

	data_members = {}

	# with open(files['users'], 'r', encoding='utf-8') as file:
	# 	data = json.load(file)

	# with open(files['users'], 'w', encoding='utf-8') as file:
	# 	for member in guild.members:
	# 		if not member.bot:
	# 			if (not str(guild.id) in data) or (not str(member.id) in data[str(guild.id)]):
	# 				data_members[str(member.id)] = {
	# 					'name': str(member.name),
	# 					'has_permissions': str(True) if ((str(member.id) in users) or (str(member.id) == ownerID)) else str(False),  
	# 				}
	# 			else:
	# 				data_members = data[str(guild.id)]

	# 	data[str(guild.id)] = data_members

	# 	json.dump(data, file, ensure_ascii=False, indent=4)

	logger.debug(f'Bot joined to new guild : {guild.name}')

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} {language[LANG]["precense_servers"][str(len(bot.guilds) % 10)]} ({len(bot.users)} {language[LANG]["precense_users"]})',
	))

@bot.event
async def on_guild_remove(guild):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		for parser in thumbnails.keys():
			channels[str(guild.id)][parser].update({
				'status' : str(False),
			})

		json.dump(channels, file, ensure_ascii=False, indent=4)
	
	logger.debug(f'Bot leave/kicked from guild : {guild.name}')

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} {language[LANG]["precense_servers"][str(len(bot.guilds) % 10)]} ({len(bot.users)} {language[LANG]["precense_users"]})',
	))

@bot.event
async def on_member_join(member):
	# with open(files['users'], 'r', encoding='utf-8') as file:
	# 	data = json.load(file)

	# with open(files['users'], 'w', encoding='utf-8') as file:
	# 	data_members = data[str(member.guild.id)]
	# 	if not str(member.id) in data_members:
	# 		data_members[str(member.id)] = {
	# 			'name': str(member.name),
	# 			'has_permissions': str(True) if ((str(member.id) in users) or (str(member.id) == ownerID)) else str(False),  
	# 		}
	# 		data[str(member.guild.id)] = data_members

	# 	json.dump(data, file, ensure_ascii=False, indent=4)

	logger.debug(f'New member : {member.name} in guild : {member.guild.name}')

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} {language[LANG]["precense_servers"][str(len(bot.guilds) % 10)]} ({len(bot.users)} {language[LANG]["precense_users"]})',
	))

@bot.event
async def on_member_remove(member):
	logger.debug(f'Member leave : {member.name} in guild : {member.guild.name}')

	await bot.change_presence(activity = discord.Activity(
		type = discord.ActivityType.watching,
		name = f'{len(bot.guilds)} {language[LANG]["precense_servers"][str(len(bot.guilds) % 10)]} ({len(bot.users)} {language[LANG]["precense_users"]})',
	))

# @bot.event
# async def on_user_update(before, after):
# 	with open(files['users'], 'r', encoding='utf-8') as file:
# 		data = json.load(file)

# 	with open(files['users'], 'w', encoding='utf-8') as file:
# 		for key, guild in data.items():
# 			if str(before.id) in guild:
# 				guild[str(before.id)] = {
# 					'name': str(after.name),
# 					'has_permissions': guild[str(before.id)]['has_permissions'],  
# 				}
	
# 		json.dump(data, file, ensure_ascii=False, indent=4)

@tasks.loop(hours=1.0, reconnect=True)
async def bot_loop_backup():
	await backup.start_backup(files.values())
	logger.debug(f'Backup is created successful')

@tasks.loop(minutes=15.0, reconnect=True)
async def bot_loop_edit_message():
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for guild in bot.guilds:
		for parser in thumbnails.keys():
			with open(files[parser], 'r', encoding = 'utf-8') as file:
				file_games = json.load(file)

			file_guild = channels[str(guild.id)][parser]

			if len(file_guild['games']) != 0:
				for key, game in file_guild['games'].items():
					if game['expired_check'] != 'True' or game['was_changed_by_user'] != 'True':
						if parser == 'epic_games':
							for region, data in file_games.items():
								if key in data:
									new_dict = {
										'title' : data[key]['title'],
										'description' : data[key]['description'],
										'url' : data[key]['url'],
										'price' : data[key]['price'],
										'date_end' : data[key]['date_end'],
										'region' : region,
									}
									diff = DeepDiff(game['game_info'], new_dict).affected_root_keys
									if len(diff) != 0:
										channel = bot.get_channel(int(game['channel_id']))
										try:
											message = await channel.fetch_message(game['message_id'])
										except Exception as e:
											pass
										else:
											embed = message.embeds[0]
											utc = timezone('UTC')
											date_end = dt.strptime(new_dict['date_end'], "%Y-%m-%d %H:%M:%S")
											date_end = utc.localize(date_end)

											embed.title = new_dict['title']
											embed.timestamp = date_end
											embed.clear_fields()
											embed.add_field(name = f'{language[LANG]["game_price"]} ({new_dict["price"]})', value = new_dict['description'], inline = False)

											label = f'{language[LANG]["not_ru_akk"]}' if new_dict['region'] == 'not_ru' else ''

											if channel.is_news() and game['was_published'] == 'True':
												embed.title = f'{new_dict["title"]} {label}'
												embed.url = new_dict['url']
												button = None
											else: 
												button = discord.ui.View()
												button.add_item(discord.ui.Button(
													label = f'{language[LANG]["game_link"]} {label}',
													style = discord.ButtonStyle.success,
													url = new_dict['url'],
													emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
													disabled = False,
												))
											
											await message.edit( 
												embed = embed,  
												view = button
											)

											game['game_info'].update(new_dict)
											logger.debug(f'{new_dict["title"]} was edited')
						elif parser == 'steam':
							for locate, data in file_games.items():
								if key in data:
									new_dict = {
										'title' : data[key]['card_name'],
										'description' : data[key]['card_desc'],
										'url' : data[key]['card_link'],
										'date_start' : data[key]['start_time'],
									}
									diff = DeepDiff(game['game_info'], new_dict).affected_root_keys
									if len(diff) != 0:
										print(new_dict)
										channel = bot.get_channel(int(game['channel_id']))
										try:
											message = await channel.fetch_message(game['message_id'])
										except Exception as e:
											pass
										else:
											utc = timezone('UTC')
											date_start = dt.strptime(new_dict['date_start'], "%Y-%m-%d %H:%M:%S")
											date_start = utc.localize(date_start)

											embed = message.embeds[0]
											embed.title = new_dict['title']
											embed.timestamp = date_start
											embed.clear_fields()
											embed.add_field(name = '', value = new_dict['description'], inline = False)

											if channel.is_news() and game['anounce_publish'] == 'True':
												embed.url = new_dict['url']
												button = None
											else:
												button = discord.ui.View()
												button.add_item(discord.ui.Button(
													label = f'{language[LANG]["game_link"]}',
													style = discord.ButtonStyle.success,
													url = new_dict['url'],
													emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
													disabled = False,
												))
											
											await message.edit( 
												embed = embed, 
												view = button,
											)

											game['game_info'].update(new_dict)
											logger.debug(f'{new_dict["title"]} was edited')

	with open(files['channels'], 'w', encoding='utf-8') as file:
		json.dump(channels, file, ensure_ascii=False, indent=4)

	#logger.debug(f'Message was editied')
								
@tasks.loop(minutes=10.0, reconnect=True)
async def bot_loop_delete_message():
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for guild in bot.guilds:
		for parser in thumbnails.keys():
			with open(files[parser], 'r', encoding='utf-8') as file:
				file_games = json.load(file)

			file_guild = channels[str(guild.id)][parser]

			if len(file_guild['games']) != 0:
				for key, game in file_guild['games'].items():
					if game['expired_check'] != 'True':
						if parser == 'epic_games':
							timenow = dt.utcnow()
							date_end = dt.strptime(game['game_info']['date_end'], "%Y-%m-%d %H:%M:%S")
							expired = True if date_end < timenow else False
						elif parser == 'steam':
							expired = False
							if key in file_games['steam_links']:
								expired = True if file_games['steam_links'][key]['card_expired'] == 'True' else False
						
						if expired:
							channel = bot.get_channel(int(game['channel_id']))
							try:
								message = await channel.fetch_message(game['message_id'])
							except Exception as e:
								pass
							else:
								if file_guild['message_after'] == 'Delete':
									await message.delete()
								elif file_guild['message_after'] == 'Edit':
									channel_game = game['game_info']

									embed = message.embeds[0]
									embed.colour = discord.Color.red()
									embed.set_footer(text = f'{language[LANG]["discount_ended"]}')
									
									if parser == 'steam':
										embed.timestamp = dt.now(timezone('UTC')) 

									label = ''
									if parser == 'epic_games':
										label = f'{language[LANG]["not_ru_akk"]}' if channel_game['region'] == 'not_ru' else ''
									
									if channel.is_news() and game['was_published'] == 'True':
										button = None
										embed.url = None
									else:
										button = discord.ui.View()
										button.add_item(discord.ui.Button(
											label = f'{language[LANG]["game_link"]} {label}',
											style = discord.ButtonStyle.success,
											url = channel_game['url'],
											emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
											disabled = True,
										))

									await message.edit(
										embed = embed,
										view = button,
									)
							finally:
								logger.info(f'Delete_MSG {parser} || Game : {game["game_info"]["title"]} || Guild : {guild.name}')
								
								file_guild['games'][str(key)].update({
									'expired_check': str(True)
								})

	with open(files['channels'], 'w', encoding='utf-8') as file:
		json.dump(channels, file, ensure_ascii=False, indent=4)
						
@tasks.loop(minutes=5.0, reconnect=True)
async def bot_loop_send_message():
	await epic_informer.start_parse()
	await steam_informer.start_parse()

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	for guild in bot.guilds:
		for parser in thumbnails.keys():

			with open(files[parser], 'r', encoding='utf-8') as file:
				game_file = json.load(file)

			file_guild = channels[str(guild.id)][parser]
			if file_guild['channel'] != 'None' and file_guild['status'] != 'False':
				channel = bot.get_channel(int(file_guild['channel']))
				
				if channel == None:
					continue
				
				for key, unique in game_file.items():
					for k, game in unique.items():
						if k not in file_guild['games']:
							if parser == 'epic_games':
								if game['expired'] == 'False' and game['started'] == 'True':
									utc = timezone('UTC')
									date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
									date_end = utc.localize(date_end)

									embed = discord.Embed()
									embed.title = game['title']
									embed.colour = discord.Color.green()
									embed.timestamp = date_end
									embed.add_field(name = f'{language[LANG]["game_price"]} ({game["price"]})', value = game['description'], inline = False)
									embed.set_image(url=game['image'])
									embed.set_thumbnail(url=thumbnails[parser])
									embed.set_footer(text = f'{language[LANG]["discount_will_ended"]}')
									
									label = f'{language[LANG]["not_ru_akk"]}' if key == 'not_ru' else ''

									if channel.is_news() and file_guild['anounce_publish'] == 'True':
										embed.url = game['url']
										embed.title = f'{game["title"]} {label}'
										button = None
										published = True
									else: 
										published = False

										button = discord.ui.View()
										button.add_item(discord.ui.Button(
											label = f'{language[LANG]["game_link"]} {label}',
											style = discord.ButtonStyle.success,
											url = game['url'],
											emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
											disabled = False,
										))
									
									content = ''

									if guild.get_role(int(file_guild['role'])) != None:
										content = guild.get_role(int(file_guild['role'])).mention

									message = await channel.send(
										content = content, 
										embed = embed, 
										allowed_mentions = discord.AllowedMentions.all(), 
										view = button,
									)

									if published:
										await message.publish()
										
									game_json = {
					                    'title': str(game['title']),
					                    'description': str(game['description']),
					                    'url': str(game['url']),
					                    'price': str(game['price']),
					                    'date_end' : str(game['date_end']),
					                    'region' : str(key)
									}

									games_channel = {
										str(k) : {
											'message_id': str(message.id),
											'channel_id': str(file_guild['channel']),
											'expired_check': str(False),
											'was_changed_by_user' : str(False),
											'was_published' : str(published),
											'game_info': game_json
										}
									}

									file_guild['games'].update(games_channel)

									logger.info(f'Send_MSG {parser} || Game : {game["title"]} was posted in {guild.name}')
							elif parser == 'steam':
								if game['card_expired'] == 'False':
									utc = timezone('UTC')
									date_start = dt.strptime(game['start_time'], "%Y-%m-%d %H:%M:%S")
									date_start = utc.localize(date_start)

									embed = discord.Embed()
									embed.title = game['card_name']
									embed.colour = discord.Color.green()
									embed.timestamp = date_start
									embed.add_field(name = '', value = game['card_desc'], inline = False)
									embed.set_image(url=game['card_image'])
									embed.set_thumbnail(url=thumbnails[parser])
									embed.set_footer(text = f'{language[LANG]["discount_started"]}')
									
									if channel.is_news() and file_guild['anounce_publish'] == 'True':
										embed.url = game['card_link']
										button = None
										published = True
									else: 
										published = False

										button = discord.ui.View()
										button.add_item(discord.ui.Button(
											label = f'{language[LANG]["game_link"]}',
											style = discord.ButtonStyle.success,
											url = game['card_link'],
											emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
											disabled = False,
										))
									
									content = ''

									if guild.get_role(int(file_guild['role'])) != None:
										content = guild.get_role(int(file_guild['role'])).mention
									
									message = await channel.send(
										content = content, 
										embed = embed, 
										allowed_mentions = discord.AllowedMentions.all(), 
										view = button,
									)

									if published:
										await message.publish()

									game_json = {
					                    'title': str(game['card_name']),
					                    'description': str(game['card_desc']),
					                    'url': str(game['card_link']),
					                    'date_start' : str(game['start_time']),
									}

									games_channel = {
										str(k) : {
											'message_id': str(message.id),
											'channel_id': str(file_guild['channel']),
											'expired_check': str(False),
											'was_changed_by_user' : str(False),
											'was_published' : str(published),
											'game_info': game_json
										}
									}

									file_guild['games'].update(games_channel)

									logger.info(f'Send_MSG {parser} || Game : {game["card_name"]} was posted in {guild.name}')
							
	with open(files['channels'], 'w', encoding='utf-8') as file:
		json.dump(channels, file, ensure_ascii=False, indent=4)

def is_owner():
	def predicate(interaction: discord.Interaction) -> bool:
		return str(interaction.user.id) == ownerID
	return app_commands.check(predicate)

# def in_list_users():
# 	def predicate(interaction: discord.Interaction) -> bool:
# 		with open(files['users'], 'r', encoding='utf-8') as file:
# 			data = json.load(file)
# 		return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False
# 	return app_commands.check(predicate)

def has_channel_permissions():
	def predicate(interaction: discord.Interaction) -> bool:
		if str(interaction.user.id) == ownerID:
			return True

		if interaction.user.guild_permissions.administrator:
			return True

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		if str(interaction.user.id) in channels[str(interaction.guild_id)]['admin_settings']['users']:
			return True

		for role in channels[str(interaction.guild_id)]['admin_settings']['roles']:
			if interaction.user.get_role(int(role)) != None:
				return True

		# with open(files['users'], 'r', encoding='utf-8') as file:
		# 	data = json.load(file)
		# return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False
		return False

	return app_commands.check(predicate)

def is_owner_not_decorator(interaction: discord.Interaction) -> bool:
	return str(interaction.user.id) == ownerID

# def in_list_users_not_decorator(interaction: discord.Interaction) -> bool:
	# with open(files['users'], 'r', encoding='utf-8') as file:
	# 	data = json.load(file)
	# return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False

def has_channel_permissions_not_decorator(interaction: discord.Interaction) -> bool:
	if str(interaction.user.id) == ownerID:
		return True

	if interaction.user.guild_permissions.administrator:
		return True

	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	if str(interaction.user.id) in channels[str(interaction.guild_id)]['admin_settings']['users']:
		return True

	for role in channels[str(interaction.guild_id)]['admin_settings']['roles']:
		if interaction.user.get_role(int(role)) != None:
			return True

	# with open(files['users'], 'r', encoding='utf-8') as file:
	# 	data = json.load(file)
	# return True if data[str(interaction.guild_id)][str(interaction.user.id)]['has_permissions'] == 'True' else False
	return False

# @bot.tree.command(name='dev_uni_test')
# @app_commands.guild_only()
# @is_owner()
# async def dev_uni_test(interaction: discord.Interaction):
# 	with open(files['epic_games'], 'r', encoding='utf-8') as file:
# 		games = json.load(file)

# 	with open(files['channels'], 'r', encoding='utf-8') as file:
# 		channels = json.load(file)

# 	for key, region in games.items():
# 		for k, game in region.items():
# 			if game['expired'] == 'False' and game['started'] == 'True':
# 				embed = discord.Embed()
# 				embed.title = game['title']
# 				embed.colour = discord.Color.green()
# 				utc = timezone('UTC')
# 				time = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
# 				time = utc.localize(time)
# 				embed.timestamp = time
# 				price = game['price']
# 				embed.add_field(name = f'{language[LANG]["game_price"]} ({price})', value = game['description'], inline = False)
# 				embed.set_image(url=game['image'])
# 				embed.set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.icon-icons.com%2Ficons2%2F2429%2FPNG%2F512%2Fepic_games_logo_icon_147294.png&f=1&nofb=1&ipt=fcb317278eedd075465f00e4f3a6c99f2a970dc635bd138a317b027b936d260e&ipo=images')
# 				embed.set_footer(text = f'{language[LANG]["discount_will_ended"]}')
				
# 				button = discord.ui.View()
# 				button.add_item(discord.ui.Button(
# 					label = f'{language[LANG]["game_link"]}',
# 					style = discord.ButtonStyle.success,
# 					url = game['url'],
# 					emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
# 					disabled = False,
# 				))

# 				await interaction.response.send_message(
# 					content='', 
# 					embed = embed, 
# 					allowed_mentions = discord.AllowedMentions.all(), 
# 					view = button,
# 					delete_after = 10.0,
# 				)

async def embedSettignsMenu(interaction: discord.Interaction, parser):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)
		
	guild = channels[str(interaction.guild.id)][parser]
	
	channel_name = language[LANG]["no_channel"]
	if bot.get_channel(int(guild['channel'])) != None:
		channel_name = bot.get_channel(int(guild['channel'])).name
	
	role_name = language[LANG]["no_role"]
	
	if interaction.guild.get_role(int(guild['role'])) != None:
		role_name = interaction.guild.get_role(int(guild['role'])).name
	
	message_after_name = language[LANG]["no_message_changes"]
	if guild['message_after'] == 'Delete':
		message_after_name = language[LANG]["message_changes_delete"]
	elif guild['message_after'] == 'Edit':
		message_after_name = language[LANG]["message_changes_edit"]

	start_stop_name = language[LANG]["bot_started"] if guild['status'] == 'True' else language[LANG]["bot_stoped"]

	embed = discord.Embed()
	embed.title = f'{language[LANG][f"settings_{parser}"]}'
	embed.add_field(name = f'{language[LANG]["current_channel"]}', value = channel_name, inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True) # Empty Field
	embed.add_field(name = f'{language[LANG]["current_role"]}', value = role_name, inline = True)
	embed.add_field(name = f'{language[LANG]["current_mode"]}', value = message_after_name, inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True) # Empty Field
	embed.add_field(name = f'{language[LANG]["bot_status"]}', value = start_stop_name, inline = True)
	embed.set_author(name = interaction.user.name, icon_url = interaction.user.display_avatar.url)
	embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
	embed.colour = discord.Color.green()
	#embed.timestamp = dt.now(timezone('UTC'))

	return embed

class _SubmitModal(discord.ui.Modal, title = language[LANG]["reset_submit_modal"]):
	check = discord.ui.TextInput(
		label = language[LANG]["reset_submit"],
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
				content = language[LANG]["reset_canceled"],
			 	view = self.view
			)

			logger.warning(f'Reset was discarded in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id})')
			return

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild.id)][self.parser].update({
				'channel': str(0),
				'anounce_publish' : str(False),
				'status': str(False),
				'role': str(0),
				'message_after': str(None)
			})

			json.dump(channels, file, ensure_ascii=False, indent=4)

		for btn in self.view.children:
			if btn.custom_id != '_return':
				btn.disabled = True

		await interaction.response.edit_message(
			content = language[LANG]["reset_successful"],
		 	view = self.view
		)

		logger.info(f'Reset was successfuled in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id})')

class _ResetMenu(discord.ui.View):
	@discord.ui.button(
		style = discord.ButtonStyle.success,
		label = language[LANG]["reset_confirm"],
	)
	async def confirm_callback(self, interaction: discord.Interaction, button):
		submit = _SubmitModal()
		submit.view = self
		submit.parser = self.parser
		await interaction.response.send_modal(submit)

class _ReturnButton(discord.ui.Button):
	def __init__(self, view, parser):
		self.menu = view
		self.parser = parser
		super().__init__(
			label = language[LANG]["return_to_settings"],
			style = discord.ButtonStyle.danger,
			custom_id = '_return',
		)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.edit_message(content = '', embed = await embedSettignsMenu(interaction, self.parser), view = self.menu)

class _StatusAnnounceButton(discord.ui.Button):
	def __init__(self, view, interaction, parser):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		self.menu = view
		self.interaction = interaction
		self.parser = parser
		super().__init__(
			label = language[LANG]["anounce_publish_start"] if channels[str(self.interaction.guild_id)][self.parser]['anounce_publish'] == 'False' else language[LANG]["anounce_publish_stop"],
			style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)][self.parser]['anounce_publish'] == 'False' else discord.ButtonStyle.danger,
			row = 1,
		)

	async def callback(self, interaction: discord.Interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild_id)][self.parser].update({
				'anounce_publish': str(True) if channels[str(interaction.guild_id)][self.parser]['anounce_publish'] == 'False' else str(False),
			})

			json.dump(channels, file, ensure_ascii=False, indent=4)

		self.menu.remove_item(self)
		self.label = language[LANG]["anounce_publish_start"] if channels[str(interaction.guild_id)][self.parser]['anounce_publish'] == 'False' else language[LANG]["anounce_publish_stop"]
		self.style = style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)][self.parser]['anounce_publish'] == 'False' else discord.ButtonStyle.danger
		self.menu.add_item(self)

		logger.info(f'Bot publish message setting was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({channels[str(interaction.guild_id)][self.parser]["anounce_publish"] == "False"} -> {channels[str(interaction.guild_id)][self.parser]["anounce_publish"] == "True"})')

		await interaction.response.edit_message(view = self.menu)

class _ChannelSettingsMenu(discord.ui.View):
	async def update_embed(self, interaction, last_channel):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		channel = channels[str(interaction.guild.id)][self.parser]['channel']
		channel_name = bot.get_channel(int(channel)).name if bot.get_channel(int(channel)) != None else language[LANG]['no_channel']

		embed = discord.Embed()
		embed.title = language[LANG]["settings_channel"]
		embed.add_field(name = f'{language[LANG]["current_channel_for"]} {interaction.guild.name} {language[LANG]["channel"]}', value = channel_name, inline = False)
		embed.add_field(name = f'{language[LANG]["last_channel"]}', value = last_channel, inline = False)
		embed.colour = discord.Color.green()
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		#embed.timestamp = dt.now(timezone('UTC'))
		
		return embed

	async def update_message(self, interaction, last_channel_par):
		self.clear_items()

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		channel = channels[str(interaction.guild.id)][self.parser]['channel']

		channel_select = discord.ui.ChannelSelect(
			channel_types = [discord.ChannelType.text, discord.ChannelType.news],
			min_values=0,
			max_values=1,
			placeholder = language[LANG]["choose_channel"],
		)

		async def select_callback(interaction: discord.Interaction):
			channel_new = [i for i in channel_select.values]
			if len(channel_new) == 0:
				channel_new_id = '0'
				channel_new_name = language[LANG]['no_channel']
			else:
				channel_new_id = channel_new[0].id
				channel_new_name = channel_new[0].name

			last_channel = bot.get_channel(int(channel))
			if last_channel == None:
				last_channel_name = language[LANG]['no_channel']
			else:
				last_channel_name = last_channel.name

			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)][self.parser].update({
					'channel': str(channel_new_id),
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)

			logger.info(f'Channel was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({last_channel_name} -> {channel_new_name})')
			#embed = await self.update_embed(interaction, last_channel_name)
			#await interaction.response.edit_message(embed = embed, view = self)
			await self.update_message(interaction, last_channel_name)

		channel_select.callback = select_callback

		self.add_item(channel_select)
		self.add_item(_ReturnButton(self.menu, self.parser))
		if interaction.guild.get_channel(int(channel)) != None and interaction.guild.get_channel(int(channel)).is_news():
			self.add_item(_StatusAnnounceButton(self, interaction, self.parser))
		elif channels[str(interaction.guild.id)][self.parser]['anounce_publish'] == 'True':
			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)][self.parser].update({
					'anounce_publish': str(False)
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)
			logger.info(f'Bot publish message setting was |automaticaly| changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({channels[str(interaction.guild_id)][self.parser]["anounce_publish"] == "False"} -> False')
		embed = await self.update_embed(interaction, last_channel_par)
		await interaction.response.edit_message(embed = embed, view = self)

class _RoleSettingsMenu(discord.ui.View):
	async def update_embed(self, interaction, last_role):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		role = channels[str(interaction.guild.id)][self.parser]['role']
		role_name = interaction.guild.get_role(int(role)).name if interaction.guild.get_role(int(role)) != None else language[LANG]['no_role']

		embed = discord.Embed()
		embed.title = language[LANG]["settings_role"]
		embed.add_field(name = f'{language[LANG]["current_role_for"]} {interaction.guild.name} {language[LANG]["channel"]}', value = role_name, inline = False)
		embed.add_field(name = f'{language[LANG]["last_role"]}', value = last_role, inline = False)
		embed.colour = discord.Color.green()
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		#embed.timestamp = dt.now(timezone('UTC'))
		
		return embed

	async def update_message(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		role = channels[str(interaction.guild.id)][self.parser]['role']

		role_select = discord.ui.RoleSelect(
			min_values=0,
			max_values=1,
			placeholder = language[LANG]["choose_role"],
		)

		async def select_callback(interaction: discord.Interaction):
			role_new = [i for i in role_select.values]
			if len(role_new) == 0:
				role_new_id = '0'
				role_new_name = language[LANG]['no_role']
			else:
				role_new_id = role_new[0].id
				role_new_name = role_new[0].name

			last_role = interaction.guild.get_role(int(role))
			if last_role == None:
				last_role_name = language[LANG]['no_role']
			else:
				last_role_name = last_role.name
			
			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)][self.parser].update({
					'role': str(role_new_id),
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)

			logger.info(f'Role was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({last_role_name} -> {role_new_name})')
			embed = await self.update_embed(interaction, last_role_name)
			await interaction.response.edit_message(embed = embed, view = self)
	
		role_select.callback = select_callback

		self.add_item(role_select)
		self.add_item(_ReturnButton(self.menu, self.parser))
		embed = await self.update_embed(interaction, '')
		await interaction.response.edit_message(embed = embed, view = self)

class _MessageAfterSettingsMenu(discord.ui.View):
	async def update_message(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		message_after = channels[str(interaction.guild.id)][self.parser]['message_after']

		message_after_list = {
			'Delete' : language[LANG]["delete_message"],
			'Edit' : language[LANG]["edit_message"],
			'None' : language[LANG]["none_message"]
		}

		message_after_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label = str(value),
					value = str(key)
				) for key, value in message_after_list.items()
			],
			placeholder = language[LANG]["choose_message"],
		)

		message_after_name = message_after_list[message_after]
		self.last_mode = message_after_name
		embed = discord.Embed()
		embed.title = language[LANG]["settings_message"]
		embed.add_field(name = f'{language[LANG]["current_message_for"]} {interaction.guild.name} {language[LANG]["channel"]}', value = self.last_mode, inline = False)
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		embed.colour = discord.Color.green()
		#embed.timestamp = dt.now(timezone('UTC'))

		async def select_callback(interaction: discord.Interaction):
			message_after_name_new = message_after_list[str(message_after_select.values[0])]
			embed.clear_fields()
			embed.add_field(name = f'{language[LANG]["current_message_for"]} {interaction.guild.name} {language[LANG]["channel"]}', value = message_after_name_new, inline = False)
			embed.add_field(name = f'{language[LANG]["last_message"]}', value = self.last_mode, inline = False)
			
			logger.info(f'MessageAfter was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({self.last_mode} -> {message_after_name_new})')
			
			self.last_mode = message_after_name_new
			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)][self.parser].update({
					'message_after': str(message_after_select.values[0])
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)

			await interaction.response.edit_message(embed = embed, view = self)
	
		message_after_select.callback = select_callback

		self.add_item(message_after_select)
		self.add_item(_ReturnButton(self.menu, self.parser))
		await interaction.response.edit_message(embed = embed, view = self)


class _AdminSettingsMenu(discord.ui.View):
	async def update_embed(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		roles = channels[str(interaction.guild.id)]['admin_settings']['roles']
		users = channels[str(interaction.guild.id)]['admin_settings']['users']
		
		embed = discord.Embed()
		embed.title = language[LANG]["admin_settings_embed_title"]
		embed.colour = discord.Color.green()
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		#embed.timestamp = dt.now(timezone('UTC'))

		role_names = [f'-{interaction.guild.get_role(int(role)).mention}' for role in roles if interaction.guild.get_role(int(role)) != None]

		embed.add_field(name = f'{language[LANG]["admin_settings_embed_roles"]} : ', value = '\n'.join(role_names), inline = True)

		user_names = [f'-{interaction.guild.get_member(int(user)).mention}' for user in users if interaction.guild.get_member(int(user)) != None]

		embed.add_field(name = f'{language[LANG]["admin_settings_embed_users"]} : ', value = '\n'.join(user_names), inline = True)
				
		return embed

	async def update_message(self, interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		roles = channels[str(interaction.guild.id)]['admin_settings']['roles']
		users = channels[str(interaction.guild.id)]['admin_settings']['users']

		role_select = discord.ui.RoleSelect(
			min_values=0,
			max_values=24,
			placeholder = language[LANG]["admin_settings_choose_role"],
		)

		async def role_callback(interaction: discord.Interaction):
			new_roles = []
			for role in role_select.values:
				new_roles.append(str(role.id))

			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)]['admin_settings'].update({
					'roles' : new_roles
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)
			
			role_names = [f'{interaction.guild.get_role(int(role)).name}' for role in roles if interaction.guild.get_role(int(role)) != None]
			new_role_names = [f'{interaction.guild.get_role(int(role)).name}' for role in new_roles if interaction.guild.get_role(int(role)) != None]
			logger.warning(f'AdminSettings : roles was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ([{", ".join(role_names)}] -> [{", ".join(new_role_names)}])')

			await interaction.response.edit_message(embed = await self.update_embed(interaction), view = self)

		role_select.callback = role_callback

		user_select = discord.ui.UserSelect(
			min_values=0,
			max_values=24,
			placeholder = language[LANG]["admin_settings_choose_user"],
		)

		async def user_callback(interaction: discord.Interaction):
			new_users = []
			for user in user_select.values:
				new_users.append(str(user.id))

			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild_id)]['admin_settings'].update({
					'users' : new_users
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)

			user_names = [f'{interaction.guild.get_member(int(user)).name}' for user in users if interaction.guild.get_member(int(user)) != None]
			new_user_names = [f'{interaction.guild.get_member(int(user)).name}' for user in new_users if interaction.guild.get_member(int(user)) != None]
			logger.warning(f'AdminSettings : users was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ([{", ".join(user_names)}] -> [{", ".join(new_user_names)}])')

			await interaction.response.edit_message(embed = await self.update_embed(interaction), view = self)

		user_select.callback = user_callback

		self.add_item(role_select)
		self.add_item(user_select)

		embed = await self.update_embed(interaction)
		await interaction.response.edit_message(embed = embed, view = self)

	@discord.ui.button(
		label = language[LANG]["return_to_settings"],
		style = discord.ButtonStyle.danger,
		row = 2,
	)
	async def return_to_settings(self, interaction: discord.Interaction, button):
		await interaction.response.edit_message(content = '', embed = None, view = self.menu)

class _StatusSettingsButton(discord.ui.Button):
	def __init__(self, view, interaction, parser):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		self.menu = view
		self.interaction = interaction
		self.parser = parser
		super().__init__(
			label = language[LANG]["bot_start"] if channels[str(self.interaction.guild_id)][self.parser]['status'] == 'False' else language[LANG]["bot_stop"],
			style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)][self.parser]['status'] == 'False' else discord.ButtonStyle.danger,
			row = 1,
		)

	async def callback(self, interaction: discord.Interaction):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild_id)][self.parser].update({
				'status': str(True) if channels[str(interaction.guild_id)][self.parser]['status'] == 'False' else str(False),
			})

			json.dump(channels, file, ensure_ascii=False, indent=4)

		self.menu.remove_item(self)
		self.label = language[LANG]["bot_start"] if channels[str(interaction.guild_id)][self.parser]['status'] == 'False' else language[LANG]["bot_stop"]
		self.style = style = discord.ButtonStyle.success if channels[str(self.interaction.guild_id)][self.parser]['status'] == 'False' else discord.ButtonStyle.danger
		self.menu.add_item(self)

		logger.info(f'Bot status was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({channels[str(interaction.guild_id)][self.parser]["status"] == "False"} -> {channels[str(interaction.guild_id)][self.parser]["status"] == "True"})')

		await interaction.response.edit_message(content = '', embed = await embedSettignsMenu(interaction, self.parser), view = self.menu)

class _SettingsMenu(discord.ui.View):
	async def update_message(self, interaction: discord.Interaction):
		embed = await embedSettignsMenu(interaction, self.parser)
		await interaction.response.edit_message(content = '', embed = embed, view = self)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]["channel_setup"],
		row = 0,
	)
	async def channel_settings(self, interaction: discord.Interaction, button):
		check_channels = [text.id for text in interaction.guild.text_channels]
		if len(check_channels) == 0:
			await interaction.response.send_message(language[LANG]["no_channels_guild"], ephemeral = True)
			return

		channel_menu = _ChannelSettingsMenu()
		channel_menu.menu = self
		channel_menu.parser = self.parser
		await channel_menu.update_message(interaction, '')

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]["message_setup"],
		row = 0,
	)
	async def need_delete_settings(self, interaction: discord.Interaction, button):
		message_menu = _MessageAfterSettingsMenu()
		message_menu.menu = self
		message_menu.parser = self.parser
		await message_menu.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]["role_setup"],
		row = 0,
	)
	async def everyone_settings(self, interaction: discord.Interaction, button):
		check_roles = [role_.id for role_ in interaction.guild.roles]
		if len(check_roles) == 0:
			await interaction.response.send_message(language[LANG]["no_roles_guild"], ephemeral = True)
			return

		role_menu = _RoleSettingsMenu()
		role_menu.menu = self
		role_menu.parser = self.parser
		await role_menu.update_message(interaction)

	@discord.ui.button(
		label = language[LANG]["return_to_main"],
		style = discord.ButtonStyle.danger,
		row = 1,
	)
	async def return_to_choose(self, interaction: discord.Interaction, button):
		await interaction.response.edit_message(content = '', embed = None, view = self.menu)

	@discord.ui.button(
		style = discord.ButtonStyle.danger,
		label = language[LANG]["reset"],
		row = 1,
	)
	async def reset_settings(self, interaction: discord.Interaction, button):
		view = _ResetMenu()
		view.guild = interaction.guild
		view.parser = self.parser

		_return = _ReturnButton(self, self.parser)
		view.add_item(_return)
		
		await interaction.response.edit_message(
			content = language[LANG]["message_reset"],
			embed = None,
			view = view
		)

class _ReturnFixMessageButton(discord.ui.Button):
	def __init__(self, view, embed):
		self.menu = view
		self.embed = embed
		super().__init__(
			label = language[LANG]["return_to_main"],
			style = discord.ButtonStyle.danger,
			custom_id = '_return_fix',
		)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.edit_message(content = '', embed = self.embed, view = self.menu)


class _ChangeMessageModal(discord.ui.Modal):
	def __init__(self, game, embed, message, game_id, parser):
		self.game = game
		self.embed = embed
		self.message = message
		self.game_id = game_id
		self.parser = parser
		super().__init__(title = language[LANG]["fix_message_editor"])

	async def on_submit(self, interaction: discord.Interaction):
		options = self.game
		for _input in self.children:
			if str(self.game[_input.custom_id]) != str(_input.value):
				if _input.custom_id == 'key':
					if _input.value != 'ru':
						if _input.value != 'not_ru':
							await interaction.response.send_message(content = language[LANG]["fix_message_error_key"], ephemeral = True)
							return
				options[str(_input.custom_id)] = str(_input.value)
		
		label = ''
		if self.parser == 'epic_games':
			self.embed.set_field_at(0, name = f'{language[LANG]["game_price"]} ({options["price"]})', value = options['description'], inline = False)
			label = f'{language[LANG]["not_ru_akk"]}' if options['region'] == 'not_ru' else ''
		elif self.parser == 'steam':
			self.embed.set_field_at(0, name = '', value = options['description'], inline = False)
			self.embed.title = options['title']

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		games = channels[str(interaction.guild.id)][self.parser]['games']
		
		if games[str(self.game_id)]['was_published'] != 'True':
			self.embed.title = f'{options["title"]} {label}'
		
		view = discord.ui.View()
		if games[str(self.game_id)]['was_published'] != 'True':
			view.add_item(discord.ui.Button(
				label = f'{language[LANG]["game_link"]} {label}',
				style = discord.ButtonStyle.success,
				url = options['url'],
				emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
				disabled = False,
			))

		button_confirm = discord.ui.Button(
			label = language[LANG]["fix_message_apply"],
			style = discord.ButtonStyle.success,
			disabled = False,
		)
		async def button_confirm_callback(interaction: discord.Interaction):
			games[str(self.game_id)]['game_info'] = options
			games[str(self.game_id)]['was_changed_by_user'] = str(True)

			with open(files['channels'], 'w', encoding='utf-8') as file:
				channels[str(interaction.guild.id)][self.parser].update({
					'games': games,
				})

				json.dump(channels, file, ensure_ascii=False, indent=4)

			if games[str(self.game_id)]['was_published'] != 'True':
				new_view = discord.ui.View()
				new_view.add_item(discord.ui.Button(
					label = f'{language[LANG]["game_link"]} {label}',
					style = discord.ButtonStyle.success,
					url = options['url'],
					emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
					disabled = False,
				))
			else:
				new_view = None

			await self.message.edit(embed = self.embed, view = new_view)
			await interaction.response.edit_message(
				content = language[LANG]["fix_message_edit_successful"],
				view = None,
				embed = None
			)
			logger.info(f'Fix_Message : message was changed in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({games[str(self.game_id)]["game_info"]["title"]})')

		button_confirm.callback = button_confirm_callback

		button_cancel = discord.ui.Button(
			label = language[LANG]["fix_message_discard"],
			style = discord.ButtonStyle.danger,
			disabled = False,
		)

		async def button_cancel_callback(interaction: discord.Interaction):
			await interaction.response.edit_message(
				content = language[LANG]["fix_message_edit_discard"],
				view = None,
				embed = None
			)
		button_cancel.callback = button_cancel_callback

		view.add_item(button_confirm)
		view.add_item(button_cancel)

		await interaction.response.edit_message(
			content = language[LANG]["fix_message_how_view"],
			view = view,
			embed = self.embed,
		)

class _SubmitMessageModal(discord.ui.Modal, title = language[LANG]["fix_message_delete_modal"]):
	check = discord.ui.TextInput(
		label = language[LANG]["fix_message_delete_submit"],
		style = discord.TextStyle.short,
		placeholder = 'SUBMIT',
		required = False,
	)

	async def on_submit(self, interaction: discord.Interaction):
		if self.check.value != 'SUBMIT': 
			await interaction.response.edit_message(
				content = language[LANG]["fix_message_delete_error"],
				embed = None,
				view = None,
			)
			return

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)
		
		games = channels[str(interaction.guild.id)][self.parser]['games']
		games[str(self.game_id)]['expired_check'] = str(True)
		games[str(self.game_id)]['was_changed_by_user'] = str(True)

		with open(files['channels'], 'w', encoding='utf-8') as file:
			channels[str(interaction.guild.id)][self.parser].update({
				'games': games,
			})

			json.dump(channels, file, ensure_ascii=False, indent=4)

		await self.message.delete()

		await interaction.response.edit_message(
			content = language[LANG]["fix_message_delete_successful"],
			embed = None,
			view = None,
		)

		logger.warning(f'Fix_Message : message was deleted in {interaction.guild.name} by {interaction.user.name} ({interaction.user.id}) ({games[str(self.game_id)]["game_info"]["title"]})')

class _FixMessageButtons(discord.ui.Button):
	def __init__(self, menu, parser):
		with open(files['channels'], 'r', encoding='utf-8') as file:
			self.channels = json.load(file)

		self.parser = parser
		self.menu = menu
		super().__init__(
			label = language[LANG][f"button_{self.parser}"],
			style = discord.ButtonStyle.primary,
			custom_id = self.parser,
		)

	async def callback(self, interaction: discord.Interaction):
		games = self.channels[str(interaction.guild.id)][self.parser]['games']
		game_select = discord.ui.Select(
			options = [
				discord.SelectOption(
					label =	message['game_info']['title'],
					value = str(key),
				) for key, message in games.items() if message['expired_check'] != 'True'
			],
			placeholder = language[LANG]["fix_message_choose"],
		)
		async def select_callback(interaction: discord.Interaction):
			channel = bot.get_channel(int(games[str(game_select.values[0])]['channel_id']))
			try:
				message = await channel.fetch_message(int(games[str(game_select.values[0])]['message_id']))
			except Exception as e:
				await interaction.response.send_message(content = language[LANG]["fix_message_message_not_exists"], ephemeral = True)
			else:
				embed = message.embeds[0]
				game = games[str(game_select.values[0])]['game_info']
				game_id = str(game_select.values[0])

				label = ''
				if self.parser == 'epic_games':
					label = language[LANG]["not_ru_akk"] if game['region'] == 'not_ru' else ''
				
				view = discord.ui.View()

				if games[str(game_select.values[0])]['was_published'] != 'True':
					view.add_item(discord.ui.Button(
						label = f'{language[LANG]["game_link"]} {label}',
						style = discord.ButtonStyle.success,
						url = game['url'],
						emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
						disabled = False,
					))

				button_change = discord.ui.Button(
					label = language[LANG]["fix_message_change_message"],
					style = discord.ButtonStyle.primary,
					disabled = False,
				)

				async def button_change_callback(interaction: discord.Interaction):
					modal = _ChangeMessageModal(game, embed, message, game_id, self.parser)
					labels = {
						'epic_games': {
							'title': language[LANG]["fix_message_modal_title"],
		                    'description': language[LANG]["fix_message_modal_description"],
		                    'url': language[LANG]["fix_message_modal_url"],
		                    'price': language[LANG]["fix_message_modal_price"],
		                    'region': language[LANG]["fix_message_modal_key"],
		                },
						'steam': {
							'title': language[LANG]["fix_message_modal_title"],
		                    'description': language[LANG]["fix_message_modal_description"],
		                    'url': language[LANG]["fix_message_modal_url"],
		                },
					}
					for key, value in game.items():
						if key.startswith('date'):
							continue
						check = discord.ui.TextInput(
							label = labels[self.parser][str(key)],
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
					label = language[LANG]["fix_message_button_delete"],
					style = discord.ButtonStyle.danger,
					disabled = False,
				)

				async def button_delete_callback(interaction: discord.Interaction):
					modal = _SubmitMessageModal()
					modal.game_id = game_id
					modal.game = game
					modal.message = message
					modal.parser = self.parser
					await interaction.response.send_modal(modal)

				button_delete.callback = button_delete_callback

				view.add_item(button_change)
				view.add_item(button_delete)

				await interaction.response.edit_message(
					content = language[LANG]["fix_message_how_view_now"], 
					embed = embed, 
					view = view,
				)

		game_select.callback = select_callback
		view = discord.ui.View()
		view.add_item(game_select)
		view.add_item(_ReturnFixMessageButton(self.menu, self.embed))
		await interaction.response.edit_message(embed = None, view = view)
		
class _FixMessageMenu(discord.ui.View):
	async def update_message(self, interaction: discord.Interaction):
		self.clear_items()

		with open(files['channels'], 'r', encoding='utf-8') as file:
			channels = json.load(file)

		items = []
		for parser in thumbnails.keys():
			parser_check = [k for k, message in channels[str(interaction.guild.id)][parser]['games'].items() if message['expired_check'] != 'True']
			if len(parser_check) == 0:
				continue

			items.append(_FixMessageButtons(self, parser))

		options_check = {}
		for parser in thumbnails.keys():
			for k, message in channels[str(interaction.guild.id)][parser]['games'].items():
				if message['expired_check'] != 'True':
					options_check.update({k : {parser : message['game_info']['title']}})

		if len(options_check) == 0:
			await interaction.response.send_message(language[LANG]["fix_message_no_messages"], ephemeral = True)
			return

		embed = discord.Embed()
		embed.title = language[LANG]['fix_message_embed_title']
		embed.colour = discord.Color.green()
		embed.set_thumbnail(url = str(interaction.guild.icon) if interaction.guild.icon != None else 'https://www.ndca.org/co/images/stock/no-image.png')
		#embed.timestamp = dt.now(timezone('UTC'))

		epic_games_list = [f'-{game}' for inside in options_check.values() for k, game in inside.items() if k == 'epic_games' ]
		embed.add_field(name = f'{language[LANG]["fix_message_embed_epic_games_list"]} : ', value = '\n'.join(epic_games_list), inline = True)
		embed.add_field(name = '\u200b', value = '\u200b', inline = True) # Empty Field
		steam_list = [f'-{game}' for inside in options_check.values() for k, game in inside.items() if k == 'steam']
		embed.add_field(name = f'{language[LANG]["fix_message_embed_steam_list"]} : ', value = '\n'.join(steam_list), inline = True)

		for item in items:
			item.embed = embed
			self.add_item(item)

		return_button = discord.ui.Button(
			label = language[LANG]['return_to_settings'],
			style = discord.ButtonStyle.danger,
		)

		async def return_callback(interaction: discord.Interaction):
			await interaction.response.edit_message(embed = None, view = self.menu)

		return_button.callback = return_callback

		self.add_item(return_button)

		await interaction.response.edit_message(embed = embed, view = self)

class _ChooseSettingsMenu(discord.ui.View):
	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]['button_epic_games'],
		row = 0,
	)
	async def epic_games_settings(self, interaction: discord.Interaction, button):
		epic_games_menu = _SettingsMenu()
		epic_games_menu.parser = 'epic_games'
		epic_games_menu.add_item(_StatusSettingsButton(epic_games_menu, interaction, 'epic_games'))
		epic_games_menu.menu = self
		await epic_games_menu.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.secondary,
		label = language[LANG]['admin_settings'],
		row = 0,
	)
	async def all_admin_settings(self, interaction: discord.Interaction, button):
		if interaction.user.guild_permissions.administrator == False and str(interaction.user.id) != ownerID:
			await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
			return

		admin_menu = _AdminSettingsMenu()
		admin_menu.menu = self
		await admin_menu.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]['button_steam'],
		row = 0,
	)
	async def steam_settings(self, interaction: discord.Interaction, button):
		steam_menu = _SettingsMenu()
		steam_menu.parser = 'steam'
		steam_menu.add_item(_StatusSettingsButton(steam_menu, interaction, 'steam'))
		steam_menu.menu = self
		await steam_menu.update_message(interaction)

	@discord.ui.button(
		style = discord.ButtonStyle.secondary,
		label = language[LANG]['in_develop'],
		row = 1
	)
	async def help_menu(self, interaction: discord.Interaction, button):
		await interaction.response.send_message(content = language[LANG]['command_in_develop'], ephemeral = True)

	@discord.ui.button(
		style = discord.ButtonStyle.primary,
		label = language[LANG]['fix_message_button'],
		row = 1
	)
	async def fix_message(self, interaction: discord.Interaction, button):
		fix_message_menu = _FixMessageMenu()
		fix_message_menu.menu = self
		await fix_message_menu.update_message(interaction)


	@discord.ui.button(
		style = discord.ButtonStyle.secondary,
		label = language[LANG]['in_develop'],
		row = 1
	)
	async def update_menu(self, interaction: discord.Interaction, button):
		await interaction.response.send_message(content = language[LANG]['command_in_develop'], ephemeral = True)


@bot.tree.command(name='uni_settings')
@app_commands.guild_only()
@has_channel_permissions()
async def uni_settings(interaction: discord.Interaction):
	view = _ChooseSettingsMenu()
	#view.embed = embed
	view.interaction = interaction
	await interaction.response.send_message(embed = None, view = view, ephemeral = True)

@bot.tree.command(name='uni_help')
async def uni_help(interaction: discord.Interaction):
		
	embed = discord.Embed()
	embed.title = f'{language[LANG]["help_title"]}'
	if has_channel_permissions_not_decorator(interaction):
		for com in language[LANG]['help_commands']['admin'].values():
			embed.add_field(name = f'{com["name"]}', value = com["description"], inline = False)
			
	for com in language[LANG]['help_commands']['not_admin'].values():
		embed.add_field(name = f'{com["name"]}', value = com["description"], inline = False)
	
	embed.set_author(name = interaction.user.name, icon_url = interaction.user.display_avatar.url)
	embed.set_footer(text = language[LANG]['help_footer'])
	embed.colour = discord.Color.green()

	await interaction.response.send_message(embed = embed, ephemeral = True)

@bot.tree.command(name='uni_ping')
async def uni_ping(interaction: discord.Interaction):
	await interaction.response.send_message(content = f'{language[LANG]["bot_latency"]} : {bot.latency:.3f}s', ephemeral = True)

# @bot.tree.command(name='dev_send_to_channel')
# @app_commands.guild_only()
# @is_owner()
# async def dev_send_to_channel(interaction: discord.Interaction, user: discord.Member):
# 	channels = interaction.guild.voice_channels
# 	view = discord.ui.View()
# 	def select_channel():
# 		channel_select = discord.ui.Select(
# 			options = [
# 				discord.SelectOption(
# 					label = voice.name,
# 					value = str(voice.id)
# 				) for voice in channels
# 			],
# 			placeholder = f'{language[LANG]["send_to_channel_choose"]} {user.name}',
# 		)
# 		async def select_callback(interaction: discord.Interaction):
# 			if user.voice == None:
# 				await interaction.response.send_message(
# 					content=f'{language[LANG]["send_to_channel_sorry"]}, {user.name} {language[LANG]["send_to_channel_no_voice"]}',
# 					ephemeral=True
# 				)
# 				return

# 			channel = bot.get_channel(int(channel_select.values[0]))
# 			await user.move_to(channel)
# 			await interaction.response.send_message(
# 				content = f'{user.name} {language[LANG]["send_to_channel_will_be_sent"]} **{channel.name}** {language[LANG]["send_to_channel_channel"]}.', 
# 				ephemeral = True,
# 			)
		
# 		channel_select.callback = select_callback
# 		return channel_select

# 	def button_all_members():
# 		button = discord.ui.Button(
# 			style = discord.ButtonStyle.success,
# 			label = language[LANG]["send_to_channel_check_all"],
# 			emoji = '<:69ca01c5525a96fd2fd6f42ff505874b:814609179352236042>',
# 		)
# 		async def btn_callback(interaction: discord.Interaction):
# 			embed = discord.Embed()
# 			for channel in channels:
# 				members = [str(m.name) for m in channel.members]
# 				embed.add_field(
# 					name = f'{channel.name} : ({len(members)} {language[LANG]["precense_users"]})',
# 					value = ', '.join(members) if len(members) != 0 else '---',
# 					inline = False,
# 				)
# 			await interaction.response.send_message(embed = embed, ephemeral = True)
# 		button.callback = btn_callback
# 		return button
	
# 	view.add_item(select_channel())
# 	view.add_item(button_all_members())

# 	await interaction.response.send_message(
# 		view = view, 
# 		ephemeral=True,
# 	)



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

# @bot.tree.command(name='dev_uni_give_permissions')
# @app_commands.guild_only()
# @app_commands.describe(boolean = language[LANG]["give_permissions_describe"])
# @is_owner()
# async def dev_uni_give_permissions(interaction: discord.Interaction, user: discord.Member, boolean: bool):
# 	if user.bot:
# 		await interaction.response.send_message(content = f'{language[LANG]["give_permissions_error_bot"]}', ephemeral = True)
# 		return
		
# 	with open(files['users'], 'r', encoding='utf-8') as file:
# 		data = json.load(file)

# 	with open(files['users'], 'w', encoding='utf-8') as file:
# 		check = data[str(interaction.guild_id)]
# 		check[str(user.id)] = {
# 			'name': str(check[str(user.id)]['name']),
# 			'has_permissions': str(boolean),
# 		}
# 		data[str(interaction.guild_id)] = check

# 		json.dump(data, file, ensure_ascii=False, indent=4)

# 	await interaction.response.send_message(content = f'{language[LANG]["give_permissions_all_ready"]}! {user.name} {language[LANG]["give_permissions_new_status"]} : {boolean}.', ephemeral = True)

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

# @dev_uni_test.error
# async def dev_uni_test_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.CheckFailure):
# 		await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'{language[LANG]["something_went_wrong"]}', ephemeral=True)

# @dev_uni_give_permissions.error
# async def dev_uni_give_permissions_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.CheckFailure):
# 		await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'{language[LANG]["something_went_wrong"]}', ephemeral=True)

# @dev_send_to_channel.error
# async def dev_send_to_channel_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.CheckFailure):
# 		await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'{language[LANG]["something_went_wrong"]}', ephemeral=True)

# @reset_settings.error
# async def reset_settings_error(interaction: discord.Interaction, error):
# 	if isinstance(error, app_commands.errors.MissingPermissions):
# 		await interaction.response.send_message(f'{interaction.user.mention} You don\'t have enough permissions', ephemeral=True)

@uni_settings.error
async def uni_settings_error(interaction: discord.Interaction, error):
	#print(error)
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
	else:
		await interaction.response.send_message(f'{language[LANG]["something_went_wrong"]}', ephemeral=True)

# @uni_fix_message.error
# async def uni_fix_message_error(interaction: discord.Interaction, error):
# 	print(error)
# 	if isinstance(error, app_commands.errors.CheckFailure):
# 		await interaction.response.send_message(f'{interaction.user.mention} {language[LANG]["dont_have_permissions"]}', ephemeral=True)
# 	else:
# 		await interaction.response.send_message(f'{language[LANG]["something_went_wrong"]}', ephemeral=True)

bot.run(token = os.environ['TOKEN'])