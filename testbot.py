import os
import discord
import random
import logging

from dotenv import load_dotenv

load_dotenv('token.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = discord.Client()

DISCORD_GUILD = os.getenv('DISCORD_GUILD')
GAME_CATEGORY_NAME = 'The Death Star (games)'

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

PREFIX = 'pb'


@CLIENT.event
async def on_ready():
    print(f'{CLIENT.user} has connected to Discord!')

    guild = discord.utils.get(CLIENT.guilds, name=DISCORD_GUILD)
    print(f'Currently in server: {guild.name}, with ID: {guild.id})')

    await CLIENT.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Almando'))


@CLIENT.event
async def on_member_join(member: discord.member):
    print(f'Salutations, {member}!')


@CLIENT.event
async def on_message(message: discord.message):
    if message.author == CLIENT.user:
        return

    if message.content.startswith(PREFIX):
        await handle_command(message)

    # TODO Dadbot feature here
    if 'I\'m' in message.content:
        pass


async def handle_command(message: discord.message):
    arguments: list
    content = message.content

    if content.startswith(f'{PREFIX} new role'):
        logging.info('Request to make new role')
        arguments = message.content.split()[3:]
        await create_new_role(arguments, message)
        return

    if content.startswith(f'{PREFIX} new game'):
        logging.info('Request to make new game')
        arguments = message.content.split()[3:]
        await create_new_game(arguments, message)
        return

    if content.startswith(f'{PREFIX} join game'):
        logging.info('Request to join a game')
        arguments = message.content.split()[3:]
        await join_game(arguments, message)
        return

    if content.startswith(f'{PREFIX} poll'):
        logging.info('Request to make a new poll')
        user_poll = await format_poll(message)
        if not user_poll:
            return
        await make_poll(user_poll, message)
        return


async def create_new_role(arguments: list, message: discord.message):
    if len(arguments) == 0:
        logging.debug('No arguments passed')
        await message.channel.send("Cannot make a new role without any arguments!")
        return

    role_name = ' '.join(arguments)

    guild = discord.utils.get(CLIENT.guilds, name=DISCORD_GUILD)
    if discord.utils.get(guild.roles, name=role_name):
        logging.debug(f'The role {role_name} already exists.')
        await message.channel.send(f'Oops! The role {role_name} already exists.')
        return

    color = discord.Colour(random.randint(0, 0xFFFFFF))
    await guild.create_role(name=role_name, colour=color)

    logging.info(f'Created role with name {role_name}')
    await message.channel.send(f'Created a new role: {role_name}')


async def create_new_game(arguments: list, message: discord.message):
    if len(arguments) == 0:
        logging.debug('No arguments passed')
        await message.channel.send("Cannot make a new game without any arguments!")
        return

    game_name = ' '.join(arguments)

    guild = discord.utils.get(CLIENT.guilds, name=DISCORD_GUILD)
    if discord.utils.get(guild.roles, name=game_name):
        logging.debug('The role {role_name} already exists.')
        await message.channel.send(f'Oops! The role {game_name} already exists.')
        return

    if discord.utils.get(guild.channels, name=game_name):
        logging.debug('The channel {role_name} already exists.')
        await message.channel.send(f'Oops! The channel {game_name} already exists.')
        return

    color = discord.Colour(random.randint(0, 0xFFFFFF))
    await guild.create_role(name=game_name, colour=color)
    game_role = discord.utils.get(guild.roles, name=game_name)

    game_category = discord.utils.get(guild.categories, name=GAME_CATEGORY_NAME)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        game_role: discord.PermissionOverwrite(read_messages=True)
    }
    await guild.create_text_channel(name=game_name, category=game_category, overwrites=overwrites)

    logging.info(f'Created new game with a new role and text channel named {game_name}')
    await message.channel.send(f'Your new game is ready, {message.author}! It\'s called {game_name}!')


async def join_game(arguments: list, message: discord.message):
    if len(arguments) == 0:
        logging.debug('No arguments passed')
        await message.channel.send("You can't join a game that doesn't have a name!")
        return

    guild = discord.utils.get(CLIENT.guilds, name=DISCORD_GUILD)

    game_name = ' '.join(arguments)
    if '-' in game_name:
        await message.channel.send("Hmm, for this command, please try to use the name of the game role instead of the "
                                   "server name please!")

    game_channel_name = game_name.replace(' ', '-').lower()
    game_role = discord.utils.get(guild.roles, name=game_name)
    game_channel = discord.utils.get(guild.channels, name=game_channel_name)

    if not (game_role and game_channel):
        logging.debug(f'The game {game_name} does not yet exist!')
        await message.channel.send(f'Oops! The game {game_name} does not yet exist!')
        return

    if game_role in message.author.roles:
        await message.channel.send(f'Hmm, seems you already play that game....')

    await message.author.add_roles(game_role)

    logging.info(f'Assigned {message.author} to {game_name}')
    await message.channel.send(f'Have fun playing {game_name}, {message.author}!')


async def format_poll(message: discord.message):
    command = message.content.replace("pb poll", '').strip()

    if "\"" not in command or ',' not in command:
        logging.debug('No poll title or arguments were passed')
        await message.channel.send("You can't just make a poll without a title or arguments! Please insert a poll "
                                   "title that is surrounded in \"\" as well as arguments proceeded with commas.")
        return

    title = command[command.find("\"") + 1:command.rfind("\"")]
    options = command.replace(f'\"{title}\"', '').strip().split(", ")
    logging.info(command)
    poll = {
        "title": title,
        "options": options
    }
    logging.info('title --' + poll.get("title"))
    logging.info(poll.get("options"))
    return poll


async def make_poll(arguments: dict, message: discord.message):
    if not arguments:
        logging.debug('No arguments passed')
        await message.channel.send("A poll has to have a title and options to vote on!")
        return

    options = arguments.get("options")
    argument_length = len(options)

    if argument_length > 9:
        logging.debug('Too many arguments passed')
        await message.channel.send("Too many poll options! The maximum amount of poll options you can add is 10!")
        return

    poll_title = arguments.get("title")
    color = discord.Colour(random.randint(0, 0xFFFFFF))
    emojis = ['🔴', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫', '⚪']
    option_string = ''
    for i in range(argument_length):
        options[i] = f"{emojis[i]} {options[i]} \n"
        option_string = f'{option_string} {options[i]}'

    poll = ''.join(options)
    poll_embed = discord.Embed(title=poll_title, description=option_string, color=color)
    logging.info(f'Sending message')
    bot_poll = await message.channel.send(embed=poll_embed)  # A bot sending a message actually returns the message!

    for i in range(argument_length):
        await bot_poll.add_reaction(emojis[i])


CLIENT.run(TOKEN)
