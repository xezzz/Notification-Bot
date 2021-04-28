import asyncio
import platform
import time
import json
import traceback
from tabulate import tabulate

import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot

from Services import http, mongo, handler


cogs = [
    "General",
    "Twitch",
    "Notifications",
    "Audio"
]

_ascii = r"""
  _      _                             _ 
 | |    (_)                           | |
 | |     ___   _____  ___ ___  _ __ __| |
 | |    | \ \ / / _ \/ __/ _ \| '__/ _` |
 | |____| |\ V /  __/ (_| (_) | | | (_| |
 |______|_| \_/ \___|\___\___/|_|  \__,_|
"""



class Livecord(AutoShardedBot):
    READY = False
    def __init__(self, *args, config, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.sent_notification = []
        self.loop.create_task(handler.handle_notifications(self))
        self.config = config
        self.color = 0x9146ff
        self.emotes = {
            "arrow": "<:arrow:836558825481568296>",
            "twitch": "<:twitch:836726608332193884>"
        }
        self.uptime = None
        self.twitch_http = http.TwitchHTTP(self)
        self.db = mongo.Mongo(self)
        #self.cluster_index = round(min(self.shard_ids) / 5)


    
    async def _run_event(self, coro, event_name, *args, **kwargs):
        while not self.READY and event_name != "on_ready":
            await asyncio.sleep(0.3)
        await super()._run_event(coro, event_name, *args, **kwargs)


    async def on_ready(self):
        if not self.READY:
            #await Twitch.init(self)
            #await API.get_bearer_token(self)
            for cog in cogs:
                try:
                    self.load_extension("Cogs.{}".format(cog))
                except Exception as e:
                    print("Failed to load cog {}: \n{}".format(cog, e))

            print(_ascii)
            table_rows = [
                ["discord.py", f"v{discord.__version__}"],
                ["python", f"v{platform.python_version()}"],
                ["system", f"{platform.system()} v{platform.version()}"],
                ["discord user", f"{self.user} (id: {self.user.id})"],
                ["guilds", len(self.guilds)],
                ["users", len(self.users)],
                ["shard ids", getattr(self, "shard_ids", "None")]
            ]
            print("\n" + tabulate(table_rows))
            self.uptime = time.time()
            await self.change_presence(activity=discord.Streaming(name="!!help", url="https://twitch.tv/ezzztv"))
            self.READY = True
        else:
            pass
        
      
    def run(self):
        try:
            self.remove_command("help")
            super().run(self.config['token'], reconnect=True)
        except Exception:
            e = traceback.format_exc()
            print("Error in run() method, aborting! \n{}".format(e))