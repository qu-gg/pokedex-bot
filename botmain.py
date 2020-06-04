"""
@file botmain.py
@author qu-gg

Script that holds the bot code for the simple Pokedex bot
"""
import discord
from discord.ext import commands
import json
import os
import config


def get_pokemon(name):
    """ Handles getting a pokemon entry from the pokedex database """
    # Loop through all of the entries to check their names
    name = str.lower(name)
    for _, pk in pokedex.items():
        if name == str.lower(pk['name']):
            return pk

    # If no pokemon found, error out
    raise NotImplementedError("Pokemon not found.")


def format_embed(pokemon):
    # Formatting the type string based on the number of types
    type_str = "{} | {}".format(pokemon['type1'].title(), pokemon['type2'].title()) \
        if pokemon['type2'] != "" else pokemon['type1'].title()

    # Types
    types = "**Types:** {}".format(type_str)

    # Base stats
    base_stats = "**HP:** {} \n" \
                 "**Attack:** {} \n" \
                 "**Defense:** {} \n" \
                 "**Sp. Atk**: {} \n" \
                 "**Sp. Def:** {} \n" \
                 "**Speed:** {} \n".format(pokemon['hp'], pokemon['attack'], pokemon['defense'], pokemon['sp_attack'],
                                           pokemon['sp_defense'], pokemon['speed'])

    # Abilities
    abilities = ""
    for ability in pokemon['abilities'].strip('[]').replace('\'', '').replace(' ', '').split(','):
        abilities += "{} \n".format(ability)

    # Misc info
    percentage_str = "None" if pokemon["percentage_male"] is None \
        else "{:2.1f}% Male | {:2.1f}% Female".format(pokemon["percentage_male"], 100 - pokemon["percentage_male"])

    misc    = "\n" \
              "\n" \
              "**Height**: {}m \n" \
              "**Weight**: {}kg \n" \
              "**Gender:** {}\n" \
              "\n" \
              "**Generation:** {} \n" \
              "**Classification:** {} \n" \
              "\n" \
              "**Base Egg Steps:** {} \n" \
              "**Capture Rate:** {} \n" \
              "**Base Happiness**: {}".format(pokemon['height_m'], pokemon['weight_kg'], percentage_str,
                                          pokemon["generation"], pokemon['classfication'],
                                          pokemon['base_egg_steps'], pokemon['capture_rate'], pokemon['base_happiness'])

    embed = discord.Embed(title="**#{} - {}**".format(pokemon['pokedex_number'], pokemon['name']))
    embed.set_image(url="https://github.com/qu-gg/pokedex-bot/raw/master/images/{:03}.png".format(pokemon["pokedex_number"]))
    embed.add_field(name="Type", value=type_str)
    embed.add_field(name="Base Stats", value=base_stats)
    embed.add_field(name="Abilities", value=abilities)
    embed.add_field(name="Misc", value=misc)
    return embed


Client = discord.Client()
client = commands.Bot(command_prefix="!")

# Loads in the JSON database
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "pokemon.json")
with open(path, encoding='utf-8') as f:
    database = json.load(f)

# Index the entries by the number
pokedex = dict()
for idx, entry in zip(range(1, len(database) + 1), database):
    print(idx, entry)
    pokedex[idx] = entry


@client.event
async def on_ready():
    print("Logged on as {}".format(client.user))
    game = discord.Game(name="!dex <pokemon ID/name> to use!")
    await client.change_presence(activity=game)


@client.command(pass_context=True)
async def dex(ctx):
    # Process incoming message
    m = ctx.message
    args = m.content.split(' ')
    inp = args[1]

    # Try turning input into the ID
    try:
        id = int(inp)

        if 1 <= id <= len(pokedex):
            pokemon = pokedex[id]
            await ctx.channel.send(embed=format_embed(pokemon))
            print(pokemon)
        else:
            await ctx.channel.send("ID out of bounds! IDs are between 1 and {}.".format(len(pokedex)))

    # Otherwise search for the name entry
    except ValueError:
        try:
            pokemon = get_pokemon(inp)
            await ctx.channel.send(embed=format_embed(pokemon))
        except NotImplementedError:
            await ctx.channel.send("Pokemon not found! Try again.")

    print("Pokemon: {}".format(inp))


client.run(config.BOT_TOKEN)