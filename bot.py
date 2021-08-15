import asyncio

import discord
import logging
import numpy as np
import matplotlib.pyplot as plt
import enum

logging.basicConfig(level=logging.INFO)
commands = []

# results of rolls in format (author_of_roll, roll)
# author_of_roll is an discord.author object
rolls = []
already_rolled = set()
set_roll = -1


# token.txt hold token for this bot, should be in the same directory
def get_token(filename):
    with open(filename) as file:
        txt = file.readlines()
        return txt[0].strip()


# returns list of all the winners
def get_all_winners(rolls):
    winning_roll = rolls[-1][1]
    winners = []
    for roll in rolls:
        if roll[1] == winning_roll:
            winners.append(roll)
    return winners, len(winners)


def get_list_of_winners(winners):
    res = ""
    for winner in winners:
        res += winner[0].mention + ", "
    return res


async def require_role(message, role_name):
    if role_name not in list(map(lambda x: x.name, message.author.roles)):
        await message.channel.send(f"Nie masz wystarczających uprawnień aby skorzystać z tej komendy. {message.author.mention}")
        return False
    return True

class Status(enum.Enum):
    Ok = 0
    Error = 1

class Command():
    def __init__(self, name, description, error_message, function, prefix):
        self.name = name
        self.prefix = prefix
        self.description = description
        self.function = function
        self.error_message = None
    async def execute(self, status, error, *args):
        try:
            await self.function(*args)
        except Exception as e:
            status = Status.Error
            error = f"{self.error_message} Exception: {e}"
        status = Status.Ok
    def get_help(self):
        return description

global_prefix = '!'

async def display_help(channel, message):
    global commands
    to_send = 'Available commands: \n'
    for command in commands:
        to_send += f"{command.prefix}{command.name}\t{command.description}\n"
    await channel.send(to_send)

commands.append(
    Command(
        name = 'help', 
        description = 'Command that displays desciptions of all available commands',
        error_message = "Something went wrong while displaying help command, make sure you typed it correctly: '!help'. ",
        function = display_help,
        prefix = global_prefix
    )
)

async def dice(channel, message):
    global rolls
    global set_roll
    if await require_role(message, "Oficer"):
        try:
            if len(message.content) > 6:
                rolls.clear()
                already_rolled.clear()
                set_roll = -1
                number = int(message.content[6:])
                set_roll = number

                await channel.send(f"Kostka ustawiona na: **{str(set_roll)}** przez {message.author.mention}")
            else:
                await channel.send(f"Pamiętaj aby podać ile 'stron' ma kostka, {message.author.mention}")

        except ValueError:
            await channel.send(message.author.mention + " typed command wrongly, did you mean '!dice NUMBER'?")

commands.append(
    Command(
        name = 'dice', 
        description = 'Command that sets rolling dice to NUMBER provided after command. the NUMBER must be a positive integer ',
        error_message = "Something went wrong while trying to set a dice, make sure you typed it correctly. ",
        function = dice,
        prefix = global_prefix
    )
)

async def brewqser_easter_egg(channel, number, author):
    brewek_rolls = [np.random.randint(low=1, high=number + 1) for _ in range(4)]
    msg = f"Ha {author.mention}! Znowu próbujesz uzyskać skarby gildyjne! " + \
    "Tym razem nie pójdzie ci tak łatwo! Rzucasz z trzykrotnym utrudnieniem! "+ \
    f"Wyrzuciłeś **{brewek_rolls[0]}**, **{brewek_rolls[1]}**, **{brewek_rolls[2]}** i **{brewek_rolls[3]}** " + \
    f",a więc ostatecznie twoim rzutem jest **{min(brewek_rolls)}**. "

    if min(brewek_rolls) == 1:
        msg += "Uuuu jedyneczka, chyba wiemy kto sponsoruje dzisiejszą loterię :> :> :>"
    elif number in brewek_rolls:
        msg += "O, patrz, a mogłeś mieć maxa, jaka szkoda... >:D"

    await channel.send(msg)

    return min(brewek_rolls)

async def roll(channel, message):
    global rolls
    global set_roll
    try:
        number = set_roll
        author = message.author
        # if str(author) == 'Brewqser#8390':
        if str(author) == 'Magomir#5691':
            roll = await brewqser_easter_egg(channel, number, author)
        else:
            roll = np.random.randint(low=1, high=number + 1)

        if str(author) not in already_rolled:
            already_rolled.add(str(author))
            rolls.append((author, roll))
            if str(author) != 'Brewqser#8390':
                await channel.send(f"Rzut kostką D{number} dla {author.mention} wynosi **{roll}**")
        else:
            await channel.send(f"W tej rundzie już rzucałeś/łaś {author.mention} ;)")


    except Exception as e:
        await channel.send(f"{author.mention} typed command wrongly or roll has not been set yet. Error: {e}")

commands.append(
    Command(
        name = 'roll', 
        description = 'Command that allows one to roll preset dice and take part in competition.',
        error_message = "Something went wrong while trying to roll the dice, make sure you typed it correctly. ",
        function = roll,
        prefix = global_prefix
    )
)

async def result(channel, message):
    global rolls
    global set_roll
    if await require_role(message, "Oficer"):
        rolls = sorted(rolls, key=lambda x: x[1])

        users = list(map(
            lambda x: x[0].nick if x[0].nick is not None else x[0].name, rolls))
        score = list(map(lambda x: x[1], rolls))

        fig = plt.figure()

        ax = fig.add_subplot(111)
        # 223 46 16

        red = 230
        green = 126
        blue = 34

        colors = list(map(lambda x: x / 255, [red, green, blue]))
        colors.append(1)

        ax.barh(users, score, color=colors)

        ax.set_title("Wyniki")
        # ax.set_ylabel("Wynik")
        # ax.set_xlabel("Wynik")

        for index, value in enumerate(score):
            plt.text(value, index, str(value))

        plt.savefig("to_send.png", bbox_inches="tight")
        with open("to_send.png", 'rb') as file:
            await channel.send(file=discord.File(file, "chart.png"))

commands.append(
    Command(
        name = 'chart', 
        description = 'Command that allows one to display a chart of everyone\'s results.',
        error_message = "Something went wrong while trying to display a chart, make sure you typed it correctly. ",
        function = result,
        prefix = global_prefix
    )
)

async def winner(channel, message):
    global rolls
    global set_roll
    if len(rolls) == 0:
        await channel.send(f"Nikt jeszcze nie rzucił kostką.")
    elif await require_role(message, "Oficer"):
        rolls = sorted(rolls, key=lambda x: x[1])
        winners, number_of_winners = get_all_winners(rolls)
        if number_of_winners == 1:
            await channel.send(f"Wygrywa {winners[0][0].mention} z wynikiem {winners[0][1]}, gratulacje!!")
        elif number_of_winners > 1:
            await channel.send(f"Mamy remis między: {get_list_of_winners(winners)}! Wasz wynik to {winners[0][1]}")
        else:
            await channel.send("Something went wrong with '!winner' command. Number of winner is less than 1 ??")

commands.append(
    Command(
        name = 'winner', 
        description = 'Command that allows one to display a winner of a roll battle!',
        error_message = "Something went wrong while trying to pick a winner, make sure you typed it correctly. ",
        function = winner,
        prefix = global_prefix
    )
)

async def reroll(channel, message):
    global rolls
    global set_roll
    if await require_role(message, "Oficer"):
        rolls.clear()
        already_rolled.clear()
        await channel.send("Reroll ready.")

commands.append(
    Command(
        name = 'reroll', 
        description = 'Command that allows one to reset dice without needing to provide value for dice.',
        error_message = "Something went wrong while trying to reset a dice, make sure you typed it correctly. ",
        function = reroll,
        prefix = global_prefix
    )
)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        channel = message.channel

        global rolls
        global set_roll

        # don't respond to ourselves
        if message.author == self.user:
            return

        for command in commands:
            if message.content.startswith(f'{command.prefix}{command.name}'):
                status, error = None, None
                await command.execute(status, error, channel, message)
                if status == Status.Error:
                    await channel.send(error)

token = get_token("token.txt")

client = MyClient()
client.run(token)