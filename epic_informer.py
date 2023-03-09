import aiohttp, asyncio
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator
from datetime import datetime as dt
from copy import deepcopy
import json, os

from language import LANG
from log_main import logger

file_name = 'epic_games.json'

APIs = {
	'not_ru': 'locale=ru-RU',
	'ru': 'locale=ru-RU&country=RU',
}

translator = GoogleTranslator(source='auto', target=LANG)

async def get_data_from_api(session, key_region='ru', API='locale=ru-RU&country=RU', all_data = {}):
	headers = {'User-Agent': f'{UserAgent().chrome}'}

	url = f'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?{API}'

	new_dict = {}
	async with session.get(url=url, headers = headers) as response:
		free_games = await response.json()

		games = free_games['data']['Catalog']['searchStore']['elements']
		games = list(sorted(
	        filter(
	            lambda g: g.get('promotions'),
	            games
	        ),
	        key=lambda g: g['title']
	    ))
		
		for game in games:
			try:
				game_price_new = game['price']['totalPrice']['fmtPrice']['discountPrice']
				if game_price_new != '0':
					continue

				game_image = ''
				for k in game['keyImages']:
					if k['type'] == 'OfferImageWide' or k['type'] == 'DieselStoreFrontWide':
						game_image = k['url']
				
				game_url = ''

				if len(game['offerMappings']) == 0:
					game_url = game['catalogNs']['mappings'][0]['pageSlug']
				else:
					game_url = game['offerMappings'][0]['pageSlug']

				game_price = game['price']['totalPrice']['fmtPrice']['originalPrice']
				game_promotions = game['promotions']['promotionalOffers']
				upcoming_promotions = game['promotions']['upcomingPromotionalOffers']

				if game_promotions and game['price']['totalPrice']['discountPrice'] == 0:
					# Promotion is active.
					date_start = dt.strptime(game_promotions[0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
					date_end = dt.strptime(game_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
				elif not game_promotions and upcoming_promotions:
					# Promotion is not active yet, but will be active soon.
					date_start = dt.strptime(upcoming_promotions[0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
					date_end = dt.strptime(upcoming_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
					game_price_new = '0'
				elif game_promotions:
					# Promotion is active.
					date_start = dt.strptime(game_promotions[0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
					date_end = dt.strptime(game_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")	
				else:
					date_start = ''
					date_end = ''

				timenow = dt.utcnow()
			except Exception as e:
				print(e)
			else:
				new_dict[str(game['id'])] = {
					'title' : str(game['title']),
					'description' : str(translator.translate(game['description'])),
					'image' : str(game_image),
					'url' : f'https://store.epicgames.com/en/p/{str(game_url)}',
					'price' : str(game_price),
					'date_start' : str(date_start),
					'date_end' : str(date_end),
					'started' : str(date_start < timenow) if date_start != '' else None,
					'expired' : str(date_end < timenow) if date_end != '' else None,
				}

				all_data[str(key_region)].update(new_dict)
				logger.info(f'[+] {key_region} : {game["title"]} async')

async def check_games(all_data):
	async with aiohttp.ClientSession() as session:
		tasks = []
		for key_region, api in APIs.items(): # 2 pages
			task = asyncio.create_task(get_data_from_api(session, key_region, api, all_data))
			tasks.append(task)

		await asyncio.gather(*tasks)

async def start_parse():
	if not os.path.exists(file_name):
		with open(file_name, 'w', encoding='utf-8') as file:
			file.write('{"ru" : {}, "not_ru" : {}}')
	
	new_all_data = {
		'ru' : {},
		'not_ru' : {}
	}

	try:
		task = asyncio.get_event_loop().create_task(check_games(new_all_data))
		await task
	except Exception as e:
		print(e)
	else:
		with open(file_name, 'r', encoding='utf-8') as file:
			async_all_data = json.load(file)

		for k, game in new_all_data['ru'].items():
			if k in new_all_data['not_ru']:
				new_all_data['not_ru'].pop(k)
				
			if k in async_all_data['not_ru']:
				async_all_data['not_ru'].pop(k)

		for k, game in new_all_data['not_ru'].items():
			if not k in new_all_data['ru'] and k in async_all_data['ru']:
				async_all_data['ru'].pop(k)

		for k in async_all_data.keys():
			async_all_data[k].update(new_all_data[k])
		
		for key, region in async_all_data.items():
			for k, game in region.items():
				timenow = dt.utcnow()
				date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
				async_all_data[key][k].update({
					'expired' : str(date_end < timenow) if date_end != '' else None,
				})

		with open(file_name, 'w', encoding='utf-8') as file:
			json.dump(async_all_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
	asyncio.run(start_parse())