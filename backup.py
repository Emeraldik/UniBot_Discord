import yadisk_async
import os, json
import asyncio, aiofiles
from dotenv import load_dotenv, find_dotenv
from datetime import datetime as dt
from pytz import timezone

from log_main import logger

load_dotenv(find_dotenv())

async def upload_files(session, file_name, time):
	async with aiofiles.open(file_name, 'rb') as f:
		try:
			await session.upload(f, f'UniBot Backup/{time}/{file_name}')
		except yadisk_async.exceptions.PathExistsError:
			pass
		else:
			logger.info(f'[+] {file_name} is upload successful in folder : {time}')

async def start_backup(files):
	tasks = []
	async with yadisk_async.YaDisk(token=os.environ['yandex_token']) as yandex:
		if not await yandex.exists('UniBot Backup'):
			await yandex.mkdir('UniBot Backup')

		date = dt.now(timezone("UTC"))
		date = date.strftime("%Y-%m-%d %H:%M")
		if not await yandex.exists(f'UniBot Backup/{date}'):
			await yandex.mkdir(f'UniBot Backup/{date}')

		for file_name in files:
			if os.path.exists(file_name):
				task = asyncio.get_event_loop().create_task(upload_files(yandex, file_name, date))
				tasks.append(task)

		await asyncio.gather(*tasks)	

if __name__ == '__main__':
	file_names = [
		'channels.json',
		'epic_games.json',
		'steam.json',
	]
	asyncio.run(start_backup(file_names))