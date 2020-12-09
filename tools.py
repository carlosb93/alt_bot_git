import config 
import asyncio
import random
from settings import all_settings

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
    'Esquire': '🐣'
}

castle_emojis = ['🥔', '🦅', '🦌', '🐉', '🦈', '🐺', '🌑']

async def noisy_sleep(t_max, t_min=0):
    rand_seconds = random.randrange(t_min, t_max)
    await asyncio.sleep(rand_seconds) 

async def user_log(client, text):
    await client.send_message(config.GROUP, text, parse_mode='html')

def bool2emoji(boolean):
    return '✔️' if boolean else '❌'

def special_validator(method, val):
    if method == "int":
        if type(val) is int:
            return True, None
        else:
            return False, ["Integer numbers"]
    if method == "order":
        if val in castle_emojis:
            return True, None
        elif val.startswith('/ga_def'):
            return True, None
        elif val.startswith('/ga_atk'):
            return True, None
        elif val == '/g_def':
            return True, None
        elif val.startswith('/g_atk'):
            return True, None
        else:
            return False, castle_emojis + ['/ga_def_xxx', '/ga_atk_xxx', '/g_def', '/g_atk TAG']


def validate(sett, subsett, val):
    values = all_settings[sett]["subsetts"][subsett]['validator']
    if type(values) is list:
        if val in values:
            return True, None
        else:
            return False, values
    elif type(values) is str:
        return special_validator(values, val)
    return False, ""

class ChatWarsCron():
    def __init__(self, server_utc):
        self.utc_delay = server_utc
        self.war_times = [7, 15, 23]

    def hours_before_war(self, h):
        assert  h >= 0
        return '00 {},{},{} * * *'.format(*((24 + i + self.utc_delay - h)%24 for i in self.war_times))    

    def minutes_before_war(self, m, h=0):
        assert m >= 0 and h >= 0
        if m >= 60:
            h += m // 60
            m =  m % 60
        m = 60 - m
        mstr = str(m)
        vals = [mstr.zfill(2-len(mstr))] + [(24 + i + self.utc_delay - (h + 1))%24 for i in self.war_times]
        return '{} {},{},{} * * *'.format(*vals)

    def hours_after_war(self, h):
        assert  h >= 0
        return '00 {},{},{} * * *'.format(*((24 + i + self.utc_delay - h)%24 for i in self.war_times))
    
    def minutes_after_war(self, m, h=0):
        assert m >= 0 and  h >= 0
        if m >= 60:
            h += m // 60
            m = m % 60
        mstr = str(m)
        vals = [mstr.zfill(2-len(mstr))] + [(24 + i + self.utc_delay + h)%24 for i in self.war_times]
        return '{} {},{},{} * * *'.format(*vals)

    def morning(self):
        return self.hours_after_war(0)

    def day(self):
        return self.hours_after_war(2)

    def evening(self):
        return self.hours_after_war(4)

    def night(self):
        return self.hours_after_war(6)
    
    def reset_time(self):
        return '30 {} * * *'.format(8 + self.utc_delay)
    
    def get_current_day_time(self, string):
        hour, minute, sec = (int(chunk) for chunk in string.split(':'))
        hour = (24 + hour - self.utc_delay + (8 - self.war_times[0])) % 24 
        cw_day_hour = hour % 8
        if cw_day_hour < 2:
            return 'morning'
        elif cw_day_hour < 4:
            return 'day'
        elif cw_day_hour < 6:
            return 'evening'
        else:
            return 'night'

    def get_current_day_third(self, string):
        hour, minute, sec = (int(chunk) for chunk in string.split(':'))
        hour = (24 + hour - self.utc_delay + (8 - self.war_times[0])) % 24
        cw_day_third = hour // 8 
        return cw_day_third + 1
       
    def get_possible_events(self, string):
        hour, minute, sec = (int(chunk) for chunk in string.split(':'))
        hour = (24 + hour - self.utc_delay + (8 - self.war_times[0])) % 24 
        cw_day_hour = hour % 8
        cw_time = cw_day_hour % 2

        minute += 60 * cw_time
        return max(int((120 - minute)/10) - 1, 0)
    
def find_emoji(text):
    words = text.split()
    for w in words:
        if w in emojis.keys():
            return emojis[w]
    return '👾'

def parse_monsters(text):
    lines = text.split('\n')
    link = lines[-1]
    description = lines[1:-2]
    levels = []
    for i, l in enumerate(description):
        if 'lvl.' in l:
            levels.append(int(l.split(' ')[-1][4:]))
            emoji = find_emoji(l)
            if l[0].isdigit():
                description[i] = description[i][:4] + emoji + description[i][4:]
            else:
                description[i] = emoji + description[i]
    link = '<a href ="https://t.me/share/url?url=' + link + '">' + link +'</a>'
    level = sum(levels)/len(levels)
    return {"link": link, "description": description, "level": level}

# c = ChatWarsCron(1)
# for i in range(24):
#     j = c.get_current_day_third('{}:10:30'.format(i))
#     print(i,j)

tiers = {
    't2Armor': ['Order Armor','Hunter Armor','Clarity Robe'],#2
    't3helmet': ['Crusader Helmet','Crusader Gauntlets','Royal Helmet','Ghost Helmet','Lion Helmet','Divine Circlet'],#2
    't4': ['Council Boots','Griffin Boots','Celestial Boots','Council Gauntlets','Council Shield','Griffin Gloves','Celestial Bracers' ,'Griffin Knife'],#2
    't4Helmet': ['Council Helmet','Griffin Helmet','Celestial Helmet','Poniard'],#3
    't5': ['Manticore','Overseer','Discarnate'],#4
}

def parse_lot(text):
    bet = ''
    quality = 'Common'
    precio = '0'
    autg = ''
    
    lines = text.split('\n')
    bet_link = lines[-1]
    for item in lines:
        if 'Quality: ' in item:
            quality = item.split('Quality: ')[1]
            
        if '🛡' in item or '⚔️' in item:
            geara = item.split(': ')[1]
            if '⚡️' in geara:
                gear = geara.split(' ')[1]
                gear2 = geara.split(' ')[2]
            else:
                gear = geara.split(' ')[0]
                gear2 = geara.split(' ')[1]
                
            autg = '{} {}'.format(gear,gear2)
            
            if autg in tiers['t2Armor']:
                precio = '2'
            if autg == 'Hunter dagger':
                precio = '1'
            if autg in tiers['t3helmet']:
                precio = '2'
            if autg in tiers['t4']:
                precio = '2'
            if autg in tiers['t4Helmet']:
                precio = '3'
            if autg in tiers['t5']:
                precio = '4'
                
    if precio == '0':
        bet = '{}'.format(bet_link)
    else:
        bet = '{}_{}'.format(bet_link,precio)
    return {"bet_link": bet, "quality": quality, "precio": precio, "gear": autg }