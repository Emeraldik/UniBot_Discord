import aiohttp, asyncio
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator
from datetime import datetime as dt
import json, os

from language import LANG
from log_main import logger

translator = GoogleTranslator(source='auto', target=LANG)

file_name = 'steam.json'

async def get_card_info(session, i, all_data, card, k):
	try:
		card_id = card.get('id').split('-')[-1]
		if card.find('div', class_='expire_stamp'):
			if str(card_id) in all_data:
				if all_data[str(card_id)]['card_expired'] != 'True':
					all_data[str(card_id)]['card_expired'] = str(True)
					logger.info(f'{card_id} was expired')
			return
		card_fulldata = card.find('div', class_='post-thumbnail')
		card_data = card_fulldata.find('a')
		card_image = card_fulldata.find('img').get('src')
		card_name = card_data.get('title')
		card_time = dt.strptime(card.find('time', class_='entry-date published').get('datetime'), "%Y-%m-%dT%H:%M:%S+00:00")
		card_link = card_data.get('href')
		
		inner_card_link = 'Not_inner : ' + str(card_link)
		inner_desc = ''
		#inner_steam_link = ''
		
		headers = {'User-Agent': f'{UserAgent().chrome}'}
		async with session.get(url = card_link, headers=headers) as inner_response:
			inner_response_content = await inner_response.text()
			inner_soup = BS(inner_response_content, 'lxml')
			inner_desc_plate = inner_soup.find('div', class_='zf_description')
			inner_desc = '\n'.join([i.text for i in inner_desc_plate.find_all('p')])
			inner_card_link = inner_soup.find('a', class_='item-url').get('onclick').strip('javascript:window.open( ); \'')
			#inner_steam_link = inner_soup.find('a', class_='zf-edit-button').get('href')

		if not 'https://store.steampowered.com/' in inner_card_link:
			return
	except Exception as e:
		return
	else:
		all_data[str(card_id)] = {
			'card_name' : str(card_name),
			'card_desc' : translator.translate(str(inner_desc)),
			'card_image' : str(card_image),
			'start_time' : str(card_time),
			'card_link' : str(inner_card_link),
			'card_expired' : str(False),
			#'steam_link' : str(inner_steam_link),
		}
		
		logger.info(f'[+] {card_name} card async')


async def get_cards(session, i, all_data):
	headers = {'User-Agent': f'{UserAgent().chrome}'}

	url = f'https://www.freesteamkeys.com/giveaways/page/{i}/'

	async with session.get(url=url, headers = headers) as response:
		response_content = await response.text()
		soup = BS(response_content, 'lxml')
		giveaways = soup.find('div', id='post-items')

		all_cards = giveaways.find_all('article', class_='post')

		cards = []
		for k, card in enumerate(all_cards):
			try:
				task = asyncio.create_task(get_card_info(session, i, all_data, card, k))
				cards.append(task)
			except Exception as e:
				continue

		await asyncio.gather(*cards)

async def check_games(all_data):
	async with aiohttp.ClientSession() as session:
		tasks = []
		for i in range(1, 3): # 2 pages
			task = asyncio.create_task(get_cards(session, i, all_data))
			tasks.append(task)

		await asyncio.gather(*tasks)

async def start_parse():
	if not os.path.exists(file_name):
		with open(file_name, 'w', encoding='utf-8') as file:
			file.write('{"steam_links" : {}, "not_steam_links" : {}}')

	with open(file_name, 'r', encoding = 'utf-8') as file:
		async_all_data = json.load(file)
	
	try:
		task = asyncio.get_event_loop().create_task(check_games(async_all_data['steam_links']))
		await task
	except Exception as e:
		print(e)
	else:
		with open(file_name, 'w', encoding='utf-8') as file:
			json.dump(async_all_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
	asyncio.run(start_parse())