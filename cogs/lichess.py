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
    async def create_arena(self, ctx, name, clock_time, clock_increment, minutes, start_date, start_time):
        """
        :note: Example command usage: #arena
        :param ctx: command
        :param string name: arena name
        :param int clock_time: amount of clock time
        :param clock_increment: clock increment
        :param minutes: how many minutes the arena will run
        :param start_date: starting date
        :param start_time: starting time
        :return: Discord message confirming tournament creation
        """
        # Date should be entered: Year/M/D H/M
        c_string = start_date + " " + start_time + ":00"
        d_time = datetime.datetime.fromisoformat(c_string)

        d_time = int(d_time.timestamp() * 1000)
        lichess.tournaments.create_arena(clock_time, clock_increment, minutes, name=name, rated="false",
                                         start_date=d_time, teamId='niner-chess-club')

        await ctx.send('Tournament created with name: ' + name)

    @commands.command(aliases=['swiss'])
    @commands.has_role("Officer")
    async def create_swiss(self, ctx, name, clock_limit: int, clock_increment, nb_rounds, start_date, start_time):
        """
        :note: Example command usage: #swiss March 10 0 5 2021-08-07 23:00
        :param ctx: command
        :param string name: swiss arena name
        :param int clock_limit: amount of clock time in minutes
        :param int clock_increment: clock increment
        :param int nb_rounds: number of rounds
        :param string start_date: date formatted year-mo-da
        :param string start_time: time formatted 00:00
        :return: Discord message confirming tournament creation
        """

        # Date should be entered: Year/M/D H/M
        c_string = start_date + " " + start_time + ":00"
        dtime = datetime.datetime.fromisoformat(c_string)

        dtime = int(dtime.timestamp())
        clocklimit_seconds = clock_limit * 60
        lichess.tournaments.create_swiss("niner-chess-club", clocklimit_seconds, clock_increment, nb_rounds,
                                         startsAt=dtime * 1000, name=name, rated="false")
        await ctx.send('Tournament created with name: ' + name)

    @commands.command()
    async def listats(self, ctx, username):
        """
        :param ctx: command
        :param string username: lichess username
        :return: embed Discord message
        """
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

    @commands.command(aliases=['standings'])
    async def arena_standings(self, ctx):
        """
        :note: embed field value can hold a maximum of 1024 characters
        :return: embed Discord message
        """
        # Start timer
        start = perf_counter()

        # Get tournament name
        recent_name = lichess.tournaments.arenas_by_team('niner-chess-club', 1)[0]['fullName']

        # Get tournament id
        recent_id = lichess.tournaments.arenas_by_team('niner-chess-club', 1)[0]['id']

        # Get tournament results information
        standings = lichess.tournaments.stream_results(recent_id)
        string_score = ''
        string_usernames = ''
        string_ranks = ''

        # Get rankings, usernames, and scores for all users
        for value in standings:
            string_usernames += f'{value["username"]}\n'
            string_ranks += f'{value["rank"]}\n'
            string_score += f'{value["score"]}\n'

        # Make Loading Embed
        stat_embed = discord.Embed(
            description='Retrieving data from lichess.org',
            color=discord.Color.dark_blue()
        )

        # Send loading message
        loading = await ctx.send(embed=stat_embed)

        stat_embed = discord.Embed(
            description='Retrieving data from lichess.org',
            color=discord.Color.dark_blue(),
            title=f'Standings for {recent_name}'
        )

        stat_embed.set_author(name='lichess.org',
                              icon_url='https://lichess1.org/assets/_QubGrC/logo/lichess-favicon-256.png',
                              url=f'https://lichess.org/tournament/{recent_id}')

        stat_embed.add_field(name='Rank', value=string_ranks, inline=True)
        stat_embed.add_field(name='Username', value=string_usernames, inline=True)
        stat_embed.add_field(name='Score', value=string_score, inline=True)

        # Get response time
        response_time = perf_counter() - start
        stat_embed.set_footer(text="Response time: {time:.3} seconds".format(time=response_time))

        # Replace embed
        await loading.delete()

        # Send final embed message
        await ctx.send(embed=stat_embed)


def setup(bot):
    bot.add_cog(LichessCog(bot))
    print("Lichess Cog successfully loaded")
