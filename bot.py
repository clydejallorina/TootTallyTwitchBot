import requests as r
import asyncio
import os
from datetime import timedelta, datetime
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
    twitch = await Twitch(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    tc = await first(twitch.get_games(names=["Trombone Champ"]))
    stream_list = {}
    
    if tc == None:
        print("CANNOT FIND TROMBONE CHAMP'S ID")
        await twitch.close()
        return
    
    while True:
        streams = twitch.get_streams(first=100, game_id=tc.id)
        currently_seen = set()
        
        async for stream in streams:
            currently_seen.add(stream.user_login)
            if not stream.user_login in stream_list:
                stream_list[stream.user_login] = [None, stream]
            else:
                stream_list[stream.user_login][1] = stream
        
        for stream_user in currently_seen:
            if stream_list[stream_user][0] != None and stream_list[stream_user][0] > datetime.utcnow() - timedelta(minutes=5):
                # Skip a stream if we already found it, and displayed it at least 5 minutes ago
                # This should stop repeats from popping up
                stream_list[stream_user][0] = datetime.utcnow()
                continue
            stream = stream_list[stream_user][1]
            stream_list[stream_user][0] = datetime.utcnow()
            print(f"Found {stream.user_name} with {stream.viewer_count} viewers")
            post_stream_to_webhook(stream.user_name, f"https://twitch.tv/{stream.user_login}", stream.viewer_count)
        
        print(f"Processing done, checking again in 30 seconds!")
        await asyncio.sleep(30)
    
asyncio.run(twitch_stream_loop())
