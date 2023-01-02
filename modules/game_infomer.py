import requests
#import translators.server as tss

file_name = 'data.txt'

def main():
	global dict_check
	dict_check = []
	games = check_new_games()

def return_games():
	games = check_new_games()
	#print(games[2])
	new_games = []

	# try:
	# 	file = open(file_name, 'r')
	# except:
	# 	add_new_games(games)
	# else:
	# 	append_new_games(games, file)
	

	# with open('data.txt','a') as file


def check_new_games():
	api = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU"
	response = requests.get(api)

	dict_check = []

	if response.status_code == 200:
		free_games = response.json()

		games = free_games['data']['Catalog']['searchStore']['elements']

		for game in games:
			if not game in dict_check: 
				print(game['title'], '\n')
				print(game['price'], '\n')
				#print(game['promotions']['promotionalOffers'][0]['promotionalOffers'] or 0)
				#print(tss.yandex(game['description'], 'en', 'ru'))
				#print(game['description'])
				# for j in game['keyImages']:
				# 	if j['type'] == 'DieselStoreFrontWide':
				# 		print(j['url'])
				dict_check.append(game)
	else:
		print('Something went wrong...')

	return dict_check

if __name__ == '__main__':
	return_games()