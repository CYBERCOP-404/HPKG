import uuid
import time
import requests
import random
import string
DEBUG = False
MAX_RETRIES = 6
games = {
    'BIKE': {
        'appToken': 'd28721be-fd2d-4b45-869e-9f253b554e50',
        'promoId': '43e35910-c168-4634-ad4f-52fd764a843f',
        'delay': 20,
        'retry': 20,
        'keys': 4,
    },
    'CLONE': {
        'appToken': '74ee0b5b-775e-4bee-974f-63e7f4d5bacb',
        'promoId': 'fe693b26-b342-4159-8808-15e3ff7f8767',
        'delay': 120,
        'retry': 20,
        'keys': 4,
    },
    'CUBE': {
        'appToken': 'd1690a07-3780-4068-810f-9b5bbf2931b2',
        'promoId': 'b4170868-cef0-424f-8eb9-be0622e8e8e3',
        'delay': 20,
        'retry': 20,
        'keys': 4,
    },
    'TRAIN': {
        'appToken': '82647f43-3f87-402d-88dd-09a90025313f',
        'promoId': 'c4480ac7-e178-4973-8061-9ed5b2e17954',
        'delay': 120,
        'retry': 20,
        'keys': 4,
    },
}

def debug(*args):
    if DEBUG:
        print(*args)

def info(*args):
    print(*args)

def uuidv4():
    return str(uuid.uuid4())

def delay(seconds):
    debug(f'Waiting {seconds}s')
    time.sleep(seconds)

def fetch_api(path, auth_token_or_body=None, body=None):
    headers = {}
    if isinstance(auth_token_or_body, str):
        headers['Authorization'] = f'Bearer {auth_token_or_body}'
    elif auth_token_or_body is not None or body is not None:
        headers['Content-Type'] = 'application/json'
        body = body or auth_token_or_body
    
    url = f'https://api.gamepromo.io{path}'
    debug(url, headers, body)
    response = requests.post(url, headers=headers, json=body)
    
    if not response.ok:
        if DEBUG:
            debug(response.text)
        response.raise_for_status()
    
    data = response.json()
    debug(data)
    return data

def get_promo_code(game_key):
    game_config = games[game_key]
    client_id = uuidv4()

    login_client_data = fetch_api('/promo/login-client', {
        'appToken': game_config['appToken'],
        'clientId': client_id,
        'clientOrigin': 'ios',
    })
    delay(game_config['delay'])

    auth_token = login_client_data['clientToken']
    promo_code = None

    for _ in range(MAX_RETRIES):
        register_event_data = fetch_api('/promo/register-event', auth_token, {
            'promoId': game_config['promoId'],
            'eventId': uuidv4(),
            'eventOrigin': 'undefined'
        })

        if not register_event_data['hasCode']:
            delay(game_config['retry'])
            continue

        create_code_data = fetch_api('/promo/create-code', auth_token, {
            'promoId': game_config['promoId'],
        })

        promo_code = create_code_data['promoCode']
        break

    if promo_code is None:
        raise Exception(f'Unable to get {game_key} promo')

    return promo_code
def display_promo_code(game_key):
    game_config = games[game_key]

    for _ in range(game_config['keys']):
        code = get_promo_code(game_key)
        info(code)
def main():
    users = ['User 1', 'User 2', 'User 3']
    
    for user in users:
        info(f'- Running for {user}')

        for game_key in games.keys():
            info(f'-- Game {game_key}')
            display_promo_code(game_key)

        info('====================')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
# code with nahid 
