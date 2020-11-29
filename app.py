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

settings = {
    'foray': {
        'status': True
    }
}

############ SETTINGS ############

@client.on(events.NewMessage(chats=config.GROUP, pattern='/settings'))
async def status_all(event):
    res = '<b>User settings:</b>\n'
    for s in settings:
        res += "{}{}: {}\n".format(tools.emojis[s], s, tools.bool2emoji(settings[s]['status']))
        for k in settings[s].keys():
            if k != 'status':
                res += "  {}: {}\n".format(k, settings[s][k])
    await tools.user_log(client, res)


############ FORAY ############

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
    





#global variables
stamina = 0
arena = 0
quest = 0
to_quest = 0
daily_arenas = 0
alt_class = ''
castle = ''

# arena_crontab
arena_crontab = '40 7,15,23 * * *'
reset_arena_crontab= '00 5 * * *'

# quest_crontab
quest_crontab_m = '00 23,8,16 * * *'
quest_crontab_d = '00 2,10,18 * * *'
quest_crontab_a = '00 4,12,20 * * *'
quest_crontab_n = '00 5,13,21 * * *'
quest_daytime = 'night'
quest_place = 'Forest'
quest_duration = 5

# battles
battles_crontab = '56 22,6,14 * * *'
report_crontab = '9 23,7,15 * * *'
shop_crontab = '15 23,7,15 * * *'


# extra data
endurance = 0
endurance_max = 0
state = ''
time_to_battle = 0
quests = 0
delay = 0
mobs = ''
champ = 0
quest_status = 1


    #*********** config.DEPOSITED SUCCESSFULLY **************************

    # @client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*config.DEPOSITed successfully.*'))
    # async def config.DEPOSITs(event):
    # 	print('config.DEPOSITing')
    # 	time.sleep(2)
    # 	await client.forward_messages(config.DEPOSIT, event.message)

    #*********** FORBIDDEN MONSTERS **************************

@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*You met some hostile creatures*'))
async def monsters(event):
    global champ
    if 'ambush!' in event.message.message:
        logging.info('Fighting Champion')
        await client.forward_messages(config.CHAMPMOBS, event.message)
        time.sleep(2)
        await client.send_message(config.CHAMPMOBS, '🔥🔥🔥 help 🔥🔥🔥')
        
    elif 'Forbidden' in event.message.message:
        logging.info('Fighting Forbidden Monsters')
        await client.forward_messages(config.BOTMOBS, event.message)
  
@client.on(events.NewMessage(chats = config.CHAMPMOBS , incoming = True, pattern='.*You met some hostile creatures*'))
async def champion(event):
    global mobs, champ
    if champ == 1:
        if 'ambush!' in event.message.message:
            if mobs == event.message.message:
                pass
            else: 
                logging.info('Fighting Champion')
                mobs = event.message.message
                await client.forward_messages(config.CHAT_WARS, event.message)
                time.sleep(1)
                await client.send_message(config.CHAMPMOBS, 'ya entre no he marcado......')

    #*********** Battle Report **************************
@aiocron.crontab(report_crontab)
async def report():
    await client.send_message(config.CHAT_WARS, '/report')

    #*********** Open shop **************************
@aiocron.crontab(shop_crontab)
async def openshop():
    global alt_class
    if alt_class == '⚒️':
        await client.send_message(config.CHAT_WARS, '/myshop_open')
 
    #*********** STAMINA RESTORED **************************

@client.on(events.NewMessage(chats = config.CHAT_WARS , incoming = True, pattern='.*Stamina restored*'))
async def stamina_restored(event):
    global stamina
    stamina = 1
    await client.send_message(config.CHAT_WARS, '🗺Quests')

    #*********** ARENAS **************************
    
@aiocron.crontab(reset_arena_crontab)
async def reset_arenas():
    global daily_arenas
    daily_arenas = 0
    
@aiocron.crontab(arena_crontab)
async def arenas():
    global arena
    arena = 1
    await client.send_message(config.CHAT_WARS, '🏅Me')

    #*********** QUESTING **************************
    
    # Defining questing place

@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/place .*'))
async def q_place(event):
        
    logging.info('Adjust quest place')
    global quest_place, quest_duration
    qplace = event.message.message[7:]
    if qplace == 'Forest':
        quest_duration = 4
        quest_place = qplace
        await client.send_message(config.GROUP, 'Place adjusted to 🌲Forest')
    elif qplace == 'Swamp':
        quest_duration = 5
        quest_place = qplace
        await client.send_message(config.GROUP, 'Place adjusted to 🍄Swamp')
    elif qplace == 'Valley':
        quest_duration = 5
        quest_place = qplace
        await client.send_message(config.GROUP, 'Place adjusted to ⛰️Valley')
    else:
        quest_duration = 5
        quest_place = qplace
        await client.send_message(config.GROUP, 'Place adjusted to Random')
   
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/time .*'))
async def q_time(event):
    logging.info('Adjust quest time')
    global quest_daytime
    qtime = event.message.message[6:]
    if qtime == 'morning':
        quest_daytime = 'morning'
        await client.send_message(config.GROUP, '⏰Questing in the Morning')
    elif qtime == 'day':
        quest_daytime = 'day'
        await client.send_message(config.GROUP, '⏰Questing in Daytime')
    elif qtime == 'night':
        quest_daytime = 'night'
        await client.send_message(config.GROUP, '⏰Questing in Nightime')
    else:
        quest_daytime = 'afternoon'
        await client.send_message(config.GROUP, '⏰Questing in Afternoon')
  
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/champ_on'))
async def champion_on(event):
    logging.info('Adjust Champion')
    global champ
    signal = event.message.message
    if signal == '/champ_on':
        champ = 1
        await client.send_message(config.GROUP, '🔥Champion enabled')
  
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/champ_off'))
async def champion_off(event):
    logging.info('Adjust Champion')
    global champ
    signal = event.message.message
    if signal == '/champ_off':
        champ = 0
        await client.send_message(config.GROUP, '🔥Champion disabled')
  
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/quest_on'))
async def quest_on(event):
    logging.info('Adjust Quest')
    global quest_status
    signal = event.message.message
    if signal == '/quest_on':
        quest_status = 1
        await client.send_message(config.GROUP, '🔥Quest enabled')
  
@client.on(events.NewMessage(chats=[config.GROUP,config.MAIN_ID], pattern='/quest_off'))
async def quest_off(event):
    logging.info('Adjust Quest')
    global quest_status
    signal = event.message.message
    if signal == '/quest_off':
        quest_status = 0
        await client.send_message(config.GROUP, '🔥Quest disabled')
   
@client.on(events.NewMessage(chats=[config.GROUP], pattern='/help'))
async def help(event):
    msg = '\n'.join([
    '⚙️ Basic help',
    '--Destination for quest:--',
    '/place Forest|Swamp|Valley none to random',
    '--Time for questing:--',
    '/time night|morning|day ',
    '--Status of the player:--',
    '/status' 
    '--Champion :--',
    '/champ_on  /champ_off' 
    '--Quest Status:--',
    '/quest_on  /quest_off' 
    ])
    await client.send_message(config.GROUP, msg)
        
@aiocron.crontab(quest_crontab_n)
async def quest_funcn():
    global quest
    if quest_daytime == 'night':
        quest = 1
    else:
        quest = 0
    await client.send_message(config.CHAT_WARS, '🏅Me')
  
@aiocron.crontab(quest_crontab_m)
async def quest_funcm():
    global quest
    if quest_daytime == 'morning':
        quest = 1
    else:
        quest = 0
    await client.send_message(config.CHAT_WARS, '🏅Me')
  
@aiocron.crontab(quest_crontab_d)
async def quest_funcd():
    global quest
    if quest_daytime == 'day':
        quest = 1
    else:
        quest = 0
    await client.send_message(config.CHAT_WARS, '🏅Me')
  
@aiocron.crontab(quest_crontab_a)
async def quest_funcd():
    global quest
    if quest_daytime == 'afternoon':
        quest = 1
    else:
        quest = 0
    await client.send_message(config.CHAT_WARS, '🏅Me')
    
@client.on(events.NewMessage(chats=config.CHAT_WARS, incoming = True, pattern=r'Battle of the seven castles in|🌟Congratulations! New level!🌟'))
async def program_quest_func(event):
 
    global arena, daily_arenas, quest, to_quest, endurance, endurance_max, state, alt_class, castle
  
    endurance = int(re.search(r'Stamina: (\d+)', event.raw_text).group(1))
    endurance_max = int(re.search(r'Stamina: (\d+)/(\d+)', event.raw_text).group(2))
    state = re.search(r'State:\n(.*)', event.raw_text).group(1)
    lines = event.raw_text.split('\n')
    for i, line in enumerate(lines):
        if len(line):
            if line[0] in ['🥔', '🦅', '🦌', '🐉', '🦈', '🐺', '🌑']:
                castle = line[0]
                if ']' in line:
                    front, back = line.split(']')
                    guild = front.split('[')[-1]
                else:
                    back = line[1:]
                last_words = back.split(' ')
                alt_class = tools.emojis[last_words[-4]]
   
    if alt_class == '⚒️' and state == '🛌Rest' and quest == 0:
        await client.send_message(config.CHAT_WARS, '/myshop_open')            
                
    if quest == 1:
        logging.info('Programming quest')
        me = event.message.message.split('\n')

        stamina = '🔋Stamina: '
        stamina_match = [elem for elem in me if stamina in elem]
        current_stamina = int(stamina_match[0].split(' ')[1].split('/')[0])

        if quest_daytime == 'night':
            doable_quests = math.floor(105/(quest_duration+3))
            range_min, range_max = (quest_duration+2)*60 +20, (quest_duration+3)*60
        elif quest_daytime == 'morning':
            doable_quests = math.floor(105/(quest_duration+1))
            range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
        elif quest_daytime == 'day':
            doable_quests = math.floor(120/(quest_duration+1))
            range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
        else:
            doable_quests = math.floor(120/(quest_duration+1))
            range_min, range_max = quest_duration*60 +20, (quest_duration+1)*60
        if current_stamina >= doable_quests:
            cumulative_sec = 0
            for i in range(0,doable_quests):
                rand_seconds = random.randrange(range_min, range_max) #seconds
                time.sleep(1)
                await client.send_message(config.CHAT_WARS, '🗺Quests', schedule=timedelta(seconds=cumulative_sec))
                cumulative_sec += rand_seconds
                
                to_quest = doable_quests
                quest = 0
            
        elif doable_quests == 0:
            pass
            
        else:
            cumulative_sec = 0
            for i in range(0,current_stamina):
                rand_seconds = random.randrange(range_min, range_max) #seconds
                time.sleep(1)
                await client.send_message(config.CHAT_WARS, '🗺Quests', schedule=timedelta(seconds=cumulative_sec))
                cumulative_sec += rand_seconds
                
                to_quest = current_stamina
                quest = 0

    if arena == 1:
        logging.info('Programming arenas')
        arena = 0
        me = event.message.message.split('\n')

        gold = '💰'
        gold_match = [elem for elem in me if gold in elem]
        current_gold = int(gold_match[0].split(' ')[0][1:])

        doable_arenas = math.floor(current_gold/5)
        
        remaining_arenas = 5 - daily_arenas

        if remaining_arenas != 0:
            if doable_arenas >= remaining_arenas:
                daily_arenas += remaining_arenas
                cumulative_sec = 0
                for i in range(0,remaining_arenas):
                    rand_seconds = random.randrange(320, 360) #seconds
                    time.sleep(2)
                    await client.send_message(config.CHAT_WARS, '▶️Fast fight', schedule=timedelta(seconds=cumulative_sec))
                    cumulative_sec += rand_seconds
            
            elif doable_arenas == 0:
                pass
            
            else:
                cumulative_sec = 0
                daily_arenas += doable_arenas
                for i in range(0,doable_arenas):
                    rand_seconds = random.randrange(320, 360) #seconds
                    time.sleep(2)
                    await client.send_message(config.CHAT_WARS, '▶️Fast fight', schedule=timedelta(seconds=cumulative_sec))
                    cumulative_sec += rand_seconds


@client.on(events.NewMessage(chats=config.CHAT_WARS, pattern='((.|\n)*)Many things can happen in the forest((.|\n)*)'))
async def clicking_quest(event):
    global to_quest, stamina, quest_place, quest_status
 
    if to_quest > 0 and quest_status == 1:
        await client.send_message(config.GROUP, 'Doing quest #'+str(to_quest))
        to_quest = to_quest - 1
        buttons = await event.get_buttons()
        for bline in buttons:
            for button in bline:
                time.sleep(1)
                if quest_place == 'random':
                    quest_place = random.choice('Forest', 'Swamp', 'Valley')
                    if quest_place in button.button.text:
                        time.sleep(1)
                        await button.click()
                else:
                    if quest_place in button.button.text:
                        time.sleep(1)
                        await button.click()

    if stamina == 1 and quest_status == 1:
        await client.send_message(config.GROUP, 'Spending Stamina 🔋')
        stamina = 0
        buttons = await event.get_buttons()
        for bline in buttons:
            for button in bline:
                time.sleep(1)
                # print(button.button.text)
                if quest_place == 'random':
                    quest_place = random.choice('Forest', 'Swamp', 'Valley')
                    if quest_place in button.button.text:
                        time.sleep(1)
                        await button.click()
                else:
                    if quest_place in button.button.text:
                        time.sleep(1)
                        await button.click()



    #*********** BATTLES **************************
@aiocron.crontab(battles_crontab)
async def def_func():
    time.sleep(1)
    await client.send_message(config.CHAT_WARS, '🛡Defend')


    
    #*********** STATUS **************************
    
@client.on(events.NewMessage(chats=config.GROUP, pattern='/status'))
async def status_all(event):
    await client.send_message(config.CHAT_WARS, '🏅Me')
    now = datetime.now()
    if quest_status == 1:
        qstatus = 'enabled'
    else:
        qstatus = 'disabled'
  
    if champ == 1:
        cstatus = 'enabled'
    else:
        cstatus = 'disabled'
     
    current_time = now.strftime("%H:%M:%S")    
    msg =  '  --- STATUS ---\n\n🔋 Stamina: {} / {}\n State: {}\n'.format(endurance, endurance_max, state) 
    msg += '🏰Castle: {} Class: {}\n'.format(castle, alt_class) 
    msg += '⛰️Quest status: {} ⚔️Champion: {}\n'.format(qstatus, cstatus) 
    msg += '🔥 Quests to do: {}\n'.format(to_quest) 
    msg += '📍 Currently: {}\n'.format(quest_place) 
    msg += '⏰ During: {}\n'.format(quest_daytime) 
    msg += '📯 Arenas Done: {}\n'.format(daily_arenas) 
    msg += '--- server time: {}\n'.format(current_time)
    
    await client.send_message(config.GROUP, msg)
            
if __name__ == '__main__':
    client.start()
    client.run_until_disconnected() 

