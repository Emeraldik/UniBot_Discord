import discord
from discord.ext import commands

from dotenv import load_dotenv, find_dotenv
from asyncio import sleep
import os
import json

files = {
	'data': 'data.json', 
	'channels': 'channels.json'
}

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

@bot.event
async def on_ready():
	for key, file_name in files.items():
		if not os.path.exists(file_name):
			with open(file_name, 'w', encoding='utf-8') as file:
				file.write('{}')

	print(f'Discord Bot {bot.user} is ready!')
	for guild in bot.guilds:
		for member in guild.members:
			#print(f'{member.name} {member.id} {member.joined_at}')
			with open(files['data'], 'r', encoding='utf-8') as file:
				data = json.load(file)

			with open(files['data'], 'w', encoding='utf-8') as file:
				if not member.bot:
					data[str(member.id)] = {
						'name': str(member.name),
						'avatar': str(member.display_avatar),
					}

				json.dump(data, file, ensure_ascii=False, indent=4)
	print('Database loaded!')

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if message.author == bot.user: 
		return

	#print(f'New message by {message.author.name} : {message}')
	# await message.channel.typing()
	# await sleep(1)
	# await message.reply(content = f'Thanks for you message, {message.author.mention}')

@bot.command()
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
	with open(files['channels'], 'r', encoding='utf-8') as file:
		channels = json.load(file)

	with open(files['channels'], 'w', encoding='utf-8') as file:
		channels[str(ctx.guild.id)] = {
			'channel': str(channel.id),
		}

		json.dump(channels, file, ensure_ascii=False, indent=4)
	await ctx.respond(content = 'New channel is setup!')

@set_channel.error
async def error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		print('Something went wrong...')

load_dotenv(find_dotenv())
bot.run(os.getenv('TOKEN'))