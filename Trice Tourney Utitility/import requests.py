import requests
import os
from dotenv import load_dotenv
r=requests.get('https://api.github.com/repos/psf/requests')
print(r.json()["description"])
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)