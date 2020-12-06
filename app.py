from telethon import TelegramClient, events, connection
import random, re
from time import sleep
from datetime import datetime, timedelta
import time
import aiocron
import asyncio
import math
import logging
import os
import json

import tools
import config

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)


############ Credentials ############ 
if config.PROXY:
    client = TelegramClient(config.SESSION,
    config.API_ID,
    config.API_HASH,
    connection_retries=1,
    timeout=180,
    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
    proxy=config.PROXY)
else:
    client = TelegramClient(config.SESSION,
    config.API_ID,
    config.API_HASH)


############ Load Stuff ############ 
jsons = os.listdir(config.DATA_FOLDER)
# Load settings
if 'settings.json' in jsons:
    datafile = os.path.join(config.DATA_FOLDER, 'settings.json')        
else:
    datafile = os.path.join(config.DATA_FOLDER, 'settings_default.json')  
with open(datafile) as data_file:
    settings = json.load(data_file)  

# Load Status
datafile = os.path.join(config.DATA_FOLDER, 'status_default.json') 
with open(datafile) as data_file:
    status = json.load(data_file)  


############ Generator of cron strings ############ 
cwc = tools.ChatWarsCron(config.UTC_DELAY)


############ STATUS ############

# Request an status update
async def request_status_update():
    try:
        await client.send_message(config.CHAT_WARS, '🏅Me')
    except ValueError:
        print('Stupid telethon has not found cw')

# Update the status parsing Me
@client.on(events.NewMessage(chats=config.CHAT_WARS, incoming = True, pattern=r'Battle of the seven castles in|🌟Congratulations! New level!🌟'))
async def update_status(event):
 
    # global arena, daily_arenas, quest, to_quest, endurance, endurance_max, state, alt_class, castle
  
    status['current_stamina'] = int(re.search(r'Stamina: (\d+)', event.raw_text).group(1))
    status['max_stamina'] = int(re.search(r'Stamina: (\d+)/(\d+)', event.raw_text).group(2))
    status['current_hp'] = int(re.search(r'Hp: (\d+)', event.raw_text).group(1))
    status['max_hp'] = int(re.search(r'Hp: (\d+)/(\d+)', event.raw_text).group(2))
    status['state'] = re.search(r'State:\n(.*)', event.raw_text).group(1)
    lines = event.raw_text.split('\n')
    for i, line in enumerate(lines):
        if len(line):
            if line[0] in ['🥔', '🦅', '🦌', '🐉', '🦈', '🐺', '🌑']:
                status['castle'] = line[0]
                if ']' in line:
                    front, back = line.split(']')
                    status['guild'] = front.split('[')[-1]
                else:
                    back = line[1:]
                last_words = back.split(' ')
                status['class'] = tools.emojis[last_words[-4]]
            if line[0].startswith('💰'):
                status['gold'] = int(line[1:].split()[0])

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")   
    status['current_time'] = current_time
    status['time_of_day'] = cwc.get_current_day_time(current_time)

# Retreive current status
@client.on(events.NewMessage(chats=config.GROUP, pattern='/status'))
async def status_all(event):
    await request_status_update()
    await tools.noisy_sleep(2, 1)
    msg =  '''
<b> Player Status:</b>\n
🏰Castle: {castle} 
👨‍🏫Class: {class}
💰 Money: {gold}
🔋 Stamina: {current_stamina}/{max_stamina}
❤️ Hp: {current_hp}/{max_hp}
📯 Arenas: {arenas}/5
Curently: {state}
In CW: {time_of_day}
--- server time: {current_time}'''.format(**status)
    
    await tools.user_log(client, msg)


@aiocron.crontab(cwc.reset_time())
async def reset_stuff():
    status['arenas'] = 0
    await tools.user_log(client, 'Counters restarted')



############ SETTINGS ############
# Retreive current user settings
@client.on(events.NewMessage(chats=config.GROUP, pattern='/settings'))
async def get_settings(event):
    res = '<b>User settings:</b>\n\n'
    for s in settings:
        res += "{} {}{}\n".format(tools.bool2emoji(settings[s]['status']),  tools.settings_emoji[s], s)
        if event.message.text == '/settingsfull':
            for k in settings[s].keys():
                if k != 'status':
                    res += "    {}: {}\n".format(k, settings[s][k])
    await tools.user_log(client, res)


def parse_value(string):
    if string == 'True' or string == 'on':
        return True
    elif string == 'False' or string == 'off':
        return False
    try : 
        string_integer = int(string)
        return string_integer
    except ValueError :
        pass
    return string

def save_settings():
    filepath = os.path.join(config.DATA_FOLDER, 'settings.json')
    with open(filepath, 'w') as f:
        json.dump(settings, f)

# Enable/disable the settings
@client.on(events.NewMessage(chats=config.GROUP, pattern='/set'))
async def update_settings(event):
    parsed_command = event.message.text.split()
    if len(parsed_command) == 3:
        if parsed_command[0] == '/set':
            if parsed_command[1] in settings.keys():
                sett = parsed_command[1]
                val = parse_value(parsed_command[2])
                if val == True or  val == False: 
                    settings[sett]['status'] = val
                    await tools.user_log(client, 'Setting updated\n/settingsfull')
                    return save_settings()                
        await tools.user_log(client, 'Wrong syntax. Try something like:\n<code>/set foray off</code>')
    if len(parsed_command) == 4:    
        if parsed_command[0] == '/set':
            if parsed_command[1] in settings.keys():
                sett = parsed_command[1]
                if parsed_command[2] in settings[sett].keys():
                    subsett = parsed_command[2]
                    val = parse_value(parsed_command[2])
                    settings[sett][subsett] = val
                    await tools.user_log(client, 'Setting updated\n/settingsfull')
                    return save_settings()
        await tools.user_log(client, 'Wrong syntax. Try something like:\n<code>/set foray pledge off</code>')
        
        


############ FORAY ############
# Reacts to foray attempts
@client.on(events.NewMessage(chats=config.CHAT_WARS, 
    pattern='((.|\n)*)You were strolling around on your horse when you noticed((.|\n)*)'))
async def stop_foray(event):
    if settings['foray']['status']:
        buttons = await event.get_buttons()
        for bline in buttons:
            for button in bline:
                await tools.noisy_sleep(120)
                await button.click()
        await tools.user_log(client, '🗡Foray Intervene ')

# Pledge
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*After a successful act of violence, as a brave knight you are, you felt some guilt and decided to talk with your victims*'))
async def pledge(event):
    await tools.noisy_sleep(40, 10)
    await client.send_message(config.CHAT_WARS, '/pledge')



############ BATTLES ############
# Gets order from botniato
@client.on(events.NewMessage(chats=config.BOTNIATO, pattern='.*Orders for next battle*'))
async def get_botniato_order(event):
    if settings['order']['status'] and settings['order']['source'] == 'botniato':
        settings['order']['target'] = '/ga_' + event.message.text.split('url?url=/ga_')[1].split()[0].split(')')[0]
        await tools.user_log(client, 'Order saved from botniato\n{}'.format(settings['order']['target']))

# Requests order from botniato
@client.on(events.NewMessage(chats=config.BOTNIATO, pattern='((.|\n)*)Check the ⚜️ Order button((.|\n)*)'))
async def ask_botniato_order(event):
    if settings['order']['status'] and settings['order']['source'] == 'botniato':
        await client.send_message(config.BOTNIATO, '⚜️ Order')
        await tools.user_log(client, 'Order requested to botniato')   

#TODO: Get order from squad


# Sets the order automatically
@aiocron.crontab(cwc.minutes_before_war(4))
async def set_order():
    if settings['order']['status']:
        await tools.noisy_sleep(60)
        target = settings['order']['target']
        # Castle Orders
        if target in tools.castle_emojis:
            if target != status['castle']:
                await client.send_message(config.CHAT_WARS, '⚔Attack')
                await tools.noisy_sleep(3,1)
                await client.send_message(config.CHAT_WARS, target)
            else:
                await client.send_message(config.CHAT_WARS, '🛡Defend')                
        # Alliance Orders
        elif target.startswith('/ga_def') or target.startswith('/ga_atk'):
            await client.send_message(config.CHAT_WARS, target)               
        # Guild Orders
        elif target.startswith('/g_def') or target.startswith('/g_atk'):
            await client.send_message(config.CHAT_WARS, target) 
        # Default Orders
        else:
            await client.send_message(config.CHAT_WARS, settings['order']['default'])   
        
        await tools.user_log(client, 'Order set!') 


############ REPORT ############
# Requests the report to cw
@aiocron.crontab(cwc.minutes_after_war(9))
async def report():
    if settings['report']['status']:
        await tools.noisy_sleep(60)
        await client.send_message(config.CHAT_WARS, '/report')
        await tools.user_log(client, 'Report requested') 

# Forward the report to the squad
@client.on(events.NewMessage(chats=config.CHAT_WARS, 
    pattern='((.|\n)*)Your result on the battlefield:((.|\n)*)'))
async def forward_report(event):
    if settings['report']['status']:
        if not 'Encounter' in event.message.text:
            await client.forward_messages(settings['report']['send_to'], event.message)      
            await tools.user_log(client, 'Report forwarded') 


############ HIDDEN LOCATIONS ############

@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You found hidden location*'))
async def location(event):
    await client.forward_messages(config.BOTNIATO, event.message) 
    

############ FORBIDDEN MONSTERS ############

# My mobs
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You met some hostile creatures*'))
async def monsters(event):
    if 'ambush!' in event.message.message:
        if settings['my_ambush']['status']:
            logging.info('Found ambush')
            await client.forward_messages(settings['my_ambush']['send_to'], event.message)     
            await tools.user_log(client, 'Found ambush') 
    else:
        if settings['my_mobs']['status']:
            logging.info('Found Forbidden Monsters')
            await client.forward_messages(settings['my_mobs']['send_to'], event.message)   
            await tools.user_log(client, 'Found forbidden Monsters') 
  

# TODO: Add logic to hunt other people mobs

# @client.on(events.NewMessage(chats = config.CHAMPMOBS , incoming = True, pattern='.*You met some hostile creatures*'))
# async def champion(event):
#     global mobs, champ
#     if champ == 1:
#         if 'ambush!' in event.message.message:
#             if mobs == event.message.message:
#                 pass
#             else: 
#                 logging.info('Fighting Champion')
#                 mobs = event.message.message
#                 await client.forward_messages(config.CHAT_WARS, event.message)
#                 time.sleep(1)
#                 await client.send_message(config.CHAMPMOBS, 'ya entre no he marcado......')



############ QUESTS AND ARENAS ############
@client.on(events.NewMessage(chats=config.CHAT_WARS, pattern='((.|\n)*)Dirty air is soaked with the thick smell of blood((.|\n)*)'))
async def clicking_arena(event): 
    status['arenas'] = int(re.search(r'Your fights: (\d+)', event.raw_text).group(1))
            

async def go_to_arena(event):
    # Clic the button of Arena
    await tools.noisy_sleep(8,5)
    buttons = await event.get_buttons()
    for bline in buttons:
        for button in bline:        
            if 'Arena' in button.button.text:
                await button.click()
    
    # Clic the button of Fast fight
    await tools.noisy_sleep(12,7)
    if status['arenas'] < 5:
        await client.send_message(config.CHAT_WARS, '▶️Fast fight')
        status['arenas'] += 1
    else:
        await client.send_message(config.CHAT_WARS, '/hero') #TODO: Change for a better '⬅️Back' 



async def go_to_quest(place, event):
    await tools.noisy_sleep(7,3)
    buttons = await event.get_buttons()
    for bline in buttons:
        for button in bline:        
            if place in button.button.text:
                await tools.noisy_sleep(5,1)
                await button.click()
                break


async def get_quest_place(text, tod):
    valid = ['Swamp', 'Valley', 'Forest']
    if settings['quest']['fire'] and '🔥' in text:
        quests = {'Swamp': 'Swamp', 'Mountain': 'Valley', 'Forest': 'Forest'}
        lines = text.split('\n')
        for line in lines:
            if len(line) and line[-1] == '🔥':
                place = line[1:].split()[0]
                for k in quests.keys():
                    if str(k) in place:
                        return quests[k]

    elif tod in settings['quest'].keys():
        place = settings['quest'][tod]
        if place == 'Random':
            return random.choice(valid)
        elif place in valid:
            return place
        else:  
            await tools.user_log(client, 'Unknown place: {} for the time: {}'.format(place, tod)) 
    else:
        await tools.user_log(client, 'Unknown time: {}'.format(tod)) 


@client.on(events.NewMessage(chats=config.CHAT_WARS, pattern='((.|\n)*)Many things can happen in the forest((.|\n)*)'))
async def clicking_quest(event): 
    if settings['arena']['status']:
        if status['time_of_day'] in ['morning', 'day', 'evening']:
            if status['arenas'] < 5 and status['gold'] > 5:
                if status['current_hp'] > settings['arena']['min_hp']:
                    await go_to_arena(event)
                    return

    if settings['quest']['status']:
        if status['current_stamina'] > 1:
            if status['current_hp'] > settings['quest']['min_hp']:
                place = await get_quest_place(text=event.message.text, tod=status['time_of_day'])
                if place:
                    await go_to_quest(place, event)
            


# This function needs to be scheduled often
async def do_something():
    await request_status_update()
    await tools.noisy_sleep(10,6)
    if status['state'] == '🛌Rest': # TODO: Add here ... or in shop
        if status['current_stamina'] >= 0 and status['current_hp'] > settings['quest']['min_hp']:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
            return True
        elif status['arenas'] < 5 and status['current_hp'] > settings['arena']['min_hp'] and status['gold'] > 5:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
            return True
        else:
            return False 


# Schedulers
async def planner(max_events, initial_sleep, first_time=False):
    if settings['arena']['status'] or settings['quest']['status'] or first_time:
        await tools.noisy_sleep(120, 60)
        await request_status_update()
        await tools.noisy_sleep(2, 1)
        total_events = 0
        if settings['arena']['status']:
            total_events += max(5 - status['arenas'], 5)
        if settings['quest']['status']:
            total_events += status['current_stamina']
        total_events = min(max_events, total_events)
        await tools.noisy_sleep(60*initial_sleep, 60*(initial_sleep-1))
        print('{} events scheduled for this period'.format(total_events))
        for e in range(total_events):
            keep_going = await do_something()
            if keep_going:
                await tools.noisy_sleep(60*8, 60*7)
            else:
                break
        # TODO: This is a great moment to open shop


#TODO: Check if there is something planed for the date_time before launching planner
@aiocron.crontab(cwc.morning())
async def morning_planner():
    await planner(12, 12)
    
@aiocron.crontab(cwc.day())
async def day_planner():
    await planner(12, 3)
    
@aiocron.crontab(cwc.evening())
async def evening_planner():
    await planner(12, 3)
    
@aiocron.crontab(cwc.night())
async def night_planner():
    await planner(10, 3)
   

#TODO: Do something with this:
 
    # if alt_class == '⚒️' and state == '🛌Rest' and quest == 0:
    #     await client.send_message(config.CHAT_WARS, '/myshop_open')            
         

#     #*********** config.DEPOSITED SUCCESSFULLY **************************

#     # @client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*config.DEPOSITed successfully.*'))
#     # async def config.DEPOSITs(event):
#     # 	print('config.DEPOSITing')
#     # 	time.sleep(2)
#     # 	await client.forward_messages(config.DEPOSIT, event.message)


#     #*********** Open shop **************************
# @aiocron.crontab(shop_crontab)
# async def openshop():
#     global alt_class
#     if alt_class == '⚒️':
#         await client.send_message(config.CHAT_WARS, '/myshop_open')
 
#     #*********** STAMINA RESTORED **************************

# @client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*Stamina restored*'))
# async def stamina_restored(event):
#     global stamina
#     stamina = 1
#     await client.send_message(config.CHAT_WARS, '🗺Quests')


async def init():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  
    await planner(cwc.get_possible_events(current_time), 1, first_time=True)

with client:
    client.start()
    client.loop.run_until_complete(init())
    client.run_until_disconnected() 
