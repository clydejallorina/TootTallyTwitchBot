import requests as r
import asyncio
import os
from twitchAPI import Twitch
from twitchAPI.helper import first
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

def post_stream_to_webhook(streamer:str, stream_link:str, viewers:int) -> None:
    r.post(DISCORD_WEBHOOK_URL, data={"content": f"{streamer} is playing Trombone Champ to {viewers} viewer/s right now!\n{stream_link}"})

async def twitch_stream_loop():
    previously_seen = set()
    twitch = await Twitch(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    tc = await first(twitch.get_games(names=["Trombone Champ"]))
    if tc == None:
        print("CANNOT FIND TROMBONE CHAMP'S ID")
        await twitch.close()
        return
    while True:
        streams = twitch.get_streams(first=100, game_id=tc.id)
        stream_list = {}
        
        currently_seen = set()
        async for stream in streams:
            currently_seen.add(stream.user_login)
            stream_list[stream.user_login] = stream
        
        new_streams = list(currently_seen - previously_seen)
        for stream_user in new_streams:
            stream = stream_list[stream_user]
            post_stream_to_webhook(stream.user_name, f"https://twitch.tv/{stream.user_login}", stream.viewer_count)
        previously_seen = currently_seen
        
        await asyncio.sleep(30)
    
asyncio.run(twitch_stream_loop())
