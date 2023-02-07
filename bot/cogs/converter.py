import re
import asyncio
import os
import functools
import discord
from io import BytesIO
from discord.ext import commands, tasks, bridge


class Converter(commands.Cog, name="Converter"):
    """
    This cog contains commands that are used to convert EasyEDA footpritns to KiCAD ones.
    """
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.tmpdir = bot.tmpdir
        self.sep = asyncio.Semaphore(12)
        self.ll = asyncio.get_event_loop()
        self.RE_lcsc_url = re.compile(r'lcsc\.com/product-detail/.+?(?=_C)([^\n\r]*)\.html')
        self.RE_lcsc_part = re.compile(f'C\d+')

    def get_footprint(self, part: int):
        # get path to the script
        path = os.path.join(self.tmpdir, "EasyEDAFootprintScraper")
        print(f"Running {part} on {path}")
        # run the script
        # args: fetchComponent.py fetchlcsc --kicadLib test.pretty --force C558438
        os.system(f"cd {self.tmpdir}; python3 {path}/fetchComponent.py fetchlcsc --kicadLib C{part}.pretty --force C{part}")
        # archive the .pretty and .3dshapes folder
        os.system(f"cd {self.tmpdir}; zip -r C{part}.zip C{part}.pretty C{part}.3dshapes")
        # read the zip file as bytesIO
        with open(f"{self.tmpdir}/C{part}.zip", "rb") as f:
            b = BytesIO(f.read())
            # delete the zip file
            os.system(f"rm {self.tmpdir}/C{part}.zip")
            # delete the .pretty and .3dshapes folder
            os.system(f"rm -r {self.tmpdir}/C{part}.pretty {self.tmpdir}/C{part}.3dshapes")
            # return the bytesIO
            return b
        return None

    async def conv_worker(self, func, name):
        file = None
        async with self.sep:
            try:
                # for some reason it never runs the function if you use an actual executor, so this is a temporary workaround
                file = await asyncio.wait_for(self.ll.run_in_executor(executor=None, func=func), timeout=30.0)
                #b2, fn = await asyncio.wait_for(self.ll.run_in_executor(self.pp, func), timeout=30.0)
            except:
                return None
        return file

    @bridge.bridge_command(aliases=["lcsc", "LCSC", "easyeda", "conv", "footprint"])
    async def convert(self, ctx: bridge.BridgeContext, url: str):
        """Converts an EasyEDA footprint to a KiCAD one. You can provide a URL to LCSC or an LCSC part number."""
        print(f"Converting {url}")
        # acknowledge the command
        await ctx.defer()
        part = None
        # check if it is a url by trying to match it
        if self.RE_lcsc_url.search(url):
            # it is a url
            part = self.RE_lcsc_url.search(url).group(1)[1:]
        else:
            # it is not a url try the part number
            if self.RE_lcsc_part.match(url):
                part = re.match(self.RE_lcsc_part, url)[0]

        # if part is not None, we have a part number
        if part is not None:
            try:
                # strip the C from the part number and convert it to an int
                part = int(part[1:])
            except:
                # if we can't convert it to an int, it is not a valid part number
                await ctx.respond("Invalid link or part number")

            # get the footprint
            file = await self.conv_worker(functools.partial(self.get_footprint, part), f"C{part}")
            # if the file is not None, we have a valid part number
            if file is not None:
                # send the file
                await ctx.respond(file=discord.File(fp=file, filename=f"C{part}.zip"))

        else:
            # if part is None, we have an invalid url or part number
            await ctx.respond("Invalid link or part number")


def setup(bot):
    bot.add_cog(Converter(bot))