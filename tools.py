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
    'my_mobs': '👾',
    'my_ambush': '🐙',
}

castle_emojis = ['🥔', '🦅', '🦌', '🐉', '🦈', '🐺', '🌑']

async def noisy_sleep(t_max, t_min=0):
    rand_seconds = random.randrange(0, t_max)
    await asyncio.sleep(rand_seconds) 

async def user_log(client, text):
    await client.send_message(config.GROUP, text, parse_mode='html')

def bool2emoji(boolean):
    return '✔️' if boolean else '❌'


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