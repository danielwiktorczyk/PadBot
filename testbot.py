import os

import discord
import random
from dotenv import load_dotenv

load_dotenv('token.env')  # We are loading file reading package so we can use it
TOKEN = os.getenv('DISCORD_TOKEN')  # We specify exactly what we want to read from the file
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()  # The client is an object that handles the API calls to Discord so the bot can do its job


@client.event
async def on_ready():  # An event handler that tells the bot what to do (in other words, the main function)
    guild = discord.utils.get(client.guilds,
                              name=GUILD)  # the get function gets the name of the server in the list of discord servers the bot is in
    print(f'{client.user} has connected to Discord!\n'
          f'{guild.name}(Server Name: {guild.id})')  # Then, we just print our server name!
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="you programmers!"))
    # The await keyword makes it so that on_ready() waits for a result from change_presence(). This only works on
    # event loops


# @client.event async def on_member_join(member):  # This function will handle with putting a role to a member when
# he first joins the server


@client.event
async def on_message(message):
    guild = discord.utils.get(client.guilds, name=GUILD)
    user = message.author
    channel_category = "The Death Star (games)"
    if message.author == client.user:  # If the message sent is by a bot, it should exit the function. We don't want
        # the bot to check its own messages as well as other bots on the server
        return  # You might think client.user is the one sending the message. But actually,
        # client.user represents the bot since a client is a bot

    if '!pad newrole ' in message.content:  # Will fix later, this will be the role system if we want to create a role
        # & channel for a game
        role_name = message.content.split('!pad newrole ')[1]
        if discord.utils.get(guild.roles, name=role_name) or discord.utils.get(guild.channels, name=role_name):  # Checking if that role
            # already exists
            await message.channel.send("This role or channel already exists. Make a role that doesn't exist.")
            return
        color = discord.Colour(random.randint(0, 0xFFFFFF))  # Randomly generates a color hex value
        await guild.create_role(name=role_name,
                                colour=color)  # Creates the role with a random color
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            role_name: discord.PermissionOverwrite(read_messages=True)
        }
        await guild.create_text_channel(name=role_name, overwrites=overwrites)
        await message.channel.send("Role and channel has been created!")

    elif '!pad assign ' in message.content:  # Assign a role to the person who asked for the role
        print(message.content.split('!pad assign '))
        role_name = message.content.split('!pad assign ')[1]
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            await message.channel.send("That role doesn't exist. Please try to assign a role that exists")
            return
        await user.add_roles(role)
        await message.channel.send("Role has been added to the user!")


client.run(TOKEN)  # Runs the bot associated with the token we defined earlier


# and I'll do it again