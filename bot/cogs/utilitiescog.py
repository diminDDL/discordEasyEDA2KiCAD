#  Copyright (c) 2019-2022 ThatRedKite and contributors
#  Copyright (c) 2022 diminDDL
#  License: MIT License

import discord
import aiohttp
import psutil
import si_prefix
from discord.ext import commands, bridge
from datetime import datetime
from bot.backend.util import EmbedColors as ec


async def _contributorjson(session: aiohttp.ClientSession):
    headers = {"User-Agent": "Converter/1.0", "content-type": "text/html"}
    async with session.get(
            f"https://github.com/diminDDL/discordEasyEDA2KiCAD/contributors?q=contributions&order=desc",
            headers=headers) as r:
        if r.status == 200:
            jsonstr = await r.json()
        else:
            return None
    return jsonstr


class UtilityCommands(commands.Cog, name="utility commands"):
    """
    Utility commands for the bot. These commands are basically informational commands.
    """
    def __init__(self, bot: commands.Bot):
        self.dirname = bot.dirname
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @bridge.bridge_command(pass_context=True, aliases=["uptime", "load"])
    async def status(self, ctx):
        """
        Displays the status of the bot.
        """
        process = psutil.Process(self.bot.pid)
        mem = process.memory_info()[0]

        cpu = psutil.cpu_percent(interval=None)
        ping = round(self.bot.latency * 1000, 1)
        uptime = str(datetime.now() - self.bot.starttime).split(".")[0]
        total_users = sum([users.member_count for users in self.bot.guilds])
        guilds = len(self.bot.guilds)

        embed = discord.Embed()
        embed.add_field(name="System status",
                        value=f"""RAM usage: **{si_prefix.si_format(mem)}B**
                                CPU usage: **{cpu} %**
                                uptime: **{uptime}**
                                ping: **{ping} ms**""")

        embed.add_field(name="Bot stats",
                        value=f"""guilds: **{guilds}**
                                extensions loaded: **{len(self.bot.extensions)}**
                                total users: **{total_users}**
                                bot version: **{self.bot.version}**
                                """, inline=False)
        try:
            embed.set_thumbnail(url=str(self.bot.user.avatar.url))
        except:
            pass

        if not self.bot.debugmode:
            if cpu >= 90.0:
                embed.color = 0xbb1e10
                embed.set_footer(text="Warning: CPU usage over 90%")
            else:
                embed.color = 0x00b51a
        else:
            embed.color = 0x47243c
        await ctx.respond(embed=embed)

    @bridge.bridge_command()
    async def invite(self, ctx):
        """This sends you an invite for the bot if you want to add it to one of your servers."""
        await ctx.author.send(
            f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=274878220352&scope=bot%20applications.commands"
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @bridge.bridge_command(pass_context=True)
    async def about(self, ctx):
        """
        This command is here to show you what the bot is made of.
        """
        embed = discord.Embed(
            color=ec.blood_orange,
            title="About EasyEDA2KiCAD",
            description="""
                This bot is made to convert EasyEDA PCB files to KiCAD PCB files. Just run the `convert` command and provide an LCSC link or part numeber to get it converted.
                The source code is available on [GitHub](https://github.com/diminDDL/discordEasyEDA2KiCAD/).
                This is a fork of the another bot made by ThatRedKite available [here](https://github.com/ThatRedKite/thatkitebot).
                """
        )
        try:
            embed.set_thumbnail(url=str(self.bot.user.avatar.url))
        except:
            pass
        # dictionary for discord username lookup from github username
        # format: "githubusername":"discordID"
        authordict = {
            "ThatRedKite":"<@249056455552925697>",
            "diminDDL":"<@312591385624576001>", 
            "Cuprum77":"<@323502550340861963>",
            "laserpup":"<@357258808105500674>",
            "woo200":"<@881362093427814440>"
        }
        try:
            jsonData = await _contributorjson(self.bot.aiohttp_session)
            # get a list of "login" field values from json string variable jsonData
            authorlist = [x["login"] for x in jsonData]
            # if a username contains [bot] remove it from the list
            authorlist = [x for x in authorlist if not x.lower().__contains__("bot")]
            # need only first 5 contributors in authorlist
            authorlist = authorlist[:5]
            embedStr = ""
            for i in authorlist:
                if i in authordict:
                    embedStr += f"{authordict[i]}\n"
                else:
                    embedStr += f"{i}\n"
            embedStr += "and other [contributors](https://github.com/diminDDL/discordEasyEDA2KiCAD/graphs/contributors)"    
            embed.add_field(
                name="Authors",
                value=embedStr
            )
        except:
            pass
        embed.set_footer(text="EasyEDA2KiCAD v{}".format(self.bot.version))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(UtilityCommands(bot))
