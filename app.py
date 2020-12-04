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


############ Load Settings ############ 
settings = {
    'foray': {
        'status': True
    },
    'report': {
        'status': True,
        'send_to': 1209077540
    },
    'order': {
        'status': True,
        'target': '/g_def',
        'default': '/g_def',
        'source': 'botniato'
    },
    'arena': {
        'status': True,
        'min_hp': 650
    },
    'quest': {
        'status': True,
        'morning': 'Swamp',
        'day': 'Forest',
        'evening': 'Valley',
        'night': 'Random',
        'min_hp': 350,
        'fire': True
    },
    'my_mobs': {
        'status': True,
        'send_to': 1209077540
    },
    'my_ambush': {
        'status': True,
        'send_to': config.CHAMPMOBS
    }
}



############ Generator of cron strings ############ 
cwc = tools.ChatWarsCron(config.UTC_DELAY)


############ STATUS ############
# Empty status
status = {
    'castle': '',
    'current_stamina': 0,
    'max_stamina': 0,
    'class': '',
    'guild': '',
    'state': '',
    'current_hp': 0,
    'max_hp': 0, 
    'arenas': 0,
    'gold': 0,
    'current_time': '00:00:00',
    'time_of_day': 'morning'

}

# Request an status update
async def request_status_update():
    await client.send_message(config.CHAT_WARS, '🏅Me')

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
    await tools.noisy_sleep(5,2)
    buttons = await event.get_buttons()
    for bline in buttons:
        for button in bline:        
            if 'Arena' in button.button.text:
                await button.click()
    
    # Clic the button of Fast fight
    await tools.noisy_sleep(5,2)
    if status['arenas'] < 5:
        await client.send_message(config.CHAT_WARS, '▶️Fast fight')
        status['arenas'] += 1
    else:
        await client.send_message(config.CHAT_WARS, '⬅️Back')



async def go_to_quest(place, event):
    await tools.noisy_sleep(5,1)
    buttons = await event.get_buttons()
    for bline in buttons:
        for button in bline:        
            if place in button.button.text:
                time.sleep(1)
                await button.click()
                break


async def get_quest_place(text, tod):
    valid = ['Swamp', 'Valley', 'Forest']
    if settings['quest']['fire'] and '🔥' in text:
        quests = {'Swamp': 'Swamp', 'Mountain': 'Valley', 'Forest': 'Forest'}
        lines = text.split('\n')
        for line in lines:
            if line[-1] == '🔥':
                place = line[1:].split()[0]
                return quests[place]

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
    print('I am doing something')
    await request_status_update()
    await tools.noisy_sleep(5,2)
    if status['state'] == '🛌Rest': # TODO: Add here ... or in shop
        if status['current_stamina'] > 0 and status['current_hp'] > settings['quest']['min_hp']:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
        elif status['arenas'] < 5 and status['current_hp'] > settings['arena']['min_hp'] and status['gold'] > 5:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
        else:
            pass #TODO: Stop scheduling upcoming events by some time and maybe shop_open


# Schedulers
async def planner(max_events, initial_sleep):
    await request_status_update()
    await tools.noisy_sleep(3,2)
    total_events = 5 - status['arenas'] + status['current_stamina']
    total_events = max(max_events, total_events)
    await tools.noisy_sleep(60*(initial_sleep+1), 60*initial_sleep)
    print('{} events schedulers for this period'.format(total_events))
    for e in range(total_events):
        await do_something()
        await tools.noisy_sleep(60*8, 60*7)



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
    
# #global variables
# stamina = 0
# arena = 0
# quest = 0
# to_quest = 0
# daily_arenas = 0
# alt_class = ''
# castle = ''

# # arena_crontab
# arena_crontab = '40 7,15,23 * * *'
# reset_arena_crontab= '00 5 * * *'

# # quest_crontab
# quest_crontab_m = '00 23,8,16 * * *'
# quest_crontab_d = '00 2,10,18 * * *'
# quest_crontab_a = '00 4,12,20 * * *'
# quest_crontab_n = '00 5,13,21 * * *'
# quest_daytime = 'night'
# quest_place = 'Forest'
# quest_duration = 5

# # battles
# battles_crontab = '56 22,6,14 * * *'
# report_crontab = '9 23,7,15 * * *'
# shop_crontab = '15 23,7,15 * * *'


# # extra data
# endurance = 0
# endurance_max = 0
# state = ''
# time_to_battle = 0
# quests = 0
# delay = 0
# mobs = ''
# champ = 0
# quest_status = 1


   
    # if alt_class == '⚒️' and state == '🛌Rest' and quest == 0:
    #     await client.send_message(config.CHAT_WARS, '/myshop_open')            
                
    # if quest == 1:
    #     logging.info('Programming quest')
    #     me = event.message.message.split('\n')

    #     stamina = '🔋Stamina: '
    #     stamina_match = [elem for elem in me if stamina in elem]
    #     current_stamina = int(stamina_match[0].split(' ')[1].split('/')[0])

    #     if quest_daytime == 'night':
    #         doable_quests = math.floor(105/(quest_duration+3))
    #         range_min, range_max = (quest_duration+2)*60 +20, (quest_duration+3)*60
    #     elif quest_daytime == 'morning':
    #         doable_quests = math.floor(105/(quest_duration+1))
    #         range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
    #     elif quest_daytime == 'day':
    #         doable_quests = math.floor(120/(quest_duration+1))
    #         range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
    #     else:
    #         doable_quests = math.floor(120/(quest_duration+1))
    #         range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
    #     if current_stamina >= doable_quests:
    #         cumulative_sec = 0
    #         for i in range(0,doable_quests):
    #             rand_seconds = random.randrange(range_min, range_max) #seconds
    #             time.sleep(1)
    #             await client.send_message(config.CHAT_WARS, '🗺Quests', schedule=timedelta(seconds=cumulative_sec))
    #             cumulative_sec += rand_seconds
                
    #             to_quest = doable_quests
    #             quest = 0
            
    #     elif doable_quests == 0:
    #         pass
            
    #     else:
    #         cumulative_sec = 0
    #         for i in range(0,current_stamina):
    #             rand_seconds = random.randrange(range_min, range_max) #seconds
    #             time.sleep(1)
    #             await client.send_message(config.CHAT_WARS, '🗺Quests', schedule=timedelta(seconds=cumulative_sec))
    #             cumulative_sec += rand_seconds
                
    #             to_quest = current_stamina
    #             quest = 0

    # if arena == 1:
    #     logging.info('Programming arenas')
    #     arena = 0
    #     me = event.message.message.split('\n')

    #     gold = '💰'
    #     gold_match = [elem for elem in me if gold in elem]
    #     current_gold = int(gold_match[0].split(' ')[0][1:])

    #     doable_arenas = math.floor(current_gold/5)
        
    #     remaining_arenas = 5 - daily_arenas

    #     if remaining_arenas != 0:
    #         if doable_arenas >= remaining_arenas:
    #             daily_arenas += remaining_arenas
    #             cumulative_sec = 0
    #             for i in range(0,remaining_arenas):
    #                 rand_seconds = random.randrange(320, 360) #seconds
    #                 time.sleep(2)
    #                 await client.send_message(config.CHAT_WARS, '▶️Fast fight', schedule=timedelta(seconds=cumulative_sec))
    #                 cumulative_sec += rand_seconds
            
    #         elif doable_arenas == 0:
    #             pass
            
    #         else:
    #             cumulative_sec = 0
    #             daily_arenas += doable_arenas
    #             for i in range(0,doable_arenas):
    #                 rand_seconds = random.randrange(320, 360) #seconds
    #                 time.sleep(2)
    #                 await client.send_message(config.CHAT_WARS, '▶️Fast fight', schedule=timedelta(seconds=cumulative_sec))
    #                 cumulative_sec += rand_seconds



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


    
# @aiocron.crontab(arena_crontab)
# async def arenas():
#     global arena
#     arena = 1
#     await client.send_message(config.CHAT_WARS, '🏅Me')

#     #*********** QUESTING **************************
    
#     # Defining questing place

# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/place .*'))
# async def q_place(event):
        
#     logging.info('Adjust quest place')
#     global quest_place, quest_duration
#     qplace = event.message.message[7:]
#     if qplace == 'Forest':
#         quest_duration = 4
#         quest_place = qplace
#         await client.send_message(config.GROUP, 'Place adjusted to 🌲Forest')
#     elif qplace == 'Swamp':
#         quest_duration = 5
#         quest_place = qplace
#         await client.send_message(config.GROUP, 'Place adjusted to 🍄Swamp')
#     elif qplace == 'Valley':
#         quest_duration = 5
#         quest_place = qplace
#         await client.send_message(config.GROUP, 'Place adjusted to ⛰️Valley')
#     else:
#         quest_duration = 5
#         quest_place = qplace
#         await client.send_message(config.GROUP, 'Place adjusted to Random')
   
# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/time .*'))
# async def q_time(event):
#     logging.info('Adjust quest time')
#     global quest_daytime
#     qtime = event.message.message[6:]
#     if qtime == 'morning':
#         quest_daytime = 'morning'
#         await client.send_message(config.GROUP, '⏰Questing in the Morning')
#     elif qtime == 'day':
#         quest_daytime = 'day'
#         await client.send_message(config.GROUP, '⏰Questing in Daytime')
#     elif qtime == 'night':
#         quest_daytime = 'night'
#         await client.send_message(config.GROUP, '⏰Questing in Nightime')
#     else:
#         quest_daytime = 'afternoon'
#         await client.send_message(config.GROUP, '⏰Questing in Afternoon')
  
# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/champ_on'))
# async def champion_on(event):
#     logging.info('Adjust Champion')
#     global champ
#     signal = event.message.message
#     if signal == '/champ_on':
#         champ = 1
#         await client.send_message(config.GROUP, '🔥Champion enabled')
  
# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/champ_off'))
# async def champion_off(event):
#     logging.info('Adjust Champion')
#     global champ
#     signal = event.message.message
#     if signal == '/champ_off':
#         champ = 0
#         await client.send_message(config.GROUP, '🔥Champion disabled')
  
# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/quest_on'))
# async def quest_on(event):
#     logging.info('Adjust Quest')
#     global quest_status
#     signal = event.message.message
#     if signal == '/quest_on':
#         quest_status = 1
#         await client.send_message(config.GROUP, '🔥Quest enabled')
  
# @client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/quest_off'))
# async def quest_off(event):
#     logging.info('Adjust Quest')
#     global quest_status
#     signal = event.message.message
#     if signal == '/quest_off':
#         quest_status = 0
#         await client.send_message(config.GROUP, '🔥Quest disabled')
   
# @client.on(events.NewMessage(chats=[config.GROUP], pattern='/help'))
# async def help(event):
#     msg = '\n'.join([
#     '⚙️ Basic help',
#     '--Destination for quest:--',
#     '/place Forest|Swamp|Valley none to random',
#     '--Time for questing:--',
#     '/time night|morning|day ',
#     '--Status of the player:--',
#     '/status' 
#     '--Champion :--',
#     '/champ_on  /champ_off' 
#     '--Quest Status:--',
#     '/quest_on  /quest_off' 
#     ])
#     await client.send_message(config.GROUP, msg)
        
# @aiocron.crontab(quest_crontab_n)
# async def quest_funcn():
#     global quest
#     if quest_daytime == 'night':
#         quest = 1
#     else:
#         quest = 0
#     await client.send_message(config.CHAT_WARS, '🏅Me')
  
# @aiocron.crontab(quest_crontab_m)
# async def quest_funcm():
#     global quest
#     if quest_daytime == 'morning':
#         quest = 1
#     else:
#         quest = 0
#     await client.send_message(config.CHAT_WARS, '🏅Me')
  
# @aiocron.crontab(quest_crontab_d)
# async def quest_funcd():
#     global quest
#     if quest_daytime == 'day':
#         quest = 1
#     else:
#         quest = 0
#     await client.send_message(config.CHAT_WARS, '🏅Me')
  
# @aiocron.crontab(quest_crontab_a)
# async def quest_funca():
#     global quest
#     if quest_daytime == 'afternoon':
#         quest = 1
#     else:
#         quest = 0
#     await client.send_message(config.CHAT_WARS, '🏅Me')
    


# @client.on(events.NewMessage(chats=config.CHAT_WARS, pattern='((.|\n)*)Many things can happen in the forest((.|\n)*)'))
# async def clicking_quest(event):
#     global to_quest, stamina, quest_place, quest_status
 
#     if to_quest > 0 and quest_status == 1:
#         await client.send_message(config.GROUP, 'Doing quest #'+str(to_quest))
#         to_quest = to_quest - 1
#         buttons = await event.get_buttons()
#         for bline in buttons:
#             for button in bline:
#                 time.sleep(1)
#                 if quest_place == 'random':
#                     quest_place = random.choice('Forest', 'Swamp', 'Valley')
#                     if quest_place in button.button.text:
#                         time.sleep(1)
#                         await button.click()
#                 else:
#                     if quest_place in button.button.text:
#                         time.sleep(1)
#                         await button.click()

#     if stamina == 1 and quest_status == 1:
#         await client.send_message(config.GROUP, 'Spending Stamina 🔋')
#         stamina = 0
#         buttons = await event.get_buttons()
#         for bline in buttons:
#             for button in bline:
#                 time.sleep(1)
#                 # print(button.button.text)
#                 if quest_place == 'random':
#                     quest_place = random.choice('Forest', 'Swamp', 'Valley')
#                     if quest_place in button.button.text:
#                         time.sleep(1)
#                         await button.click()
#                 else:
#                     if quest_place in button.button.text:
#                         time.sleep(1)
#                         await button.click()


    



async def init():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  
    await planner(cwc.get_possible_events(current_time), 3)

with client:
    client.start()
    client.loop.run_until_complete(init())
    client.run_until_disconnected() 

# if __name__ == '__main__':
#     client.start()
#     client.run_until_disconnected() 

