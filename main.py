
import config
from discord.ext import commands


initial_extensions = ['cogs.lichess']

bot = commands.Bot(command_prefix="#")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    print('Successfully logged in and booted')


bot.run(config.API_KEYS['DISCORD_TOKEN'])
