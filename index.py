import os
from datetime import datetime

from dotenv import load_dotenv
import discord
import requests

load_dotenv()
notion_database_id = os.getenv('NOTION_DATABASE_ID')
notion_auth_token = os.getenv('NOTION_AUTH_TOKEN')
notion_version = os.getenv('NOTION_VERSION')
daily_goal = int(os.getenv('DAILY_GOAL'))
discord_login_token = os.getenv('DISCORD_LOGIN_TOKEN')
karuna_id = os.getenv('KARUNA_ID')
time_interval = int(os.getenv('TIME_INTERVAL'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    user = await client.fetch_user(karuna_id)
    await user.send('Required amount of solutions ain\'t uploaded!')
    await client.close()

response = requests.post('https://api.notion.com/v1/databases/' + notion_database_id + '/query',
                         headers={'Authorization': 'Bearer ' + notion_auth_token,
                                  'Notion-Version': notion_version})
response = response.json()
last_edited_time = response['results'][daily_goal-1]['last_edited_time']
target_date = datetime.fromisoformat(last_edited_time[:-1])
curr_date = datetime.utcnow()
if ((curr_date-target_date).seconds >= time_interval):
    print('Sometime we just need a break.')
    client.run(discord_login_token)
    print('But the robot did its job.')
else:
    print('One more step on the great journey.')
    

