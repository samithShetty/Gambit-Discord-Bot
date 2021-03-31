import discord
from discord.ext import commands
import config
import berserk
import datetime
from time import perf_counter

session = berserk.TokenSession(config.API_KEYS['ADMIN_LICHESS_TOKEN'])
lichess = berserk.Client(session=session)


class LichessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['arena'])
    @commands.has_role("Officer")
    async def create_arena(self, ctx, name, clockTime, clockIncrement, minutes, startDate, startTime):
        # Date should be entered: Year/M/D H/M
        cString = startDate + " " + startTime + ":00"
        dTime = datetime.datetime.fromisoformat(cString)

        # Returns an epoch timestamp, when Lichess only accepts millisecond timestamps, hence the iTime * 1000 on l.26
        dTime = int(dTime.timestamp() * 1000)
        lichess.tournaments.create_arena(clockTime, clockIncrement, minutes, name=name, rated="false",
                                         start_date=dTime, teamId='niner-chess-club')


        test = lichess.tournaments.arenas_by_team('niner-chess-club')
        await ctx.send('Tournament created with name: ' + name)

    @commands.command(aliases=['swiss'])
    @commands.has_role("Officer")
    async def create_swiss(self, ctx, name, clockLimit: int, clockIncrement, nbRounds, startDate, startTime):
        cString = startDate + " " + startTime + ":00"
        dTime = datetime.datetime.fromisoformat(cString)
        dTime = int(dTime.timestamp())
        clockLimit_seconds = clockLimit * 60
        lichess.tournaments.create_swiss(clockLimit_seconds, clockIncrement, nbRounds, dTime * 1000, name=name,
                                         rated="false")
        await ctx.send('Tournament created with name: ' + name)

    @commands.command()
    async def listats(self, ctx, username):
        # Start timer
        start = perf_counter()

        # Make Loading Embed
        stat_embed = discord.Embed(
            description='Retrieving data from lichess.org',
            color=discord.Color.dark_blue()
        )
        stat_embed.set_author(name='lichess.org',
                              icon_url='https://lichess1.org/assets/_QubGrC/logo/lichess-favicon-256.png',
                              url=f'https://lichess.org/@/{username}')

        # Send temporary Loading message
        loading = await ctx.send(embed=stat_embed)

        # Retrieve User Profile
        profile = lichess.users.get_public_data(username)

        # Get case-sensitive username
        username = profile['username']

        # Get ratings
        gameModes = profile['perfs']

        # storm does not have a rating field so is removed
        gameModes.pop('storm', None)
        for gameMode in list(gameModes.keys()):
            # Change camelCase to Space Separated
            mode = ''
            for l in gameMode:
                if l.isupper():
                    mode += ' '
                mode += l
            mode = mode[0].upper() + mode[1:]

            # Generate field using proper mode name and corresponding rating
            rating = gameModes[gameMode]['rating']
            stat_embed.add_field(name=mode, value=rating)

        # Update embed
        stat_embed.title = f"Stats for {username}"
        response_time = perf_counter() - start
        stat_embed.set_footer(text="Response time: {time:.3} seconds".format(time=response_time))

        # Replace embed
        await loading.delete()
        await ctx.send(embed=stat_embed)
        print(
            "{outcome:<12} {site:>12} {user:^24}  Response time = {time:1.3}".format(outcome='Success', site='lichess',
                                                                                     user=username, time=response_time))


def setup(bot):
    bot.add_cog(LichessCog(bot))
    print("Lichess Cog successfully loaded")
