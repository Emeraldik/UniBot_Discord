import requests
import os
import json
from datetime import datetime as dt
from deep_translator import GoogleTranslator

from language import LANG


file_name = 'games.json'

APIs = {
	'not_ru': 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU',
	'ru': 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU&country=RU',
}

translator = GoogleTranslator(source='auto', target=LANG)

def check_games():
	for key, api in APIs.items():
		check_new_games(key, api)

def check_new_games(key='ru', API='https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU&country=RU'):
	
	if not os.path.exists(file_name):
		with open(file_name, 'w', encoding='utf-8') as file:
			file.write('{}')

	api = str(API)
	response = requests.get(api)

	if response.status_code == 200:
		free_games = response.json()

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
				with open(file_name, 'r', encoding='utf-8') as file:
					gm = json.load(file)
			except:
				with open(file_name, 'w', encoding='utf-8') as file:
					file.write('{}')

				with open(file_name, 'r', encoding='utf-8') as file:
					gm = json.load(file)

			with open(file_name, 'w', encoding='utf-8') as file:
				try:
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
					game_price_new = game['price']['totalPrice']['fmtPrice']['discountPrice']
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
					if game_price_new == '0':
						gm[str(game['id'])] = {
							'id' : str(game['id']),
							'title' : str(game['title']),
							'description' : str(translator.translate(game['description'])),
							'image' : str(game_image),
							'url' : f'https://store.epicgames.com/en/p/{str(game_url)}',
							'price' : str(game_price),
							'date_end' : str(date_end),
							'days_left' : str(date_end - timenow) if date_end != '' else '',
							'days_left_seconds': str((date_end - timenow).total_seconds()) if date_end != '' else '',
							'started' : str(date_start < timenow) if date_start != '' else None,
							'expired' : str(date_end < timenow) if date_end != '' else None,
							'key': str(key),
						}
				finally:
					json.dump(gm, file, ensure_ascii=False, indent=4)

	else:
		pass
		#print('Something went wrong...')

	with open(file_name, 'r', encoding='utf-8') as file:
		gm = json.load(file)

	with open(file_name, 'w', encoding='utf-8') as file:
		for key, game in gm.items():
			timenow = dt.utcnow()
			date_end = dt.strptime(game['date_end'], "%Y-%m-%d %H:%M:%S")
			gm[key] = {
				'id' : str(game['id']),
				'title' : str(game['title']),
				'description' : str(game['description']),
				#'description' : str(game['description']),
				'image' : str(game['image']),
				'url' : str(game['url']),
				'price' : str(game['price']),
				'date_end' : str(game['date_end']),
				'days_left' : str(date_end - timenow) if date_end != '' else '',
				'days_left_seconds': str((date_end - timenow).total_seconds()) if date_end != '' else '',
				'started' : str(game['started']),
				'expired' : str(date_end < timenow) if date_end != '' else None,
				'key': str(game['key']),
			}

		json.dump(gm, file, ensure_ascii=False, indent=4)	

if __name__ == '__main__':
	check_games()