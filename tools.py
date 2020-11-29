import config 
import asyncio

emojis = {
    'Bear': '🐻',
    'Wolf': '🐺',
    'Boar': '🐗',
    'Knight': '⚔️',
    'Sentinel': '🛡️',
    'Ranger': '🏹',
    'Blacksmith': '⚒️',
    'Alchemist': '⚗️',
    'Collector': '📦',
    'Master': '🐣',
    'Esquire': '🐣',
    'foray': '🗡'
}


async def noisy_sleep(t_max):
    rand_seconds = random.randrange(0, t_max)
    await asyncio.sleep(rand_seconds) 

async def user_log(client, text):
    await client.send_message(config.GROUP, text, parse_mode='html')

def bool2emoji(boolean):
    return '✔️' if boolean else '❌'