import discord
import logging
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

#results of rolls in format (author_of_roll, roll)
#author_of_roll is an discord.author object
rolls = []
already_rolled = set()


def get_token(filename):
    with open(filename) as file:
        txt = file.readlines()
        return txt[0].strip()

def get_all_winners(rolls):
    reverse_i = -1
    winners = [rolls[-1]]
    if rolls[-1][1] == rolls[-2][1]:
        while(rolls[reverse_i][1] == rolls[reverse_i - 1][1]):
            winners.append(rolls[reverse_i - 1])
    return winners, len(winners)


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves

        channel = message.channel

        global rolls

        if message.author == self.user:
            return

        if message.content.startswith('!test'):
            await channel.send(message.author.name)

        if message.content.startswith('!dice '):
            try:
                number = int(message.content[6:])
                author = message.author
                roll = np.random.randint(number) + 1

                # if str(author) not in already_rolled:
                already_rolled.add(str(author))
                rolls.append((author, roll))

                await channel.send(author.mention + " is rolling " + str(number) + " dice! And rolled " + str(roll))
            except ValueError:
                await channel.send(message.author.mention + " typed command wrongly, I give up.")

        if message.content == "!res":
            rolls = sorted(rolls, key=lambda x: x[1])

            users = list(map(lambda x: x[0].nick + str(np.random.randint(1234352))  if x[0].nick is not None else x[0].name + str(np.random.randint(1234352)), rolls))
            score = list(map(lambda x: x[1], rolls))
            await channel.send(rolls)

            fig = plt.figure()

            ax = fig.add_subplot(111)
            ax.barh(users, score)

            ax.set_title("Rolls for each participant")
            ax.set_ylabel("Rolls")
            ax.set_xlabel("Users")

            for index, value in enumerate(score):
                plt.text(value, index, str(value))

            plt.savefig("to_send.png", bbox_inches = "tight")
            plt.show()
            with open("to_send.png", 'rb') as file:
                await channel.send(file = discord.File(file, "chart.png"))
        if message.content == "!winner":
            rolls = sorted(rolls, key=lambda x: x[1])
            winners = get_all_winners(rolls)




token = get_token("token.txt")

client = MyClient()
client.run(token)
