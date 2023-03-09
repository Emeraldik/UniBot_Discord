import asyncio, aiohttp
from bs4 import BeautifulSoup as BS

from datetime import datetime as dt
from pytz import timezone

import json, os

from log_main import logger
from language import language, LANG

file_name = 'steam.json'

async def get_cards(session, all_data):
    cookies = {
        'cf_chl_2': '483ead1c46bc2ba',
        'cf_clearance': 'NTtHkvLcAf85VlNygUzCwVSF5KiS96P_8mL0x5krOc4-1677783538-0-250',
        '__cf_bm': 'dcd21SOPCxCMZCU1pf8EjFbKxK5tK8k7BEf8IGN4vLo-1677783554-0-AeYOskU4rArXynZlpfzgMDsIbKGDikHgT/h9gMSSLDvHKl6LxZrFScsl9TeswU1KNbZREVB0O7wChI6l9wQD5UEaR8AZORi15KsCf5IU4SAjXvPjPWumt+RdqEf1EAOa0LcIeGqkXV2ISpcEeTZbrghhle5EYFig9cZLtjkJvIGZE8VIs87tiPtTNTZzCbG05A==',
    }

    headers = {
        'authority': 'steamdb.info',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://steamdb.info/tokendumper/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    url = 'https://steamdb.info/upcoming/free/'

    async with session.get(url=url, headers = headers, cookies=cookies) as response:
        response_content = await response.text()
        soup = BS(response_content, 'lxml')

        for k, game in enumerate(soup.find_all('tr', class_='app')):
            try:
                game_id = game.get('data-appid')
                if game_id in all_data:
                    continue

                if game.get('data-subid') == '61':
                    continue

                if not game.find('td', class_='price-discount'):
                    continue 
                

                applogo = game.find('td', class_='applogo').find('a')
                game_link = applogo.get('href').strip('?curator_clanid=4777282&utm_source=SteamDB')
                
                async with session.get(url=game_link, headers = headers, cookies=cookies) as response:
                    inner_response_content = await response.text()
                    inner_soup = BS(inner_response_content, 'lxml')

                    try:
                        game_price = inner_soup.find('div', class_='discount_original_price').text
                    except:
                        game_price = language[LANG]['price_unavailable']

                    game_logo = inner_soup.find('link', {'href' : True, 'rel': 'image_src'}).get('href')
                game_title = game.find_all('td')[2].find('b').text

                # convert from Moscow to UTC time
                time_z = timezone('UTC')
                utc_three = timezone('Europe/Moscow')
                times = [time_z.normalize(utc_three.localize(dt.strptime(i.get('data-time'), "%Y-%m-%dT%H:%M:%S+00:00"))) for i in game.find_all('td', class_='timeago')]
            except Exception as e:
                print(e)
            else:
                all_data.update({
                    game_id : {
                        'card_name' : game_title,
                        'card_link' : game_link,
                        'card_image' : game_logo,
                        'card_price' : game_price,
                        'start_time' : str(dt.strptime(str(times[0]), "%Y-%m-%d %H:%M:%S+00:00")),
                        'end_time' : str(dt.strptime(str(times[1]), "%Y-%m-%d %H:%M:%S+00:00")),
                        'started' : str(times[0] < dt.now(timezone('UTC'))),
                        'expired' : str(times[1] < dt.now(timezone('UTC')))
                    }
                })

async def check_games(all_data):
    async with aiohttp.ClientSession() as session:
        await get_cards(session, all_data)

async def start_parse():
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('{"steam_links" : {}}')

    with open(file_name, 'r', encoding = 'utf-8') as file:
        async_all_data = json.load(file)
    
    try:
        task = asyncio.get_event_loop().create_task(check_games(async_all_data['steam_links']))
        await task
    except Exception as e:
        print(e)
    else:
        for k, game in async_all_data['steam_links'].items():
            if game.get('expired') == 'False':
                game['expired'] = str(dt.strptime(game['end_time'], "%Y-%m-%d %H:%M:%S") < dt.utcnow())

        logger.info(f'[+] {[i.get("card_name") for i in async_all_data["steam_links"].values() if i.get("expired") == "False"]} card async')
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(async_all_data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    from time import perf_counter
    start = perf_counter()
    asyncio.run(start_parse())
    print(f'Time : {(perf_counter() - start):.3f}s')