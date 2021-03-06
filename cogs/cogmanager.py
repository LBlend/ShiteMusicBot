# Discord Packages
from discord.ext import commands

import traceback

# Bot Utilities
from cogs.helpformatter import commandhelper
from cogs.utils.paginator import Scroller


class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.settings

    @commands.group(name='cogmanager', hidden=True)
    @commands.is_owner()
    async def _cogmanager(self, ctx):
        if ctx.invoked_subcommand is None:
            ctx.localizer.prefix = 'help'  # Ensure the bot looks for locales in the context of help, not cogmanager.
            paginator = commandhelper(ctx, ctx.command, ctx.invoker, include_subcmd=True)
            scroller = Scroller(ctx, paginator)
            await scroller.start_scrolling()

    @_cogmanager.command()
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(f'cogs.{module}')
            await ctx.send(f'{module} loaded')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @_cogmanager.command()
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        if module == "cogmanager":
            return await ctx.send('Unloading this cog is not allowed')
        try:
            self.bot.unload_extension(f'cogs.{module}')
            await ctx.send(f'{module} unloaded')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @_cogmanager.command(name='reload')
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(f'cogs.{module}')
            self.bot.load_extension(f'cogs.{module}')
            await ctx.send(f'{module} reloaded')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @_cogmanager.command(name='reloadall')
    @commands.is_owner()
    async def _relaod_all(self, ctx):
        """Reloads all extensions"""
        try:
            for extension in self.bot.extensions:
                if extension == 'cogs.cogmanager':
                    continue
                self.bot.unload_extension(f'{extension}')
                self.bot.load_extension(f'{extension}')
            await ctx.send('Extensions reloaded')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @_cogmanager.command(name='shutdown')
    @commands.is_owner()
    async def _shutdown(self, ctx):
        """Logs out and stops."""
        self.bot.lavalink.player_manager.players.clear()
        await self.bot.logout()


def setup(bot):
    bot.add_cog(CogManager(bot))
