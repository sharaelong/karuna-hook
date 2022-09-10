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
for i in range(16, 21):
    platinum_cnt += response[i]['total']
    solved_platinum_cnt += response[i]['solved']
ratio = 100 * solved_platinum_cnt / platinum_cnt

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
        embed.add_field(name="Details", value="{0} / {1} solved. {2:0.2f}% completed.".format(solved_platinum_cnt, platinum_cnt, ratio))
        embed.set_footer(text=footer)
    
        await user.send(embed=embed)
        await client.close()
    except Exception as e:
        print(e)
        sys.exit(1)

client.run(discord_login_token)
