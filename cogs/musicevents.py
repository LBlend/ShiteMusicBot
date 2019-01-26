"""
A cog to separate events from regular music commands
"""

import asyncio

import discord
import lavalink
from discord.ext import commands
import time

from .utils.mixplayer import MixPlayer
from lavalink.events import *

from lavasettings import *


class MusicEvents:
    def __init__(self, bot):
        self.bot = bot
        # TODO: maybe only load when Music loads
        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id, player=MixPlayer)
            bot.lavalink.add_node(host, port, password, region, 'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        bot.lavalink.add_event_hook(self.track_hook)

    def __unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def track_hook(self, event):
        if isinstance(event, TrackEndEvent):
            pass  # Send track ended message to channel.
        if isinstance(event, TrackStartEvent):
            pass
        if isinstance(event, QueueEndEvent):
            channel = self.bot.get_channel(event.player.fetch('channel'))
            await self.check_leave_voice(channel.guild)
        if isinstance(event, PlayerUpdateEvent):
            pass
        if isinstance(event, NodeDisconnectedEvent):
            pass
        if isinstance(event, NodeConnectedEvent):
            pass
        if isinstance(event, NodeChangedEvent):
            pass

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            player = self.bot.lavalink.players.get(member.guild.id)
            if player is not None:
                player.update_listeners(member, after)
                await self.check_leave_voice(member.guild)

    async def check_leave_voice(self, guild):
        """ Checks if the bot should leave the voice channel """
        # TODO, disconnect timer?
        player = self.bot.lavalink.players.get(guild.id)
        if len(player.listeners) == 0 and player.is_connected:
            if player.queue.empty and player.current is None:
                await player.stop()
                await self.connect_to(guild.id, None)


def setup(bot):
    bot.add_cog(MusicEvents(bot))