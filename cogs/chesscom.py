import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import perf_counter

#Icon Emoji Setup
ICONS = { #Icons for chess.com ratings section
    'Bullet' : '<:Bullet:785227771914747904>',
    'Blitz' : '<:Blitz:785223179723079690>',
    'Puzzle Rush' : '<:PuzzleRush:785229768051654668>',
    'Puzzles' : '<:Puzzles:785229768131608597>',
    'Rapid' : '<:Rapid:785229768354168873>',
    'Daily' : '<:Daily:785229768617492501>',
    'Daily 960' : '<:Daily960:785227771584053309>',
    'Live 960' : '<:Live960:785227771776335943>',
    '3 Check' : '<:3Check:785224017602674738>',
    'Crazyhouse' : '<:Crazyhouse:785227771935850556>',
    'Bughouse' : '<:Bughouse:785227771936243783>',
    'King of the Hill' : '<:KingoftheHill:785229768605433896>'
}

GENERAL_ICONS = { #Icons for chess.com general section
    'Games' : '<:Games:785305238668050484>',
    'Puzzles' : '<:PuzzlesGray:785305239070179368>',
    'Lessons' : '<:Lessons:785305238889693237>'
}
COMP_ICONS = [ #Player Icons for compare function (To be mapped to called usernames)
    "<:RedPawn:796081831510147135>",
    "<:BluePawn:796081831715667973>",
    "<:YellowPawn:796081831782383657>",
    "<:GreenPawn:796083866439909447>",
    "<:OrangePawn:796081831530201128>"
]

driver = webdriver.Firefox(firefox_binary = r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe', 
        executable_path = r'C:\Program Files (x86)\geckodriver.exe')

class User404Exception(Exception):
        def __init__(self, message = "User does not exist"):
            super().__init__(message)

class ChessComCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    #Helper function to retrieve, order, and return stats as dict
    def get_ratings(self, username):

        #Go to profile page
        url = "https://www.chess.com/member/" + username
        driver.get(url)

        #Check if directed to error page
        try:
            driver.find_element_by_css_selector('.error-pages-wrapper')
        except:
            pass
        else:
            raise User404Exception(f"User '{username}' does not exist")

        #Initialize default stats dict
        stats = {
        'Bullet' : None,
        'Blitz' : None,
        'Rapid' : None,
        'Daily' : None,
        'Puzzles' : None,
        'Puzzle Rush' : None,
        'Live 960' : None,
        'Daily 960' : None,
        'Bughouse' : None,
        'Crazyhouse' : None,
        '3 Check' : None,
        'King of the Hill' : None
        }


        #Retrieve stats for all modes and ratings (Blitz, Crazyhouse, Puzzle Rush, etc.)
        #Explicitly wait for up to .75 seconds for first search
        try:
            modes = WebDriverWait(driver,.75).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.stat-section-section-link-name')))
        except: #TimeoutException thrown when existing user has no ratings
            modes = []

        ratings = driver.find_elements_by_css_selector('.stat-section-user-rating')

        for i in range(len(modes)):
            stats[modes[i].text] = ratings[i].text

        return stats

    #Helper function to retrive and return general info as dict 
    def get_general(self):
        general = {}
        categories = driver.find_elements_by_css_selector('.sidebar-ratings-label')
        stats = driver.find_elements_by_css_selector('.sidebar-ratings-rating')

        for i in range(len(categories)):
            general[categories[i].text] = stats[i].text

        return general


    @commands.command(aliases = ['rating','ratings','stat'])
    async def stats(self, ctx, username):
        #Start timer
        start = perf_counter()

        #Create the Loading Embed
        my_embed = discord.Embed(
            description = "Retrieving data from chess.com...",
            color = discord.Color.dark_green()  
        )
        my_embed.set_author(name = 'Chess.com', url = "https://www.chess.com/member/" + username, icon_url= 'https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/SamCopeland/phpmeXx6V.png')

        #Send Loading Message
        message = await ctx.send(embed = my_embed)

        #(Try to) Go to profile page and get ratings
        try:
            #Goes to user profile and returns dict of ratings (throws exception if username does not exist)
            ratings = self.get_ratings(username)


        except User404Exception as e: #If username does not exist
        
            #Update embed with error message
            my_embed.title = "Error 404"
            my_embed.description = str(e)
            response_time = perf_counter()-start
            my_embed.set_footer(text = "Response time: {time:1.3} seconds".format(time = response_time))

            #Replace loading message
            await message.edit(embed=my_embed)

            print("{outcome:<12} {site:>12} {user:^24}  Response time = {time:1.3}".format(outcome = 'Error 404', site = 'Chess.com', user = username, time = response_time))
            return 
        #Set new field for each rating
        for mode in ratings.keys():
            if ratings[mode] is not None:
                my_embed.add_field(name= f'{ICONS[mode]} {mode}  \u200b \u200b \u200b \u200b \u200b', value= ratings[mode])


        #Set description with general stats
        general = self.get_general()
        my_embed.description = ''
        for section in (general.keys()):
            my_embed.description += f'{GENERAL_ICONS[section]} **{section}** \u200b \u200b {general[section]}\n'

        #Set description in case of user having no stats/ratings
        if len(my_embed.fields) == 0 :
            my_embed.description = 'This user has no ratings...'

        #Get profile picture and (case-sensitive) username
        profile_pic = driver.find_element_by_css_selector('.post-view-meta-image ')
        username = profile_pic.get_attribute("alt")
        pic_url = profile_pic.get_attribute("src")
        if(pic_url[-3:]=='svg'): #Link to default profile picture is not supported by discord, replace it
            pic_url = 'https://cdn.discordapp.com/attachments/785212221444718633/785315817611984906/noavatar_l.png'


        #Update embed
        my_embed.title = f'Stats for {username}'
        my_embed.set_thumbnail(url = pic_url)
        response_time = perf_counter()-start
        my_embed.set_footer(text = "Response time: {time:1.3} seconds".format(time = response_time))

        #Replace earlier message
        await message.edit(embed=my_embed)
        print("{outcome:<12} {site:>12} {user:^24}  Response time = {time:1.3}".format(outcome = 'Success', site = 'Chess.com', user = username, time = response_time))

    @commands.command(aliases = ['compare'])
    async def compareStats(self, ctx,*usernames):
        start = perf_counter()
        all_ratings = {
        'Bullet' : {},
        'Blitz' : {},
        'Rapid' : {},
        'Daily' : {},
        'Puzzles' : {},
        'Puzzle Rush' : {},
        'Live 960' : {},
        'Daily 960' : {},
        'Bughouse' : {},
        'Crazyhouse' : {},
        '3 Check' : {},
        'King of the Hill' : {}
        }

        my_embed = discord.Embed(
            description = "Retrieving data from chess.com...",
            color = discord.Color.dark_green()  
        )
        my_embed.set_author(name = 'Chess.com', icon_url= 'https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/SamCopeland/phpmeXx6V.png')

        message = await ctx.send(embed = my_embed)

        user_icons = {}
        my_embed.description = '**Key**\n'
        usernames = list(usernames)
        for i in range(len(usernames)):
            try:
                user_ratings = self.get_ratings(usernames[i])
                usernames[i] = driver.find_element_by_id("view-profile").get_attribute("data-username")
                user_icons[usernames[i]] = COMP_ICONS[i]
                my_embed.description += f'{COMP_ICONS[i]} = {usernames[i]}\n'

                for rating in user_ratings:
                    all_ratings[rating][usernames[i]] = user_ratings[rating]

            except User404Exception as e:
                my_embed.title = "Error 404"
                my_embed.description = str(e)
                response_time = perf_counter()-start
                my_embed.set_footer(text = "Response time: {time:1.3} seconds".format(time = response_time))
                await message.edit(embed=my_embed)
                #TODO: print(console log)
                return

        for mode in all_ratings.keys():
            sorted_user_ratings = sorted(all_ratings[mode].items(), key= lambda x: int(x[1]) if x[1] is not None and x[1] != 'Unrated' else -1, reverse = True)
            sorted_ratings = ""

            for user_ratings in sorted_user_ratings:
                if user_ratings[1] is None or user_ratings[1] == 'Unrated':
                    break
                sorted_ratings += f'{user_icons[user_ratings[0]]} {user_ratings[1]}\n'

            if sorted_ratings != "":
                my_embed.add_field(name = f' \u200b \n{ICONS[mode]} __{mode}__  \u200b \u200b \u200b \u200b \u200b', value = sorted_ratings)

        my_embed.set_footer(text = 'Reponse time: {:1.3} seconds'.format(perf_counter()-start))
        await message.edit(embed = my_embed)        

def setup(bot):
    bot.add_cog(ChessComCog(bot))
    print("Chess.com Cog successfully Loaded")