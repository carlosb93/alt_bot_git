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
from settings import all_settings
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
def save_settings():
    filepath = os.path.join(config.DATA_FOLDER, 'settings.json')
    with open(filepath, 'w') as f:
        json.dump(my_settings, f)

jsons = os.listdir(config.DATA_FOLDER)
# Load settings
if 'settings.json' in jsons:
    datafile = os.path.join(config.DATA_FOLDER, 'settings.json')         
    with open(datafile) as data_file:
        my_settings = json.load(data_file)  
else:
    my_settings = {}

for sett in all_settings.keys():
    if not sett in my_settings.keys():
        my_settings[sett] = {}
    for subsett in all_settings[sett]['subsetts'].keys():
        if not subsett in my_settings[sett].keys():
            my_settings[sett][subsett] = all_settings[sett]['subsetts'][subsett]['default']
save_settings()


# Load Status
datafile = os.path.join(config.DATA_FOLDER, 'status_default.json') 
with open(datafile) as data_file:
    status = json.load(data_file)  


############ Generator of cron strings ############ 
cwc = tools.ChatWarsCron(config.UTC_DELAY)

############ SHOP #############
async def open_shop(intensive=False):
    if intensive == True and not my_settings['my_shop']['intensive']:
        return

    if  status['state'] == '🛌Rest' and my_settings['my_shop']['status'] == True:
        await tools.noisy_sleep(10)
        await client.send_message(config.CHAT_WARS, '/myshop_open') 

# open shop after battle
@aiocron.crontab(cwc.minutes_after_war(15))
async def openshop():
    await open_shop(intensive=True)


############ STATUS ############
status['block'] = False

# Request an status update
async def request_status_update():
    try:
        await client.send_message(config.CHAT_WARS, '🏅Me')
    except ValueError:
        print('Stupid telethon has not found cw')

# Update the status parsing Me
@client.on(events.NewMessage(chats=config.CHAT_WARS, incoming = True, pattern=r'Battle of the seven castles in|🌟Congratulations! New level!🌟'))
async def update_status(event):
    status['current_stamina'] = int(re.search(r'Stamina: (\d+)', event.raw_text).group(1))
    status['max_stamina'] = int(re.search(r'Stamina: (\d+)/(\d+)', event.raw_text).group(2))
    status['current_hp'] = int(re.search(r'Hp: (\d+)', event.raw_text).group(1))
    status['max_hp'] = int(re.search(r'Hp: (\d+)/(\d+)', event.raw_text).group(2))
    status['current_mana'] = int(re.search(r'Mana: (\d+)', event.raw_text).group(1))
    status['max_mana'] = int(re.search(r'Mana: (\d+)/(\d+)', event.raw_text).group(2))
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
                
            if line[1:6] == 'Level':
                status['level'] = int(line[8:])
                
            if line[0].startswith('💰'):
                status['gold'] = int(line[1:].split()[0])
                
    if status['class'] in ['⚒️','⚗️','📦'] and my_settings['daily_craft']['status'] == True:           
        if status['daily_craft'] == 1:
            await daily_craft()
        elif status['current_mana'] == status['max_mana'] and my_settings['extra_craft']['status'] == True:
            await extra_craft()   
                        
    await open_shop(intensive=True)
                
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
👨‍🏫Class: {class} 🏅Level: {level}
💰 Money: {gold}
🔋 Stamina: {current_stamina}/{max_stamina}
❤️ Hp: {current_hp}/{max_hp}
💧 Mana: {current_mana}/{max_mana}
📯 Arenas: {arenas}/5
Block: {block}
Curently: {state}
In CW: {time_of_day}
--- server time: {current_time}'''.format(**status)
    
    await tools.user_log(client, msg)


@aiocron.crontab(cwc.reset_time())
async def reset_stuff():
    status['arenas'] = 0
    status['daily_craft'] = 1
    await tools.user_log(client, 'Counters restarted')


############ HELP ############
# Show current commands
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/help'))
async def help(event):
    res = '<b>Commands available:</b>\n\n'
    res += '/settings <i>Shows your current configuration</i>\n'
    res += '/status <i>Shows your current status</i>\n'
    res += '/settingsfull <i>Show a detailed configuration</i>\n'
    res += '/set <i>Allows you to modify your settings</i>\n'
    await tools.user_log(client, res)


############ SETTINGS ############
# Retreive current user settings
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/settings'))
async def get_settings(event):
    res = '<b>User settings:</b>\n\n'
    for s in my_settings:
        res += "{} {}{}\n".format(tools.bool2emoji(my_settings[s]['status']),  all_settings[s]['emoji'], s)
        if event.message.text == '/settingsfull':
            for k in my_settings[s].keys():
                if k != 'status':
                    res += "    {}: {}\n".format(k, my_settings[s][k])
    await tools.user_log(client, res)


def parse_value(string):
    if string == 'True' or string == 'on':
        return True
    elif string == 'False' or string == 'off':
        return False
    elif string == 'None':
        return None
    try : 
        string_integer = int(string)
        return string_integer
    except ValueError :
        pass
    return string


# Enable/disable the settings
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/set'))
async def update_settings(event):
    parsed_command = event.message.text.split()
    if parsed_command[0] == '/set':
        if len(parsed_command) == 3:
            sett = parsed_command[1]
            if sett in my_settings.keys():
                val = parse_value(parsed_command[2])
                status, values = tools.validate(sett, 'status', val)
                if status: 
                    my_settings[sett]['status'] = val
                    await tools.user_log(client, 'Setting updated\n/settingsfull')
                    return save_settings()
                else:
                    ret = '<b>Wrong Syntax</b>\n\n Command:\n/set {} <code>param</code>\n'.format(sett) 
                    ret += 'acepts only <code>param</code> within:\n✔️True\n✔️False\n✔️on\n✔️off' 
                    return await tools.user_log(client, ret)    
            else:
                return await tools.user_log(client, "Unknown setting {}\nType /settings to see all available ones".format(sett))           
            
        elif len(parsed_command) == 4:    
            sett = parsed_command[1]
            if sett in my_settings.keys():
                subsett = parsed_command[2]
                if subsett in my_settings[sett].keys():
                    val = parse_value(parsed_command[3])
                    status, values = tools.validate(sett, subsett, val)
                    if status:
                        my_settings[sett][subsett] = val
                        await tools.user_log(client, 'Setting updated\n/settingsfull')
                        return save_settings()
                    else:
                        ret = '<b>Wrong Syntax</b>\n\n Command:\n/set {} {} <code>param</code>\n'.format(sett, subsett)
                        ret += 'acepts only <code>param</code> within:\n'
                        for v in values:
                            ret += '✔️{}\n'.format(v)
                        return await tools.user_log(client, ret)
                else:
                    return await tools.user_log(client, "Unknown subsetting <code>{}</code> for setting {}\nType /settingsfull to see all available ones".format(subsett, sett))
            else:
                return await tools.user_log(client, "Unknown setting {}\nType /settings to see all available ones".format(sett))
            
        else:
            await tools.user_log(client, 'Wrong syntax. Try something like:\n<code>/set foray off</code>')    
            

        


############ FORAY ############
# Reacts to foray attempts
@client.on(events.NewMessage(chats=config.CHAT_WARS, 
    pattern='((.|\n)*)You were strolling around on your horse when you noticed((.|\n)*)'))
async def stop_foray(event):
    if my_settings['foray']['status']:
        status['block'] =  True
        buttons = await event.get_buttons()
        for bline in buttons:
            for button in bline:
                await tools.noisy_sleep(120)
                await button.click()
        await tools.user_log(client, '🗡Foray Intervene ')
        status['block'] =  False

# Pledge
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*After a successful act of violence, as a brave knight you are, you felt some guilt and decided to talk with your victims*'))
async def pledge(event):
    if my_settings['foray']['status'] and my_settings['foray']['pledge']:
        await tools.noisy_sleep(40, 10)
        await client.send_message(config.CHAT_WARS, '/pledge')

# Trader
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You defended villagers well. In exchange for your help, local trader offered you a deal*'))
async def trader(event):
    if my_settings['foray']['status'] and my_settings['foray']['trader']:
        res = tools.int2res(my_settings['foray']['trader'])
        cant = int(event.message.text.split('\n')[0].split()[-1][:-1])
        await tools.noisy_sleep(40, 10)
        await client.send_message(config.CHAT_WARS, '/sc {} {}'.format(res, cant))


############ BATTLES ############
# Gets order from botniato
@client.on(events.NewMessage(chats=config.BOTNIATO, pattern='.*Orders for next battle*'))
async def get_botniato_order(event):
    if my_settings['order']['status'] and my_settings['order']['source'] == 'botniato':
        my_settings['order']['target'] = '/ga_' + event.message.text.split('url?url=/ga_')[1].split()[0].split(')')[0]
        await tools.user_log(client, 'Order saved from botniato\n{}'.format(my_settings['order']['target']))
        return save_settings()

# Requests order from botniato
@client.on(events.NewMessage(chats=config.BOTNIATO, pattern='((.|\n)*)Check the ⚜️ Order button((.|\n)*)'))
async def ask_botniato_order(event):
    if my_settings['order']['status'] and my_settings['order']['source'] == 'botniato':
        await client.send_message(config.BOTNIATO, '⚜️ Order')
        await tools.user_log(client, 'Order requested to botniato')   

# TODO: Test this before moving to production (ORDER_ID undefined, all_settings validator has no attribute squad, etc)
# Requests order from squad
# @client.on(events.NewMessage(from_users=ORDER_ID))
# async def get_order(event):
#     if my_settings['order']['status'] and my_settings['order']['source'] == 'squad':
#         if '⚔️' in event.raw_text or  '😡' in event.raw_text:
#             words = event.raw_text.split()
#             for w in words:
#                 if w in tools.castle_emojis:
#                    my_settings['order']['target'] = tools.castle_emojis[w]
#         else:
#             my_settings['order']['target']  = '🛡Defend'
#         return save_settings()
        

async def order_setter():
    if my_settings['order']['status']:
        await tools.noisy_sleep(60)
        target = my_settings['order']['target']
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
            await client.send_message(config.CHAT_WARS, my_settings['order']['default'])   
        
        await tools.user_log(client, 'Order set!') 

# Sets the order automatically
@aiocron.crontab(cwc.minutes_before_war(4))
async def set_order():
    if my_settings['order']['status']:
        if not my_settings['order']['aiming']:
            await order_setter()
        else:
            status['block'] = False
            await tools.user_log(client, 'Unloking quest to aimers') 


@aiocron.crontab(cwc.minutes_before_war(59))
async def set_order():
    if my_settings['order']['status'] and my_settings['order']['aiming']:
        await order_setter()
        status['block'] = True
        await tools.user_log(client, 'Loking quest to aimers') 

############ REPORT ############
# Requests the report to cw
@aiocron.crontab(cwc.minutes_after_war(11))
async def report():
    if my_settings['report']['status']:
        await tools.noisy_sleep(60)
        await client.send_message(config.CHAT_WARS, '/report')
        await tools.user_log(client, 'Report requested') 

# Forward the report to the squad
@client.on(events.NewMessage(chats=config.CHAT_WARS, 
    pattern='((.|\n)*)Your result on the battlefield:((.|\n)*)'))
async def forward_report(event):
    if my_settings['report']['status']:
        if not 'Encounter' in event.message.text:
            await client.forward_messages(my_settings['report']['send_to'], event.message)      
            await tools.user_log(client, 'Report forwarded') 


############ HIDDEN LOCATIONS ############

@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You found hidden*'))
async def location(event):
    await client.forward_messages(config.BOTNIATO, event.message) 
    

############ FORBIDDEN MONSTERS ############
# Event Mobs
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You found a strange hideout*'))
async def event(event):
    await client.forward_messages(my_settings['my_mobs']['send_to'], event.message)     
    await tools.user_log(client, 'Found event') 
   

# My mobs
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You met some hostile creatures*'))
async def monsters(event):
    if 'ambush!' in event.message.message:
        if my_settings['my_ambush']['status']:
            logging.info('Found ambush')
            await client.forward_messages(my_settings['my_ambush']['send_to'], event.message)     
            await tools.user_log(client, 'Found ambush') 
    else:
        if my_settings['my_mobs']['status']:
            logging.info('Found Forbidden Monsters')
            await client.forward_messages(my_settings['my_mobs']['send_to'], event.message)   
            await tools.user_log(client, 'Found forbidden Monsters') 
  
# TODO: Fix this implementation
# Hunting other people mobs
@client.on(events.NewMessage(chats = [my_settings['get_mobs']['from_group'], my_settings['get_ambush']['from_group']], incoming = True, pattern='.*You met some hostile creatures*'))
async def mobs_from_group(event):
    # Check if is sleep time
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return

    if my_settings['get_mobs']['status'] or my_settings['get_ambush'] ['status']:
        # Update status before choosing
        lines = event.message.message.split('\n')
        link = lines[-1]
        if not status['mobsmsg'] == link:
            await request_status_update()
            parsed_mobs = tools.parse_monsters(event.raw_text)
            await tools.noisy_sleep(2,1)

            # Check if there is stamina or the player is not in other duties
            if status['current_stamina'] > 0 and (status['state'] in ['🛌Rest', '⚒At the shop', '⚗️At the shop']): 
                is_ambush = 'ambush!' in event.message.message                
                if is_ambush and my_settings['get_ambush']['status'] and status['current_hp'] > my_settings['arena']['min_hp']: #TODO: Update with a dedicated min_hp param for ambush
                    message = '👾Fighting ambush'
                elif not is_ambush and  my_settings['get_mobs']['status'] and status['current_hp'] > my_settings['arena']['min_hp']: #TODO: Update with a dedicated min_hp param for mobs
                    message = '👾Fighting mobs from group'
                else:
                    return
                
                valid = ['Me fui', 'toy', 'se fue', 'next', 'estoy', 'go', 'me fui', 'entré', 'voy pa dentro', '👀']

                min_level = parsed_mobs['level'] - 10
                max_level = parsed_mobs['level'] + 10
                
                
                if status['level'] in range(int(min_level), int(max_level)):
                    message += ' in range.'
                    
                    await tools.noisy_sleep(5)
                    status['mobsmsg'] = link
                    await tools.user_log(client, message)
                    await client.forward_messages(config.CHAT_WARS, event.message)
                    await tools.noisy_sleep(10)
                    msg = random.choice(valid)
                    await client.send_message(config.CHAMPMOBS, msg)
                # elif (parsed_mobs['level'] < status['level']) and is_ambush:
                #     message += ' of lower level.'
                else:
                    return

# Hunting other people mobs
@client.on(events.NewMessage(chats = config.BOTNIATO, incoming = True, pattern='((.|\n)*)needs your help((.|\n)*)'))
async def mobs_from_bot(event):
    if 'EVENT' in event.message.message:
        return
    else:
        # Check if is sleep time
        if my_settings['sleep']['status']:
            third = check_third_of_day()
            if third == my_settings['sleep']['third']:
                return
        
        if my_settings['get_mobs']['status'] or my_settings['get_ambush'] ['status']:
            # Update status before choosing
            lines = event.message.message.split('\n')
            link = lines[-1] 
            if not status['mobsmsg'] == link:
                await request_status_update()
                await tools.noisy_sleep(2,1)
        
                # Check if there is stamina or the player is not in other duties
                if status['current_stamina'] > 0 and (status['state'] == '🛌Rest' or status['state'] == '⚒At the shop'): 
                    is_ambush = 'ambush!' in event.message.message                
                    if is_ambush and my_settings['get_ambush']['status'] and status['current_hp'] > my_settings['arena']['min_hp']: #TODO: Update with a dedicated min_hp param for ambush
                        message = '👾Fighting ambush'
                    elif not is_ambush and  my_settings['get_mobs']['status'] and status['current_hp'] > my_settings['arena']['min_hp']: #TODO: Update with a dedicated min_hp param for mobs
                        message = '👾Fighting mobs from bot'
                    else:
                        return
                    status['mobsmsg'] = link
                    await tools.user_log(client, message)
                    await client.forward_messages(config.CHAT_WARS, event.message)
# Hunting event
@client.on(events.NewMessage(chats = config.BOTNIATO, incoming = True, pattern='((.|\n)*)You were chosen to event fight.((.|\n)*)'))
async def event_from_bot(event):
    message = '👾Fighting event mobs from bot'
    await tools.user_log(client, message)
    await client.forward_messages(config.CHAT_WARS, event.message)


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
        await tools.user_log(client, 'Doing arena {}'.format(status['arenas'])) 
    else:
        await client.send_message(config.CHAT_WARS, '⬅️Back')



async def go_to_quest(place, event):
    await tools.noisy_sleep(7,3)
    buttons = await event.get_buttons()
    for bline in buttons:
        for button in bline:        
            if place in button.button.text:
                await tools.noisy_sleep(5,1)
                await button.click()
                await tools.user_log(client, 'Going quest to {}'.format(place)) 
                break


async def get_quest_place(text, tod):
    valid = ['Swamp', 'Valley', 'Forest']
    if my_settings['quest']['fire'] and '🔥' in text:
        quests = {'Swamp': 'Swamp', 'Mountain': 'Valley', 'Forest': 'Forest'}
        lines = text.split('\n')
        for line in lines:
            if len(line) and line[-1] == '🔥':
                place = line[1:].split()[0]
                for k in quests.keys():
                    if str(k) in place:
                        return quests[k]

    elif tod in my_settings['quest'].keys():
        place = my_settings['quest'][tod]
        if place == 'Random':
            return random.choice(valid)
        elif place in valid or place == 'Foray':
            return place
        else:  
            await tools.user_log(client, 'Unknown place: {} for the time: {}'.format(place, tod)) 
    else:
        await tools.user_log(client, 'Unknown time: {}'.format(tod)) 


@client.on(events.NewMessage(chats=config.CHAT_WARS, pattern='((.|\n)*)Many things can happen in the forest((.|\n)*)'))
async def clicking_quest(event): 
    if my_settings['arena']['status']:
        if status['time_of_day'] in ['morning', 'day', 'evening']:
            if status['arenas'] < 5 and status['gold'] > 5:
                if status['current_hp'] > my_settings['arena']['min_hp']:
                    await go_to_arena(event)
                    return

    if my_settings['quest']['status']:
        if status['current_stamina'] > 0:
            if status['current_hp'] > my_settings['quest']['min_hp']:
                place = await get_quest_place(text=event.message.text, tod=status['time_of_day'])
                if place:
                    await go_to_quest(place, event)
                    
                    
############ AUCTION ############            
@client.on(events.NewMessage(chats = my_settings['auction']['from_group'] , incoming = True, pattern='.*Lot *'))
async def auction_check(event):
    if my_settings['auction']['status']:
        parsed_lot = tools.parse_lot(event.raw_text)
        if parsed_lot and parsed_lot['quality'] == 'Common':
            msg = parsed_lot['bet_link']
            await client.send_message(config.CHAT_WARS, msg)
            await tools.user_log(client, '{}\n{}'.format(parsed_lot['gear'], parsed_lot['bet_link']))  
        

# This function needs to be scheduled often
async def do_something():
    await request_status_update()
    await tools.noisy_sleep(10,6)
    if status['state'] in ['🛌Rest', '⚒At the shop', '⚗️At the shop']:
        if status['current_stamina'] > 1 and status['current_hp'] > my_settings['quest']['min_hp']:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
            return True
        elif status['arenas'] < 5 and status['current_hp'] > my_settings['arena']['min_hp'] and status['gold'] > 5:
            await client.send_message(config.CHAT_WARS, '🗺Quests')
            return True
        else:
            return False 


# Schedulers
async def planner(max_events, initial_sleep, first_time=False):
    if (my_settings['arena']['status'] and status['arenas'] != 5) or my_settings['quest']['status'] or first_time:
        await tools.noisy_sleep(60*initial_sleep, 60*(initial_sleep-1))
        await request_status_update()
        await tools.noisy_sleep(7, 5)
        total_events = 0
        if my_settings['arena']['status']:
            total_events += max(5 - status['arenas'], 5)
        if my_settings['quest']['status']:
            total_events += status['current_stamina']
        total_events = min(max_events, total_events)
        await tools.user_log(client, '{} events scheduled for this period'.format(total_events)) 
        for e in range(total_events):
            await tools.user_log(client, 'Doing event {}'.format(e + 1)) 
            if status['block'] ==  False:
                keep_going = await do_something()
                if keep_going:
                    await tools.noisy_sleep(60*8, 60*7)
                else:
                    await tools.user_log(client, 'Schedule cancelled') 
                    break
            else:
                await tools.user_log(client, 'Schedule waiting for foray to end') 

        await tools.user_log(client, 'Schedule finished') 
        await request_status_update()
        await tools.noisy_sleep(7,3)
        await open_shop()

def check_third_of_day():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return cwc.get_current_day_third(current_time)


@aiocron.crontab(cwc.morning())
async def morning_planner():
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return
    if my_settings['quest']['morning']:
        await planner(12, 12)
    
@aiocron.crontab(cwc.day())
async def day_planner():
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return
    if my_settings['quest']['day']:
        await planner(12, 3)
    
@aiocron.crontab(cwc.evening())
async def evening_planner():
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return
    if my_settings['quest']['evening']:
        await planner(12, 3)
    
@aiocron.crontab(cwc.night())
async def night_planner():
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return
    if my_settings['quest']['night']:
        await planner(12, 3)
   

########### STAMINA RESTORED ###########
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*Stamina restored*'))
async def stamina_restored(event):
    if my_settings['sleep']['status']:
        third = check_third_of_day()
        if third == my_settings['sleep']['third']:
            return    
    await planner(1, 3)
    
########### Daily Craft ###########
async def daily_craft():
    if status['state'] in ['🛌Rest', '⚒At the shop', '⚗️At the shop'] and status['max_mana'] != 0:
        if status['current_mana'] >= 100:
            to_craft = '/{}'.format(my_settings['daily_craft']['craft'])
            await tools.noisy_sleep(5,3)
            await client.send_message(config.CHAT_WARS, to_craft)
            
async def extra_craft():
    if status['state'] in ['🛌Rest', '⚒At the shop', '⚗️At the shop'] and status['max_mana'] != 0:
        to_craft = '/{}'.format(my_settings['extra_craft']['craft'])
        await tools.noisy_sleep(5,3)
        await client.send_message(config.CHAT_WARS, to_craft)
            
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*Not enough materials to craft *'))
async def buy_materials(event):
    amount= None
    code= None
    if my_settings['daily_craft']['status'] == True:
        if int(status['gold']) > int(my_settings['daily_craft']['gold']):
            lines = event.raw_text.split('\n')
            for line in lines:
                if ' x ' in line:
                    amount= int(line.split(' x ')[0])
                    resource = line.split(' x ')[1].strip()
                    if resource in tools.resource_list.keys():
                        code = tools.resource_list[resource] 
                    if code != None and amount != None:
                        await tools.noisy_sleep(5,3)    
                        await client.send_message(config.CHAT_WARS, '/wtb_{}_{}'.format(code,amount))

                
        
@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*Crafted: *'))
async def check_craft(event):
    if '\n' in event.raw_text:
        lines = event.raw_text.split('\n')
        for line in lines:
            if 'Earned:' in line:
                await tools.noisy_sleep(5,3)
                await daily_craft()
            else:
                status['daily_craft'] = 0
    else:
        status['daily_craft'] = 0


async def init():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  
    await planner(cwc.get_possible_events(current_time), 1, first_time=True)

with client:
    client.start()
    client.loop.run_until_complete(init())
    client.run_until_disconnected() 
