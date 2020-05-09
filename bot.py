import asyncio

import discord
import logging
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

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
        await message.channel.send("Nie masz wystarczających uprawnień aby skorzystać z tej komendy. " + message.author.mention)
        return False
    return True


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves

        channel = message.channel

        global rolls
        global set_roll

        if message.author == self.user:
            return

        if message.content.startswith('!majojohelp'):
            await channel.send("Available commands: !majojohelp, !dice, !roll, !res, !winner, !clear, !reroll")

        if message.content.startswith('!dice '):
            if await require_role(message, "Oficer"):
                try:
                    number = int(message.content[6:])
                    set_roll = number

                    await channel.send("Dice set to: " + str(set_roll) + " by " + message.author.mention)
                except ValueError:
                    await channel.send(message.author.mention + " typed command wrongly, I give up.")

        if message.content == '!roll':
            try:
                number = set_roll
                author = message.author
                roll = np.random.randint(number) + 1

                if str(author) not in already_rolled:
                    already_rolled.add(str(author))
                    rolls.append((author, roll))

                await channel.send("Rzut kostką D" + str(number) + " dla " + author.mention + " wynosi **" + str(roll) + "**")
            except ValueError:
                await channel.send(message.author.mention + " typed command wrongly or roll has not been set yet, "
                                                            "I give up.")

        if message.content == "!res":
            if await require_role(message, "Oficer"):
                rolls = sorted(rolls, key=lambda x: x[1])

                users = list(map(
                    lambda x: x[0].nick if x[0].nick is not None else x[0].name, rolls))
                score = list(map(lambda x: x[1], rolls))

                fig = plt.figure()

                ax = fig.add_subplot(111)
                ax.barh(users, score)

                ax.set_title("Wyniki dla każdego uczestnika")
                ax.set_ylabel("Wynik")
                # ax.set_xlabel("")

                for index, value in enumerate(score):
                    plt.text(value, index, str(value))

                plt.savefig("to_send.png", bbox_inches="tight")
                plt.show()
                with open("to_send.png", 'rb') as file:
                    await channel.send(file=discord.File(file, "chart.png"))

        if message.content == "!winner":
            if await require_role(message, "Oficer"):
                rolls = sorted(rolls, key=lambda x: x[1])
                winners, number_of_winners = get_all_winners(rolls)
                if number_of_winners == 1:
                    await channel.send("Wygrywa " + winners[0][0].mention + " z wynikiem " + str(
                        winners[0][1]) + ", gratulacje!!")
                elif number_of_winners > 1:
                    await channel.send("Mamy remis między: " + get_list_of_winners(
                        winners) + ". Wszyscy posiadają wynik równy " + str(winners[0][1]))
                else:
                    await channel.send("Something went wrong with '!winner' command.")


        if message.content == "!new":
            if await require_role(message, "Oficer"):
                rolls.clear()
                already_rolled.clear()
                set_roll = -1
                await channel.send("Rolls cleared.")
        if message.content == "!reroll":
            if await require_role(message, "Oficer"):
                rolls.clear()
                already_rolled.clear()
                await channel.send("Reroll ready.")


token = get_token("token.txt")

client = MyClient()
client.run(token)
