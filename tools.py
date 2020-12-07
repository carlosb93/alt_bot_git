import config 
import asyncio
import random

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

settings_emoji = {
    'foray': '🗡',
    'report': '📜',
    'order': '⚜️',
    'arena': '📯',
    'quest': '🗺',
    'my_mobs': '👾',
    'my_ambush': '🐙',
}

castle_emojis = ['🥔', '🦅', '🦌', '🐉', '🦈', '🐺', '🌑']

async def noisy_sleep(t_max, t_min=0):
    rand_seconds = random.randrange(t_min, t_max)
    await asyncio.sleep(rand_seconds) 

async def user_log(client, text):
    await client.send_message(config.GROUP, text, parse_mode='html')

def bool2emoji(boolean):
    return '✔️' if boolean else '❌'


validator = {
    "foray": {
        "status": [True, False], 
        "pledge": [True, False]
        }, 
    "report": {
        "status": [True, False], 
        "send_to": "int"
        }, 
    "order": {"status": [True, False], 
        "target": "order", 
        "default": "order", 
        "source": ["botniato", "default"]
    }, 
    "arena": {
        "status": [True, False], 
        "min_hp": "int"
        }, 
    "quest": {
        "status": [True, False], 
        "morning": ["Random", "Swamp", "Forest", "Valley", "Foray"], 
        "day": ["Random", "Swamp", "Forest", "Valley", "Foray"], 
        "evening": ["Random", "Swamp", "Forest", "Valley", "Foray"], 
        "night": ["Random", "Swamp", "Forest", "Valley", "Foray"], 
        "min_hp": "int",
         "fire": [True, False]
         }, 
    "my_mobs": {
        "status": [True, False], 
        "send_to": "int"
        }, 
    "my_ambush": {
        "status": [True, False], 
        "send_to": "int"
        }
    }



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
    values = validator[sett][subsett]
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

    def get_possible_events(self, string):
        hour, minute, sec = (int(chunk) for chunk in string.split(':'))
        hour = (24 + hour - self.utc_delay + (8 - self.war_times[0])) % 24 
        cw_day_hour = hour % 8
        cw_time = cw_day_hour % 2

        minute += 60 * cw_time
        return max(int((120 - minute)/10) - 1, 0)