import os
import sys
from datetime import datetime

from dotenv import load_dotenv
import discord
import requests
import json

load_dotenv()
notion_database_id = os.getenv('NOTION_DATABASE_ID')
notion_auth_token = os.getenv('NOTION_AUTH_TOKEN')
notion_version = os.getenv('NOTION_VERSION')
daily_goal = int(os.getenv('DAILY_GOAL'))
discord_login_token = os.getenv('DISCORD_LOGIN_TOKEN')
karuna_id = os.getenv('KARUNA_ID')
time_interval = int(os.getenv('TIME_INTERVAL'))

# Check Notion documents
headers = {'Authorization': 'Bearer ' + notion_auth_token, 'Notion-Version': notion_version, 'Content-Type': 'application/json'}
data = {'sorts':[{'timestamp': 'last_edited_time', 'direction': 'descending'}]}
response = requests.post('https://api.notion.com/v1/databases/' + notion_database_id + '/query',
                         headers=headers, data=json.dumps(data))
response = response.json()
last_edited_time = response['results'][daily_goal-1]['last_edited_time']
target_date = datetime.fromisoformat(last_edited_time[:-1])
curr_date = datetime.utcnow()
is_success = (curr_date-target_date).total_seconds() <= time_interval

# Get solved.ac problems
response = requests.get('https://solved.ac/api/v3/user/problem_stats?handle=jhwest2').json()
platinum_cnt = 0
solved_platinum_cnt = 0
total_platinum_exp = 0
solved_platinum_exp = 0
exp_table = [172714, 265117, 408280, 630792, 977727]
for i in range(16, 21):
    platinum_cnt += response[i]['total']
    solved_platinum_cnt += response[i]['solved']
    total_platinum_exp += response[i]['total'] * exp_table[i-16]
    solved_platinum_exp += response[i]['solved'] * exp_table[i-16]
ratio = 100 * solved_platinum_cnt / platinum_cnt
exp_ratio = 100 * solved_platinum_exp / total_platinum_exp

def progressBar(ratio, prefix = '', suffix = '', length = 100, fill = '#'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:0.2f}").format(ratio)
    filledLength = int(length * ratio / 100)
    bar = fill * filledLength + '-' * (length - filledLength)
    return '''```json
"{prefix}|{bar}| {percent}%{suffix}"```'''.format(prefix=prefix, bar=bar, percent=percent, suffix=suffix)

# Send Message
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    try:
        user = await client.fetch_user(karuna_id)
        title = "Today's goal achieved!" if is_success else "Today's goal failed..."
        description = curr_date.strftime('Date: %Y-%m-%d (%a)')
        color = 0x4BFD2F if is_success else 0xF81B1B
        footer = 'One more step on the great journey.' if is_success else 'Sometime we just need a break. But the robot did its job.'
        embed = discord.Embed(title=title, description=description, color=color)
        embed.add_field(name="Solved Details", value="{0} / {1} solved. {2:0.2f}% completed.".format(solved_platinum_cnt, platinum_cnt, ratio))
        embed.add_field(name="Exp Details", value="{0:,} / {1:,}\n{2}".format(solved_platinum_exp, total_platinum_exp, progressBar(exp_ratio, length=40)), inline=False)
        embed.set_footer(text=footer)
    
        await user.send(embed=embed)
        await client.close()
    except Exception as e:
        print(e)
        sys.exit(1)

client.run(discord_login_token)
