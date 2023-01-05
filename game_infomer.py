import requests
import os
import json
from datetime import datetime as dt
from python_translator import Translator

#import translators.server as tss

file_name = 'games.json'

def check_new_games():
	
	if not os.path.exists(file_name):
		with open(file_name, 'w', encoding='utf-8') as file:
			file.write('{}')

	api = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU&country=RU"
	translator = Translator()
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
			# print(game['title'], '\n')
			# if len(game['promotions']['promotionalOffers']) != 0 and len(game['promotions']['upcomingPromotionalOffers']) == 0:
			# 	print(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate'])
			# 	print(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate'])
			# 	timeend = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
			# 	timeend = dt.strptime(timeend, "%Y-%m-%dT%H:%M:%S.%fZ")
			# 	#2023-01-05T16:00:00.000Z
			# 	print(dt.utcnow())
			# 	print(timeend - dt.utcnow())
			try:
				with open(file_name, 'r', encoding='utf-8') as file:
					gm = json.load(file)
			except:
				with open(file_name, 'w', encoding='utf-8') as file:
					file.write('{}')

				with open(file_name, 'r', encoding='utf-8') as file:
					gm = json.load(file)

			with open(file_name, 'w', encoding='utf-8') as file:
				game_image = ''
				for k in game['keyImages']:
					if k['type'] == 'OfferImageWide' or k['type'] == 'DieselStoreFrontWide':
						game_image = k['url']

				game_url = game['catalogNs']['mappings'][0]['pageSlug']
				game_promotions = game['promotions']['promotionalOffers']
				upcoming_promotions = game['promotions']['upcomingPromotionalOffers']

				if game_promotions and game['price']['totalPrice']['discountPrice'] == 0:
					# Promotion is active.
					date_end = dt.strptime(game_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
				elif not game_promotions and upcoming_promotions:
					# Promotion is not active yet, but will be active soon.
					date_end = dt.strptime(upcoming_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
				elif game_promotions:
					# Promotion is active.
					date_end = dt.strptime(game_promotions[0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
				else:
					date_end = ''


				gm[str(game['id'])] = {
					'title' : str(game['title']),
					'description' : str(translator.translate(game['description'], 'russian', 'english')),
					#'description' : str(game['description']),
					'image' : str(game_image),
					'url' : f'https://store.epicgames.com/en/p/{str(game_url)}',
					'date_end' : str(date_end),
					'days_left' : str(date_end - dt.utcnow()) if date_end != '' else '',
					'expired' : str(date_end < dt.utcnow()) if date_end != '' else None,
				}

				json.dump(gm, file, ensure_ascii=False, indent=4)	

	else:
		pass
		#print('Something went wrong...')

if __name__ == '__main__':
	check_new_games()