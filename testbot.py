import os

import discord
from dotenv import load_dotenv

load_dotenv('token.env')  # We are loading file reading package so we can use it
TOKEN = os.getenv('DISCORD_TOKEN')  # We specify exactly what we want to read from the file
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()  # The client is an object that handles the API calls to Discord so the bot can do its job

@client.event
async def on_ready():  # An event handler that tells the bot what to do (in other words, the main function)
    for guild in client.guilds:  # Looping through the discord servers that the API sent us until we find our server
        if guild == GUILD:
            break

    print(f'{client.user} has connected to Discord!\n'
          f'{guild.name}(Server Name: {guild.id})')  # Then, we just print our server name!
    await client.change_presence(activity=discord.CustomActivity(type=discord.ActivityType.listening, name="you programmers!"))
    # The await keyword makes it so that on_ready() waits for a result from change_presence(). This only works on
    # event loops

client.run(TOKEN)  # Runs the bot associated with the token we defined earlier

# Test line for github education, remove afterward
#another test
# blah blah

# and I'll do it again