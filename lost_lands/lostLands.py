import difflib
import interactions, asyncio, os, random, io
from interactions.ext.tasks import IntervalTrigger, create_task
from random import choice
from datetime import datetime, timedelta
import requests
import re
from io import BytesIO
import json
import unicodedata
from urllib.parse import urlparse
from utils import textwrite
import collections
import time
import csv
import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cv2
import numpy as np
import pickle
from definitions import *
from utils.db.database import Database

database = Database()


class LostLandsManager:
    def __init__(self, bot):
        self.database = database
        self.games = {}
        self.players = {}
        self.teams = {}
        self.items = item_defitions
        self.use_database = False
        self.bot = bot

@create_task(IntervalTrigger(300))
async def update_tasks(server_id):
    print("Updating the board.")
    await send_lost_board(server_id)


firstUpdate = False
from taskItems import *

event_code_word = "lltracker2023"
#### Check if barrages are casted:
#### if last_roll_obj > datetime.now():
##link to the manual submission guidelines
shop_list_msgid = 1123366570425585774
lostLandsManualSubmissions = f"https://discord.com/channels/616498757441421322/1123239204613267456"
global_footer = "Lost Lands v1.2"
##global editing lock
is_editing = False





    @bot.command(
        name="startevent",
        description="Begin a clan event (beta :>)",
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        options=[
            interactions.Option(
                name="type",
                description="What type of event would you like to start?",
                type=interactions.OptionType.STRING,
                required=True
            )
        ]
    )
    async def startevent(ctx: interactions.CommandContext, type: str = ""):
        server_id = ctx.guild_id
        if server_id == "1131575888937504798" or server_id == 1131575888937504798:
            server_id = 616498757441421322
        print("Starting an event")
        if type == "Lost Lands":
            await start_lost_lands(ctx, server_id)
            await send_lost_board(server_id)


async def ref_updates(action, player, timestamp, team):
    ref_channel = await interactions.get(bot, interactions.Channel, object_id=1164317801213861929)
    text_string = (f"{action} \n {player}")
    await ref_channel.send(text_string)


@create_task(IntervalTrigger(3600))
async def send_shop_update():
    global shop_list_msgid
    shop_list_msgid = await update_shop(616498757441421322)
    print(f"The shop has been successfully refreshed.")


async def update_shop(server_id):
    global shop_list_msgid
    if server_id == 1131575888937504798:
        server_id = 616498757441421322
    path = f'data/{server_id}/events'
    current_date = datetime.today().date()
    shop_file = f"shop_items({str(current_date)}).json"
    shop_loc = os.path.join(path, shop_file)
    lost_channel = await read_properties('lostLandsChannel', server_id)
    lost_shop_channel = 1158500924457750660
    channel = await interactions.get(bot, interactions.Channel, object_id=lost_shop_channel)
    try:
        await channel.purge(5)
    except Exception as e:
        print(f"Unable to purge shop channel: {e}")

        # Check stock before proceeding
    if os.path.exists(shop_loc):
        with open(shop_loc, 'r', encoding='utf-8') as f:
            shop_data = json.load(f)
            item_stock = shop_data["stock"]
            stored_date = shop_data["date"]
            if stored_date != str(current_date):
                try:
                    os.remove(shop_loc)
                except Exception as e:
                    print(f"Unable to delete the old shop when refreshing -- {e}")
            else:
                shop_list = shop_data["shop_list"]
                selected_emojis = shop_data["selected_emojis"]
                new_shop_list = ""
                for item_name, item_properties in shop_emojis.items():
                    if item_properties["emoji"] not in selected_emojis:
                        continue
                    emoji = item_properties["emoji"]
                    description = item_properties["description"]
                    price = item_properties["price"]
                    formatted_name = " ".join(word.capitalize() for word in item_name.split())
                    stock = int(item_stock.get(item_name.lower(), 0))
                    if stock > 0:  # If item has stock
                        new_shop_list += f"## <{emoji}> **{formatted_name}**\n> **Stock**: `{int(stock)}`\n> <:1GP:980287772491403294> **Price**: `{price} coins`\n> {description}\n ** **\n"
                    else:
                        # Option 1: Cross out the item name
                        new_shop_list += f"## <{emoji}> ~~**{formatted_name}**~~\n> **Stock**: `{int(stock)}`\n> ~~<:1GP:980287772491403294> Price: {price} coins~~\n> ~~*{description}*~~\n ** **\n"
                        selected_emojis.remove(emoji)
                shop_list = new_shop_list
    if not os.path.exists(shop_loc):
        shop_list = ""
        items_by_type = {"t": [], "o": [], "d": [], "e": []}
        for item_name, item_properties in shop_emojis.items():
            items_by_type[item_properties["type"]].append((item_name, item_properties))

        # Decide how many items of each type to include
        trap_items = random.sample(items_by_type["t"], random.randint(1, 1))
        off_items = random.sample(items_by_type["o"], random.randint(1, 2))
        def_items = random.sample(items_by_type["d"], random.randint(1, 3))
        ench_items = random.sample(items_by_type["e"], random.randint(1, 2))

        selected_items = {
            "t": trap_items,
            "o": off_items,
            "d": def_items,
            "e": ench_items
        }

        selected_emojis = []
        stock_data = {}
        for item_type, items in selected_items.items():
            for item_name, item_properties in items:
                stock = 0
                if item_type == "t":
                    stock = random.randint(1, 2)
                elif item_type == "o":
                    stock = random.randint(1, 2)
                elif item_type == "d":
                    stock = random.randint(1, 2)
                elif item_type == "e":
                    stock = random.randint(1, 2)
                stock_data[item_name.lower()] = stock
                emoji = item_properties["emoji"]
                description = item_properties["description"]
                price = item_properties["price"]
                formatted_name = " ".join(word.capitalize() for word in item_name.split())
                shop_list += f"## <{emoji}> **{formatted_name}** (Stock: {stock})\n> ### <:1GP:980287772491403294> Price: `{price} coins`\n> {description}\n ** **\n"
                selected_emojis.append(emoji)

        # Store the generated shop list and emojis in the file
        shop_data = {
            "date": str(current_date),
            "shop_list": shop_list,
            "selected_emojis": selected_emojis,
            "stock": stock_data
        }
        with open(shop_loc, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, indent=4)
    shop_embed = interactions.Embed(name="", description="**ITEM RULES**")
    shop_embed.add_field(name="", value="**ITEMS DO NOT AFFECT MERCY RULES**", inline=False)
    shop_embed.add_field(name="",
                         value="**ANY GIVEN ITEM ONLY HAS EFFECT ON ONE TEAM UNLESS EXPLICITLY STATED OTHERWISE**",
                         inline=False)
    shop_embed.add_field(name="",
                         value="**IF AN ITEM DOES NOT HAVE IT'S EXPECTED EFFECT, PLEASE OPEN A TICKET TO HAVE IT RESOLVED! (#HELP)**",
                         inline=False)
    shop_embed.set_footer(text="*To buy an item, your *captain* must react to this message!*")
    if len(shop_list) > 2000:
        # Split the message into two parts
        part1 = shop_list[:2000]
        # Find the last newline in the first 2000 characters to avoid cutting off in the middle of an item
        last_newline = part1.rfind("\n")
        part1 = shop_list[:last_newline]
        part2 = shop_list[last_newline:]
        await channel.send(f"# The Wandering Wares\n" +
                           "The Wise Old Man presents himself, accompanied by a random assortment of buffs, weapons, and shields.\n" +
                           "Each time *The Wandering Wares* appears, the stock contained within will change, alongside the quantities of each.\n" +
                           "So, choose wisely.")
        await channel.send(part1)
        shop_list_msg = await channel.send(part2, embeds=[shop_embed])
    else:
        shop_list_msg = await channel.send(shop_list, embeds=[shop_embed])

    current_time = datetime.now()
    midnight = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
    midnight_timestamp = int(time.mktime(midnight.timetuple()))
    await channel.send(f"The next shop reset occurs <t:{midnight_timestamp}:R>")
    shop_list_msgid = str(shop_list_msg.id)
    for emoji in selected_emojis:
        try:
            await shop_list_msg.create_reaction(emoji)
            await asyncio.sleep(1)
        except Exception as e:
            print("Couldn't create reactions: ", e)
    if os.path.exists(f"data/616498757441421322/events/lost_lands.json"):
        with open(f"data/616498757441421322/events/lost_lands.json", 'r') as jsonfile:
            data = json.load(jsonfile)
        for item in data:
            if 'shopPostID' in item:
                item['shopPostID'] = str(shop_list_msg.id)
                shop_list_msgid = str(shop_list_msg.id)
                print("Saved the new shop post ID.")
    with open(f"data/616498757441421322/events/lost_lands.json", 'w') as jsonfile:
        print("Saved the new data to the file.")
        json.dump(data, jsonfile, indent=4)
    print(f"Returning this message id: {shop_list_msgid}")
    return shop_list_msgid


async def start_lost_lands(ctx, server_id):
    lost_team_selection = await read_properties('lostLandsTeamSelect', server_id)
    print("Attempting to start lost lands.")
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    path = f'data/{server_id}/events'
    filename = "lost_lands.json"
    os.makedirs(path, exist_ok=True)
    file = os.path.join(path, filename)
    global shop_list_msgid
    current_date = datetime.today().date()
    shop_file = f"shop_items({str(current_date)}).json"
    shop_loc = os.path.join(path, shop_file)
    shop_id = await update_shop(server_id)
    shop_link = f"https://discord.com/channels/1131575888937504798/1158500924457750660/{shop_id}"
    i = 1
    data = []
    board_tiles = await generate_lost_board(server_id)
    data.append({
        "Mercy Rule": 48,
        "Board Tiles": board_tiles,
        "pickingMsg": "0",
        "shopLink": shop_link,
        "shopPostID": str(shop_list_msgid),
        "effectedTiles": [],
    })
    selection_data = {}
    ## Grab defined team captains from text file
    for i in range(9):
        team_captain = "None"
        if i == 0:
            emoji = ":bandos:1163953194527883374"
            teamname = "Bandos"
        elif i == 1:
            emoji = ":zamorak:1163953196385976370"
            teamname = "Zamorak"
        elif i == 2:
            emoji = ":armadyl:1163953319316815965"
            teamname = "Armadyl"
        elif i == 3:
            emoji = ":tumeken:1163953238303842374"
            teamname = "Tumeken"
        elif i == 4:
            emoji = ":seren:1163953199309406349"
            teamname = "Seren"
        elif i == 5:
            emoji = ":guthix:1163953193647083622"
            teamname = "Guthix"
        elif i == 6:
            emoji = ":saradomin:1163953195404501054"
            teamname = "Saradomin"
        elif i == 7:
            emoji = ":zaros:1163953273347256482"
            teamname = "Zaros"
        elif i == 8:
            emoji = ":xeric:1163953198147567777"
            teamname = "Xeric"
        selection_data[i] = {
            "name": teamname,
            "emoji": emoji
        }
        # Create forums for each team
        team_channel_id, new_role_id = await create_team(ctx, teamname)
        # new_post = await (name=f"{teamname}", content=f"<@&{new_role_id}>", reason="Lost Lands")
        ## send the team status page
        for item in board_tiles:
            if item['number'] == 1:
                tile_type = item['type']
        data.append({
            "Number": i + 1,
            "Team name": teamname,
            "Current Tile": 1,
            "Current Type": str(tile_type),
            "Previous Tile": 0,
            "Previous Type": "None",
            "Team Captain": "none",
            "colead": 0,
            "Team Points": 0,
            "currentTurn": 1,
            "Status": 0,
            "Thread ID": str(team_channel_id),
            "Members": [],
            "taskNumber": 0,
            "taskItemsObtained": [],
            "captainOnly": False,
            "roleID": int(new_role_id),
            "mainmsg": 0,
            "mercyRule": str(datetime.now() + timedelta(days=1)),
            "last_roll": str(datetime.now()),
            "Inventory": [
                {"item": "ghommal's lucky penny", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "gertrude's cat", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "pirate pete's parrot", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "duplication glitch", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "questmaster's gauntlets", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "mind goblin", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "blood tithe", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "dragon spear", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "shadow barrage", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "ice barrage", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "nieve's elysian", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "ward of the leech", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "ward of mending", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "hunter's box traps", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "barrelchest anchor", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "smoke barrage", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "binding necklace", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "strange old man's spade", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "rune scroll", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "ancient rune", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "alchemist's blessing", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "lightbearer", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "dinh's bulwark", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "teleportation tablet", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "the mimic", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "hespori's vines", "quantity": 0, "cooldown": 0, "votes": 0},
                {"item": "tumekenian's quicksand", "quantity": 0, "cooldown": 0, "votes": 0}
            ],
            "teamEmoji": emoji,
            "teamChannelLink": f"https://discord.com/channels/{server_id}/{str(team_channel_id)}",
        })
        active_cooldowns.initialize(server_id, 0, teamname)

    with open(file, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    # await team_picker(server_id)
    for i in range(9):
        await sendTeamStatus(i + 1, server_id)
    await send_team_selection(ctx, selection_data, lost_team_selection)


@bot.command(
    name="rfsel",
    description="Refreshes the team selection page with new data.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def rfsel(ctx):
    server_id = ctx.guild.id
    lost_team_selection = 1166165832469069904
    selection_data = {}
    for i in range(9):
        team_captain = "None"
        if i == 0:
            emoji = ":bandos:1163953194527883374"
            teamname = "Bandos"
        elif i == 1:
            emoji = ":zamorak:1163953196385976370"
            teamname = "Zamorak"
        elif i == 2:
            emoji = ":armadyl:1163953319316815965"
            teamname = "Armadyl"
        elif i == 3:
            emoji = ":tumeken:1163953238303842374"
            teamname = "Tumeken"
        elif i == 4:
            emoji = ":seren:1163953199309406349"
            teamname = "Seren"
        elif i == 5:
            emoji = ":guthix:1163953193647083622"
            teamname = "Guthix"
        elif i == 6:
            emoji = ":saradomin:1163953195404501054"
            teamname = "Saradomin"
        elif i == 7:
            emoji = ":zaros:1163953273347256482"
            teamname = "Zaros"
        elif i == 8:
            emoji = ":xeric:1163953198147567777"
            teamname = "Xeric"
        selection_data[i] = {
            "name": teamname,
            "emoji": emoji
        }
    await send_team_selection(ctx, selection_data, lost_team_selection)


async def send_team_selection(ctx, selection_data, lost_team_selection):
    server_id = ctx.guild.id
    lost_team_selection = 1166165832469069904
    global team_actives, team_passives
    if lost_team_selection == 0 or lost_team_selection == "0":
        print("No team selection channel was found to send the embed options to")
        return
    select_chan = await interactions.get(bot, interactions.Channel, object_id=lost_team_selection)
    past_msg = await select_chan.get_history()
    print(past_msg)
    ## clear the channel of any pre-existing messages
    teams_embed = interactions.Embed(title="Lost Lands - Team Selection",
                                     description="Select which team you'd like to participate in by pressing one of the buttons below.\n" +
                                                 "However, we advise that first you read each one above to understand its benefits and disadvantages.")
    buttons = []
    # text_string = ("# God Alignments\n" + "> In the mystical realm of the Lost Lands, the god alignments manifest as enigmatic forces. " +
    #     "These alignments bestow teams with unique affiliations to the major gods of Old School RuneScape, " +
    #     "imbuing them with the very essence of their chosen deity. These divine bonds weave themselves into " +
    #     "the tapestry of the land's history, granting teams access to special powers and abilities.\n\n" +
    #     "## Each team has its own <:active:1163953192531411014> **Active** and <:passive:1163953191789011016> **Passive** abilities.\n\n" +
    #     "### An <:active:1163953192531411014> **active** ability must be activated manually. \n### <:passive:1163953191789011016> **Passive** abilities have a *random* chance of activating automatically.\n\n\n")
    rows = []
    for key, team in selection_data.items():
        # text_string += f"## <{team['emoji']}> {team['name']}"
        print(team_actives[team['name'].lower()])
        team_active_name, description = [s.strip() for s in team_actives[team['name'].lower()].split(":")]
        team_active_name = team_active_name.replace("*", "").replace(":", "")
        team_passive_name, passive_desc = [s.strip() for s in team_passives[team['name'].lower()].split(":")]
        team_passive_name = team_passive_name.replace("*", "").replace(":", "")
        passive_desc = passive_desc.replace(":", "").replace("\n", "\n> ")
        description = description.replace(":", "").replace("\n", "\n> ")
        # text_string += f"\n> ### <:active:1163953192531411014>  {team_active_name} → `{description}` \n{team_active_long[team['name'].lower()]}"
        # text_string += f"\n> ### <:passive:1163953191789011016> {team_passive_name} → `{passive_desc}` \n{team_passive_long[team['name'].lower()]}\n"
        emname, emoji_id = team['emoji'].strip(":").split(":")
        team_button = interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            emoji=interactions.Emoji(name=emname, id=emoji_id),
            label=team['name'],
            custom_id=f"{team['name']}_select_button"
        )
        buttons.append(team_button)

        # When we have 5 buttons, add them as a row and clear the buttons list
        if len(buttons) == 5:
            rows.append(buttons)
            buttons = []
        await asyncio.sleep(1)

    # If there are any remaining buttons, add them as a final row
    if buttons:
        rows.append(buttons)
    teams_embed.set_thumbnail(url="http://www.droptracker.io/img/ll-logo.png")
    selection_message = await select_chan.send(embeds=teams_embed, components=rows)


async def create_team(ctx, teamname):
    print(f"Creating a new thread for {teamname}.")
    guild = await interactions.get(bot, interactions.Guild, object_id=ctx.guild.id)
    guild_roles = await guild.get_all_roles()
    found = False
    guild_channels = await guild.get_all_channels()
    chan_found = False
    for channel in guild_channels:
        if channel.name.lower() == teamname.lower():
            chan_found = True
            team_channel = channel
    for role in guild_roles:
        if role.name.lower() == teamname.lower():
            found = True
            new_role = role
            new_role_id = str(role.id)
    if found == False:
        new_role = await ctx.guild.create_role(teamname, mentionable=True)
        new_role_id = str(new_role.id)
    if chan_found == False:
        team_channel = await guild.create_channel(name=f"{teamname}", type=interactions.ChannelType.GUILD_TEXT,
                                                  parent_id=1153326187192520814)
    await team_channel.send(
        f"{teamname.capitalize()} has been created!\n\nThere is currently no standing team captain!")
    return team_channel.id, new_role_id


@bot.event
async def on_message_reaction_add(reaction: interactions.MessageReaction):
    global is_editing
    global shop_list_msgid
    if reaction.member.user.bot:
        return
    if reaction.member.user.system:
        return
    reaction_msg_id = reaction.message_id
    reaction_msg_id = int(reaction_msg_id)
    if reaction.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = reaction.guild_id
    shop_list_id = shop_list_msgid
    if not shop_list_id:
        print("Doesn't appear an event is running.")
        return

    def get_team_by_message(reaction_msg_id):
        cache = False
        binding = False
        for team_id, msg_id in cache_msgs.items():
            if msg_id == reaction_msg_id:
                cache = True
                return team_id, binding, cache  # Returns the team_id if a match is found
        for team_id, msg_id in binding_msgs.items():
            print(int(msg_id))
            print(int(reaction_msg_id))
            if int(msg_id) == int(reaction_msg_id):
                binding = True
                return team_id, binding, cache

        return None, None, None  # Returns None if no match was found

    team_id, binding, cache = get_team_by_message(reaction.message_id)
    if team_id is not None:
        if cache == True:
            with open(f"data/{server_id}/events/{team_id}-cache.json", 'r') as jsonfile:
                options = json.load(jsonfile)
            emoji_one = unicodedata.normalize('NFC', '1️⃣')
            emoji_two = unicodedata.normalize('NFC', '2️⃣')
            emoji_three = unicodedata.normalize('NFC', '3️⃣')

            # Normalize reaction emoji
            reacted_emoji = unicodedata.normalize('NFC', reaction.emoji.name)
            # Compare the normalized strings
            if reacted_emoji == emoji_one:
                task_selected = options[0]
            elif reacted_emoji == emoji_two:
                task_selected = options[1]
            elif reacted_emoji == emoji_three:
                task_selected = options[2]
            else:
                task_selected = None

            if task_selected is not None:
                with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfi:
                    eventdatas = json.load(jsonfi)
                    for item in eventdatas:
                        if 'Number' in item:
                            if int(item['Number']) == int(team_id):
                                item['taskNumber'] = task_selected
                                item['Status'] = 0
                with open(f"data/{server_id}/events/lost_lands.json", 'w') as jsonfil:
                    json.dump(eventdatas, jsonfil, indent=4)
                is_editing = False
                await sendTeamStatus(team_id, server_id)
                reacted_message = await interactions.get(bot, interactions.Message, channel_id=reaction.channel_id,
                                                         object_id=reaction.message_id)
                await reacted_message.delete()
                return
            else:
                print("Invalid reaction emoji")
        elif binding == True:
            with open(f"data/{server_id}/events/binding_options.json", 'r') as jsonfile:
                options = json.load(jsonfile)

            emoji_one = unicodedata.normalize('NFC', '1️⃣')
            emoji_two = unicodedata.normalize('NFC', '2️⃣')

            # Normalize reaction emoji
            reacted_emoji = unicodedata.normalize('NFC', reaction.emoji.name)
            # Compare the normalized strings
            if reacted_emoji == emoji_one:
                task_selected = options[0]
            elif reacted_emoji == emoji_two:
                task_selected = options[1]
            else:
                task_selected = None

            if task_selected is not None:
                with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfi:
                    eventdatas = json.load(jsonfi)
                    for item in eventdatas:
                        if 'Number' in item:
                            if int(item['Number']) == int(team_id):
                                item['taskNumber'] = task_selected['taskNumber']
                                item['Status'] = 0
                                item['Current Type'] = task_selected['type']
                                item['Current Tile'] = task_selected['new_pos']
                                item['Team Points'] += task_selected['addpts']
                                team_status_cache[item['Number']] = 0

                with open(f"data/{server_id}/events/lost_lands.json", 'w') as jsonfi:
                    json.dump(eventdatas, jsonfi, indent=4)
                reacted_message = await interactions.get(bot, interactions.Message, channel_id=reaction.channel_id,
                                                         object_id=reaction.message_id)
                await reacted_message.reply(f"You have selected {task_selected['task']}.")
                await sendTeamStatus(team_id, server_id)
                await updateBoard(server_id)
                await asyncio.sleep(1)
                await reacted_message.delete()
                return

    else:
        print("Reaction message ID not found in cache_msgs")
    if int(reaction.message_id) != int(shop_list_msgid):
        return
    with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfile:
        eventData = json.load(jsonfile)

    # Define team_index as a flag to indicate if a team is found
    team_index = None
    canPurchase = False
    for index, item in enumerate(eventData):
        if 'Number' in item:
            teamMembers = item['Members']
            teamCaptain = item['Team Captain']
            teamCoCap = item['colead']
            if item['Team Captain'] != "none" and item['Team Captain'] != "None":
                if int(reaction.member.id) == int(item['Team Captain']):
                    team_index = index
                    canPurchase = True
                elif int(reaction.member.id) == int(item['colead']):
                    team_index = index
                    canPurchase = True
            else:
                print("Team_index is none?")
            if teamMembers != []:
                for member in teamMembers:
                    if member['id'] == reaction.member.id:
                        team_index = index
    reacted_message = await interactions.get(bot, interactions.Message, channel_id=reaction.channel_id,
                                             object_id=reaction.message_id)
    member_reacting = await interactions.get(bot, interactions.Member, guild_id=reaction.guild_id,
                                             object_id=reaction.member.id)
    if team_index is None:
        ## no team was found
        print(f"{reaction.member.name} has reacted to the shop, but was not found on a team.")
    if canPurchase == False:
        try:
            await member_reacting.send(f"Only your team captain, <@{teamCaptain}> can purchase items from the shop!")
        except Exception:
            await reacted_message.reply(
                f"<@{reaction.member.id}>\nOnly your team captain, <@{teamCaptain}> can purchase items from the shop!")
        # await reacted_message.remove_all_reactions()
        # await update_shop(server_id)
        return
    team = eventData[team_index]
    teamInvent = team['Inventory']
    if team == {}:
        ## no team was found
        print(f"{reaction.member.name} has reacted to the shop, but was not found on a team.")
        return
    print(reaction)
    if teamInvent == []:
        return
    print(shop_emojis.keys())
    itemPurchase = None
    # object represents all items in shop stock
    dict_formatted = f":{reaction.emoji.name}:{reaction.emoji.id}"
    for object, details in shop_emojis.items():
        emoji_name = details["emoji"]
        item_price = details["price"]
        lowobject = object.lower()
        if emoji_name == dict_formatted:
            itemPurchase = object
            itemPrice = details["price"]
            break
    if itemPurchase != None:
        path = f'data/{server_id}/events'
        current_date = datetime.today().date()
        shop_file = f"shop_items({str(current_date)}).json"
        shop_loc = os.path.join(path, shop_file)
        with open(shop_loc, 'r', encoding='utf-8') as f:
            shop_data = json.load(f)
            item_stock = shop_data["stock"]
        print(f"itempurch: `{itemPurchase}`")

        if itemPurchase in item_stock and item_stock[itemPurchase] > 0:
            # Decrement the stock since an item is being purchased
            item_stock[itemPurchase] -= 1
            # Save the updated stock back to the file
            with open(shop_loc, 'w', encoding='utf-8') as f:
                print("Saved the new shop stocks")
                json.dump(shop_data, f, indent=4)
            await asyncio.sleep(1)
        else:
            current_time = datetime.now()
            midnight = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
            midnight_timestamp = int(time.mktime(midnight.timetuple()))
            no_stock_msg = await reacted_message.reply(
                f"<@{reaction.member.id}>\nSorry, `{itemPurchase}` is out of stock!\n> Next restock: <t:{midnight_timestamp}:R> ")
            await asyncio.sleep(30)
            await no_stock_msg.delete()
            return
        print("Continuing!")
        team_cap = team['Team Captain']
        team_colead = team['colead']
        if team['Team Points'] < item_price:
            nopoints = await reacted_message.reply(
                f"<@{reaction.member.id}>\nYou need at least `{item_price}` points to buy a {object}!")
            await asyncio.sleep(30)
            await nopoints.delete()
            return
        group_channel = team['Thread ID']
        group_chan = await interactions.get(bot, interactions.Channel, object_id=group_channel)
        if team_cap == "None" or team_cap == "none":
            team_cap = 0
        if team_colead == "none" or team_colead == "None":
            team_colead = 0
        if member_reacting.id != int(team_cap) and member_reacting.id != int(team_colead):
            try:
                await member_reacting.send(
                    f"<@{member_reacting.id}>\nOnly the team captain (<@{team_cap}) or co-captain (<@{team_colead}) can authorize purchases from the store!")
            except:
                await group_chan.send(
                    f"<@{member_reacting.id}>\nOnly the team captain or co-captain can authorize purchases from the store!")
            return
        else:
            team_channel = await interactions.get(bot, interactions.Channel, object_id=team['Thread ID'])
            await reacted_message.remove_all_reactions()
            for item in teamInvent:
                if item['item'] == itemPurchase.lower():
                    item['quantity'] += 1
            team['Team Points'] -= item_price
            response = await team_channel.send(
                f"<@{member_reacting.id}> purchased `1` {object}!\nYour team has `{team['Team Points']}` points remaining!")
            with open(f"data/{server_id}/events/lost_lands.json", 'w') as jsonfile:
                json.dump(eventData, jsonfile, indent=4)
        await asyncio.sleep(0.2)
        await update_shop(server_id)

    # Update the json file with the new data
    with open(f"data/{server_id}/events/lost_lands.json", 'w') as jsonfile:
        json.dump(eventData, jsonfile, indent=4)
    time.sleep(1)
    await sendTeamStatus(team['Number'], str(server_id))

    # if team != {} and teamInvent != []:
    #     for item in teamInvent:
    #         if item['item']


last_message = None
###Message handler for checking drops automatically
can_select = True
user_list = []
pairs = {}
final_pairs = {}


def save_pairs_to_file(filename="pairs.json"):
    global pairs
    with open(filename, 'w') as file:
        json.dump(final_pairs, file)


def load_pairs_from_file(filename="pairs.json"):
    global pairs
    try:
        with open(filename, 'r') as file:
            pairs = json.load(file)
    except FileNotFoundError:
        pairs = {}  # If the file doesn't exist, initialize an empty dictionary


@bot.event(name="on_message_create")
async def message_handler(message: interactions.Message, image_upload: interactions.Attachment = None):
    global pairs
    global user_list
    global last_message
    global final_pairs
    if message.author.id == 703000962964652082:
        return
    if last_message != None:
        if message.embeds:
            if last_message.embeds == message.embeds:
                return
    last_message = message
    global is_editing
    if message.attachments:
        for attachment in message.attachments:
            # Check if the attachment is an image (by checking its content type)
            if "image" in attachment.content_type and "link" in message.content.lower():
                url, extratxt = attachment.url.split("?")

                # Send the URL in a format that makes it easily copyable
                response_msg = await message.reply(f"Image URL: ```{url.lower()}```")
                await asyncio.sleep(20)
                try:
                    await response_msg.delete()
                except Exception as e:
                    print(f"Unable to remove message: {e}")
                return  # Exit after sending the image URL, or remove this if you want to continue with the rest of the logic

    serverid = str(message.guild_id)
    if serverid == 1131575888937504798:
        serverid = 616498757441421322
    webhook_channel = await read_properties('drop_webhook_channel', serverid)
    if image_upload != None:
        image_url = image_upload.url
    else:
        image_url = "none"
    if message.channel_id == webhook_channel:
        receivedFrom = ""
        if message.embeds:
            for embed in message.embeds:
                if embed.title == "```CONFIRMED DROP```":
                    for field in embed.fields:
                        player_name = embed.author.name
                        if field.name == "Item name":
                            itemname = field.value.lower().strip("`").strip()
                        player_id = await playerfiles.get_id_from_name(player_name, serverid)
                        if field.name == "Value":
                            price = field.value.strip("`").strip("\n")
                        if field.name == "auth":
                            auth_token = field.value.strip("`")
                        if field.name == "From":
                            if "(" in field.value:
                                receivedFrom, lvl = field.value.strip("`").strip().split("(")
                            else:
                                receivedFrom = field.value.strip("`").strip()
                            receivedFrom = receivedFrom.lower()
                        quantity = 1
                elif embed.title == "low-value":
                    for field in embed.fields:
                        if field.name == "auth":
                            auth_token = field.value.strip("`")
                            player_name = embed.author.name
                            player_id = await playerfiles.get_id_from_name(player_name, serverid)
                        if field.name == "item":
                            itemname = field.value
                        if field.name == "amt":
                            try:
                                quantity = int(field.value)
                            except:
                                print(f"Exception casting quantity to int: {quantity} =/= int. Set to 1.")
                                quantity = 1
                        if field.name == "Value":
                            price = field.value
                        if field.name == "source":
                            receivedFrom = field.value
                if receivedFrom != "":
                    if 'impling jar' in receivedFrom.lower():
                        ##skip impling jars
                        return
                    if 'loot chest' in receivedFrom.lower():
                        return
                    if 'supply crate' in receivedFrom.lower():
                        return
                    if 'seed pack' in receivedFrom.lower():
                        return
                    if "larran's big chest" in receivedFrom.lower():
                        return
                    if 'brimstone key' in receivedFrom.lower():
                        return
                try:
                    correct_auth = await check_auth(player_id, auth_token, serverid)
                except Exception as e:
                    print("An exception occured:", e)
                ##after we've iterated through each field
                ##we are still looping the embeds here
                if correct_auth is not None and correct_auth == True:
                    mainChannel = await interactions.get(bot, interactions.Channel, object_id=1122983028872978542)
                    if serverid == 1131575888937504798:
                        serverid = 616498757441421322
                    await drop_handler(bot, itemname, player_id, quantity, price, mainChannel, serverid, image_url,
                                       receivedFrom)


@bot.command(
    name="active",
    description="Uses your team's **active ability**. Will cast a vote inside the team channel."
)
async def use_active(ctx):
    server_id = ctx.guild_id if ctx.guild_id != 1131575888937504798 else 616498757441421322
    player_id = ctx.author.id
    player_team = await get_team_from_player(player_id)
    if player_team is None:
        await ctx.send(f"You are not on any teams.", ephemeral=True)
        return
    guild = await interactions.get(bot, interactions.Guild, object_id=ctx.guild.id)
    guild_roles = await guild.get_all_roles()
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    team_id = team_name_to_id(player_team)
    for item in current_data:
        if 'Number' in item:
            if int(item['Number']) == int(team_id):
                current_turn = item['currentTurn']
    is_in_cooldown, left = active_cooldowns.check_active(server_id, (current_turn), player_team.lower())
    print(f"Is in cooldown? {is_in_cooldown}. Amount left: {left}")
    if is_in_cooldown != False:
        await ctx.send(f"Your active ability is still in cooldown!\n> You can activate it again in `{left}` turns",
                       ephemeral=True)
        return
    if player_team == None:
        await ctx.send(f"You do not appear to be a member of any teams.", ephemeral=True)
        return
    try:
        print("Adding vote to the team.")
        success, amount = actives_object.add_vote(server_id, player_team, player_id)
        print(f"Amount now: {amount}")
    except Exception as e:
        print(f"Unable to add a vote to the team's active ability queue.\n{e}")
    if success:
        await ctx.send(f"Your vote has been added to your team's active ability.", ephemeral=True)
        if amount == 1:
            team_button = interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                emoji=interactions.Emoji(name='active', id=1163953192531411014),
                label='Vote!',
                custom_id=f"{player_team.lower()}_active_button"
            )

            found = False
            guild_channels = await guild.get_all_channels()
            chan_found = False

            for channel in guild_channels:
                if channel.name.lower() == player_team.lower():
                    if channel.type != interactions.ChannelType.GUILD_VOICE:
                        chan_found = True
                        team_channel = channel
            for role in guild_roles:
                if role.name.lower() == player_team.lower():
                    found = True
                    new_role = role
                    role_id = str(role.id)
            team_active_name, description = [s.strip() for s in team_actives[player_team.lower()].split(":")]
            team_active_name = team_active_name.replace("*", "").replace(":", "")
            team_active_name, cooldown = team_active_name.split("-")
            team_active_name, cooldown = team_active_name.replace("-", ""), cooldown.replace("-", "")
            cooldown = cooldown.replace(" turn cooldown", "")
            team_active_final = f"{team_active_name}\nCooldown {cooldown}\n> {description}"
            await team_channel.send(
                f"# <@&{role_id}>\n> ### <@{ctx.author.id}> has cast a vote to enable your team's **active ability**!\n")
            await team_channel.send(
                f"## <:active:1163953192531411014> {team_active_name} <:active:1163953192531411014>\n" +
                f"> ### {description}\n" +
                f"\n> Votes: {amount}/4", components=team_button)
            actives_object.save_to_file()
    else:
        await ctx.send(f"Either you have `already voted` for this active ability or you are `not on any teams.")
    print("")


@bot.event
async def on_interaction(interaction):
    global waiting_rolls
    global divine_intervention
    global ascendance
    print(f"Waiting rolls: {waiting_rolls}")
    serverid = interaction.guild_id
    if serverid == 1131575888937504798:
        serverid = 616498757441421322
    if interaction.type == interactions.InteractionType.MESSAGE_COMPONENT:
        # Check if the component type within the interaction is BUTTON
        if interaction.data.component_type == interactions.ComponentType.BUTTON:
            teams = []
            for i in range(9):
                if i == 0:
                    continue
                teams.append(team_id_to_name(i))
            for team in teams:
                print("Interaction customID: ", interaction.data.custom_id)
                if interaction.data.custom_id == f'{team}_select_button':
                    if team not in team_choices:
                        team_choices[team] = 1
                    else:
                        team_choices[team] += 1
                    await ref_updates(
                        f'<@{interaction.user.id}> requested to join {team}.\nTotal votes: {team_choices[team]}', '',
                        '', team)
                    await interaction.send(f"Your vote has been added for {team}", ephemeral=True)
                    return
                elif interaction.data.custom_id == f'{team.lower()}_active_button':
                    player_team = await get_team_from_player(interaction.user.id)
                    ## Check if the team's active cooldown is still in effect:
                    fp = f"data/{serverid}/events/lost_lands.json"
                    if os.path.exists(fp):
                        with open(fp, 'r') as jsonfile:
                            current_data = json.load(jsonfile)
                    team_id = team_name_to_id(team)
                    for item in current_data:
                        if 'Number' in item:
                            if int(item['Number']) == int(team_id):
                                current_turn = item['currentTurn']
                    is_in_cooldown, left = active_cooldowns.check_active(serverid, current_turn, team.lower())
                    print(f"Is in cooldown? {is_in_cooldown}. Amount left: {left}")
                    if is_in_cooldown != False:
                        await interaction.send(
                            f"Your active ability is still in cooldown!\n> You can activate it again in `{left}` turns",
                            ephemeral=True)
                        return
                    team_active_name, description = [s.strip() for s in team_actives[team.lower()].split(":")]
                    team_active_name = team_active_name.replace("*", "").replace(":", "")
                    team_active_name, cooldown = team_active_name.split("-")
                    team_active_name, cooldown = team_active_name.replace("-", ""), cooldown.replace("-", "")
                    if player_team == team:
                        success, amount = actives_object.add_vote(serverid, team.lower(), interaction.user.id)
                        print(f"Success? {success} Amount of votes: {amount}")
                        if success:
                            print("Success.")
                            channel = await interactions.get(bot, interactions.Channel,
                                                             object_id=interaction.channel_id)
                            past_msgs = await channel.get_history(100)
                            found = False
                            for msg in past_msgs:
                                if msg.components:
                                    for component in msg.components:
                                        if component.type == interactions.ComponentType.ACTION_ROW:
                                            for comp in component.components:
                                                if 'active_button' in comp.custom_id:
                                                    found = True
                                                    true_msg = msg
                                                    break
                            if found == False:
                                true_msg = await channel.send(f"Loading...")
                            print("Past the for msg in past_msgs...")
                            if amount < 4:
                                print("Less than 4 votes received?")
                                team_button = interactions.Button(
                                    style=interactions.ButtonStyle.PRIMARY,
                                    emoji=interactions.Emoji(name='active', id=1163953192531411014),
                                    label='Vote!',
                                    custom_id=f"{player_team.lower()}_active_button"
                                )
                                await true_msg.edit(
                                    f"## <:active:1163953192531411014> {team_active_name} <:active:1163953192531411014>\n" +
                                    f"> ### {description}\n" +
                                    f"\n> Votes: {amount}/4", components=team_button)
                                await interaction.send(
                                    f'Your vote has been cast. `{4 - amount} votes` are still required.',
                                    ephemeral=True)
                            else:
                                print("Required votes reached for an active ability.")
                                ## Required votes have been acquired, now we need to initialize the team active.
                                await activate_ability(bot, player_team, serverid)
                                print("Sent to activate_ability")
                                await true_msg.edit(
                                    f"<:active:1163953192531411014> {team_active_name} has been activated!")
                        else:
                            await interaction.send(f"You have already voted for this active ability!", ephemeral=True)
                    else:
                        await interaction.send(f"You must be on this team to vote for the active ability!")
                elif interaction.data.custom_id == f'{team.lower()}_roll_button':
                    sara_null = random.randint(1, 1000)
                    if not waiting_rolls.get(team.lower(), False):
                        await interaction.send(f"Unable to roll (this interaction expired / you have no roll waiting!)")
                        return
                    else:
                        fp = f"data/{serverid}/events/lost_lands.json"
                        found = False
                        current_data = []
                        global binding_actives
                        # dinhed = False
                        blank = ""
                        channel = await interactions.get(bot, interactions.Channel, object_id=interaction.channel_id)
                        past_msgs = await channel.get_history(100)
                        found = False
                        for msg in past_msgs:
                            if msg.components:
                                for component in msg.components:
                                    if component.type == interactions.ComponentType.ACTION_ROW:
                                        for comp in component.components:
                                            if 'roll_button' in comp.custom_id:
                                                found = True
                                                true_msg = msg
                                                break
                        if found == True:
                            await true_msg.delete()
                        if os.path.exists(fp):
                            with open(fp, 'r') as jsonfile:
                                current_data = json.load(jsonfile)
                        team_locations = {}
                        team_data = {}
                        for item in current_data:
                            if 'Number' in item:
                                if int(item['Current Tile']) > 1:
                                    team_locations[item['Team name']] = item['Current Tile']
                                    team_data[item['Team name']] = {"id": item['Number'],
                                                                    "role": item['roleID'],
                                                                    "channel": item['Thread ID']}
                        will_spawn = False
                        sara_chance = random.randint(1, 100)
                        for item in current_data:
                            if 'Board Tiles' in item:
                                board_tiles = item['Board Tiles']
                            if 'effectedTiles' in item:
                                effectedTiles = item['effectedTiles']
                                print("Found effected tiles stored in json: ", effectedTiles)
                            if 'Number' in item:
                                if item['Team name'].lower() == team.lower():
                                    current_loc = item['Current Tile']

                                    item['currentTurn'] += 1
                                    will_receive = False
                                    if team.lower() == "zaros":
                                        if random.randint(1, 100) >= 90:
                                            item_names = list(shop_emojis.keys())
                                            # Use random.choice to select a random item name from the list
                                            random_item_name = random.choice(item_names)
                                            random_item_data = shop_emojis[random_item_name]
                                            await ref_updates(
                                                f"**{item['Team name']}** has received a random item from the shop:\n**{random_item_name}**",
                                                '', '', '')
                                            team_chanob = await interactions.get(bot, interactions.Channel,
                                                                                 object_id=item['Thread ID'])
                                            await team_chanob.send(
                                                f"Your team has received a random item from the shop due to your passive ability: **{random_item_name}**")
                                            will_receive = True
                                    for itemss in item['Inventory']:
                                        if itemss['cooldown'] >= 1:
                                            itemss['cooldown'] -= 1
                                        if will_receive == True:
                                            if itemss['item'] == random_item_name:
                                                itemss['quantity'] += 1
                                    currentTurn = item['currentTurn']
                                    team_chan = item['Thread ID']
                                    if team.lower() == "guthix":
                                        new_roll = 2
                                    else:
                                        new_roll = random.randint(1, 4)
                                    if team.lower() == "guthix":
                                        lushtreechance = random.randint(1, 1000)
                                        if lushtreechance >= 900:
                                            will_spawn = True
                                            new_task = await taskManager(0, "air")
                                            new_quantity = await taskQuantity(team.lower(), new_task['taskNumber'],
                                                                              serverid)
                                            for team, tile in team_locations.items():
                                                # guthix_extra.bob_ross(serverid, tile)
                                                team_channel_id = team_data[team]["channel"]
                                                effected_object = await interactions.get(bot, interactions.Channel,
                                                                                         object_id=team_channel_id)
                                                team_role = team_data[team]["role"]
                                                new_task = await taskManager(0, "air")
                                                new_quantity = await taskQuantity(team.lower(), new_task['taskNumber'],
                                                                                  serverid)
                                                await effected_object.send(
                                                    f"<@&{team_role}>\nGuthix's *passive ability* has procced!\n" +
                                                    "As a result, you will be required to complete an additional air rune tier task on this tile:\n" +
                                                    f" {new_quantity} {new_task['task']}\n\n" +
                                                    f"This **will not** be tracked by the bot. Failure to complete it before rolling forward will result in penalties.\n" +
                                                    f"Post evidence of your completion of the above here, and tag a <@&1166538049757384725>.")
                                            # guthix_extra.bob_ross(serverid,current_loc)
                                    if team.lower() == "armadyl":
                                        if ascendance == True:
                                            new_roll *= 2
                                            blank += "\n <:active:1163953192531411014> Ability was active! `+2` added to the team's roll."
                                    if team.lower() == "seren":
                                        seren_chance = random.randint(1, 1000)
                                        if seren_chance >= 900:
                                            blank += "\n <:passive:1163953191789011016> Passive activated! `+1` added to the team's roll."
                                            new_roll += 1
                                        elif divine_intervention == True:
                                            blank += "\n<:active:1163953192531411014> Ability was active! You must select a task below to continue:"

                                    team_id = team_name_to_id(team.lower())
                                    sara_check = True if team.lower() == "saradomin" and sara_chance < 80 else False
                                    if int(frozen_states.get(int(item['Number']), 0)) == int(
                                            current_loc) and sara_check:
                                        blank += "\n > Your team was under the effects of an **Ice Barrage** <:IceBarrage:1119686930255315055>!"
                                        new_roll = 0
                                        frozen_states[int(item['Number'])] = 0
                                    # if inverted_roll.get(team.lower(), False) == True:
                                    #     if team.lower() != "guthix":
                                    #         new_roll *= -1
                                    #     inverted_roll[team.lower()] = False
                                    currentLoc = (current_loc + new_roll)
                                    teamPoints = item['Team Points']
                                    item['Current Tile'] = currentLoc
                                    teamPing = item['roleID']
                                    team_status_cache[int(team_id)] = 0
                                    for tile in board_tiles:
                                        if int(tile['number']) == int(currentLoc):
                                            current_rune = tile['type']
                                    item['Current Type'] = current_rune
                                    break

                        def find_type(number):
                            for tile in board_tiles:
                                if tile["number"] == number:
                                    return tile['type']

                        will_reroll = False
                        if "glowing_" in current_rune:
                            await ref_updates(f'{team.lower()} landed on a glowing rune!', '', '', '')
                            reroll_chance = random.randint(1, 1000)
                            if reroll_chance >= 800:
                                ### ZAMORAK IS RE-ROLLING EVERYBODY'S TASKS
                                # Cursed Catalyst - Have a 20% chance to reroll all team's quests on a glowing rune.
                                will_reroll = True
                                glowing, stripped_type = current_rune.split("_")
                                glowing, stripped_type = glowing.replace("_", ""), stripped_type.replace("_", "")
                            with open(f"data/glowing_tasks.json", 'r') as jsonfile:
                                glowing_tasks = json.load(jsonfile)
                            glowing_task = random.randint(1, 17)
                            glowing_assignment = glowing_tasks.get(str(glowing_task))
                            randomnum = random.randint(1, 100)
                            reward_text = ""
                            if randomnum >= 80:
                                reward_text = f"> 1st: 5 points.\n> 2nd: 3 points.\n> 3rd: 1 point."
                            elif randomnum >= 50 and randomnum < 80:
                                reward_text = f"> 1st: Move forward 2 tiles.\n2nd: Move forward 1 tile.\nNote: `Tasks do not get re-rolled`"
                            else:
                                reward_text = f"> 1st: Free random shop item\n> 2nd: 5 points.\n> 3rd: 3 points."

                            for data in current_data:
                                if 'Number' in data:
                                    team_channel_id = data['Thread ID']
                                    team_role_id = data['roleID']
                                    team_chanobj = await interactions.get(bot, interactions.Channel,
                                                                          object_id=team_channel_id)
                                    if glowing_assignment['task'] == "Purple Hunters":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Purple Hunters**\n" +
                                            f"Compete to be the first team to acquire ANY of the rare and coveted unique items that can be found within the chambers of the challenging Raids.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Helm of the Fremennik":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Helm of the Fremennik**\n" +
                                            f"Test your luck at Barbarian Assault's High Level Gambles as you strive to be the first team to obtain a prized Fremennik Helm.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Cave Race":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Cave Race**\n" +
                                            f"Put your speed and combat prowess to the test by achieving the fastest average completion time for a single run through the perilous TzHaar Fight Caves.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Teleportation Tango":
                                        if int(data['Current Tile']) >= int(currentLoc):
                                            difference = int(currentLoc) - int(data['Current Tile'])
                                        else:
                                            difference = int(data['Current Tile']) - int(currentLoc)
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a Glowing Rune, and rolled **Teleportation Tango**!\n" +
                                            f"### All teams have been teleported to their current location: `{currentLoc}` ({difference})\n" +
                                            f"\nYour task has **not been re-rolled** in the process, however.")
                                        data['Current Tile'] = currentLoc
                                    elif glowing_assignment['task'] == "Forgotten Warriors":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Forgotten Warriors**\n" +
                                            f"Seek and collect a full set of either Skeletal, Rock-shell, or Spined Armor as your team competes to be the first to assemble these often-overlooked, yet formidable sets of gear.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Trophy Fishermen":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Trophy Fishermen**\n" +
                                            f"Prove your angling skills by being the first to obtain a Trophy fish!\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Hell's Kitchen":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Hell's Kitchen**\n" +
                                            f"Delight in the culinary delights of the Gnome Restaurant and compete to be the first team to obtain a unique reward.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Mage Arena Showdown":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Mage Arena Showdown**\n" +
                                            f"The first team to defeat the Mage Arena II bosses and claim their capes will be victorious.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Champion Scrolls":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Champion Scrolls**\n" +
                                            f"Teams race to obtain 3 different Champion Scrolls by defeating various Champion monsters and presenting the scrolls as proof of their dominance.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Hallowed Sepulchre":
                                        await team_chanobj.send(
                                            f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                            f"**Hallowed Sepulchre**\n" +
                                            f"Race through the Hallowed Sepulchre and have the fastest average time on each floor. The fastest average time per team, per floor will be granted a point value and the team with the most points wins.\n" +
                                            f"The rewards:\n{reward_text}")
                                    elif glowing_assignment['task'] == "Rune of Radiance":
                                        if int(data['Number']) == int(team_id):
                                            await team_chanobj.send(
                                                f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, starting a board-wide event!\n" +
                                                f"**Rune of Radiance**\n" +
                                                f"The enchanting energy of the Radiance Rune illuminates your team's way, enabling you to progress forward by two tiles on the game board.\n" +
                                                f"The rewards:\n{reward_text}")
                                            data['Current Tile'] += 2
                                    elif glowing_assignment['task'] == "Rune of Augmentation":
                                        if int(data['Number']) == int(team_id):
                                            await team_chanobj.send(
                                                f"<@&{team_role_id}>\n> Your team has landed on a Glowing Rune, which had the following effects:\n" +
                                                f"**Rune of Augmentation**\n" +
                                                f"This enchanted rune infuses your team with the essence of anticipation, doubling the power of your next roll, propelling your progress forward in the game.\n")
                                    elif glowing_assignment['task'] == "Rune of Harmony":
                                        current_rune_type = current_rune.replace("glowing_", "").replace("cracked_", "")
                                        current_data_type = data['Current Type'].replace("glowing_", "").replace(
                                            "cracked_", "")
                                        if current_data_type == current_rune_type:
                                            await team_chanobj.send(
                                                f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, with board-wide effects!\n" +
                                                f"**Rune of Harmony**\n" +
                                                f"Upon activation, this luminous rune bathes the entire game board in a serene radiance, bringing teams together in a harmonious dance of progression. All teams on the same rune difficulty move forward one tile, benefiting from the newfound harmony it creates.\n" +
                                                f"")
                                            data['Current Tile'] += 1
                                    elif glowing_assignment['task'] == "Gales of Adaptation":
                                        if int(data['Number']) == int(team_id):
                                            current_rune_type = current_rune.replace("glowing_", "").replace("cracked_",
                                                                                                             "")
                                            new_task = await taskManager(currentLoc, current_rune)
                                            if new_task['quantity'] > 1:
                                                new_task['quantity'] -= int(new_task['quantity'] / 2)
                                                halved_task[team.lower()] = True
                                                effects = f"Your task quantity has been reduced in half! Required: `{new_task['quantity']}`"
                                            else:
                                                water_emoji = await getRuneEmoji('water')
                                                air_emoji = await getRuneEmoji('air')
                                                earth_emoji = await getRuneEmoji('earth')
                                                fire_emoji = await getRuneEmoji('fire')
                                                if new_task['difficulty'] == "medium":
                                                    data['Current Type'] = 'air'
                                                    data['taskNumber'] = 0
                                                    effects = f"Your task difficulty has been reduced from {water_emoji} to {air_emoji}, and re-rolled:\n"
                                                elif new_task['difficulty'] == "hard":
                                                    data['Current Type'] = 'water'
                                                    data['taskNumber'] = 0
                                                    effects = f"Your task difficulty has been reduced from {earth_emoji} to {water_emoji}, and re-rolled:\n"
                                                elif new_task['difficulty'] == "elite":
                                                    data['Current Type'] = 'earth'
                                                    data['taskNumber'] = 0
                                                    effects = f"Your task difficulty has been reduced from {fire_emoji} to {earth_emoji}, and re-rolled:\n"
                                                else:
                                                    effects = f"None! You had a task quantity of 1 and it was an 'easy' tier! \n" + "### Ask a referee for your NEXT TASK to be modified, refer to this message!"
                                                new_task = await taskManager(0, data['Current Type'])
                                                new_amount_req = await taskQuantity(data['Team name'],
                                                                                    new_task['taskNumber'], serverid)
                                                data['taskNumber'] = new_task['taskNumber']
                                                team_status_cache[data['Number']] = 0
                                                effects += f"> {new_amount_req} x {new_task['task']}"
                                                await team_chanobj.send(f"### GLOWING RUNE " +
                                                                        f"**Gales of Adaptation**\n" +
                                                                        f"Under the influence of this arcane wind, your team gains the ability to adapt swiftly. Your current task has become less demanding!\n" +
                                                                        f"The effects:\n> {effects}"
                                                                        f"")
                                    elif glowing_assignment['task'] == "Gales of Hospitality":
                                        if int(data['Number']) == int(team_id):
                                            chance_calc = random.randint(1, 100)
                                            if chance_calc >= 50:
                                                all_items = []
                                                for item_name, item_properties in shop_emojis.items():
                                                    all_items.append(item_name)
                                                random_item = random.choice(all_items)
                                                effects = f"You've received a random item from the shop: `{random_item}`"
                                            for inventory in data['Inventory']:
                                                if inventory['item'].lower() == random_item.lower():
                                                    inventory['quantity'] += 1
                                            else:
                                                coins = random.randint(1, 100)
                                                if coins >= 90:
                                                    coins = random.randint(4, 8)
                                                else:
                                                    coins = random.randint(1, 4)
                                                effects = f"You've earned some free coins for use in the shop: `{coins}`"
                                            await team_chanobj.send(
                                                f"<@&{team_role_id}>\n> {team.capitalize()} has landed on a glowing rune, with board-wide effects!\n" +
                                                f"**Rune of Harmony**\n" +
                                                f"A benevolent breeze envelops your team as you approach the radiant rune. Instead of sacrifice, this gust brings unexpected hospitality. The rune rewards your team with GP or an item from the shop, allowing you to choose your gift as a token of goodwill.\n" +
                                                f"Its effects: \n{effects}")
                                    await ref_updates(
                                        f"A glowing rune has been activated:\n{glowing_assignment['task']} by <@&{team_role_id}>\n>.",
                                        '', '', '')

                        if team.lower() != "zamorak":
                            will_reroll = False
                        if team.lower() != "guthix":
                            will_spawn = False
                        if will_reroll:
                            zam_emoji = get_team_emoji('zamorak')
                            for item in current_data:
                                if 'Number' in item:
                                    team_current = item['Current Type']
                                    if "glowing_" in team_current or "cracked_" in team_current:
                                        spec, team_type = team_current.split("_")
                                        spec, team_type = glowing.replace("_", ""), stripped_type.replace("_", "")
                                    else:
                                        team_type = team_current
                                    if stripped_type == team_type:
                                        print(
                                            "Team has the same rune type as zamorak as their passive ability procced, so they will be rerolled...")
                                        skip = False
                                        if team.lower() == "saradomin":
                                            if sara_null >= 7500:
                                                skip = True
                                        if skip == False:
                                            item['taskNumber'] = 0
                                            new_task = await taskManager(0, team_type)
                                            item['taskNumber'] = new_task['taskNumber']
                                            team_chan_id = item['Thread ID']
                                            team_role = item['roleID']
                                            team_status_cache[item['Number']] = 0
                                            team_chanob = await interactions.get(bot, interactions.Channel,
                                                                                 object_id=team_chan_id)
                                            await team_chanob.send(
                                                f"# Hey, <@&{team_role}>! Bad news!\n### <{zam_emoji}> Zamorak landed on a **glowing rune**, and their <:passive:1163953191789011016> Passive Ability procced!\n" +
                                                f"Since you were both on `{team_type}` rune types, your task has been **RE-ROLLED**!\n\n" +
                                                f"### Your new assignment:\n> `{new_task['quantity']}` x `{new_task['task']}`")
                        ## Handle cracked/glowing runes
                        waiting_rolls[team.lower()] = False
                        team_channel = await interactions.get(bot, interactions.Channel, object_id=team_chan)
                        # if dinhed == True:
                        #     await team_channel.send(f"# <@&{teamPing}>\n### <:DinhsBulwark:1119687103505248347> Your team has hit a Dinh's bulwark on tile `#{currentLoc}`\n" +
                        #                             f"> The dinh's has been destroyed in the process, but your roll has been reduced from `{new_roll}` to `{current_loc - currentLoc}`")
                        print(f"Current rune: {current_rune}")
                        if "cracked_" in current_rune:
                            if mending.get(team_id, False) == True:
                                if random.randint(1, 100) >= 50:
                                    skip = True
                                    await team_channel.send(
                                        f"Your Ward of Mending has shattered after nullifying this cracked rune.")
                                    mending[team_id] = False
                            skip = False
                            if team.lower() == "saradomin":
                                if sara_null >= 7500:
                                    skip = True
                            if skip == False:
                                cracked_task, hasReacted = await get_cracked(team.lower(), serverid, currentLoc)
                                if hasReacted == True:
                                    print("New cracked rune")
                                    ## Handle a newly assigned cracked rune
                                    if cracked_task['teamOnly'] == True:
                                        if cracked_task['task'].lower() == "rune of instability":
                                            for item in current_data:
                                                if 'Number' in item:
                                                    if item['Team name'].lower() == team.lower():
                                                        item['Current Tile'] -= 1
                                                        ## Move the team back 1 tile without changing their task.
                                        elif cracked_task['task'].lower() == "rune of inversion":
                                            inverted_roll[team.lower()] = True
                                        elif cracked_task['task'].lower() == "tempest of the abyss":
                                            for item in current_data:
                                                if 'Number' in item:
                                                    if item['Team name'].lower() == team.lower():
                                                        item['Team Points'] -= 4
                                        elif cracked_task['task'].lower() == "tempest of erosion":
                                            for item in current_data:
                                                if 'Number' in item:
                                                    if item['Team name'].lower() == team.lower():
                                                        item['Team Points'] -= 8
                                        else:
                                            await ref_updates(
                                                f"WE NEED TO HANDLE A TEAM-ONLY CRACKED EFFECT FOR {team.lower()} :)",
                                                '', '', '')
                                        print("team-only cracked task...")
                                        ## send the message only to the team
                                        await team_channel.send(
                                            f"<:cracked:1165405245954871326> Your team has landed on a cracked rune.\n<@&{teamPing}>\n" +
                                            "> The cracked rune has only effected your team, as its power was too weak to reach any further.\n " +
                                            "\nThe cracked rune's effects:" +
                                            f"\n> Task name: {cracked_task['task']}" +
                                            f"\n> Description: {cracked_task['description']}\n\n")
                                        await ref_updates(
                                            f"Cracked effect for {team.lower()}:\n{cracked_task['task']} ({cracked_task['description']})",
                                            '', '', '')
                                    else:
                                        print("event-wide cracked task..")
                                        main_chanid = 1148240308467929178
                                        main_chan = await interactions.get(bot, interactions.Channel,
                                                                           object_id=main_chanid)
                                        mainEmbed = interactions.Embed(title="# <:cracked:1165405245954871326>",
                                                                       description=f"{team.capitalize()} has landed on a cracked rune!")
                                        mainEmbed.add_field(name="CRACKED EVENT",
                                                            value=f"### {cracked_task['task']}\n\n> {cracked_task['description']}")
                                        mainEmbed.add_field(name="All teams are being summoned!",
                                                            value="> Cracked runes throughout the Lost Lands have a chance of summoning all teams' participation in an event-wide competition!",
                                                            inline=False)
                                        mainEmbed.add_field(name="",
                                                            value="The <:cracked:1165405245954871326> Cracked Rune tasks begin 1 hour after they are queued.",
                                                            inline=False)
                                        unix_when = int((datetime.now() + timedelta(hours=1)).timestamp())
                                        mainEmbed.add_field(name="",
                                                            value=f"> This 'competition' will begin <t:{unix_when}:R>",
                                                            inline=False)
                                        await main_chan.send(f"@everyone", embeds=[mainEmbed])
                                        await ref_updates(
                                            f'@everyone\n\n# CRACKED TASK ROLLED\n> Event should begin in: <t:{unix_when}:R>\n> Rolled by: <@&{teamPing}>',
                                            f'', '', '')

                                else:
                                    print("Old cracked rune")

                                current_rune = current_rune.replace("cracked_", "")
                        print("Rolln button getting a new task: ", currentLoc, current_rune)
                        new_task = await taskManager(0, current_rune)
                        cracked = False
                        if team.lower() == "bandos":
                            cracked_chance = random.randint(1, 100)
                        for item in current_data:
                            if team.lower() == "bandos":
                                if cracked_chance >= 900:
                                    new_cracked = currentLoc - new_roll
                                    if 'Board Tiles' in item:
                                        for tile in item:
                                            if tile['number'] == int(new_cracked):
                                                past_type = tile['type']
                                                new_type = f"cracked_{past_type}"
                                                tile['type'] = new_type
                                                cracked = True
                            if 'Number' in item:
                                if int(item['Number']) == int(team_id):
                                    item['taskNumber'] = new_task['taskNumber']
                                    print("Updated the stored task number : ", item['taskNumber'])
                                if effectedTiles != []:
                                    for tile in effectedTiles:
                                        movement_tiles = list(range(current_loc, currentLoc - 1))
                                        print(f"Current loc: {current_loc} currentLoc: {currentLoc}")
                                        print(f"Movement tiles: {movement_tiles}")
                                        if any(tile for tile in effectedTiles if
                                               tile.get('type') == "dinh" and int(tile.get('tile')) in movement_tiles):
                                            print("Dinh is in the movement tiles?")
                                            dinh_teamid = tile.get('team', 0)
                                            dinh_teamname = team_id_to_name(dinh_teamid)
                                            if dinh_teamname.lower() == team.lower():
                                                skip = True
                                            skip = False
                                            if team.lower() == "saradomin":
                                                if sara_null >= 7500:
                                                    skip = True
                                            if team.lower() == "seren":
                                                if divine_intervention == True:
                                                    skip = True
                                            if skip == False:
                                                effect_hit_on = tile.get('tile')
                                                if int(effect_hit_on) < int(current_loc):
                                                    print(
                                                        f"Skipping a dinh effect, not sure why this was able to hit anyways? (dinh: {effect_hit_on} -> currentloc: {current_loc})")
                                                else:
                                                    print(f"Team will hit a dinh on tile {effect_hit_on}")
                                                    current_loc = currentLoc
                                                    currentLoc = effect_hit_on
                                                    await removeDinh(tile, serverid)
                                                    await team_channel.send(
                                                        f"# <@&{teamPing}>\n### <:DinhsBulwark:1119687103505248347> Your team has hit a Dinh's bulwark on tile `#{currentLoc}`\n" +
                                                        f"> The dinh's has been destroyed in the process, but your roll has been reduced from `{new_roll}` to `{current_loc - currentLoc}`")
                                                    item['Current Tile'] = currentLoc
                                        elif tile.get('type') == 'teletab' and int(tile.get('tile')) == int(currentLoc):
                                            tiles = 0
                                            direction = 0
                                            tiles = random.randint(1, 5)
                                            direction = random.randint(1, 10)
                                            if direction >= 7:
                                                ##Forward
                                                moved = 1
                                            else:
                                                moved = 0
                                            direct_txt = "foward" if moved == 1 else "backward"
                                            if moved == 0:
                                                tiles *= -1
                                            await ref_updates(
                                                f'<@&{teamPing}> hit a teleport tablet and it moved them {tiles} {direct_txt}.')
                                            item['Current Tile'] = int(item['Current Tile']) + tiles

                        # if team.lower() == "guthix":
                        #                 lush_tile = currentLoc
                        #                 lushtreechance = random.randint(1,1000)
                        #                 if lushtreechance >= 900:
                        #                     will_spawn = True
                        #                     guthix_extra.add_tile(serverid,lush_tile)
                        #                     if will_spawn == True:
                        #                         main_chanid = 1148240308467929178
                        #                         main_chan = await interactions.get(bot, interactions.Channel,object_id=main_chanid)
                        #                         await main_chan.send(f"@everyone\n# Guthix has spawned an additional air task on tile #`{lush_tile}`!\n" +
                        #                                             "Any team who lands here now must also complete the *lush tree task* created!")
                        # if guthix_extra.bob_ross(serverid,currentLoc) == True and team.lower() != "guthix":
                        #     skip = False
                        #     if team.lower() == "saradomin":
                        #         if sara_null >= 7500:
                        #             skip = True
                        #     if skip == False:
                        #         new_random_task = await taskManager(0, 'air')
                        #         new_task_amount = await taskQuantity(team.lower(), new_random_task['taskNumber'],serverid)
                        #         await ref_updates(f"@everyone\nBOB ROSS HAPPY TREES HAS PROCCED!\nTEAM EFFECTED:\n> {team.lower()} \nTile number:\n> {currentLoc}\n\n" +
                        #                         "WE NEED TO >>>MANUALLY<<< ENSURE THEY COMPLETE A DUPLICATE TASK:\n" +
                        #                         f"> {new_task_amount} x {new_random_task['task']}",'','','')
                        #         await team_channel.send(f"<@&{teamPing}> Your team has landed on a **LUSH TREE** spawned by **<:guthix:1163953193647083622> Guthix**!" +
                        #                                 "\nAs a result, you will be required to complete the task below in addition to your current task!\n" +
                        #                                 f"> {new_task_amount} x {new_random_task['task']}")
                        if team.lower() == "seren" and divine_intervention == True:
                            await sendSerenOptions(teamPing, team_chan, current_rune)
                        with open(fp, 'w') as jsonfile:
                            json.dump(current_data, jsonfile, indent=4)
                        print("Data saved.")
                        team_channel = await interactions.get(bot, interactions.Channel, object_id=team_chan)
                        team_history = await team_channel.get_history(50)
                        for message in team_history:
                            if message.components:
                                for component in message.components:
                                    if component.type == interactions.ComponentType.ACTION_ROW:
                                        try:
                                            await message.delete()
                                            break
                                        except:
                                            continue
                        taskUpdate = interactions.Embed(title="New Assignment",
                                                        description="Your team has rolled a new task!", color=0x00ff00)
                        taskUpdate.add_field(name="You rolled:", value=new_roll, inline=True)
                        taskUpdate.add_field(name="New location:", value=currentLoc, inline=True)
                        task_amt = await taskQuantity(team.lower(), new_task['taskNumber'], serverid)
                        taskUpdate.add_field(name="", value=f"> Your new task is {task_amt} x {new_task['task']}")

                        main_chanid = 1148240308467929178
                        main_chan = await interactions.get(bot, interactions.Channel, object_id=main_chanid)
                        mainEmbed = interactions.Embed(title=f"{team.capitalize()} has been assigned a new task!",
                                                       description=f"Roll: `{new_roll}` <:llandsdice:1122984846965358612>")
                        new_loctype = find_type(currentLoc)
                        new_locemoji = await getRuneEmoji(new_loctype)
                        mainEmbed.add_field(name="", value=f"{currentLoc - new_roll} → {new_locemoji} {currentLoc}",
                                            inline=False)
                        mainEmbed.add_field(name="New assignment", value=f"`{task_amt}` x {new_task['task']}",
                                            inline=False)
                        mainEmbed.add_field(name="Team points", value=f"> <:1GP:980287772491403294> `{teamPoints}`",
                                            inline=False)
                        if cracked == True:
                            mainEmbed.add_field(name=f"<:passive:1163953191789011016> Passive procced!",
                                                value=f"<:bandos:1163953194527883374> Bandos has created a new **cracked rune**" +
                                                      f" on tile number `{currentLoc - new_roll}`!\n" +
                                                      f"This will, however, not appear on the physical board!")
                        mainEmbed.set_footer(text=f"{global_footer} | Turn #: {currentTurn}")
                        await main_chan.send(f"", embeds=[mainEmbed])
                        await team_channel.send(f"", embeds=[taskUpdate])
                        if team.lower() == "seren":
                            divine_intervention = False
                        halved_task[team.lower()] = False
                elif interaction.data.custom_id == f'referee_support':
                    targ_guild = await interactions.get(bot, interactions.Guild, object_id=interaction.guild.id)
                    support_channel = await targ_guild.create_channel(name=f"{interaction.user.username}-support",
                                                                      parent_id=1166520249319968848,
                                                                      type=interactions.ChannelType.GUILD_TEXT)
                    memberob = await interactions.get(bot, interactions.Member, object_id=interaction.user.id,
                                                      guild_id=interaction.guild.id)
                    new_link = f"https://discord.com/channels/{interaction.guild.id}/{support_channel.id}"
                    await interaction.send(f"Opened a new channel for you: {new_link}", ephemeral=True)
                    close_button = interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        emoji=interactions.Emoji(name="closeticket", id=1166522776627204106),
                        label=f"Close ticket",
                        custom_id=f"close_button"
                    )
                    await support_channel.send(
                        f"{interaction.user.mention} has opened a ticket\n> ### @everyone\n\nSo, `{interaction.user.username}`, how can we help you?",
                        components=[close_button])
                    return
                elif interaction.data.custom_id == 'close_button':
                    try:
                        targ_channel = await interactions.get(bot, interactions.Channel,
                                                              object_id=interaction.channel_id)
                        await interaction.send("This channel will be removed in 30 seconds.")
                        await asyncio.sleep(30)
                        await targ_channel.delete()
                    except Exception as e:
                        await interaction.send(f"Unable to remove this channel.")
                elif interaction.data.custom_id == "seren_choice_1" or interaction.data.custom_id == "seren_choice_2":
                    player_team = get_team_from_player(int(interaction.user.id))
                    if player_team.lower() != "seren":
                        await interaction.send(f"You are not on Seren, so you can't make choices for them!")
                        return
                    if not divine_intervention:
                        await interaction.send(f"Your team does not currently have divine intervention active!")
                        return
                    else:
                        if interaction.data.custom_id == "seren_choice_2":
                            task_selection = seren_options[1]
                        else:
                            task_selection = seren_options[0]
                        for item in current_data:
                            if 'Number' in item:
                                if item['Team name'].lower() == "seren":
                                    rolid = item['roleID']
                                    current_type = item['Current Type']
                        new_task = await taskManager(task_selection, current_type)
                        new_quantity = await taskQuantity('seren', new_task['taskNumber'], int(interaction.guild.id))
                        playername = interaction.user.nick if interaction.user.nick != None else interaction.user.username
                        await interaction.send(
                            f"<@&{rolid}>\n### {playername} has selected your new task: \n> {new_quantity} x {new_task}")
                        await interaction.message.delete()
                        seren_options = []
                        divine_intervention = False


@bot.command(
    name="cooldowns",
    description="View your current item/active cooldowns.",
    options=[
        interactions.Option(
            name="team_name",
            description="Would you like to view another team's cooldowns? (Ref only)",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def view_cooldowns(ctx, team_name: str = ""):
    cooldowns = {
        "bandos": 5,
        "zamorak": 6,
        "armadyl": 6,
        "tumeken": 5,
        "seren": 4,
        "guthix": 5,
        "saradomin": 6,
        "zaros": 4,
        "xeric": 5
    }
    server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    found = False
    current_data = []
    global binding_actives
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    ref = False
    if team_name != "":
        player_obj = await interactions.get(bot, interactions.Member, object_id=ctx.author.id, guild_id=ctx.guild.id)
        for role in player_obj.roles:
            if role == 1166538049757384725:
                ref = True
        if ctx.author.id == 528746710042804247:
            ref = True
        if ref == False:
            await ctx.send(
                "You do not have permission to view another team's cooldowns.\n> This command is reserved for Referees.")
            return
        player_team = team_name.lower()
    else:
        player_team = await get_team_from_player(ctx.author.id)
    cooldownEmbed = interactions.Embed(title="Current Cooldowns", description=f"Your current item/ability cooldowns:")
    for item in current_data:
        if 'Number' in item:
            if item['Team name'].lower() == player_team.lower():
                current_location = item['Current Tile']
                current_turn = item['currentTurn']
                rune_emoji = await getRuneEmoji((item['Current Type']))
                cooldownEmbed.add_field(name="Current Turn",
                                        value=f"{current_turn} (Tile #{current_location} / {rune_emoji})", inline=False)
                team_inventory = item['Inventory']
                team_points = item['Team Points']
                enchanted_cooldown = 0
                trap_cooldown = 0
                defensive_cooldown = 0
                offensive_cooldown = 0
                for object in team_inventory:
                    current_cooldown = object['cooldown']
                    if current_cooldown >= 1:
                        item_type = get_item_type_from_shop(object['item'], shop_emojis)
                        if item_type == "t":
                            trap_cooldown += current_cooldown
                        elif item_type == "d":
                            defensive_cooldown += current_cooldown
                        elif item_type == "e":
                            enchanted_cooldown += current_cooldown
                        elif item_type == "o":
                            offensive_cooldown += current_cooldown
                cooldownEmbed.add_field(name=f"Offensive Items", value=f"{offensive_cooldown}/2 turns left",
                                        inline=True)
                cooldownEmbed.add_field(name=f"Defensive Items", value=f"{defensive_cooldown}/2 turns left",
                                        inline=True)
                cooldownEmbed.add_field(name=f"Trap Items", value=f"{trap_cooldown}/2 turns left", inline=True)
                cooldownEmbed.add_field(name=f"Enchanted Items", value=f"{enchanted_cooldown}/3 turns left",
                                        inline=True)
    is_cooldown_active, turns_left = active_cooldowns.check_active(server_id, current_turn, player_team)
    if is_cooldown_active:
        # If the ability is on cooldown, inform the user how many turns are left
        cooldownEmbed.add_field(name=f"<:active:1163953192531411014> Active Ability",
                                value=f"{turns_left}/{cooldowns[player_team.lower()]} turns left", inline=False)
    else:
        # If there's no cooldown, the ability can be used
        cooldownEmbed.add_field(name=f"<:active:1163953192531411014> Active Ability", value=f"Currently available!",
                                inline=False)
    cooldownEmbed.set_footer(text=f"Current team points: {team_points}")
    await ctx.send(embeds=[cooldownEmbed])


async def sendSerenOptions(role_id, chan_id, tile_type):
    global seren_options
    serverid = 616498757441421322
    channel = await interactions.get(bot, interactions.Channel, object_id=chan_id)
    text = f"Divine Intervention"
    new_image = textwrite.generate_image(text=text, is_header=True, centerpiece_image_url=None)
    image_obj = interactions.File(new_image)
    random_task1 = await taskManager(0, tile_type)
    random_task2 = await taskManager(0, tile_type)
    await taskQuantity
    while random_task1 == random_task2:
        random_task2 = await taskManager(0, tile_type)
    task1q = await taskQuantity("seren", random_task1['taskNumber'], serverid)
    task2q = await taskQuantity("seren", random_task2['taskNumber'], serverid)
    opt_text = f"{task1q} x {random_task1['task']}\n{task2q} x {random_task2}"
    options_image = textwrite.generate_image(text=text, is_header=False, centerpiece_image_url=None)
    options = interactions.File(options_image)
    selection_button1 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label=f"{task1q} x {random_task1['task']}",
        custom_id=f"seren_choice_1"
    )
    selection_button2 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label=f"{task2q} x {random_task2['task']}",
        custom_id=f"seren_choice_2"
    )
    await channel.send(files=[image_obj])
    await channel.send(f"<@&{role_id}>\nYou have a choice between two tasks:", files=[options],
                       components=[selection_button1, selection_button2])
    seren_options = [int(random_task1['taskNumber']), int(random_task2['taskNumber'])]
    return random_task1['taskNumber'], random_task2['taskNumber']


async def get_cracked(team_name, server_id, current_tile):
    cracked_task = cracked_storage.get_cracked(server_id, team_name, current_tile)
    with open(f"data/cracked_tasks.json", 'r') as jsonfile:
        cracked_tasks = json.load(jsonfile)

    team_only_tasks = [key for key, value in cracked_tasks.items() if value["teamOnly"] is True]
    non_team_only_tasks = [key for key, value in cracked_tasks.items() if value["teamOnly"] is False]
    if cracked_task is None:
        # 90% chance for teamOnly tasks and 10% chance for non-teamOnly tasks
        if random.random() < 0.9 and team_only_tasks:
            cracked_task = random.choice(team_only_tasks)
        elif non_team_only_tasks:  # Ensure the list is not empty
            cracked_task = random.choice(non_team_only_tasks)
        else:
            cracked_task = random.choice(team_only_tasks)  # Fallback in case non_team_only_tasks is empty
        cracked_assignment = cracked_tasks.get(str(cracked_task))
        return cracked_assignment, True

    cracked_assignment = cracked_tasks.get(str(cracked_task))
    return cracked_assignment, False


async def activate_ability(bot, team_name, server_id):
    global ascendance
    global divine_intervention
    print(f"ACTIVE ABILITY HAS BEEN ENABLED BY {team_name}")
    water_emoji = await getRuneEmoji('water')
    air_emoji = await getRuneEmoji('air')
    earth_emoji = await getRuneEmoji('earth')
    fire_emoji = await getRuneEmoji('fire')
    actives_object.clear_votes(server_id, team_name)
    fp = f"data/{server_id}/events/lost_lands.json"
    found = False
    current_data = []
    global binding_actives
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    if team_name.lower() == "bandos":
        ## WARSTRIKE
        ## All teams on the same rune type as bandos are moved back one tile and quests are re-rolled.
        for data in current_data:
            if 'Board Tiles' in data:
                board_tiles = data['Board Tiles']
            if 'Number' in data:
                team_id = data['Number']
                teamname = team_id_to_name(team_id)
                if teamname.lower() == "bandos":
                    bandos_rune_type = data['Current Type']
                    bandos_emoji = data['teamEmoji']
                    currentTurn = data['currentTurn']
                team_channel = data['Thread ID']
                team_role = data["roleID"]
                current_rune = data['Current Type']
                if current_rune == bandos_rune_type and teamname.lower() != "bandos":
                    if barrelchest[teamname] == False:
                        data['Current Tile'] -= 1
                        teamEmoji = data['teamEmoji']
                        team_chanob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                        for tile in board_tiles:
                            if tile['number'] == data['Current Tile']:
                                current_rune = tile['type']
                        new_task = await taskManager(0, current_rune)
                        data['taskNumber'] = new_task['taskNumber']
                        team_status_cache[int(team_id)] = 0
                        rune_emoji = await getRuneEmoji(current_rune)
                        if_string = ""
                        if new_task['description'] != "" and new_task['description'] != "none":
                            if_string += new_task['description']
                        await team_chanob.send(
                            f"# <@&{team_role}> <{teamEmoji}>\n<{bandos_emoji}> Bandos has used their <:active:1163953192531411014> *active ability*, **Warstrike**!\n" +
                            f"Your team was also on a `{current_rune.capitalize()}` rune tile, and so you've been moved back one!\n" +
                            f"\n> New location: {rune_emoji} `{data['Current Tile']}`\n" +
                            f"### Your new task is: {new_task['quantity']} x {new_task['task']}.\n" +
                            f"{if_string}")
                    else:
                        barrelchest[teamname] = False
        with open(fp, 'w') as jsonfile:
            json.dump(current_data, jsonfile, indent=4)
        print("Activating WARSTRIKE")
    elif team_name.lower() == "zamorak":
        ## Dark Disruption
        ## Reroll all team's quests and reduce the difficulty by one level for Zamorakian quests.
        for data in current_data:
            if 'Board Tiles' in data:
                board_tiles = data['Board Tiles']
            if 'Number' in data:
                team_channel = data['Thread ID']
                team_role = data["roleID"]
                team_id = data['Number']
                teamEmoji = data['teamEmoji']
                teamname = team_id_to_name(team_id)
                team_chanob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                zam_emoj = get_team_emoji('zamorak')
                if teamname.lower() == "zamorak":
                    currentnum = data['Current Tile']
                    current_rune = data['Current Type']
                    currentTurn = data['currentTurn']
                    effect = ""
                    rune_emoji = ""
                    print("Current rune type: ", current_rune)
                    if current_rune == "water":
                        data['Current Type'] = "air"
                        effect = f"(from {water_emoji} → {air_emoji})"
                        rune_emoji = air_emoji
                    elif current_rune == "earth":
                        data['Current Type'] = "water"
                        effect = f"(from {earth_emoji} → {water_emoji})"
                        rune_emoji = water_emoji
                    elif current_rune == "fire":
                        data['Current Type'] = "earth"
                        effect = f"(from {fire_emoji} → {earth_emoji})"
                        rune_emoji = earth_emoji
                    elif current_rune == "air":
                        effect = f"(nowhere! {air_emoji} → {air_emoji})"
                        rune_emoji = air_emoji
                    new_task = await taskManager(0, data['Current Type'])
                    data['taskNumber'] = new_task['taskNumber']
                    team_status_cache[int(team_id)] = 0
                    print("Current rune type: ", current_rune)
                    await team_chanob.send(
                        f"# <@&{team_role}> <{teamEmoji}>\n\nYour team has used your <:active:1163953192531411014> *active ability*, **Dark Disruption**!\n" +
                        f"Your task has been rerolled, one difficulty tier lower! {effect}\n" +
                        f"\n> New location: {rune_emoji} `{data['Current Tile']}`\n" +
                        f"### Your new task is: {new_task['quantity']} x {new_task['task']}.\n")
                    await sendTeamStatus(team_id, server_id)

                else:
                    current_rune = data['Current Type']
                    new_task = await taskManager(0, current_rune)
                    data['taskNumber'] = new_task['taskNumber']
                    team_status_cache[int(team_id)] = 0
                    current_rune_emoji = await getRuneEmoji(data['Current Type'])
                    await team_chanob.send(
                        f"# <@&{team_role}> <{teamEmoji}>\n<{zam_emoj}> Zamorak has used their <:active:1163953192531411014> *active ability*, **Dark Disruption**!\n" +
                        f"Your team's task has been re-rolled\n" +
                        f"> Your new task is: {new_task['quantity']} x {new_task['task']}.\n")
                    await sendTeamStatus(team_id, server_id)
                    await asyncio.sleep(0.25)
        with open(fp, 'w') as jsonfile:
            json.dump(current_data, jsonfile, indent=4)
        print("Activating DARK DISRUPTION")
    elif team_name.lower() == "armadyl":
        # Armadyl's ascendance
        ## Your next roll is doubled
        ascendance = True
    elif team_name.lower() == "tumeken":
        # Solar Flare
        # Force all teams ahead of Tumekenian to reroll their current quests.
        tumeken_loc = 100
        for data in current_data:
            if 'Number' in data:
                team_name = data['Team name']
                team_id = data['Number']
                if team_name.lower() == "tumeken":
                    tum_emoji = data['teamEmoji']
                    tumeken_loc = data['Current Tile']
                    currentTurn = data['currentTurn']
        for data in current_data:
            if 'Number' in data:
                team_name = data['Team name']
                team_id = data['Number']
                if team_name.lower() != "tumeken":

                    team_loc = data['Current Tile']
                    if int(team_loc) > int(tumeken_loc):
                        team_status_cache[int(team_id)] = 0
                        team_channel = data['Thread ID']
                        team_role = data["roleID"]
                        teamEmoji = data['teamEmoji']
                        current_type = data['Current Type']
                        new_task = await taskManager(0, data['Current Type'])
                        data['taskNumber'] = new_task['taskNumber']
                        channel_ob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                        await channel_ob.send(
                            f"# <@&{team_role}> <{teamEmoji}>\n<{tum_emoji}> Tumeken has used their <:active:1163953192531411014> *active ability*, **Solar Flare**!\n" +
                            f"Your task has been re-rolled, since your team was `{int(team_loc) - int(tumeken_loc)}` tiles ahead of their team!\n" +
                            f"> ### Your new task is {new_task['quantity']} x `{new_task['task']}`")

        print("Activating Solar Flare")
    elif team_name.lower() == "seren":
        ## Divine Intervention
        ## Remove all negative effects, gain immunity to traps, choose between 2 quests on the next roll
        ## Remove shadow barrage, ice barrage, etc if they're effective currently
        divine_intervention = True
        for item in current_data:
            if 'Number' in item:
                if item['Team name'].lower() == team_name.lower():
                    team_location = int(item['Current Tile'])
                    if int(frozen_states[item['Number']]) and int(frozen_states[item['Number']]) == int(team_location):
                        ##Removes a freeze
                        frozen_states[item['Number']] = 0
        ## TODO: Implement checking divine_intervention on a new task assignment
    elif team_name.lower() == "guthix":
        ## Necessary Pruning
        ## Reroll your current quest one difficulty lower.

        effect = ""
        rune_emoji = ""
        for data in current_data:
            if 'Number' in data:
                if data['Team name'].lower() == "guthix":
                    current_rune = data['Current Type']
                    if current_rune != "air":
                        if current_rune == "water":
                            data['Current Type'] = "air"
                            effect = f"(from {water_emoji} → {air_emoji})"
                            rune_emoji = air_emoji
                        elif current_rune == "earth":
                            data['Current Type'] = "water"
                            effect = f"(from {earth_emoji} → {water_emoji})"
                            rune_emoji = water_emoji
                        elif current_rune == "fire":
                            data['Current Type'] = "earth"
                            effect = f"(from {fire_emoji} → {earth_emoji})"
                            rune_emoji = earth_emoji
                    else:
                        effect = f"(nowhere! {air_emoji} → {air_emoji})"
                        rune_emoji = air_emoji
                    new_task = await taskManager(0, data['Current Type'])
                    team_channel = data['Thread ID']
                    team_role = data["roleID"]
                    team_id = data['Number']
                    currentTurn = data['currentTurn']
                    teamEmoji = data['teamEmoji']
                    teamname = team_id_to_name(team_id)
                    team_chanob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                    await team_chanob.send(
                        f"# <@&{team_role}> <{teamEmoji}>\n\nYour team has used your <:active:1163953192531411014> *active ability*, **Necessary Pruning**!\n" +
                        f"Your task has been rerolled, one difficulty tier lower! {effect}\n" +
                        f"\n> Location: {rune_emoji} `{data['Current Tile']}`\n" +
                        f"### Your new task is: {new_task['quantity']} x {new_task['task']}.\n")
        with open(fp, 'w') as jsonfile:
            json.dump(current_data, jsonfile, indent=4)
    elif team_name.lower() == "saradomin":
        ## Zilyana's Grace - Instantly complete your current quest and earn double rewards for its completion.
        await drop_handler(bot, "zilyana's grace", f"n/a", 1, 1, "n/a", server_id,
                           "http://www.droptracker.io/img/teams/active.png", "active")
        for data in current_data:
            if 'Number' in data:
                if data['Team name'].lower() == "saradomin":
                    current_rune = data['Current Type']
                    team_channel = data['Thread ID']
                    team_role = data["roleID"]
                    currentTurn = data['currentTurn']
                    teamEmoji = data['teamEmoji']
                    team_chanob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                    await team_chanob.send(
                        f"# <@&{team_role}> <{teamEmoji}>\n\nYour team has used your <:active:1163953192531411014> *active ability*, **Zilyana's Grace**!\n" +
                        f"Your task has been instantly completed, rewarding double! <:1GP:980287772491403294>\n")
    elif team_name.lower() == "zaros":
        randomnum = 7
        for item in current_data:
            if 'Number' in item:
                ## Random selection of the team that will be swapped
                if int(item['Number']) == randomnum:
                    stolen_task = item['taskNumber']
                    stolen_name = item['Team name'].lower()
                    team_status_cache[item['Number']] = 0
                    stolen_chan = item['Thread ID']
                    stolen_role = item['roleID']
                    activatedtype = item['Current Type']
                    team_id = team_name_to_id(team_name.lower())
                    team_status_cache[team_id] = 0
        for item in current_data:
            if 'Number' in item:
                if item['Team name'].lower() == team_name.lower():
                    ##This is the team who activated the ability, they will steal the task and give the old one to the above team.
                    old_task = item['taskNumber']
                    item['taskNumber'] = stolen_task
                    attack_chan = item['Thread ID']
                    attack_role = item['roleID']
                    effectedtype = item['Current Type']
        for item in current_data:
            if 'Number' in item:
                if item['Team name'].lower() == stolen_name:
                    item['taskNumber'] = old_task
        team_channelob = await interactions.get(bot, interactions.Channel, object_id=attack_chan)
        targ_channel = await interactions.get(bot, interactions.Channel, object_id=stolen_chan)
        text = f"Eldritch Manipulation\nSwap quests with another team (resets quest progress)"
        new_image = textwrite.generate_image(text=text, is_header=False, centerpiece_image_url=None)
        image_obj = interactions.File(new_image)
        ## new_stolen defines the new task for the team who had their task stolen
        new_stolen = await taskManager(old_task, effectedtype)
        ## new stealer defines the new task assigned to the team who activated the ability.
        new_stealer = await taskManager(stolen_task, activatedtype)
        await targ_channel.send(
            f"<@&{stolen_role}>\n> <:zaros:1163953273347256482> **Zaros** has used their active ability, swapping your quest with theirs!",
            files=[image_obj])
        await team_channelob.send(
            f"Your team has activated their <:active:1163953192531411014> *active ability*:\n**Eldritch Manipulation**\nYour task progress has been reset.\n" +
            f"\n> New task: {new_stolen['task']}\n(use `/task` for more details.)")
        ## Eldritch Manipulation
        ## Swap quests with another team (resets quest progress).
        ## Channel the eldritch powers of Zaros to weave a web of trickery.
        ## Activate this effect to instantly swap your team's quest with another team's quest, but beware, for all progress on both quests is reset.
    elif team_name.lower() == "xeric":
        print("Xeric")
        path = f'data/{server_id}/events'
        current_date = datetime.today().date()
        shop_file = f"shop_items({str(current_date)}).json"
        shop_loc = os.path.join(path, shop_file)
        if os.path.exists(shop_loc):
            with open(shop_loc, 'r') as jsonfile:
                shop_data = json.load()
        possible_selections = []
        selected_emojis = shop_data["selected_emojis"]
        for item_name, item_properties in shop_emojis.items():
            if item_properties["emoji"] not in selected_emojis:
                continue
            possible_selections.append(item_name)
        random_item = random.choice(possible_selections)
        for item in current_data:
            if 'Number' in item:
                if item['Team name'].lower() == 'xeric':
                    team_chan = item['Thread ID']
                    team_role = item['roleID']
                    team_inventory = item['Inventory']
                    for item in team_inventory:
                        if item['item'].lower() == random_item.lower():
                            item['quantity'] += 1
        team_chanobj = await interactions.get(bot, interactions.Channel, object_id=team_channel)
        await team_chanobj.send(
            f"<@&{team_role}>\nYour team's <:active:1163953192531411014> active ability has been activated.\n**Great Olm's Blessing**\nYou received:\n> `1x {random_item.capitalize()}`")
        ## Great Olm's Blessing -- Receive a random item from the shop as a gift.
    with open(fp, 'w') as jsonfile:
        json.dump(current_data, jsonfile, indent=4)

    active_cooldowns.use_active(server_id, currentTurn, team_name)
    cooldowns = {
        "bandos": 5,
        "zamorak": 6,
        "armadyl": 6,
        "tumeken": 5,
        "seren": 4,
        "guthix": 5,
        "saradomin": 6,
        "zaros": 4,
        "xeric": 5
    }
    cooldown_expiry = currentTurn + cooldowns[team_name.lower()]
    active_cooldowns.set_cooldown(server_id, team_name.lower(), cooldown_expiry)
    await ref_updates('Active Ability enabled', 'n/a', int(datetime.now().timestamp()), team_name)


@bot.command(
    name="assign",
    description="Assign players to a team for the lost lands event.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="player",
            description="Select the player you will be adding to the team",
            type=interactions.OptionType.MENTIONABLE,
            required=True
        ),
        interactions.Option(
            name="team",
            description="Which team are you adding them to?",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="captain",
            description="Is this player going to be the new team captain?",
            type=interactions.OptionType.BOOLEAN,
            required=False
        ),
        interactions.Option(
            name="colead",
            description="Will they be the new team co-captain?",
            type=interactions.OptionType.BOOLEAN,
            required=False
        ),
    ]
)
async def addplayer(ctx, player, team, captain: bool = False, colead: bool = False):
    await ref_updates('Player added to a team', f'{ctx.author.id}', 'now', team)
    serverid = ctx.guild.id
    if serverid == 1131575888937504798:
        serverid = 616498757441421322
    playerid = int(player.id)
    fp = f"data/{serverid}/events/lost_lands.json"
    teamid = team_name_to_id(team.lower())
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    memberct = 0
    for item in current_data:
        if 'Number' in item:
            print(f"Number in item. {item['Number']}/{teamid}")
            if int(item['Number']) == int(teamid):
                team_link = item['teamChannelLink']
                team_role = item['roleID']
                print(f"Set team role: {team_role}")
                if captain == True:
                    item['Team Captain'] = playerid
                elif colead == True:
                    item['colead'] = playerid
                members = item['Members']
                if item['Members'] != []:
                    members.append({"id": playerid,
                                    "points": 0})
                else:
                    members = ([{"id": playerid,
                                 "points": 0}])
                item['Members'] = members
                memberct += len(members)
                print("Team_role: ")
                team_role = await interactions.get(bot, interactions.Role, object_id=team_role)
                await player.add_role(team_role, ctx.guild.id, reason="Lost Lands")
    with open(fp, 'w') as jsonfile:
        json.dump(current_data, jsonfile, indent=4)
    await ctx.send(f"Added {player.username} to {team}.\n" +
                   f"Total members: {memberct}", ephemeral=True)
    team_emoji = get_team_emoji(team.lower())
    await player.send(f"# Lost Lands\n" +
                      f"### You have been assigned to a team for the upcoming event:\n" +
                      f"## <{team_emoji}> {team.capitalize()}\n"
                      f"> Your team's channel can be found here: {team_link}\n")
    await sendTeamStatus(teamid, serverid)


@bot.command(
    name="initializecool",
    description="Start the cooldowns for team active abilities.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def initialize_cooldowns(ctx):
    team_names = ["saradomin", "guthix", "zamorak", "tumeken", "bandos", "armadyl", "seren", "xeric", "zaros"]
    server_id = ctx.guild.id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    for team in team_names:
        active_cooldowns.initialize(server_id, 0, team)
    await ctx.send(f"Initialized all team active ability cooldowns.", ephemeral=True)
    active_cooldowns.save_to_file()


@bot.command(
    name="set_item",
    description="Modify whether a team has an item active currently.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="team_name",
            description="Team name (string)",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="item",
            description="What item/local object are you changing?",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True
        ),
        interactions.Option(
            name="newval",
            description="What should the new value be?",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def set_item_admin(ctx, team_name, item, newval):
    server_id = ctx.guild.id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    if item == "leech":
        if leechward.get(team_name.lower(), False) == False:
            leechward[team_name.lower()] = True
            await ctx.send(f"Set {team_name.capitalize()} **Ward of the Leech** to active.", ephemeral=True)
        else:
            await ctx.send("Item was already active.", ephemeral=True)
    elif item == "serenity":
        serenity = True
        await ctx.send("Serenity activated.", ephemeral=True)
    if item == "mending":
        if mending.get(team_name.lower(), False) == False:
            mending[team_name.lower()] = True
            await ctx.send(f"Set {team_name.capitalize()} **Ward of the Leech** to active.", ephemeral=True)
        else:
            await ctx.send("Item was already active.", ephemeral=True)


@set_item_admin.autocomplete(name="item")
async def pointDictTypes(ctx, user_input: str = ""):
    type_list = [
        "leech", "serenity", mending
    ]
    choices = []
    for types in type_list:
        if user_input:
            if user_input.lower() in types.lower():  # Added .lower() to make the comparison case-insensitive
                choices += [interactions.Choice(name=f"{types.capitalize()} status", value=types)]
        else:
            choices += [interactions.Choice(name=f"{types.capitalize()} status", value=types)]
    await ctx.populate(choices)


@bot.command(
    name="setcooldown",
    description="Set the cooldown for a specific team's active ability.",
    options=[
        interactions.Option(
            name="team_name",
            description="Name of the team.",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="cooldown_expiry",
            description="Turn that their cooldown should expire on. Check /cooldowns for their current turn.",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def set_cooldown_command(ctx, team_name: str, cooldown_expiry: int):
    if ctx.author.id != 528746710042804247 and ctx.author.id != 322792646072336386 and ctx.author.id != 217849931984142346 and ctx.author.id != 966700986024476743:
        await ctx.send(f"You do not have permission to use this command.", ephemeral=True)
        return
    server_id = ctx.guild.id
    # Convert the server_id to the required format if necessary
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322

    # Set the cooldown for the specified team
    active_cooldowns.set_cooldown(server_id, team_name, cooldown_expiry)

    # Provide a confirmation message to the user
    await ctx.send(f"Cooldown for team '{team_name}' has been set to their {cooldown_expiry}st/th turn.",
                   ephemeral=True)

    # Save the updated cooldowns to a file
    active_cooldowns.save_to_file()


def get_team_emoji(teamname):
    team_emojis = {
        "bandos": ":bandos:1163953194527883374",
        "zamorak": ":zamorak:1163953196385976370",
        "armadyl": ":armadyl:1163953319316815965",
        "tumeken": ":tumeken:1163953238303842374",
        "seren": ":seren:1163953199309406349",
        "guthix": ":guthix:1163953193647083622",
        "saradomin": ":saradomin:1163953195404501054",
        "zaros": ":zaros:1163953273347256482",
        "xeric": ":xeric:1163953198147567777"
    }

    return team_emojis.get(teamname, None)  # Returns the emoji if exists, otherwise returns None


@bot.command(
    name="setcurrentstatus",
    description="Set the current stored team status",
    options=[
        interactions.Option(
            name="team",
            description="Which team are you modifying?",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="new_value",
            description="New task completion amount",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="task_number",
            description="Changing the task number?",
            type=interactions.OptionType.STRING
        ),
        interactions.Option(
            name="new_points",
            description="What amount of points are they supposed to have?",
            type=interactions.OptionType.INTEGER
        ),
        interactions.Option(
            name="new_location",
            description="What tile are they supposed to be on?",
            type=interactions.OptionType.INTEGER
        ),
        interactions.Option(
            name="silent",
            description="Silently modify the values, without pinging the team?",
            type=interactions.OptionType.BOOLEAN
        )
    ]
)
async def setcurrentstatus(ctx: interactions.CommandContext, task_number: str = "", team: str = "", new_value: int = 0,
                           new_points: int = 150, new_location: int = 150, silent: bool = False):
    try:
        team_id = int(team)
    except:
        team_id = team_name_to_id(team.lower())
    team = team_id
    if len(task_number) < 1:
        task_number = "none"
    if ctx.author.id != 528746710042804247 and ctx.author.id != 322792646072336386 and ctx.author.id != 217849931984142346 and ctx.author.id != 966700986024476743:
        return
    if ctx.author.id != 528746710042804247 and silent == True:
        silent = False
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfile:
        data = json.load(jsonfile)
    for item in data:
        if 'Number' in item:
            print(item['Number'], team)
            if int(item['Number']) == int(team):
                if task_number != "none":
                    item['taskNumber'] = str(task_number)
                if new_points != 150:
                    item['Team Points'] = new_points
                if new_location != 150:
                    item['Current Tile'] = new_location
                item['Status'] = new_value
                effected_team_channel = item['Thread ID']
                teamRoleID = item['roleID']
                with open(f"data/{server_id}/events/lost_lands.json", 'w') as jsonfile:
                    json.dump(data, jsonfile, indent=4)
                if silent == False:
                    changedChan = await interactions.get(bot, interactions.Channel, object_id=effected_team_channel)
                    await changedChan.send(
                        f"Hey, <@&{teamRoleID}>\nYour task status, location, or points have been corrected by a staff member. Check it with `/task`.")
    team_status_cache[int(team)] = new_value
    print(team_status_cache)
    await ctx.send("Set the team's current status.", ephemeral=True)
    await sendTeamStatus(int(team), server_id)
    # correct_token = await playerfiles.check_auth(player_uid, auth_token, serverid)


@bot.command(
    name="force_active",
    description="Send active ability (forbily) for team",
    options=[
        interactions.Option(
            name="team_name",
            description="Team name (string)",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def force_active(ctx, team_name: str = ""):
    authorid = str(ctx.author.id)
    if authorid != "528746710042804247" and authorid != "217849931984142346" and authorid != "966700986024476743":
        await ctx.send(f"You do not have permissions to use this command!")
        return
    player_team = team_name.lower()
    serverid = 616498757441421322
    await activate_ability(bot, player_team, serverid)
    await ctx.send(f"Forced the activation of an ability for {team_name}")


@bot.command(
    name="submit",
    description="Manually submit an item for your team's current Lost Lands task",
    options=[
        interactions.Option(
            name="itemname",
            description="What item are you submitting?",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="image_url",
            description="A valid image url is **REQUIRED**! Check the event rules for info.",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="quantity",
            description="How many of the item did you receive?",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def submitcmd(ctx: interactions.CommandContext, itemname: str, image_url: str = "", quantity: int = 1):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    mainChannel = await interactions.get(bot, interactions.Channel, object_id=1122983028872978542)
    print(f"ctx author: {ctx.author.id}")
    print(f"They are submitting an {itemname} with imgaeurl {image_url} quantity {quantity}")
    tresponse = await ctx.send(f"Attempting to submit a drop....")

    def is_valid_image_url(url):
        # List of valid image file extensions
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif']

        # Parse the URL
        parsed = urlparse(url)

        # Check if it's a valid URL
        if bool(parsed.netloc) and bool(parsed.scheme):
            # Check if it points to a valid image file
            return any(parsed.path.endswith(ext) for ext in image_extensions)

        return False

    if is_valid_image_url(image_url):
        if server_id == 1131575888937504798:
            server_id = 616498757441421322
        await drop_handler(bot, itemname, str(ctx.author.id), quantity, 0, mainChannel, server_id, image_url, "manual")
    else:
        await tresponse.edit(f"You need to enter a valid image URL for your submission!\n" +
                             f"{image_url}\n" +
                             "The link must end in `.png`, `.jpg`, `.jpeg` or `.gif`.\n" +
                             "Use this webpage to generate a valid URL:\nhttp://www.droptracker.io/ll/")


last_executions = {}
last_drops = collections.deque(maxlen=5)


async def drop_handler(bot, itemname, player_id, quantity, price, mainChannel, serverid, image_url, receivedFrom):
    global last_drops
    lost_data = f"data/{serverid}/events/lost_lands.json"
    global is_editing
    drop_id = f"{itemname}-{player_id}-{quantity}-{price}"
    ##TODO WHEN RUNELITE UPDATES REMOVE DEQUE SYSTEM
    if drop_id in last_drops:
        return
    if os.path.exists(lost_data):
        with open(lost_data, 'r') as f:
            game_object = json.load(f)
        playerteam = False
        finalFound = False
        for i in range(len(game_object)):
            if 'Number' in game_object[i]:
                team_members = game_object[i]['Members']
                if itemname.lower() == "zilyana's grace":
                    teamnum = team_name_to_id("saradomin")
                    if int(teamnum) == i:
                        print(f"Team name : {game_object[i]['Team name']}")
                        current_task = game_object[i]['taskNumber']
                        current_type = game_object[i]['Current Type']
                        currentLoc = game_object[i]['Current Tile']
                        task_details = await taskManager(current_task, current_type)
                        task_amt = task_details['quantity']
                        per_member = task_details['per']
                        memberct = len(game_object[i]['Members'])
                        teamname = game_object[i]['Team name']
                        playerteam = True
                        teamnum = game_object[i]['Number']
                        teamPing, teamChannel = game_object[i]['roleID'], game_object[i]['Thread ID']
                        current_assignment = task_details['task']
                        teamLink = game_object[i]['teamChannelLink']
                        mercy_rule = datetime.strptime(game_object[i]['mercyRule'], "%Y-%m-%d %H:%M:%S.%f")
                        team_cap = game_object[i]['Team Captain']
                if str(player_id) == str(game_object[i]['Team Captain']):
                    team_cap = game_object[i]['Team Captain']
                    current_task = game_object[i]['taskNumber']
                    current_type = game_object[i]['Current Type']
                    currentLoc = game_object[i]['Current Tile']
                    task_details = await taskManager(current_task, current_type)
                    task_amt = task_details['quantity']
                    per_member = task_details['per']
                    memberct = len(game_object[i]['Members'])
                    teamname = game_object[i]['Team name']
                    playerteam = True
                    teamnum = game_object[i]['Number']
                    teamPing, teamChannel = game_object[i]['roleID'], game_object[i]['Thread ID']
                    current_assignment = task_details['task']
                    teamLink = game_object[i]['teamChannelLink']
                    mercy_rule = datetime.strptime(game_object[i]['mercyRule'], "%Y-%m-%d %H:%M:%S.%f")
                else:
                    if isinstance(player_id, str):
                        if not playerteam:
                            if player_id != "n/a":

                                for member in team_members:
                                    if int(player_id) == int(member['id']):
                                        team_cap = game_object[i]['Team Captain']
                                        current_task = game_object[i]['taskNumber']
                                        currentLoc = game_object[i]['Current Tile']
                                        current_type = game_object[i]['Current Type']
                                        memberct = len(game_object[i]['Members'])
                                        mercy_rule = datetime.strptime(game_object[i]['mercyRule'],
                                                                       "%Y-%m-%d %H:%M:%S.%f")
                                        teamname = game_object[i]['Team name']
                                        task_details = await taskManager(current_task, current_type)
                                        task_amt = await taskQuantity(teamname, task_details['taskNumber'], serverid)
                                        per_member = task_details['per']
                                        teamPing, teamChannel = game_object[i]['roleID'], game_object[i]['Thread ID']
                                        teamLink = game_object[i]['teamChannelLink']
                                        current_assignment = task_details['task']
                                        playerteam = True
                                        teamnum = game_object[i]['Number']
            else:
                if isinstance(mainChannel, str):
                    mainChannel = await interactions.get(bot, interactions.Channel, object_id=1148240308467929178)
                elif mainChannel.id and int(mainChannel.id) != 1148240308467929178:
                    mainChannel = await interactions.get(bot, interactions.Channel, object_id=1148240308467929178)
                if 'Board Tiles' in game_object[i]:
                    board_tiles = game_object[i]['Board Tiles']
                if 'effectedTiles' in game_object[i]:
                    effectedTiles = game_object[i]['effectedTiles']
        last_drops.append(drop_id)
        is_editing = False
        if playerteam != True:
            return
        current_time = datetime.now()
        mercy_ruled = False
        if mercy_rule < current_time:
            mercy_ruled = True
            correct_item = True
        if playerteam == True:
            if task_details['npc'] != "none" and task_details['npc'] != "NEED NAME":
                if receivedFrom.lower() != task_details['npc'].lower():
                    print(f"{receivedFrom.lower()} != {task_details['npc']}")
                    if receivedFrom.lower() != "manual":
                        print("Invalid source for the task!")
                        return
                    else:
                        print("Manual submission passing npc checks...")
            if itemname == "zilyana's grace":
                correct_item, counted, isPart = True, task_amt, False
            else:
                correct_item, counted, isPart = await check_drop(itemname.lower(), current_assignment)
            counted = int(counted)
            if player_id in last_executions and current_time - last_executions[player_id] < 1:
                print("Waiting a few moments before checking this drop to avoid problems editing the file..")
                time.sleep(0.5)
                last_executions[player_id] = datetime.now()
            if itemname.lower() != "toktz-xil-ul":
                counted *= quantity
            if correct_item == True:
                print("Correct item: True")
                foundTile = False
                notificationGroupChannel = await interactions.get(bot, interactions.Channel, object_id=teamChannel)
                is_editing = True
                for i in range(len(game_object)):
                    if 'Number' in game_object[i]:
                        if game_object[i]['Number'] == teamnum:
                            print(f"We've counted {counted} {itemname} for this drop...")
                            team_name = team_id_to_name(game_object[i]['Number'])
                            task_amt = await taskQuantity(team_name, game_object[i]['taskNumber'], serverid)
                            if correct_item != True:
                                return
                            playerpoints = await player_points(counted, game_object[i]['taskNumber'], team_name,
                                                               serverid)
                            playerpoints = int(playerpoints)
                            member_pts = {}
                            try:
                                player_id = int(player_id)
                            except Exception as e:
                                print(f"Can't cast player ID to integer...")
                            for member in game_object[i]['Members']:
                                if isinstance(player_id, int):
                                    if int(member['id']) == int(player_id):
                                        member['points'] += playerpoints
                                        player_total = member['points']
                                member_pts[member['id']] = member['points']
                            top_members = sorted(member_pts, key=lambda x: member_pts[x], reverse=True)
                            all_ranks = await eventMvpCalc(serverid)
                            if isinstance(player_id, int):
                                player_overall = all_ranks.index(int(player_id)) + 1
                                player_rank = top_members.index(int(player_id)) + 1
                            else:
                                player_overall = 0
                                player_rank = 0
                            print(f"Player earned {playerpoints} for their contribution to this task.")
                            team_status_cache[game_object[i]['Number']] = team_status_cache.get(
                                game_object[i]['Number'], 0) + counted
                            print(f"Current team completion status: {team_status_cache[game_object[i]['Number']]}")
                            task_amt = await taskQuantity(team_name, game_object[i]['taskNumber'], serverid)

                            if per_member == True and isPart != True:
                                team_name = game_object[i]['Team name'].lower()
                                print(f"Required quantity for {game_object[i]['taskNumber']}: {task_amt}")
                                print(f"Task amt: {task_amt}")
                                print(f"Status: {team_status_cache[game_object[i]['Number']]}")
                                if mercy_ruled == True:
                                    current_status = task_amt
                                    print("Team was mercy ruled.")
                                else:
                                    current_status = team_status_cache[game_object[i]['Number']]
                                if itemname == "zilyana's grace":
                                    team_status_cache[game_object[i]['Number']] = task_amt + 1
                                    current_status = task_amt + 1
                                if current_status < task_amt:

                                    print("Task is incomplete..")
                                    if isinstance(player_id, int):
                                        msg = (
                                                    f"<@{player_id}> has received a {itemname} for your task: \n{task_details['task']} #`{current_status}/{task_amt}`\n" +
                                                    f"They've earned `{playerpoints}` (Total: `{player_total}`)\n> **Team rank**: {player_rank}\n" +
                                                    f"> **Overall rank**: {player_overall}\n" +
                                                    f"Your team is currently on tile `#{game_object[i]['Current Tile']}`, with <:1GP:980287772491403294> `{game_object[i]['Team Points']}` coins!")
                                    else:
                                        msg = (
                                                    f"<:active:1163953192531411014> **Zilyana's Grace** \n{task_details['task']} #`{current_status}/{task_amt}`\n" +
                                                    f"" +
                                                    f"> **Overall rank**: {player_overall}\n" +
                                                    f"Your team is currently on tile `#{game_object[i]['Current Tile']}`, with <:1GP:980287772491403294> `{game_object[i]['Team Points']}` coins!")
                                    if image_url != "none":
                                        msg += f"\n{image_url}"
                                    await notificationGroupChannel.send(msg)
                                    print(f"Saving the new file to {lost_data} ?")
                                    try:
                                        with open(lost_data, 'w') as dumpf:
                                            json.dump(game_object, dumpf, indent=4)
                                    except Exception as e:
                                        print(f"Exception when writing to file: {e}")
                                    print("Saved.")
                                    is_editing = False
                                    await sendTeamStatus(i, serverid)
                                    break
                                else:
                                    print(f"{current_status} is greater than {task_amt}")

                            current_status = team_status_cache[game_object[i]['Number']]
                            print(f"isPart? {isPart}")
                            if isPart == True:
                                print("Ispart")
                                parts_obt = []
                                current_pieces = game_object[i]['taskItemsObtained']
                                for parts in current_pieces:
                                    if parts['item'].lower() == itemname.lower():
                                        return
                                    parts_obt.append(parts['item'])
                                player_name = await playerfiles.get_name_from_id(player_id, serverid)
                                game_object[i]['taskItemsObtained'].append(
                                    {'item': itemname, 'player': player_name, 'team': i})
                                try:
                                    print("Checking completion")
                                    finished, remaining = await checkCompletion(game_object[i]['taskItemsObtained'],
                                                                                task_details['task'], serverid)
                                    if finished == True:
                                        game_object[i]['taskItemsObtained'] = []
                                        game_object[i]['Status'] = 0
                                        team_status_cache[game_object[i]['Number']] = 0
                                except Exception as e:
                                    print(f"Error: {e}")
                                required_str = ""
                                if remaining != [] and len(remaining) < 10:
                                    required_str += "**Items left**: "
                                    required_str += ", ".join([f"`{item}`" for item in remaining])
                                if finished != True:
                                    msg = (
                                                f"<@{player_id}> has received a {itemname} for your task: \n{task_details['task']}\n" +
                                                f"Items remaining:\n> `{required_str}`\n" +
                                                f"Your team is currently on tile `#{game_object[i]['Current Tile']}`, with <:1GP:980287772491403294> `{game_object[i]['Team Points']}` coins!")
                                    if image_url != "none":
                                        msg += f"\n{image_url}"
                                    await notificationGroupChannel.send(msg)
                                    await sendTeamStatus(i, serverid)
                                    with open(lost_data, 'w') as dumpf:
                                        json.dump(game_object, dumpf, indent=4)
                                    await send_lost_board(serverid)
                                    is_editing = False
                                    return
                            elif current_status < task_amt:
                                print(f"Status: {current_status} amount: {task_amt}")
                                msg = (
                                            f"<@{player_id}> has received a {itemname} for your task: \n{task_details['task']} #`{current_status}/{task_amt}`\n" +
                                            f"They've earned `{playerpoints}` (Total: `{player_total}`)\n> **Team rank**: {player_rank}\n" +
                                            f"> **Overall rank**: {player_overall}\n" +
                                            f"Your team is currently on tile `#{game_object[i]['Current Tile']}`, with <:1GP:980287772491403294> `{game_object[i]['Team Points']}` coins!")
                                if image_url != "none":
                                    msg += f"\n{image_url}"
                                await notificationGroupChannel.send(msg)
                                print(f"Saving the new file to {lost_data} ?")
                                try:
                                    with open(lost_data, 'w') as dumpf:
                                        json.dump(game_object, dumpf, indent=4)
                                except Exception as e:
                                    print(f"Exception when writing to file: {e}")
                                print("Saved.")
                                is_editing = False
                                await sendTeamStatus(i, serverid)
                                return
                            ## check for ice barrage and assign them another new task
                            game_object[i]['taskNumber'] = 0
                            game_object[i]['Status'] = 0
                            game_object[i]['last_roll'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                            game_object[i]['mercyRule'] = str(datetime.now() + timedelta(days=1))

                            def find_type(number):
                                for tile in board_tiles:
                                    if tile["number"] == number:
                                        return tile['type']

                            team_name = team_id_to_name(i)
                            if actives_object.is_active(serverid, team_name, 'binding necklace'):
                                print("Binding necklace is active for this")
                                # deactivate the necklace first
                                actives_object.deactivate_item(serverid, team_name, 'binding necklace')
                                # find two new random rolls
                                new_roll_1 = random.randint(1, 4)
                                new_roll_2 = random.randint(1, 4)
                                if team_name.lower() == "seren":
                                    seren_chance = random.randint(1, 1000)
                                    if seren_chance <= 100:
                                        new_roll_1 += 1
                                    elif seren_chance > 100 and seren_chance <= 200:
                                        new_roll_2 += 1
                                while new_roll_2 == new_roll_1:
                                    new_roll_2 = random.randint(1, 4)
                                new_pos1, new_pos2 = currentLoc + new_roll_1, currentLoc + new_roll_2
                                new_type1, new_type2 = find_type(new_pos1), find_type(new_pos2)
                                new_task1 = await taskManager(0, new_type1)
                                new_task2 = await taskManager(0, new_type2)
                                if task_details['difficulty'] == "easy":
                                    earnedPts = 1
                                elif task_details['difficulty'] == "medium":
                                    earnedPts = 2
                                elif task_details['difficulty'] == "hard":
                                    earnedPts = 3
                                elif task_details['difficulty'] == "elite":
                                    if team_name.lower() == "tumeken":
                                        earnedPts = 8
                                    else:
                                        earnedPts = 5

                                while new_task1 == new_task2:
                                    new_task2 == await taskManager(0, new_type2)
                                task1amt = new_task1['quantity'] if new_task1['per'] == False else new_task1[
                                                                                                       'quantity'] * len(
                                    team_members)
                                task2amt = new_task2['quantity'] if new_task2['per'] == False else new_task2[
                                                                                                       'quantity'] * len(
                                    team_members)
                                binding_msg = await notificationGroupChannel.send(
                                    f"<@&{teamPing}> You have completed your task, however you have a <:BindingNecklace:1119686932943867974> active!\n" +
                                    "Please react to this message with which of the following two rolls you'd prefer:\n" +
                                    f":one: <:llandsdice:1122984846965358612>`{new_roll_1}`<:llandsdice:1122984846965358612>\n" +
                                    f"`{currentLoc}` → `{new_pos1}`\n" +
                                    f"Task: {task1amt} {new_task1['task']}\n"
                                    f":two: <:llandsdice:1122984846965358612>`{new_roll_2}`<:llandsdice:1122984846965358612>\n" +
                                    f"`{currentLoc}` → `{new_pos2}`\n" +
                                    f"Task: {task2amt} {new_task2['task']}")
                                await binding_msg.create_reaction("1️⃣")
                                await binding_msg.create_reaction("2️⃣")
                                binding_options = []
                                new_task1['type'] = new_type1
                                new_task1['new_pos'] = new_pos1
                                new_task1['addpts'] = earnedPts
                                new_task2['type'] = new_type2
                                new_task2['new_pos'] = new_pos2
                                new_task2['addpts'] = earnedPts
                                binding_options.append(new_task1)
                                binding_options.append(new_task2)
                                binding_msgs[teamnum] = int(binding_msg.id)

                                with open(f"data/{serverid}/events/binding_options.json", "w") as bindingfile:
                                    json.dump(binding_options, bindingfile)

                                with open(lost_data, 'w') as dumpf:
                                    json.dump(game_object, dumpf, indent=4)
                                return
                            # new_roll = random.randint(1,4)
                            # new_location = int(currentLoc) + int(new_roll)
                            # game_object[i]['Current Tile'] = new_location

                            earnedPts = 0
                            if task_details['difficulty'] == "easy":
                                earnedPts = 1
                            elif task_details['difficulty'] == "medium":
                                earnedPts = 2
                            elif task_details['difficulty'] == "hard":
                                earnedPts = 3
                            elif task_details['difficulty'] == "elite":
                                if team_name.lower() == "tumeken":
                                    earnedPts = 8
                                else:
                                    earnedPts = 5
                            if alchemists_blessing.get(i, False) == True:
                                earnedPts *= 2
                                alchemists_blessing[i] = False
                            if itemname == "zilyana's grace":
                                earnedPts *= 2
                            if team_name.lower() == "tumeken":
                                if random.randint(1, 100) >= 90:
                                    earnedPts *= 2
                            game_object[i]['Team Points'] += earnedPts
                            game_object[i]['taskNumber'] = 0
                            new_location = game_object[i]['Current Tile']
                            team_status_cache[game_object[i]['Number']] = 0
                            total_points = game_object[i]['Team Points']
                            currentTurn = game_object[i]['currentTurn']
                            foundTile = True
                            print("Assigned new points and reset the team's status cache.")
                if foundTile == True:
                    with open(lost_data, 'w') as dumpf:
                        json.dump(game_object, dumpf, indent=4)
                    try:
                        print("Sending the task completion message.")
                        # mainChanId = await read_properties('lostLandsMainChannel', serverid)
                        await sendTaskCompletion(team_name, teamPing, notificationGroupChannel, earnedPts, total_points,
                                                 serverid, currentLoc)

                        current_rune_emoji = await getRuneEmoji(current_type)
                        mainChanEmbed = interactions.Embed(title="",
                                                           description=f"### {team_name} completed their {current_rune_emoji} task `{task_details['task']}`!",
                                                           color=0x00FF00)
                        if task_details['task'].lower() != itemname.lower():
                            mainChanEmbed.add_field(name="", value=f"> <@{player_id}> received a drop: `{itemname}`")
                        else:
                            mainChanEmbed.add_field(name="", value=f"> Received by: <@{player_id}>")

                        # mainChanEmbed.add_field(name="Roll:",value=f"> <:llandsdice:1122984846965358612> `{new_roll}` <:llandsdice:1122984846965358612>\n`{currentLoc}` → `{new_location}`",inline=False)
                        # mainChanEmbed.add_field(name="New task:",value=f"> {new_task['task']}")
                        if earnedPts > 1:
                            mainChanEmbed.add_field(name="Earned:",
                                                    value=f"> <:1GP:980287772491403294> `{earnedPts}` points",
                                                    inline=True)
                        else:
                            mainChanEmbed.add_field(name="Earned:",
                                                    value=f"> <:1GP:980287772491403294> `{earnedPts}` point",
                                                    inline=True)
                        mainChanEmbed.add_field(name="Total:", value=f"> <:1GP:980287772491403294> `{total_points}`",
                                                inline=True)
                        mainChanEmbed.set_footer(global_footer)
                        new_tiletype = find_type(new_location)
                        new_tileemoji = await getRuneEmoji(new_tiletype)
                        mainChanEmbed.add_field(name="Current Location:",
                                                value=f"{new_tileemoji} {new_location}\n(Turn #{currentTurn})")
                        if image_url != "none":
                            mainChanEmbed.set_thumbnail(url=image_url)
                        else:
                            try:
                                item_id = find_item_id(itemname)
                                if item_id != None:
                                    mainChanEmbed.set_thumbnail(
                                        url=f'http://www.droptracker.io/img/itemdb/{item_id}.png')
                            except Exception as e:
                                print(f"An error occurred getting an image for the embed: {e}")

                        await mainChannel.send(f"### Task Completed", embeds=[mainChanEmbed])
                        await sendTeamStatus(teamnum, serverid)
                        await updateBoard(serverid)
                        time.sleep(1)
                        await send_lost_board(serverid)
                    except Exception as e:
                        print(f"{e} exception inside drop_handler?\n{e.with_traceback}")


def find_item_id(item_name):
    with open("data/items.json", 'r') as jsonfile:
        items = json.load(jsonfile)
    # Normalize the search term to lowercase
    search_name = item_name.lower()
    # Try to find an exact match first (case insensitive)
    for item in items:
        if item['Name'].lower() == search_name and not item['Noted']:
            return item['ID']
    # If no exact match, find the closest match regardless of case
    item_names = [item['Name'] for item in items if not item['Noted']]
    closest_matches = difflib.get_close_matches(search_name, item_names, n=1, cutoff=0.0)
    if closest_matches:
        closest_match = closest_matches[0].lower()
        # Return the ID of the closest match
        for item in items:
            if item['Name'].lower() == closest_match and not item['Noted']:
                return item['ID']
    # If no match is found
    return None


async def eventMvpCalc(server_id):
    fp = f"data/{server_id}/events/lost_lands.json"
    member_pts = {}
    all_members = []
    if os.path.exists(fp):
        with open(fp, 'r') as jsonf:
            data = json.load(jsonf)
        for line in data:
            if 'Number' in line:
                for member in line['Members']:
                    all_members.extend(line['Members'])
                    if line['Members'] == []:
                        continue
                    for member in all_members:
                        member_pts[member['id']] = member['points']
        top_members = sorted(member_pts, key=lambda x: member_pts[x], reverse=True)
        return top_members
    else:
        return


async def sendTaskCompletion(team_name, teamPing, notificationGroupChannel, earnedPts, total_points, serverid,
                             currentLoc):
    global waiting_rolls
    print("Entering sendTaskCompletion")
    msg = (f"<@&{teamPing}>\n# Task Completed.\n")
    teamTaskNoti = interactions.Embed(name="", description="", color=0x00FF00)
    teamTaskNoti.add_field(name="Points earned:", value=f"> <:1GP:980287772491403294> `{earnedPts}`", inline=True)
    teamTaskNoti.add_field(name="Total points:", value=f"> <:1GP:980287772491403294> `{total_points}`", inline=True)
    teamTaskNoti.add_field(name="", value="**Press the roll button below to execute your next roll!**", inline=False)
    print("Embed has been created.")
    roll_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        emoji=interactions.Emoji(name="llandsdice", id=1122984846965358612),
        label='Roll!',
        custom_id=f"{team_name.lower()}_roll_button"
    )
    print(f"NotificationGroupChannel object is currently: {notificationGroupChannel}")
    try:
        if isinstance(notificationGroupChannel, str):
            not_chan = await interactions.get(bot, interactions.Channel, object_id=notificationGroupChannel)
        else:
            not_chan = notificationGroupChannel
        if not isinstance(not_chan, str):
            await not_chan.send(f"{msg}", embeds=[teamTaskNoti], components=roll_button)
        else:
            print(f"The not_chan is still returning as a string? {not_chan}")
    except Exception as e:
        print(f"Error: {e}")
    print(f"Created button? {roll_button}")
    if waiting_rolls.get(team_name) is None:
        waiting_rolls[team_name.lower()] = True
    else:
        waiting_rolls[team_name.lower()] = True


async def checkCompletion(parts, taskn, serverid):
    print("Current parts:", parts)
    if parts != []:
        required = []
        if taskn.lower() == "malediction ward":
            required = malediction_ward
        elif taskn.lower() == "odium ward":
            required = odium_ward
        elif taskn.lower() == "godsword shard":
            required = godsword_shards
        elif taskn == "With Elegance":
            required_categories = [["skirt", "legs"], ["blouse", "shirt"]]
            found_categories = [False, False]

            for part in parts:
                partname = part['item']
                for i, category in enumerate(required_categories):
                    if any(partname.lower().endswith(word) for word in category):
                        found_categories[i] = True
                        break
            print("Elegant outfit progress:", parts)

            remaining_items = []
            for i, category in enumerate(required_categories):
                if not found_categories[i]:
                    remaining_items.extend(category)
            required = remaining_items
            if all(found_categories):
                print("Elegant outfit complete!")
                return True, required
            print("Looped all parts. Remaining:", remaining_items)
        elif taskn.lower() == "wilderness lord of the rings":
            required = lotr_wilderness
        elif taskn.lower() == "dks lord of the rings":
            required = lotr_dks
        elif taskn.lower() == "gem collector":
            required = gem_collector
        elif taskn.lower() == "mystic robes set (dark)":
            required = mystic_robes_dark
        elif taskn.lower() == "mystic robe set (light)":
            required = mystic_robes_light
        elif taskn.lower() == "boidwaker":
            required = voidwaker
        elif taskn.lower() == "where's my baguette?":
            required = sandwich_lady
        if required != []:
            for part in parts:
                for item in required:
                    if part['item'].lower() == item['name'].lower():
                        required.remove(item)
            print("Looped all parts. Remaining: ", required)

        if required == []:
            print("Task appears to be completed!")
            return True, required
        else:
            return False, required
    else:
        print("No parts!")
        return False


@bot.command(
    name="task",
    description="View your team's currently assigned task. (Lost Lands)"
)
async def taskViewer(ctx: interactions.CommandContext):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfile:
        eventdata = json.load(jsonfile)
    print(team_status_cache)
    team = None
    team_statuses = []
    for item in eventdata:
        if 'Number' in item:
            if str(item['Team Captain']) == str(ctx.author.id):
                team = item
                break
            for member in item['Members']:  # Access the 'Members' key directly
                if str(member['id']) == str(ctx.author.id):
                    team = item
                    break
            team_statuses.append({"team": item['Number'], "loc": item['Current Tile']})
    team_statuses.sort(key=lambda x: x['loc'], reverse=True)
    team_position = None
    if not team:
        await ctx.send(f"Your account was not found on any teams inside this event!")
        return
    team_number = team['Number']
    # for i, team_status in enumerate(team_statuses):
    #     if team_status['team'] == team_number:
    #         team_position = i
    #         break
    # if not team_position:
    #     team_position = 0
    runeIcon = await getRuneEmoji(team['Current Type'])
    if team != None:
        teamTask = team['taskNumber']
        teamMercyRule = team['mercyRule']
        last_roll_obj = datetime.strptime(teamMercyRule, "%Y-%m-%d %H:%M:%S.%f")
        unix = last_roll_obj.timestamp()
        current_task = await taskManager(teamTask, team['Current Type'])
        teamid = team['Number']
        teamname = team_id_to_name(teamid)
        team_points = team['Team Points']
        taskamt = await taskQuantity(teamname, teamTask, server_id)
        currentTaskEmbed = interactions.Embed(title=f"<{team['teamEmoji']}> {team['Team name']}", description=f"")
        currentTaskEmbed.add_field(name="Mercy Rule", value=f"<t:{int(unix)}:R>", inline=False)
        currentTaskEmbed.add_field(name="Current location:", value=f"Tile #{team['Current Tile']} ({runeIcon})")
        currentTaskEmbed.add_field(name="Current Points:", value=team_points, inline=False)
        # if team_position == 0:
        #     currentTaskEmbed.add_field(name="Position",value=f"Unranked")
        # else:
        #     currentTaskEmbed.add_field(name="Position",value=f"{team_position + 1}")
        if str(current_task['taskNumber']) == "148":
            taskamt = await format_gp(current_task['quantity'])
        currentTaskEmbed.add_field(name="Task:", value=f"`{taskamt}` {current_task['task']}(s)", inline=False)
        try:
            currentAmt = team_status_cache[team['Number']]
        except Exception:
            currentAmt = 0
        if str(current_task['taskNumber']) == "148":
            currentAmt = await format_gp(currentAmt)
        currentTaskEmbed.add_field(name="Current Completion", value=f"`{currentAmt}/{taskamt}`")
        await ctx.send(embeds=[currentTaskEmbed])
    else:
        await ctx.send("You must be part of a team to check your current task!", ephemeral=True)


async def taskQuantity(team_name, task_number, server_id):
    with open(f"data/new_events.json", 'r') as jsonfile:
        tasks = json.load(jsonfile)
    current_task = tasks.get(str(task_number))
    if task_number == 0 or task_number == "0":
        return 1
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfile:
        eventdata = json.load(jsonfile)
    amt = 0
    for item in eventdata:
        if 'Number' in item:
            if item['Team name'].lower() == team_name.lower():
                for member in item['Members']:
                    amt += 1
    if current_task['per'] == True:
        required = current_task['quantity'] * amt
    else:
        required = current_task['quantity']
    if team_name.lower() == "armadyl" and required >= 5:
        required = int(required * 0.80)
    if halved_task.get(team_name, False) == True:
        required -= int(required / 2)
    return required


async def getRuneEmoji(type):
    if "glowing_" or "cracked_" in type:
        type = type.replace("glowing_", "").replace("cracked_", "")
    if type == "air":
        runeIcon = "<:AirRune:1120709577210609695>"
    elif type == "water":
        runeIcon = "<:WaterRune:1120709575151194113>"
    elif type == "earth":
        runeIcon = "<:EarthRune:1120709572173250662>"
    elif type == "fire":
        runeIcon = "<:FireRune:1120709570591981649>"
    elif type == "death":
        runeIcon = "<:DeathRune:1120709565340712990>"
    elif type == "chaos":
        runeIcon = "<:ChaosRune:1120709568381599834>"
    elif type == "cosmic":
        runeIcon = "<:CosmicRune:1120709562325016588>"
    else:
        runeIcon = "?"
    return runeIcon


@bot.command(
    name="random_shop_item",
    description="Assign a random item from the shop to the targetted team",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="team",
            description="Enter the team name that will receive the item",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def random_shop_item(ctx, team: str = ""):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    with open(fp, 'r') as jsonfile:
        eventdata = json.load(jsonfile)
    for item in eventdata:
        if 'Number' in item:
            if item['Team name'].lower() == team.lower():
                current_loc = item['Current Tile']
                item_names = list(shop_emojis.keys())
                # Use random.choice to select a random item name from the list
                random_item_name = random.choice(item_names)
                random_item_data = shop_emojis[random_item_name]
                await ref_updates(f'**Zaros** has received a random item from the shop:\n**{random_item_name}**', '',
                                  '', '')
                team_chanob = await interactions.get(bot, interactions.Channel, object_id=item['Thread ID'])
                await team_chanob.send(
                    f"Your team has received a random item from the shop from a <@&1166538049757384725>: **{random_item_name}**")
                will_receive = True
                for itemss in item['Inventory']:
                    if itemss['item'] == random_item_name:
                        itemss['quantity'] += 1
    with open(fp, 'w') as jsonf:
        json.dump(eventdata, jsonf, indent=4)
    await ctx.send(f"Success. The team won the following item: {random_item_name}", ephemeral=True)


@bot.command(
    name="shop_item",
    description="Assign a random item from the shop to the targetted team",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="team",
            description="Enter the team name that will receive the item",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="item_name",
            description="Select which item they will receive.",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True
        )
    ]
)
async def shop_item(ctx, team: str = "", item_name: str = ""):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    with open(fp, 'r') as jsonfile:
        eventdata = json.load(jsonfile)
    for item in eventdata:
        if 'Number' in item:
            if item['Team name'].lower() == team.lower():
                current_loc = item['Current Tile']
                await ref_updates(f'{team} has been given an item by a ref:\n**{item_name}**', '', '', '')
                team_chanob = await interactions.get(bot, interactions.Channel, object_id=item['Thread ID'])
                await team_chanob.send(
                    f"Your team has received a random item from the shop from a <@&1166538049757384725>: **{item_name}**")
                will_receive = True
                for itemss in item['Inventory']:
                    if itemss['item'].lower() == item_name.lower():
                        itemss['quantity'] += 1
    with open(fp, 'w') as jsonf:
        json.dump(eventdata, jsonf, indent=4)
    await ctx.send(f"Success. The team was given the following item: {item}", ephemeral=True)


@shop_item.autocomplete(name="item_name")
async def item_name_autocomp(ctx, user_input: str = ""):
    item_names = list(shop_emojis.keys())
    choices = []
    for types in item_names:
        if user_input:
            if user_input.lower() in types.lower():  # Added .lower() to make the comparison case-insensitive
                choices += [interactions.Choice(name=f"{types}", value=types)]
        else:
            choices += [interactions.Choice(name=f"{types}", value=types)]
    await ctx.populate(choices)


@bot.command(
    name="deactivateitem",
    description="Force de-activate a specific item",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="team",
            description="Enter the team name that has the item active",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="item",
            description="Enter the item name that will be deactivated exactly as it appears in shop.",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def deactivate_item(ctx, team: str = "", item: str = ""):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    deleted = actives_object.deactivate_item(server_id, team.lower(), item.lower())
    if deleted == True:
        await ctx.send(f"Deactivated the item for {team}")
    else:
        await ctx.send(f"Unable to deactivate the item...")


@bot.command(
    name="llstatus",
    description="View the current game status, including a picture."
)
async def gameStatusCommand(ctx: interactions.CommandContext):
    server_id = ctx.guild_id
    if server_id == "1131575888937504798" or server_id == 1131575888937504798:
        server_id = 616498757441421322
    with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonfile:
        eventdata = json.load(jsonfile)
    team_statuses = []
    for item in eventdata:
        if 'Number' in item:
            team_statuses.append({"team": item['Number'],
                                  "loc": item['Current Tile'],
                                  "teamEmoji": item['teamEmoji'],
                                  "teamName": item['Team name'],
                                  "Current Type": item['Current Type'],
                                  "taskNumber": item['taskNumber'],
                                  "Members": item['Members']})
    with open(jsonfile, 'w') as jsondump:
        json.dump(data, jsondump)
    team_statuses.sort(key=lambda x: x['loc'], reverse=True)

    # Initialize the embed outside the loop
    currentTaskEmbed = interactions.Embed(title="# Lost Lands Status",
                                          description="Here is the current status of all teams:")

    for team_status in team_statuses:
        runeIcon = await getRuneEmoji(team_status['Current Type'])

        teamTask = team_status['taskNumber']
        current_task = await taskManager(teamTask, team_status['Current Type'])
        taskamt = await taskQuantity(team_status['teamName'].lower(), teamTask, server_id)

        # Add a field for each team
        team_position = team_statuses.index(team_status) + 1
        try:
            currentAmt = team_status_cache[team_status['team']]
        except Exception as e:
            print(e, "currentAmt")
            currentAmt = 0
        if team_position == 1:
            team_position = "1st"
        elif team_position == 2:
            team_position = "2nd"
        elif team_position == 3:
            team_position = "3rd"
        elif team_position == 4:
            team_position = "4th"

        # Construct a single string that contains all the team's information
        team_info = f"Current location: Tile #{team_status['loc']} ({runeIcon})\n"
        team_info += f"Task: `{taskamt}` {current_task['task']}(s)\n"
        team_info += f"Current Completion: `{currentAmt}/{taskamt}`"

        currentTaskEmbed.add_field(name=f"`{team_position}` - <{team_status['teamEmoji']}> {team_status['teamName']}",
                                   value=team_info, inline=False)

    # Send the embed after the loop, so it includes all teams

    board_img = interactions.File(f'data/{server_id}/events/lost-lands.png')
    await ctx.send(embeds=[currentTaskEmbed], files=board_img, ephemeral=True)


async def removeDinh(dinhobj, serverid):
    fp = f"data/{serverid}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonf:
            data = json.load(jsonf)
        for line in data:
            if 'effectedTiles' in line:
                # Build the dinh effect object from the passed dinhobj
                dinh_effect = {'type': "dinh", 'tile': dinhobj['tile'], 'team': dinhobj['team']}
                if dinh_effect in line['effectedTiles']:
                    line['effectedTiles'].remove(dinh_effect)
                    print("Removed Dinh's effect.")
                else:
                    print("Dinh's effect not found.")
        with open(fp, 'w') as jsondump:
            json.dump(data, jsondump)
    await send_lost_board(serverid)


async def check_drop(item: str, current_task: str):
    # returns:
    # 1. true if item is correct/part of set
    # 2. amount of the item that was counted. (points for sets)
    # 3. whether or not it was part of a set
    if current_task.lower() == "mystic robe set (light)":
        print("Current task is mystic robe set (light)")
        for drop in mystic_robes_light:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "mystic robe set (dark)":
        for drop in mystic_robes_dark:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "slayer trophies":
        for drop in slayer_trophies:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "tzharr points":
        for drop in tzhaar:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "beginner clue points":
        for drop in beginner_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "easy clue points":
        for drop in easy_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "medium clue points":
        for drop in medium_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "hard clue points":
        for drop in hard_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "elite clue points":
        for drop in elite_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "master clue points":
        for drop in master_clue:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gamble points":
        for drop in high_gamble_points:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "sandwich lady":
        for drop in sandwich_lady:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "soul wars weaponry":
        for drop in soul_wars_weaponry:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "soul wars junk":
        for drop in soul_wars_junk:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "barbarian assault freminnik helm":
        for drop in barbarian_assault_freminnik_helm:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "barbarian assault any seed":
        for drop in barbarian_assault_any_seed:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "camdozaal treasure":
        for drop in camdozaal_treasure:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "barrows points":
        for drop in barrows:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "wilderness points":
        for drop in wilderness:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dagannoth points":
        for drop in dagannoth:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "slayer points":
        for drop in slayer_boss:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gwd points":
        for drop in godwars:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gwd unique":
        for drop in godwars:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "wintertodt points":
        for drop in wintertodt:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "tempoross points":
        for drop in tempoross:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "revenant points":
        for drop in revenant:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "revenant unique":
        for drop in revenant:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "elegant piece":
        for drop in elegant_pieces:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "bob shirt":
        for drop in bob_shirts:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "medium clue boots":
        for drop in medium_clue_boots:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "god robe piece":
        for drop in god_robe_pieces:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "wintertodt logs":
        for drop in wintertodt_logs:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "tempoross fish":
        for drop in tempoross_fish:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "champion scroll":
        for drop in champion_scrolls:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "godsword shard":
        for drop in godsword_shards:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "general graardor unique":
        for drop in general_graardor:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "general graardor points":
        for drop in general_graardor:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "commander zilyana unique":
        for drop in commander_zilyana:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "commander zilyana points":
        for drop in commander_zilyana:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "kree'arra unique":
        for drop in kreearra:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "kree'arra points":
        for drop in kreearra:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "k'ril tsutsaroth unique":
        for drop in kril_tsutsaroth:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "k'ril tsutsaroth points":
        for drop in kril_tsutsaroth:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "malediction ward":
        for drop in malediction_ward:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "odium ward":
        for drop in odium_ward:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "hard clue cavalier":
        for drop in hard_clue_cavalier:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "medium clue animal mask":
        for drop in medium_clue_animal_mask:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dagon'hai robe piece":
        for drop in dagonhai_robe_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dusk mystic robe piece":
        for drop in dusk_mystic_robe_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gorilla unique":
        for drop in gorilla_points:
            if item.lower() == drop["name"].lower():
                return True, 1, False

    if current_task.lower() == "gorilla points":
        for drop in gorilla_points:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dks lord of the rings":
        for drop in lotr_dks:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "wilderness lord of the rings":
        for drop in lotr_wilderness:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "voidwaker":
        for drop in voidwaker:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "elite clue ornament kit":
        for drop in elite_clue_ornament_kits:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dragon mask":
        for drop in dragon_masks:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "virtus robe piece":
        for drop in virtus_robe_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "soulreaper axe piece":
        for drop in soulreaper_axe_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "vestige":
        for drop in vestige:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "godsword":
        for drop in godsword:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "zalcano unique":
        for drop in zalcano_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "chambers of xeric unique":
        for drop in chambers_of_xeric:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "xeric points":
        for drop in chambers_of_xeric:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "tombs of amascut unique":
        for drop in tombs_of_amascut:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "amascut points":
        for drop in tombs_of_amascut:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "nex unique":
        for drop in nex:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "corporeal beast unique":
        for drop in corporeal_beast:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "corporeal points":
        for drop in corporeal_beast:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "nightmare unique":
        for drop in nightmare_of_ashihama:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "red dragonhide set":
        for drop in red_dragonhide_set:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "black dragonhide set":
        for drop in black_dragonhide_set:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "zulrah points":
        for drop in zulrah:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "any visage":
        for drop in visage:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "god d'hide piece":
        for drop in god_dhide_pieces:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gem collector":
        for drop in gem_collector:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True
    if current_task.lower() == "crystal keys":
        if item.lower() == "crystal key":
            return True, 1, False
    if current_task.lower() == "crystal key":
        for drop in crystal_key:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], True

    if current_task.lower() == "wyrm unique":
        for drop in wyrm_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "drake unique":
        for drop in drake_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "hydra unique":
        for drop in hydra_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "cerberus unique":
        for drop in cerberus_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gauntlet unique":
        for drop in gauntlet:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "gauntlet points":
        for drop in gauntlet:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dark totem":
        for drop in dark_totem:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "bludgeon piece":
        for drop in bludgeon_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "ahrim piece":
        for drop in ahrim_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "karil piece":
        for drop in karil_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "dharok piece":
        for drop in dharok_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "guthan piece":
        for drop in guthan_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "torag piece":
        for drop in torag_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "verac piece":
        for drop in verac_piece:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "any raid unique":
        for drop in raid_unique:
            if item.lower() == drop["name"].lower():
                return True, drop['points'], False

    if current_task.lower() == "nex's rune sword":
        if item.lower() == 'rune sword':
            return True, 1, False

    ## item is not part of a set task and does match the required item for the supplied task
    if current_task.lower().strip() == item.lower().strip():
        return True, 1, False
    else:
        return False, 0, False


async def format_gp(number):
    number = int(number)
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.3f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:,}"


@bot.command(
    name="ll",
    description="View info about point-related tasks in the Lost Lands event.",
    options=[
        interactions.Option(
            name="type",
            description="Which assignment would you like to view the point values for?",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True
        )
    ]
)
async def ll(ctx: interactions.CommandContext, type):
    if len(type) < 3:
        await ctx.send("An error occured.")
        return
    responseEmbed = interactions.Embed(name=f"{type.capitalize()}", value="Point values")
    pointValues = ""
    textr = ""
    if type == "arma":
        for item in kreearra:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "bandos":
        for item in general_graardor:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "zammy":
        for item in kril_tsutsaroth:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "sara":
        for item in commander_zilyana:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "dks":
        for item in dagannoth:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "demonics":
        for item in gorilla_points:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "gwd":
        for item in godwars:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "cox":
        for item in chambers_of_xeric:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "Slayer Trophy":
        for item in slayer_trophies:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "Slayer":
        for item in slayer_boss:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "tob":
        for item in theatre_of_blood:
            pointValues += f"`{item['points']}` - {item['name']}\n"

        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "toa":
        for item in tombs_of_amascut:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "gamble":
        for item in high_gamble_points:
            pointValues += f"`{item['points']}` - {item['name']}\n"
    elif type == "barrows":
        for item in barrows:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "beginners":
        ctr = 0
        for item in beginner_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
    elif type == "easy":
        ctr = 0
        pages = 1
        for item in easy_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
            if len(textr) > 1900:
                pages += 1
                await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                               f"{textr} \n: {pages}", ephemeral=True)
                textr = ""
    elif type == "medium":
        ctr = 0
        pages = 1
        for item in medium_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
            if len(textr) > 1900:
                pages += 1
                await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                               f"{textr} \n: {pages}", ephemeral=True)
                textr = ""
    elif type == "hard":
        ctr = 0
        pages = 1
        for item in hard_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
            if len(textr) > 1900:
                pages += 1
                await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                               f"{textr} \n: {pages}", ephemeral=True)
                textr = ""
    elif type == "elite":
        ctr = 0
        pages = 1
        for item in elite_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
            if len(textr) > 1900:
                pages += 1
                await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                               f"{textr} \n: {pages}", ephemeral=True)
                textr = ""
    elif type == "master":
        ctr = 0
        pages = 1
        for item in master_clue:
            if ctr < 3:
                textr += f"{item['points']} - {item['name']} |"
                ctr += 1
            else:
                textr += f"{item['points']} - {item['name']} \n"
                ctr = 0
            if len(textr) > 1900:
                pages += 1
                await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                               f"{textr} \n: {pages}", ephemeral=True)
                textr = ""
    elif type == "baguette":
        pointValues += f"**Items required for the `Where's my Baguette` challenge**:"
        for item in sandwich_lady:
            pointValues += f"`{item['item'].capitalize()}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    elif type == "foot fetish":
        pointValues += f"**Obtain any `one` of the following boots**:\n"
        for items in medium_clue_boots:
            pointValues += f"{items['item'].capitalize()}"
    elif type == "with elegance":
        pointValues += f"**You must obtain a `blouse` **or** a `shirt`, **and** a `skirt` **or** a pair of `legs` from the list below**:"
        for item in elegant_pieces:
            pointValues += f"{item['item'].capitalize()}"
        responseEmbed.add_field(name="", value=pointValues, inline=False)

    elif type == "wilderness":
        for item in wilderness:
            pointValues += f"`{item['points']}` - {item['name']}\n"
        responseEmbed.add_field(name="", value=pointValues, inline=False)
    responseEmbed.set_footer(global_footer)
    try:
        if textr != "":
            await ctx.send(f"**Point values for {type.capitalize()}**:\n" +
                           f"{textr}", ephemeral=True)
        else:
            await ctx.send(f"**Point values for {type}**", embeds=[responseEmbed])
    except Exception as e:
        await ctx.send(f"An error occured: {e}", ephemeral=True)


@ll.autocomplete(name="type")
async def pointDictTypes(ctx, user_input: str = ""):
    type_list = [
        "arma", "bandos", "sara", "zammy", "dks", "demonics", "gwd", "cox", "tob", "toa", "barrows", "beginners",
        "easy", "medium", "hard", "elite", "master",
        "baguette", "foot fetish", "with elegance", "Slayer Trophy", "Slayer", "wilderness"
    ]
    choices = []
    for types in type_list:
        if user_input:
            if user_input.lower() in types.lower():  # Added .lower() to make the comparison case-insensitive
                choices += [interactions.Choice(name=f"{types.capitalize()} Points", value=types)]
        else:
            choices += [interactions.Choice(name=f"{types.capitalize()} Points", value=types)]
    await ctx.populate(choices)


async def sendTeamStatus(teamid, serverid):
    global frozen_states
    if serverid == 1131575888937504798:
        serverid = 616498757441421322
    fp = f"data/{serverid}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            data = json.load(jsonfile)
        for i in range(len(data)):
            if 'Mercy Rule' in data[i]:
                board_tiles = data[i]['Board Tiles']
                shop_link = data[i]['shopLink']
            else:
                if int(data[i]['Number']) == int(teamid):
                    teamname = data[i]['Team name']
                    currentTile = data[i]['Current Tile']
                    teamThreadID = data[i]['Thread ID']
                    lastroll = data[i]['last_roll']
                    currentType = data[i]['Current Type']
                    captain = data[i]['Team Captain']
                    colead = data[i]['colead']
                    teamMembers = data[i]['Members']
                    member_pts = []
                    if teamMembers != []:
                        member_str = ""
                        member_pts = {}
                        for mem in teamMembers:
                            if isinstance(mem, dict) and 'id' in mem and 'points' in mem:
                                member_pts[mem['id']] = mem['points']
                            if str(mem['id']) != str(captain):
                                member_str += f"<@{mem['id']}>\n"
                        top_member = sorted(member_pts, key=lambda x: member_pts[x], reverse=True)
                        total_members = len(teamMembers)
                    else:
                        member_str = "None"
                        total_members = 1
                    taskNumber = data[i]['taskNumber']
                    inventory = data[i]['Inventory']
                    teamEmoji = data[i]['teamEmoji']
                    points = data[i]['Team Points']
                    currentTurn = data[i]['currentTurn']
                    try:
                        status = team_status_cache[data[i]['Number']]
                    except KeyError:
                        status = 0
                    mercy_rule = data[i]['mercyRule']
                    threadobj = await interactions.get(bot, interactions.Channel, object_id=teamThreadID)
                    main_msg = data[i]['mainmsg']
                    for tile in board_tiles:
                        if tile['number'] == currentTile:
                            current_rune = tile['type']
                    data[i]["Current Type"] = current_rune
                    last_roll_obj = datetime.strptime(lastroll, "%Y-%m-%d %H:%M:%S.%f")
                    reroll_time = last_roll_obj + timedelta(days=1)
                    unix = reroll_time.timestamp()
                    embed = interactions.Embed(title=f"<{teamEmoji}> {teamname}", description="")
                    current_timestamp = int(datetime.now().timestamp())
                    try:
                        if frozen_states[i] and frozen_states[i] == currentTile:
                            ##Team is currently effected by the ice barrage!
                            print(f"The team is frozen on tile {frozen_states[i]}")
                            embed.add_field(name=f"", value=f"Current tile: {current_rune} (`#{currentTile}`)",
                                            inline=True)
                            embed.add_field(
                                name=f"<:IceBarrage:1119686930255315055> Ice Barrage <:IceBarrage:1119686930255315055>",
                                value=f"Two tasks are required on tile `{frozen_states[i]}`!")
                    except Exception:
                        embed.description = f"Current tile: {current_rune} (`#{currentTile}`)"

                    active_cooldown, remaining_turns = active_cooldowns.check_active(serverid, currentTurn,
                                                                                     teamname.lower())
                    print("Passed: ", serverid, currentTurn, teamname.lower())
                    team_active_name, description = [s.strip() for s in team_actives[teamname.lower()].split(":")]
                    team_active_name = team_active_name.replace("*", "").replace(":", "")
                    print(f"Active cooldown? {active_cooldown}. Remaining turns: {remaining_turns}")
                    if active_cooldown and remaining_turns >= 1:
                        team_active_name, cooldown = team_active_name.split("-")
                        team_active_name, cooldown = team_active_name.replace("-", ""), cooldown.replace("-", "")
                        cooldown = cooldown.replace(" turn cooldown", "")
                        team_active_final = f"{team_active_name}\n> Available after `{remaining_turns}` more turns.\n{description}"
                        embed.add_field(name=f"<:active:1163953192531411014> {team_active_final}", value=f"",
                                        inline=True)
                    else:
                        team_active_name, cooldown = team_active_name.split("-")
                        team_active_name, cooldown = team_active_name.replace("-", ""), cooldown.replace("-", "")
                        team_active_final = f"{team_active_name}\n> Available now!\n{description}"
                        embed.add_field(name=f"<:active:1163953192531411014> {team_active_name}",
                                        value=f"> `{description}`\n> Use `/active` to use your abilities!", inline=True)
                    team_passive_name, passive_desc = [s.strip() for s in team_passives[teamname.lower()].split(":")]
                    team_passive_name = team_passive_name.replace("*", "").replace(":", "")
                    passive_desc = passive_desc.replace(":", "").replace("\n", "\n> ")
                    embed.add_field(name=f"<:passive:1163953191789011016> {team_passive_name}", value=f"{passive_desc}",
                                    inline=True)
                    embed.add_field(name="** **", value="** **", inline=False)
                    task = await taskManager(taskNumber, current_rune)
                    task_name = task['task']
                    data[i]['taskNumber'] = task['taskNumber']
                    data[i]['Status'] = 0
                    task_amt = task['quantity']
                    if task['per'] == True:
                        task_amt = total_members * task['quantity']
                    if task['description'] == "none" or task['description'] == "":
                        if task['quantity'] == 1 and task['per'] == False:
                            description = f"Obtain `1` {task['task']}."
                        elif task['per'] == False:
                            description = f"Obtain `{task['quantity']}` {task['task']}s"
                        else:
                            description = f"Obtain `{task['quantity']}` {task['task']}(s) per member of your team."
                    else:
                        print(f"New task desc: {task['description']}")
                        description = task['description']
                    embed.add_field(name="Task", value=f'`{task_name}`\n> {description}', inline=True)
                    if status == "":
                        status = 0
                    else:
                        status = int(status)
                    embed.add_field(name="Completion:", value=f"> `{status}/{task_amt}`", inline=True)
                    embed.add_field(name="Mercy Rule", value=f"> <t:{int(unix)}:R>", inline=False)
                    if captain != "0" and captain != 0:
                        embed.add_field(name="Captain", value=f"<@{captain}>", inline=True)
                    else:
                        embed.add_field(name="Captain", value="*None*", inline=True)
                    if colead != 0:
                        embed.add_field(name="Co-captain", value=f"<@{colead}>", inline=True)

                    if member_str != "None":
                        embed.add_field(name="Members", value=member_str, inline=False)
                        if member_pts[top_member[0]] > 1:
                            embed.add_field(name="MVP", value=f"<@{top_member[0]}> | `{member_pts[top_member[0]]} pts`",
                                            inline=False)
                    invent_str = ""
                    invent_emojis = []
                    for invitem in inventory:
                        item_name = invitem['item']
                        quantity = invitem['quantity']
                        for shop_item, item_properties in shop_emojis.items():
                            if shop_item == item_name:
                                emoji = item_properties["emoji"]
                        if quantity >= 1:
                            if emoji != "🎲":
                                invent_str += f"<{emoji}> **{item_name.capitalize()}**: `{quantity}`\n"
                            else:
                                invent_str += f"{emoji} **{item_name.capitalize()}**: `{quantity}`\n"
                            invent_emojis.append(emoji)
                    required_votes = int(total_members / 3) * 2

                    if required_votes < 1:
                        required_votes = 1
                    if invent_str != "":
                        embed.add_field(name="Inventory", value=invent_str, inline=True)
                        embed.add_field(name="`/inventory`", value=f"(`{required_votes} member votes required`)",
                                        inline=True)
                    embed.add_field(name=f"Current Points {shop_link}", value=f"`{points}`", inline=False)
                    if main_msg != 0:
                        main_msg_ob = await interactions.get(bot, interactions.Message, parent_id=teamThreadID,
                                                             object_id=main_msg)
                        for field in embed.fields:
                            if field.name == "`/inventory`":
                                field.value = f"(`{required_votes} member votes required`)"
                            if field.name == "Inventory":
                                for invitem in inventory:
                                    item_name = invitem['item']
                        ##Discord API Rate Limit
                        await asyncio.sleep(2)
                        try:
                            await main_msg_ob.edit(embeds=[embed])
                        except Exception as e:
                            print(f"An error occured editing the main message object: {e}")
                        previous_history = await threadobj.get_history(100)
                        for messages in previous_history:
                            if 'has been created!' in messages.content:
                                await messages.delete()
                        new_message_id = main_msg_ob.id
                        data[i]['mainmsg'] = str(main_msg_ob.id)
                    else:
                        new_message = await threadobj.send(embeds=[embed])
                        previous_history = await threadobj.get_history(100)
                        for messages in previous_history:
                            if 'has been created!' in messages.content:
                                await messages.delete()
                        if not new_message.pinned:
                            await new_message.pin()
                    try:
                        new_message_id = main_msg_ob.id
                        data[i]['mainmsg'] = str(main_msg_ob.id)
                        if not main_msg_ob.pinned:
                            await main_msg_ob.pin()
                    except UnboundLocalError:
                        new_message_id = new_message.id
                        data[i]['mainmsg'] = str(new_message.id)
                    with open(fp, 'w') as jsonf:
                        json.dump(data, jsonf, indent=4)
                    print(f"Sent the message ({new_message_id}) to ", threadobj.id)
    else:
        print(f"{serverid} is not running a lost lands event. {teamid} tried to update their statuss... ")


async def use_item(team, item, server_id):
    print(f"team {team} using item {item}")


def save_messages(messages):
    data = []
    for message in messages:
        if message.embeds:
            for embed in message.embeds:
                data.append({
                    f'<@{message.author.id}>': f'[Embedded Message] {embed.title} - {embed.description}'
                })
                for i, field in enumerate(embed.fields):
                    data.append({
                        f'{field.name}': f'{field.value}'
                    })
                data.append({'\n': ''})
        else:
            data.append({
                f'<@{message.author.id}>': f'{message.content}\n'
            })
    unix = int(datetime.now().timestamp())
    with open(f'purge_backup/{unix}.json', 'w') as jsonfile:
        json.dump(data, jsonfile)


@bot.command(
    name="purge",
    description="Remove messages. Keeps a backup.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="amount",
            description="Amount of messages to remove",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please specify a valid number of messages to purge.")
        return

    # Fetch the specified number of messages
    channelob = await interactions.get(bot, interactions.Channel, object_id=ctx.channel.id)
    channel_msgs = await channelob.get_history(amount)
    # Save the messages before deleting
    print(f"{ctx.author.name} is clearing {amount} messages from {channelob.name}. {int(datetime.now().timestamp())}")
    save_messages(channel_msgs)

    # Delete the messages
    await channelob.purge(amount=amount)
    await ctx.send(f"I've cleared {amount} messages from this channel & saved the data locally.", ephemeral=True)


async def check_item_cooldowns(ctx, item_name, inventory, shop_emojis, total_members):
    """Check if any items of the same type as the given item name have a cooldown."""
    if not item_name:
        return

    # Determine the type of the given item name from the shop
    item_type = get_item_type_from_shop(item_name, shop_emojis)

    if not item_type:
        return

    # Iterate over each item in the inventory
    for invitem in inventory:
        # Determine the type of the current inventory item from the shop
        invitem_type = get_item_type_from_shop(invitem['item'], shop_emojis)

        if not invitem_type:
            continue

        # Check if this inventory item's type matches the given item's type and has a cooldown
        if invitem_type == item_type and invitem['cooldown'] >= 1:
            msg = get_item_type_message(item_type)
            text = f"Your {msg} are still under a cooldown!\nYou can use them again in {invitem['cooldown']} more turns."
            new_image = textwrite.generate_image(text=text, is_header=False, centerpiece_image_url=None)
            image_obj = interactions.File(new_image)
            await ctx.send(files=[image_obj], ephemeral=True)
            return False
    return True


def get_item_type_message(item_type):
    """Return a message corresponding to the item type."""
    type_messages = {
        "t": "trap items",
        "e": "enchanted items",
        "d": "defensive items",
        "o": "offensive items"
    }
    return type_messages.get(item_type, "")


def get_item_type_from_shop(item_name, shop_emojis):
    """Return the type of an item based on its name from the shop."""
    if item_name in shop_emojis:
        return shop_emojis[item_name]["type"]
    return None


@bot.command(
    name="inventory",
    description="(Lost Lands) Use an item from your team's inventory.",
    options=[
        interactions.Option(
            name="item",
            description="What item are you using?",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True
        ),
        interactions.Option(
            name="targteam",
            description="Which team are you using the item against?",
            type=interactions.OptionType.STRING,
            required=False,
            autocomplete=True
        )
    ]
)
async def inventory_cmd(ctx: interactions.CommandContext, item: str, targteam: str = ""):
    global goblin_tasks_info
    global frozen_states
    player_id = ctx.member.id
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    found = False
    current_data = []
    team_roles = []
    captain = False
    global binding_actives
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    used_teamname = None
    board_tiles = ""
    for data in current_data:
        if 'Number' in data:
            teamed_members = [member['id'] for member in
                              data['Members']]  # Assuming 'Members' are stored as list of dicts with 'id' key
            if player_id == data['Team Captain']:
                print("Captain is true!")
                captain = True
            if player_id in teamed_members:
                team_id = data['Number']
                inventory = data['Inventory']
                found = True
                total_members = len(teamed_members)
                team_channel = data['Thread ID']
                team_role = data["roleID"]
                team_casted_bys_task = data['taskNumber']
                current_rune = data['Current Type']
                currentTurn = data['currentTurn']
                teamEmoji = data['teamEmoji']
                team_chanob = await interactions.get(bot, interactions.Channel, object_id=team_channel)
                team_roles.append(data['roleID'])
                used_teamname = data['Team name']
                team = data
                if board_tiles != "":
                    break
        elif 'Board Tiles' in data:
            board_tiles = data['Board Tiles']
    if found:
        required = 4
        if required == 0:
            required = 1
        done_cooldown = await check_item_cooldowns(ctx, item, inventory, shop_emojis, total_members)
        if done_cooldown == False:
            return
        ##We made it through all of the items with the same item type in the team's storage, and none of them had a cooldown active.
        for invitem in inventory:
            if invitem['item'] == item:

                if invitem['quantity'] >= 1:
                    invitem['votes'] += 1
                    if captain == True:
                        print("Captain is true!")
                        invitem['votes'] = 10
                    if invitem['votes'] >= required:
                        full_item = shop_emojis[item]
                        item_type = full_item["type"]
                        ### Handle the actual functions of each item being used, they reached the required votes
                        invitem['quantity'] -= 1
                        invitem['votes'] = 0  # reset votes after requirement is met
                        if targteam and nieve.get(targteam, False) == True:
                            await ctx.send(
                                f"The team you selected had **Nieve's Elysian** active!\nYour item had no effect on them, but was still used in the process.")
                            nieve[targteam] = False
                            with open(fp, 'w') as jsonfile:
                                json.dump(current_data, jsonfile)
                            return
                        if targteam and smoke_barrage.get(targteam, False) == True:
                            smoke_barrage[targteam] = False
                            item = "smokebarrageeffect"
                            with open(fp, 'w') as jsonfile:
                                json.dump(current_data, jsonfile)
                            return
                        if targteam and leechward.get(targteam, False) == True:
                            for itemss in current_data:
                                if 'Number' in itemss:
                                    if int(itemss['Number']) == int(targteam):
                                        team_invent = itemss['Inventory']
                                        for inventitem in team_invent:
                                            if inventitem['item'] == item:
                                                inventitem['quantity'] += 1
                            item = "none"
                        cooldown = (itemCooldownTimers(invitem['item']) + 1)
                        invitem['cooldown'] += cooldown
                        if item == "ghommal's lucky penny":
                            emoji = shop_emojis["ghommal's lucky penny"]["emoji"]
                            new_task = await taskManager(0, current_rune)
                            await team_chanob.send(
                                f"#<{teamEmoji}><@&{team_role}>\n<{emoji}>\n<@{ctx.author.id}> has cast the last vote required to use ghommal's lucky penny and re-roll your current task.\n\n" +
                                f"Your team's new {current_rune} task is \n # `{new_task['task']}`")
                            current_unix = int(datetime.now().timestamp())
                            await ref_updates('used a reroll', f'{ctx.author.id}', f'{int(current_unix)}',
                                              f'{team_role}')
                            for data in current_data:
                                if 'Number' in data and data['Number'] == team_id:
                                    data['taskNumber'] = new_task['taskNumber']
                                    data['Status'] = 0
                        elif item == "ice barrage":
                            ## TODO : : ICE BARRAGE KEEPS THE TEAM ON THE CURRENT TILE AFTER COMPLETING THEIR TASK.
                            ## NOTE: GLOBAL OBJECT (IS_FROZEN[TEAM_NAME]) TO STORE FROZEN
                            for data in current_data:
                                if 'Number' in data and int(data['Number']) == int(targteam):
                                    if leechward.get(data['Team name'].lower(), False) == True:
                                        await ctx.send(
                                            "The team you casted your ice barrage against had a Ward of the Leech active!\nThey've stolen your item.")
                                        await ref_updates(
                                            f'We need to give {targteam} an ice barrage because their ward of the leech stole it from {ctx.author.name}')
                                        break
                                    elif smoke_barrage.get(data['Team name'].lower(), False) == True:
                                        await ctx.send(
                                            "The team you casted your ice barrage against had a Smoke Barrage active, preventing it from having any effect!")
                                        break
                                    elif nieve.get(data['Team name'].lower(), False) == True:
                                        await ctx.send(
                                            "The team you casted your ice barrage against had Nieve's Elysian equipped; so your item had no effect!")
                                        break
                                    ## Target team is frozen
                                    future_time = datetime.now() + timedelta(hours=1)
                                    frozen_states[int(targteam)] = data['Current Tile']
                                    casted_name = data['Team name']
                                    casted_role = data['roleID']
                                    casted_channel = data['Thread ID']
                                    target_chan = await interactions.get(bot, interactions.Channel,
                                                                         object_id=casted_channel)
                                    await target_chan.send(
                                        f"### <@&{casted_role}>\n Your team has been hit with an <:IceBarrage:1119686930255315055> **Ice Barrage**!\nYou will need to complete two tasks on this tile before moving forward!>\n\n" +
                                        f"> You can send your complaints to <@&{team_role}> <:modjed:1088922691999899772>")
                                    current_unix = int(datetime.now().timestamp())
                                    # await ref_updates(f'used an ice barrage against <@&{casted_role}>. \n>> Expires: <t:{int(when_unix)}:R>', f'{ctx.author.id}',f'{int(current_unix)}',f'{team_role}')
                                    with open(fp, 'w') as jsonfile:
                                        json.dump(current_data, jsonfile)
                                    await sendTeamStatus(data['Number'], server_id)
                                    await team_chanob.send(
                                        f"#<{teamEmoji}><@&{team_role}>\n<@{ctx.author.id}> has cast the last vote required to cast an <:IceBarrage:1119686930255315055> **Ice Barrage** against <@&{casted_role}>!\n\n" +
                                        f"")
                                    return
                            await team_chanob.send(
                                f"<@&{team_role}>\n<@{ctx.author.id}> has cast an <:IceBarrage:1119686930255315055> **Ice Barrage** against <@&{casted_role}> ({casted_name})")
                        elif item == "dinh's bulwark":
                            for data in current_data:
                                if 'Number' in data and data['Number'] == team_id:
                                    current_tile = data['Current Tile']
                                    current_rune = data['Current Type']
                            ping_str = ""
                            for role in team_roles:
                                if role != team_role:
                                    ping_str += f"<@&{role}>"
                            message = f"{ping_str}\n<@&{team_role}> has just placed a `Dinh's Bulwark` on tile `#{current_tile}`({current_rune})\n"
                            if ctx.channel_id != team_channel:
                                await team_chanob.send(message)
                                await ctx.send(message, ephemeral=True)
                            else:
                                await ctx.send(message)
                            for line in current_data:
                                if 'effectedTiles' in line:
                                    if {'type': "dinh", 'tile': current_tile, 'team': team_id} not in line[
                                        'effectedTiles']:
                                        line['effectedTiles'].append(
                                            {'type': "dinh", 'tile': current_tile, 'team': team_id})
                                    else:
                                        print("Dinh's was already placed, skipping adding it to the data again.")
                            # TODO: Test updateBoard await place_dinhs(current_tile, team_id, str(ctx.guild_id))
                            await updateBoard(str(server_id))
                            current_unix = int(datetime.now().timestamp())
                            await ref_updates(f'placed a {item.capitalize()} on tile `{current_tile}`',
                                              f'{ctx.author.id}', f'{int(current_unix)}', f'{team_role}')
                            print("Sent the updateBoard function")
                            await send_lost_board(server_id)
                            await team_chanob.send(message)
                        elif item == "binding necklace":
                            teamname = team_id_to_name(team_id)
                            activation_bool = actives_object.activate_item(server_id, teamname, item, currentTurn,
                                                                           item_type)
                            print(f"Binding activation bool: {activation_bool}")
                            if activation_bool:
                                await ctx.send(
                                    f"You have activated a <:BindingNecklace:1119686932943867974> `Binding Necklace`.\n " +
                                    "You will be prompted to select your desired roll next time you complete a task.")

                                current_unix = int(datetime.now().timestamp())
                                await ref_updates('activated a binding necklace', f'{ctx.author.id}',
                                                  f'{int(current_unix)}', f'{team_role}')
                            else:
                                print("Binding necklace failed to activate? ")
                        elif item == "gertrude's rat":
                            if targteam == "":
                                await ctx.send(
                                    "You need to select which team you are attempting to steal an item from!\n> Check for the `targteam` parameter when you use `/inventory`!")
                            else:
                                if targteam in hunter_traps and hunter_traps[targteam] == True:
                                    await ctx.send(
                                        f"The team you attacked with Gertrude's Rat had Hunter's Box Traps placed!\n" +
                                        "Your item usage has been nulled.")
                                else:
                                    for data in current_data:
                                        if 'Number' in data and str(data['Number']) == str(targteam):
                                            targ_channel = data['Thread ID']
                                            targ_chanob = await interactions.get(bot, interactions.Channel,
                                                                                 object_id=targ_channel)
                                            ## This team is having an item stolen from them
                                            target_inventory = data['Inventory']
                                            targ_role = data['roleID']
                                            targ_name = data['Team name']
                                            # defines a dict of possible items that can be stolen from
                                            possibles = []
                                            for i, items in enumerate(target_inventory):
                                                if items['quantity'] >= 1:
                                                    possibles.append(items['item'])
                                            if possibles == []:
                                                await ctx.send(
                                                    f"The team you selected has no items for you to steal! \n Try another team.")
                                                return
                                            selected_item = random.choice(possibles)
                                            for i, items in enumerate(data['Inventory']):
                                                if items['item'] == selected_item:
                                                    ## This is the item that will be stolen
                                                    print(
                                                        f"{used_teamname} has used gertrude's rat to steal {items['item']} from {targ_name}!")
                                                    await ref_updates(
                                                        f"{used_teamname} has used gertrude's rat to steal {items['item']} from {targ_name}!",
                                                        f"", f"", f"")
                                                    items['quantity'] -= 1
                                                    if items['quantity'] == 0:
                                                        items['votes'] = 0
                                                    await targ_chanob.send(
                                                        f"<@&{targ_role}>\n### Your team has been hit by the effects of Gertrude's Rat!\n> {used_teamname} has stolen your {items['item'].capitalize()}!")
                                            await team_chanob.send(
                                                f"<:Rat:1167108968951324692> You've stolen **{selected_item}** from {targ_name}!")
                                    for data in current_data:
                                        if 'Number' in data and str(data['Number']) == str(team_id):
                                            for inv_item in data['Inventory']:
                                                if inv_item['item'] == selected_item:
                                                    inv_item['quantity'] += 1
                        elif item == "pirate pete's parrot":
                            print("Pirate pete's parrot")
                            amount_stolen = random.randint(4, 8)
                            possibles = []
                            for item in current_data:
                                if 'Number' in item:
                                    if item['Team Captain'] != "none" and item['Team Captain'] != "None" and int(
                                            item['Number']) != int(team_id):
                                        if item['Team Points'] >= amount_stolen:
                                            possibles.append(item['Number'])
                                            print(f"Adding {item['Number']} to {possibles}")
                            random_team = random.choice(possibles)
                            print(f"Selected {random_team}, casting team is {team_id}")
                            if len(possibles) > 1:
                                while random_team in hunter_traps and hunter_traps[random_team] == True:
                                    possibles.remove(random_team)
                                    print("Removing a team because they have box traps active")
                                    random_team = random.choice(possibles)
                                print(f"Total possible teams was >1, we selected {random_team}")
                            if int(random_team) == int(team_id):
                                await ctx.send("No teams have enough GP for you to steal right now! Try again later.")
                                print("No teams had enough GP.")
                                return
                            random_name = team_id_to_name(random_team)
                            print(f"caster: {used_teamname} | receiver: {random_name}")
                            null = False
                            if hunter_traps.get(random_team, False) == True:
                                null = True
                            if null == False:
                                for item in current_data:
                                    if 'Number' in item:
                                        if item['Number'] == random_team:
                                            item['Team Points'] -= amount_stolen
                                            targ_channel = item['Thread ID']
                                            target_role = item['roleID']
                                        elif item['Number'] == team_id:
                                            item['Team Points'] += amount_stolen
                                print("Added points and stole from other team... assigning channels.")
                                attack_target_channel = await interactions.get(bot, interactions.Channel,
                                                                               object_id=targ_channel)
                                attacked_text = f"\n{used_teamname} has stolen {amount_stolen} coins from your team!"
                                attacked_image_obj = textwrite.generate_image(text=attacked_text, is_header=False,
                                                                              centerpiece_image_url="http://www.droptracker.io/img/emoji/piratepetesparrot.png")
                                attacked_image_objt = interactions.File(attacked_image_obj)
                                await attack_target_channel.send(f"<@&{target_role}>", files=attacked_image_objt)
                                text = f"\nYou have stolen {amount_stolen} coins from {random_name}"
                                new_image = textwrite.generate_image(text=text, is_header=False,
                                                                     centerpiece_image_url="http://www.droptracker.io/img/emoji/piratepetesparrot.png")
                                image_obj = interactions.File(new_image)
                                await team_chanob.send(f"<@&{team_role}>", files=image_obj)
                        elif item == "duplication glitch":
                            if targteam == "":
                                await ctx.send(f"You must select a target team for this item!")
                                return
                            for item in current_data:
                                if 'Number' in item:
                                    if int(item['Number']) == int(targteam):
                                        item['taskNumber'] = team_casted_bys_task
                                        target_chan = item['Thread ID']
                                        target_role = item['roleID']
                                        target_name = item['Team name']
                                        target_emoji = item['teamEmoji']
                                        team_status_cache[item['Number']] = 0
                                        target_type = item['Current Rune']
                            casted_name = team_id_to_name(team_id)
                            await ctx.send(
                                f"Success!\n> You've forced <{target_emoji}> {target_name} to adopt your current task!\n")
                            new_task = await taskManager(team_casted_bys_task, target_type)
                            new_amt = await taskQuantity(target_name.lower(), new_task['taskNumber'], ctx.guild.id)
                            targ_chan = await interactions.get(bot, interactions.Channel, object_id=target_chan)
                            await targ_chan.send(
                                f"### Hey <@&{target_role}>!\n{casted_name.capitalize()} has used **Duplication Glitch** against your team!\n" +
                                "In other words, they forced you to adopt their current task:\n" +
                                f"> {new_amt} x {new_task['task']}")
                        elif item == "questmaster's gauntlets":
                            if targteam == "":
                                await ctx.send(f"You must select a target team for this item!")
                                return
                            casted_name = team_id_to_name(team_id)
                            for item in current_data:
                                if 'Number' in item:
                                    if int(item['Number']) == int(targteam):
                                        target_task = item['taskNumber']
                                        stolen_name = item['Team name']
                                        rerolled_task = await taskManager(0, item['Current Type'])
                                        item['taskNumber'] = rerolled_task['taskNumber']
                                        new_taskamt = await taskQuantity(item['Team name'], rerolled_task['taskNumber'],
                                                                         ctx.guild.id)
                                        target_channel = await interactions.get(bot, interactions.Channel,
                                                                                object_id=item['Thread ID'])
                                        team_status_cache[item['Number']] = 0
                                        team_status_cache[team_id] = 0
                                        await target_channel.send(f"### Hey, <@&{item['roleID']}>!\n" +
                                                                  f"{casted_name} has used **Questmaster's Gauntlet** to steal your current task!\n" +
                                                                  f"In the process, your task was re-rolled:\n" +
                                                                  f"> {new_taskamt} x {rerolled_task['task']}")
                            for item in current_data:
                                if 'Number' in item:
                                    if item['Number'] == team_id:
                                        item['taskNumber'] = target_task
                            teamname1 = team_id_to_name(team_id)
                            new_teams_task = await taskManager(target_task, 'air')
                            new_team_quant = await taskQuantity(teamname1, target_task, ctx.guild.id)
                            await team_chanob.send(f"Your team has stolen {stolen_name}'s task!\n" +
                                                   f"{new_team_quant} x {new_teams_task['task']}")
                        elif item == "mind goblin":
                            possible_tasks = []
                            if targteam == "":
                                await ctx.send("You need to select a target team for this item!")
                                return
                            else:
                                for item in current_data:
                                    if 'Number' in item:
                                        if int(item['Number']) == int(targteam):
                                            target_role = item['roleID']
                                            target_chan = item['Thread ID']
                            casted_name = team_id_to_name(team_id)
                            target_channel = await interactions.get(bot, interactions.Channel, object_id=target_chan)
                            nieve[targteam] = True
                            selected_name = team_id_to_name(int(targteam))
                            if targteam and nieve.get(targteam, False) == True:
                                await target_channel.send(
                                    f"Your **Nieve's Elysian** effect has been destroyed by {casted_name}'s **Mind Goblin**!")
                                await ctx.send(
                                    f"The team you selected had **Nieve's Elysian** active!\nYour item had no effect on them, but was still used in the process.")
                                nieve[targteam] = False
                                with open(fp, 'w') as jsonfile:
                                    json.dump(current_data, jsonfile)
                                return

                            for item in current_data:
                                if 'Number' in item:
                                    if int(item['Number']) == int(targteam):
                                        target_difficulty = item['Current Type']
                                with open(f"data/new_events.json", 'r') as jsonfile:
                                    tasks = json.load(jsonfile)
                                for task_key, task in tasks.items():
                                    if str(task['difficulty']).lower() == target_difficulty.lower():
                                        quantity = await taskQuantity(selected_name.lower(), task_key, ctx.guild.id)
                                        possible_tasks.append({"task": {task['task']}, "quantity": quantity})
                            goblin_tasks_info[selected_name] = {
                                'caster': team_id,
                                'tasks': possible_tasks
                            }
                            await team_chanob.send(
                                f"<:MindGoblin:1167108965239373844> Your team has chosen to use a Mind Goblin against {selected_name}!\n" +
                                f"You can now select which task they must complete from the `{target_difficulty.capitalize()}` tier.\n ")

                            await target_channel.send(
                                f"<:MindGoblin:1167108965239373844> Your team has been hit by a Mind Goblin!\n{casted_name} is currently deciding your task...")
                            message_text = ""
                            message_2 = ""
                            for i, task in enumerate(possible_tasks):
                                message_text += f"{i}. {task['quantity']} x {task['task']}\n"
                                if len(message_text) >= 1500:
                                    message_2 = message_text
                                    message_text = ""
                            await team_chanob.send(
                                f"{message_text}\n### To select the team's new task, type /mindgoblin followed by the number displayed above." +
                                f"")
                        elif item == "blood tithe":
                            for datitem in current_data:
                                if 'Number' in datitem:
                                    if int(datitem['Number']) == int(team_id):
                                        if barrelchest.get(team_id, False) == False:
                                            datitem['Current Tile'] -= 1
                                            current_tile = datitem['Current Tile']
                                            for boarditem in board_tiles:
                                                if int(boarditem['number']) == int(current_tile):
                                                    tile_type = boarditem['type']
                                            new_task1 = await taskManager(0, tile_type)
                                            casted_chan = datitem['Thread ID']
                                            casted_role = datitem['roleID']
                                            casted_name = datitem['Team name']
                                            new_task_q = await taskQuantity(casted_name, new_task1['taskNumber'],
                                                                            ctx.guild.id)

                                    elif int(datitem['Number']) == int(targteam):
                                        if barrelchest.get(targteam, False) == False:
                                            datitem['Current Tile'] -= 1
                                            current_loc = datitem['Current Tile']
                                            for boarditem in board_tiles:
                                                if int(boarditem['number']) == int(current_loc):
                                                    tile_type = boarditem['type']
                                            new_task2 = await taskManager(0, tile_type)
                                            effected_chan = datitem['Thread ID']
                                            effected_role = datitem['roleID']
                                            new_task2_q = await taskQuantity(datitem['Team name'],
                                                                             new_task2['taskNumber'], ctx.guild.id)
                                            effected_channel = await interactions.get(bot, interactions.Channel,
                                                                                      object_id=effected_chan)
                                            await effected_channel.send(
                                                f"### <@&{effected_role}>\nYour team has been hit by a <:BloodTithe:1167108961879719946> **Blood Tithe** by {casted_name}!\n" +
                                                "Both of your teams have been moved back one tile, and your quests re-rolled.\n" +
                                                f"Your new task is:\n" +
                                                f"> {new_task2_q} x {new_task2['task']}")
                                            await team_chanob.send(
                                                f"### <@&{casted_role}>\nYour team has cast a <:BloodTithe:1167108961879719946> **Blood Tithe** against {datitem['Team name'].capitalize()}!\nBoth of your teams have been moved back one tile, and your quests re-rolled.\n" +
                                                f"Your new task is:\n" +
                                                f"> {new_task_q} x {new_task1['task']}")
                                        else:
                                            await team_chanob.send(
                                                f"The team you casted against blocked your blood tithe with a barrelchest anchor!")

                        elif item == "dragon spear":
                            if targteam == "":
                                await ctx.reply("You must select a team to use this item against!")
                                return
                            for item in current_data:
                                if 'Number' in item:
                                    if item['Number'] == team_id:
                                        team_location = item['Current Tile']
                                    elif int(item['Number']) == int(targteam):
                                        targ_location = item['Current Tile']
                            text = f""
                            new_location = 0
                            for item in current_data:
                                if 'Number' in item:
                                    if item['Number'] == int(targteam):
                                        targ_chanid = item['Thread ID']
                                        targ_role = item['roleID']
                                        targ_chanob = await interactions.get(bot, interactions.Channel,
                                                                             object_id=targ_chanid)
                                        if barrelchest.get(targteam, False) == False:
                                            if int(team_location) >= int(targ_location):
                                                old_location = item['Current Tile']
                                                item['Current Tile'] -= 1
                                                new_location = item['Current Tile']
                                                text = f"ahead of you, your team moved **back 1 tile**"
                                            else:
                                                old_location = item['Current Tile']
                                                item['Current Tile'] += 1
                                                new_location = item['Current Tile']
                                                text = f"behind you, your team moved **forward 1 tile**"
                                        else:
                                            await targ_chanob.send(
                                                f"Your Barrelchest Anchor has protected you from a dragon spear special attack!")
                                        targ_chanob = await interactions.get(bot, interactions.Channel,
                                                                             object_id=targ_chanid)
                                        await targ_chanob.send(f"### Hey, <@&{targ_role}>!\n" +
                                                               f"<@&{team_role}> has hit your team with a **Dragon Spear**!\n" +
                                                               f"Since they were {text}!\n" +
                                                               f"`{old_location}` → `{new_location}`")
                        elif item == "shadow barrage":
                            await ref_updates(
                                f'Shadow barrage casted against {targteam}! expires in 12hrs, they cannot use abilities.',
                                '', '', '')
                        elif item == "nieve's elysian":
                            nieve[team_id] = True
                            await team_chanob.send(f"Your team has activated **Nieve's Elysian**!\n" +
                                                   "Any items used against you will be nullified in the process.")
                        elif item == "ward of the leech":
                            leechward[team_id] = True
                            await ctx.send(f"You've activated **Ward of the Leech**. Nobody is aware besides you.",
                                           ephemeral=True)
                        elif item == "ward of mending":
                            mending[team_id] = True
                            await team_chanob.send(
                                "You've activated a **Ward of Mending**, giving you a 50% chance to nullify Cracked Rune effects.")
                        elif item == "hunter's box traps":
                            hunter_traps[team_id] = True
                            await team_chanob.send(
                                "You've activated **Hunter's Box Traps**, which nulls pest/rodent items.")
                        elif item == "barrelchest anchor":
                            barrelchest[team_id] = True
                            await team_chanob.send(
                                "You've activated a **Barrelchest Anchor**, preventing movement effects from moving your team.")
                        elif item == "smoke barrage":
                            smoke_barrage[team_id] = True
                            await team_chanob.send(
                                "You've activated a **Smoke Barrage**, preventing your team from being targetted by items.")
                        elif item == "strange old man's spade":
                            for key, data in shop_emojis.items():
                                current_date = datetime.today().date()
                                shop_file = f"shop_items({str(current_date)}).json"
                                path = f'data/{server_id}/events'
                                shop_loc = os.path.join(path, shop_file)
                                # Check stock prior
                                possible_items = []
                                if os.path.exists(shop_loc):
                                    with open(shop_loc, 'r', encoding='utf-8') as f:
                                        shop_data = json.load(f)
                                        item_stock = shop_data["stock"]
                                        print(f"stock: {item_stock}")
                                        stored_date = shop_data["date"]
                                        shop_list = shop_data["shop_list"]
                                        selected_emojis = shop_data["selected_emojis"]
                                        for key, details in shop_emojis.items():
                                            if item_stock.get(key.lower(), None) == None:
                                                possible_items.append(key)
                                        # stock = int(item_stock.get(key.lower(), 100))
                                        # print(f"{key} stock: {stock}")
                                        # if stock > 1:
                                        #     possible_items.append(key)
                            print(f"possible items: {possible_items}")
                            if possible_items != []:
                                new_item = random.choice(possible_items)
                                print(f"Randomly selected an item {new_item}")
                                for data in current_data:
                                    if 'Number' in data:
                                        if data['Number'] == team_id:
                                            team_inventory = data['Inventory']
                                            for invent_item in team_inventory:
                                                if invent_item['item'] == new_item:
                                                    invent_item['quantity'] += 1
                                                    break
                            await team_chanob.send(
                                f"You've used **Strange Old Man's Spade** to dig up a random item not available in the current shop:\n" +
                                f"> {new_item.capitalize()}")
                            await ref_updates(f'{ctx.author.name} has used Strange Old Man''s Spade', '', '', '')
                        elif item == "alchemist's blessing":
                            alchemists_blessing[team_id] = True
                        elif item == "lightbearer":
                            lightbearer = active_cooldowns.lightbearer(server_id, currentTurn, used_teamname)
                            if lightbearer == "now":
                                await team_chanob.send(
                                    f"### <:lightbearer:1163182778901340302> Your team has used a Lightbearer!\n> Your active ability is now available!\n> Use it with `/active`")
                            else:
                                await team_chanob.send(
                                    f"### <:lightbearer:1163182778901340302> Your team has used a Lightbearer!" +
                                    "\n> Your active ability cooldown has been reduced by half of its original timer!" +
                                    f"\n> Time left: `{lightbearer}` turns")
                        elif item == "teleportation tablet":
                            for data in current_data:
                                if 'Number' in data:
                                    if data['Number'] == team_id:
                                        effected_tile = data['Current Tile']
                            for line in current_data:
                                if 'effectedTiles' in line:
                                    if {'type': "teletab", 'tile': current_tile, 'team': team_id} not in line[
                                        'effectedTiles']:
                                        line['effectedTiles'].append(
                                            {'type': "teletab", 'tile': current_tile, 'team': team_id})
                                    else:
                                        print("Dinh's was already placed, skipping adding it to the data again.")
                        elif item == "smokebarrageeffect":
                            await team_chanob.send(f"The team you selected had **Smoke Barrage** active.\n" +
                                                   "The usage of your item has been nulled!")

                        elif item == "none":
                            await team_chanob.send(
                                f"The team you used your item against had a Ward of the Leech active!\n" +
                                "They've stolen your item as a result, and it was rendered useless for you.")
                            leechward[targteam] = False
                    else:
                        await ctx.send(f"You voted for {item} \n" +
                                       f"Required votes: {invitem['votes']}/{required}", ephemeral=True)
                        player_name = ctx.author.nick
                        if player_name == None or player_name == "None":
                            player_name = ctx.author.username
                        text = f"{player_name} has cast a vote to use {item.capitalize()}!\n\nRequired votes: {invitem['votes']}/{required}"
                        new_image = textwrite.generate_image(text=text, is_header=False, centerpiece_image_url=None)
                        image_obj = interactions.File(new_image)
                        await team_chanob.send(f"<@&{team_role}>", files=image_obj)
        with open(fp, 'w') as jsonfile:
            json.dump(current_data, jsonfile)
    actives_object.save_to_file()
    if team_id:
        await sendTeamStatus(team_id, str(server_id))


# @bot.command(
#     name="reset_data",
#     description="Reset Lost Lands to its beginning state.",
#     default_member_permissions=interactions.Permissions.ADMINISTRATOR
# )
# async def reset_data(ctx):
#     server_id = 616498757441421322
#     fp = f"data/{server_id}/events/lost_lands.json"
#     message_reply = await ctx.send(f"Attempting to reset all event data to its origin.")
#     if os.path.exists(fp):
#         with open(fp, 'r') as jsonfile:
#             current_data = json.load(jsonfile)
#     for item in current_data:
#         if 'Number' in item:
#             item['Current Tile'] = 1
#             item['Current Type'] = 'air'
#             item['currentTurn'] = 1
#             team_invent = item['Inventory']
#             for invitem in team_invent:
#                 invitem['quantity'] = 0
#                 invitem['cooldown'] = 0
#                 invitem['votes'] = 0
#             mercyRuleTime = datetime.now() + timedelta(days=1)
#             item['mercyRule'] = mercyRuleTime.strftime("%Y-%m-%d %H:%M:%S.%f")
#             item['last_roll'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
#             item['Members'] = []
#             item['Team Captain'] = "none"
#             item['colead'] = 0
#     with open(fp, 'w') as jsonfile:
#             json.dump(current_data, jsonfile)
#     await message_reply.edit(f"Success! All teams have been completely reset to the beginning of the event.")


@bot.command(
    name="mindgoblin",
    description="Designed to be used to select another team's task after using a mind goblin against them.",
    options=[
        interactions.Option(
            name="new_task",
            description="Use the task ID given to you when you used the mind goblin.",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def mindgoblin(ctx, new_task: str = ""):
    command_user_team = await get_team_from_player(ctx.author.id)
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    if not command_user_team:
        await ctx.send(f"You were not found on any teams..")
        return
    command_user_teamid = team_name_to_id(command_user_team.lower())
    for target, info in goblin_tasks_info.items():
        possible_tasks = info['tasks']
        if int(info['caster']) == int(command_user_teamid):
            target_team = target
            break
    if int(new_task) not in possible_tasks:
        await ctx.send(f"You didn't select a task from the provided list!")
        return
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    for item in current_data:
        if 'Number' in item:
            if int(item['Number']) == int(target_team):
                item['taskNumber'] == new_task
                target_name = item['Team name']
                target_channel = item['Thread ID']
                target_role = item['roleID']
                team_status_cache[item['Number']] = 0
    target_chan = await interactions.get(bot, interactions.Channel, object_id=target_channel)
    new_task = await taskManager(new_task, 'air')
    new_quant = await taskQuantity(target_name, new_task['taskNumber'], ctx.guild.id)
    await target_chan.send(f"### Hey, <@&{target_role}>!\n" +
                           f"{command_user_team.capitalize()} has used a <:MindGoblin:1167108965239373844> **Mind Goblin** against your team!\n" +
                           f"They chose to reroll your task to:\n" +
                           f"> {new_quant} x {new_task}")
    with open(fp, 'w') as jsonfile:
        json.dump(current_data, jsonfile)


def itemCooldownTimers(item_type):
    if item_type != "o" and item_type != "d" and item_type != "e" and item_type != "t":
        item_type = get_item_type_from_shop(item_type, shop_emojis)
    if item_type == "o":
        return 2
    elif item_type == "d":
        return 2
    elif item_type == "e":
        return 3
    elif item_type == "t":
        return 2


async def get_team_from_player(player):
    print(f"Finding the team for player {player}")
    serverid = 616498757441421322
    if isinstance(player, str):
        ## sent with player name
        playerid = await playerfiles.get_id_from_name(player, serverid)
    else:
        playerid = player
    print(f"Player id returns as {playerid} on {serverid} for {player}")
    fp = f"data/{serverid}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
        for team in current_data[1:]:
            if team["Team Captain"] == playerid:
                return team["Team name"]
            if team["colead"] == playerid:
                return team["Team name"]
            for member in team["Members"]:
                if member['id'] == playerid:
                    return team["Team name"]
    else:
        return None
    return None  # Player not found in any team


@inventory_cmd.autocomplete(name="item")
async def inventory_items(ctx, user_input: str = ""):
    choices = []
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    for item in current_data:
        if 'Mercy Rule' not in item:
            if 'Number' in item:
                teamed_members = [member['id'] for member in item['Members']]
            total_members = len(teamed_members)
            if ctx.member.id in teamed_members or ctx.member.id == item['Team Captain']:
                member_teamid = item['Number']
                inventory = item['Inventory']
                found = True
    required = total_members // 3 * 2
    if required == 0:
        required = 1
    if found == True:
        for invitem in inventory:
            item_name = invitem['item']
            quantity = invitem['quantity']
            votes = invitem['votes']
            if int(votes) >= 1:
                vote_str = f"{votes}/{required} votes required."
            else:
                vote_str = f"0/{required} votes required."
            if int(quantity) >= 1:
                choices += [interactions.Choice(name=f"{item_name.capitalize()} {vote_str} (Stored: {quantity})",
                                                value=item_name)]
        if len(choices) < 1:
            choices = interactions.Choice(name="No items found in your team's inventory!", value="none")
    await ctx.populate(choices)


@inventory_cmd.autocomplete(name="targteam")
async def inventory_teams(ctx, user_input: str = ""):
    choices = []
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    for item in current_data:
        if 'Mercy Rule' not in item:
            if 'Number' in item:
                if ctx.author.id not in item['Members'] and ctx.author.id != item['Team Captain']:
                    choices += [interactions.Choice(
                        name=f"{item['Team name']} | Current tile: {item['Current Tile']} | Current points: {item['Team Points']}",
                        value=str(item['Number']))]

    await ctx.populate(choices)


async def place_dinhs(fresh_image, current_tile, team_id, server_id):
    # base_img = Image.open(f"data/{server_id}/events/lost-lands.png").convert("RGBA")
    rs_font_path = "font/runescape_uf.ttf"
    main_font = ImageFont.truetype(rs_font_path, 45)
    red = (255, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    ##default offset for any direction that the dinhs will be from the current rune image
    moveint = 50
    ##pull the coordinates for board tiles
    tile_coords = {}
    print("Placing a dinhs.")
    with open("data/lost-lands-map.csv", 'r') as csvfile:
        data = csvfile.readlines()
        for line in data:
            parts = re.split(r', (?=\()', line.strip())  # Split on the comma that is followed by a '('
            if len(parts) == 2:
                tile_num, coords = parts
                tile_coords[int(tile_num)] = tuple(map(int, re.findall(r'\d+', coords)))
            else:
                # Handle the error or skip the line
                print(f"Invalid line format: {line}")
    effectText = f"{current_tile}"
    dinhs_img_path = f"data/{server_id}/events/dinhs.png"
    dinhs_img = add_border(dinhs_img_path, border_color=(0, 0, 0, 255))
    dinhs_img = Image.fromarray(dinhs_img).resize((75, 75))
    x_coord, y_coord = tile_coords[current_tile]
    x_coord *= 2
    y_coord *= 2
    ##Move the effect image below the rune, as its the easiest to see... unless we're on sides
    rightTiles = [1, 2, 3, 4, 38, 39, 40, 42, 43, 44, 68, 69, 70, 71, 85, 86, 87, 88]
    leftTiles = [21, 78, 79, 80, 98, 99]
    topTiles = [64, 65, 66, 35]
    badTile = False
    for tilenumber in rightTiles:
        if current_tile == tilenumber:
            x_coord += moveint
            badTile = True
    for tilenumber in leftTiles:
        if current_tile == tilenumber and badTile == False:
            x_coord -= moveint
            badTile = True
    for tilenumber in topTiles:
        if current_tile == tilenumber and badTile == False:
            y_coord += moveint
            badTile = True
    if badTile == False:
        y_coord += moveint
    ##paste it back into the base_img at the specified coordinates
    fresh_image.paste(dinhs_img, (x_coord, y_coord), dinhs_img)
    (dinhx, dinhy) = dinhs_img.size
    txt_x, txt_y = x_coord + (dinhx // 2), y_coord + (dinhy // 2)
    textdrawer = ImageDraw.Draw(fresh_image)
    # Draw the tile number above the center of the rune
    text_pos = (txt_x, txt_y)
    textdrawer.text(text_pos, effectText, font=main_font, fill=red, stroke_width=1, stroke_fill=white)
    return fresh_image


def add_border(image_path, border_color, border_size=7):
    # Read image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Make sure it's RGBA
    if len(img.shape) < 3 or img.shape[2] < 4:
        raise ValueError("Image must be RGBA")

    # Convert the original image to B/W where white is the object
    _, alpha = cv2.threshold(img[:, :, 3], 0, 255, cv2.THRESH_BINARY)

    # Dilate the alpha channel (object boundary becomes bigger)
    dilated = cv2.dilate(alpha, None, iterations=border_size)

    # Invert the alpha channel (so object is black)
    inverted = cv2.bitwise_not(alpha)

    # Bitwise AND between inverted and dilated image, gives the border
    border = cv2.bitwise_and(dilated, inverted)

    # Color the border by replacing the original image border pixels
    img[border > 0] = border_color

    return img


##generates the board (runeType and numerical location)
async def generate_lost_board(server_id):
    num_total = 177
    num_cosmic = 6
    num_death = 7
    num_chaos = 7
    # populate the special tiles first
    tile_list = []
    glowing, cracked = await generate_specials()

    def pickrandomnumbers(n):
        return random.sample(list(set(range(1, 101))), n)

    with open(f"new_tiles.json", 'r') as jsonfile:
        new_tiledata = json.load(jsonfile)
    board_tiles = []
    tile_loop = 1
    for i in range(1, num_total + 1):
        runeType = None
        while runeType is None:
            if i in glowing:
                runeType = "glowing"
            elif i in cracked:
                runeType = "cracked"
            else:
                runeType = new_tiledata[str(i)]
        board_tiles.append({
            "number": i,
            "type": runeType,
        })
        #     # Handle regular tiles
        #     if tile_loop == 1:
        #         runeType = "air"
        #     elif tile_loop == 2:
        #         runeType = "earth"
        #     elif tile_loop == 3:
        #         runeType = "water"
        #     else:
        #         runeType = "fire"
        #         tile_loop = 0
        #     board_tiles.append({
        #         "number": i,
        #         "type": runeType,
        #     })
        tile_loop += 1

    # Place tiles along the path
    blank_image = "img/v3-lostlands.png"
    # board_image = place_tiles(blank_image, board_tiles)
    board_image = Image.open(blank_image).convert("RGBA")
    board_image.save(f"data/{server_id}/events/fresh-lost-lands.png")
    board_image.save(f"data/{server_id}/events/lost-lands.png")
    return board_tiles


@bot.command(
    name="genspecials",
    description="Generate special tile numbers for lost lands"
)
async def genspec(ctx):
    server_id = ctx.guild.id
    if server_id == 1131575888937504798:
        server_id = 616498757441421322
    glowing, cracked = await generate_specials()

    await updateBoard(str(server_id))
    await ctx.send(f"Glowing locations: \n> {glowing}\n" +
                   f"Cracked locations: \n> {cracked}")


async def generate_specials():
    crack_ct = 20
    glow_ct = 20

    def is_valid_distance(num, rune_list):
        return all(abs(num - rune) > 6 for rune in rune_list)

    glowing = []
    while len(glowing) < glow_ct:
        new_rune = random.choice(range(1, 177))
        if new_rune not in glowing and is_valid_distance(new_rune, glowing):
            glowing.append(new_rune)

    cracked = []
    while len(cracked) < crack_ct:
        new_rune = random.choice(range(1, 177))
        if new_rune not in cracked and new_rune not in glowing and is_valid_distance(new_rune, cracked):
            cracked.append(new_rune)

    return glowing, cracked


async def updateBoard(server_id):
    if not os.path.exists(f"data/{server_id}/events/lost_lands.json"):
        print("No file exists. can't update board.")
        return
    else:
        fresh_path = f"data/{server_id}/events/fresh-lost-lands.png"
        fresh_image = Image.open(fresh_path).convert("RGBA")
        with open(f"data/{server_id}/events/lost_lands.json", 'r') as jsonf:
            eventData = json.load(jsonf)
        team_imgs = []
        tile_coords = {}
        with open("data/lost-lands-map.csv", 'r') as csvfile:
            data = csvfile.readlines()
            for line in data:
                tile_num, coords = line.strip().split(", (")
                original_coords = tuple(map(int, coords.strip("()").replace(" ", "").split(",")))
                tile_coords[int(tile_num)] = tuple(coord for coord in original_coords)
        for item in eventData:
            if 'effectedTiles' in item:
                currentEffects = item['effectedTiles']
                if currentEffects != []:
                    for effect in currentEffects:
                        if effect['type'] == "dinh":
                            fresh_image = await place_dinhs(fresh_image, effect['tile'], effect['team'], server_id)
            elif 'Number' in item:
                team_name = team_id_to_name(item['Number'])
                # team_icon = team_icons[item['Number']]
                team_icon = f"http://www.droptracker.io/img/teams/{team_name.lower()}.png"
                if item['Members'] != []:
                    team_imgs.append({"image": team_icon, "team": item['Number'], "tile": item['Current Tile']})
        edited_path = f"data/{server_id}/events/lost-lands.png"
        # edited = Image.open(edited_path).convert("RGBA")
        black = (0, 0, 0)
        offsetx, offsety = 0, 0
        ##only offset the teams image if they are on the same tile as another team
        last_tiles = []
        for img in team_imgs:
            coordx, coordy = tile_coords[img['tile']]
            # Check if the current tile has already been encountered
            if img['tile'] in last_tiles:
                # Count the number of teams on the same tile
                team_count = last_tiles.count(img['tile'])
                coordx, coordy = tile_coords[img['tile']]
                if team_count == 1:
                    coordy += 65
                elif team_count == 2:
                    coordx += 30
                elif team_count == 3:
                    coordx += 13
                    coordy += 25
                elif team_count == 4:
                    coordx -= 14
                    coordy += 20
                elif team_count == 5:
                    coordx -= 30
                elif team_count == 6:
                    coordx += 15
                    coordy -= 26
                elif team_count == 7:
                    coordx -= 15
                    coordy -= 26
                elif team_count == 8:
                    coordx -= 25
                elif team_count == 9:
                    coordy += 25
            ##team is not in the last tiles data then we can just paste them onto the standard tile
            try:
                response = requests.get(img['image'])
                print(response.status_code)
                imgpath = Image.open(BytesIO(response.content)).convert("RGBA")
                width = int(imgpath.width)
                height = int(imgpath.height)
                new_width = int(width * 2.0)
                new_height = int(height * 2.0)
                new_size = (new_width, new_height)
                img_resize = imgpath.resize(new_size, Image.ANTIALIAS)
                fresh_image.paste(img_resize, (coordx, coordy), img_resize)
                print(f"Pasted the team's image onto the board at {coordx}, {coordy}")
            except Exception as e:
                print(f"Failed to process image {img['image']}: {e}")
                continue

            # Store the current tile in the list of last_tiles
            last_tiles.append(img['tile'])
        fresh_image.save(edited_path)
        fresh_image.save("C:/xampp/htdocs/img/lost-lands.png")
        print("Saved the new board.")
        # await send_lost_board(server_id)


@bot.command(
    name="glowing_event",
    description="Send a notification for glowing events. SEND FROM #ANNOUNCEMENTS!",
    options=[
        interactions.Option(
            name="event_type",
            description="Type of event that is being started (mini-type, not glowing/cracked)",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="info_text",
            description="Text to use in the image",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def glowing_event_cmd(ctx, event_type: str = "", info_text: str = ""):
    if ctx.author.id != 528746710042804247 and ctx.author.id != 217849931984142346 and ctx.author.id != 966700986024476743:
        await ctx.send("You do not have permission.")
        return
    text1 = "Glowing Rune Event"
    new_image1 = textwrite.generate_image(text=text1, is_header=True, centerpiece_image_url=None)
    image1_obj = interactions.File(new_image1)
    await ctx.channel.send(files=[image1_obj])
    event_image = textwrite.generate_image(text=f"{event_type}", is_header=False, centerpiece_image_url=None)
    event_type_img = interactions.File(event_image)
    await ctx.channel.send(files=[event_type_img])
    # new_image = textwrite.generate_image(text=text,is_header=False,centerpiece_image_url=None)
    # image_obj = interactions.File(new_image)
    # await ctx.channel.send(files=[image_obj])
    current_time = datetime.now()
    time_plus_24hrs = current_time + timedelta(hours=24)
    unix_timestamp = int(time_plus_24hrs.timestamp())
    if info_text != "":
        info_text = f"\n> **Information**: {info_text}\n"
    await ctx.channel.send(
        f"@everyone\n### A {event_type} mini-event has been started!\n{info_text}\nThe event will end <t:{unix_timestamp}:R>.")


def team_name_to_id(team_name):
    team_name_low = team_name.lower()
    if team_name_low == "bandos":
        team_id = 1
    if team_name_low == "zamorak":
        team_id = 2
    if team_name_low == "armadyl":
        team_id = 3
    if team_name_low == "tumeken":
        team_id = 4
    if team_name_low == "seren":
        team_id = 5
    if team_name_low == "guthix":
        team_id = 6
    if team_name_low == "saradomin":
        team_id = 7
    if team_name_low == "zaros":
        team_id = 8
    if team_name_low == "xeric":
        team_id = 9
    return team_id


def team_id_to_name(team_id):
    if team_id == 1:
        team_name = "Bandos"
    if team_id == 2:
        team_name = "Zamorak"
    if team_id == 3:
        team_name = "Armadyl"
    if team_id == 4:
        team_name = "Tumeken"
    if team_id == 5:
        team_name = "Seren"
    if team_id == 6:
        team_name = "Guthix"
    if team_id == 7:
        team_name = "Saradomin"
    if team_id == 8:
        team_name = "Zaros"
    if team_id == 9:
        team_name = "Xeric"
    return team_name


async def send_lost_board(serverid):
    ##called every time a board update happens
    if serverid == 1131575888937504798:
        serverid = 616498757441421322
    lost_channel = await read_properties('lostLandsMainChannel', serverid)
    lost_obj = await interactions.get(bot, interactions.Channel, object_id=lost_channel)
    lost_msg = await read_properties('lostLandsMessage', serverid)
    global firstUpdate
    if firstUpdate == False:
        await updateBoard(serverid)
        firstUpdate = True
    lost_datafile = f"data/{serverid}/events/lost_lands.json"
    with open(lost_datafile, 'r') as jsonfile:
        current_data = json.load(jsonfile)
    mercy_length = current_data[0]['Mercy Rule']

    lost_chan_ob = await interactions.get(bot, interactions.Channel, object_id=lost_channel)
    embeds = []  # Start with currentStatus in the list
    tilenum = []
    runetype = []
    for item in current_data:
        if 'Mercy Rule' in item:
            mercy_length = item
            for tile in item['Board Tiles']:
                tilenum.append(tile["number"])
                runetype.append(tile["type"])
        else:
            if item['Members'] != []:
                emoji = item['teamEmoji']
                team_embed = interactions.Embed(title="",
                                                description=f"<{emoji}> {item['Team name']} | Current location: {item['Current Tile']}")
                team_embed.add_field(name="Captain", value=f"<@{item['Team Captain']}>")
                invent_str = ""
                inventory = item['Inventory']
                points = item['Team Points']
                current_task = await taskManager(item['taskNumber'], item['Current Type'])
                current_task_amt = await taskQuantity(item['Team name'], item['taskNumber'], serverid)
                try:
                    current_prog = team_status_cache[item['Number']]
                except:
                    current_prog = 0
                team_embed.add_field(name="Current Task",
                                     value=f"{current_prog}/{current_task_amt} x {current_task['task']}")
                if inventory != []:
                    for invitem in inventory:
                        item_name = invitem['item']
                        quantity = invitem['quantity']
                        for shop_item, item_properties in shop_emojis.items():
                            if shop_item == item_name:
                                emoji = item_properties["emoji"]
                        if quantity >= 1:
                            if emoji != "\U0001F3B2":
                                invent_str += f"<{emoji}> **{item_name.capitalize()}**: `{quantity}`\n"
                            else:
                                invent_str += f"{emoji} **{item_name.capitalize()}**: `{quantity}`\n"
                    team_embed.add_field(name="Inventory", value=invent_str, inline=False)
                if int(points) > 1:
                    team_embed.set_footer(f"{item['Team name']}'s points: {points}")
                team_embed.add_field(name="",
                                     value=f"[Click to view {item['Team name']}'s channel](https://discord.com/channels/{serverid}/{item['Thread ID']})")
                member_string = "*None*" if item['Members'] == [] else "\n".join(
                    [f"<@{member['id']}>" for member in item['Members']])
                # captain = "*None*" if item['Team Captain'] == 0 else f"<@{item['Team Captain']}>"
                team_embed.add_field(name="Members", value=member_string, inline=False)

                embeds.append(team_embed)
                item['teamChannelLink'] = f"https://discord.com/channels/{serverid}/{item['Thread ID']}"
    with open(lost_datafile, 'w') as jsonfile:
        json.dump(current_data, jsonfile, indent=4)
    image_obj = interactions.File(f'data/{serverid}/events/lost-lands.png')
    title_img = interactions.File(f'data/{serverid}/events/lost-lands-title.png')
    if lost_msg != 0 and lost_msg != "0":
        print(f"lost_channel: {lost_channel} lost_msg: {lost_msg}")
        try:
            lost_msg_obj = await interactions.get(bot, interactions.Message, parent_id=lost_channel, object_id=lost_msg)
        except:
            lost_chan_ob = await interactions.get(bot, interactions.Channel, object_id=lost_channel)
            lost_msg_obj = await lost_chan_ob.send(f"# Lost Lands")
        if lost_msg_obj.attachments is not None:
            lost_msg_obj.attachments = []
        await lost_msg_obj.edit("# <:lllogo:1163587767930982430> **Lost Lands** <:lllogo:1163587767930982430>",
                                embeds=embeds, files=image_obj)
        if not lost_msg_obj.pinned:
            await lost_msg_obj.pin()
    else:
        await lost_obj.send(files=title_img)
        new_message = await lost_obj.send("# <:lllogo:1163587767930982430> Lost Lands <:lllogo:1163587767930982430>",
                                          embeds=embeds, files=image_obj)
        msg_id = new_message.id
        if not new_message.pinned:
            await new_message.pin()
        await set_property('lostLandsMessage', msg_id, serverid)


@bot.command(
    name="ll_reroll",
    description="Administration commands for the Lost Lands event",
    options=[
        interactions.Option(
            name="team",
            description="Select which team you are re-rolling the task for.",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True
        ),
        interactions.Option(
            name="mercyreset",
            description="Would you like to reset the team's mercy rule timer?",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )
    ]
)
async def ll_reroll(ctx: interactions.CommandContext, mercyreset: bool = False, team: str = ""):
    player_obj = await interactions.get(bot, interactions.Member, object_id=ctx.author.id, guild_id=ctx.guild.id)
    for role in player_obj.roles:
        if role == 1166538049757384725:
            ref = True
    if ctx.author.id == 528746710042804247:
        ref = True
    if ref == False:
        await ctx.send(
            "You do not have permission to view another team's cooldowns.\n> This command is reserved for Referees.")
        return
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    with open(fp, 'r') as jsonfile:
        data = json.load(jsonfile)

    team_index = None
    for i, item in enumerate(data):
        if 'Number' in item and item['Number'] == int(team):
            current_type = item['Current Type']
            team_index = i
            break

    new_task = await taskManager(0, current_type)
    await ctx.send(f"Team's task type: {current_type}")
    if team_index is not None:
        data[team_index]['taskNumber'] = new_task['taskNumber']
        data[team_index]['Status'] = 0
        data[team_index]['last_roll'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if mercyreset == True:
            mercyRuleTime = datetime.now() + timedelta(days=1)
            data[team_index]['mercyRule'] = mercyRuleTime.strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(fp, 'w') as jsonf:
            json.dump(data, jsonf)
    await ctx.send(f"Successfully re-rolled the team's task. Their new task is {new_task['task']}!")
    await sendTeamStatus(team_index, server_id)
    await send_lost_board(server_id)


@ll_reroll.autocomplete(name="team")
async def adminRerollTeams(ctx, user_input: str = ""):
    choices = []

    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    for item in current_data:
        if 'Mercy Rule' not in item:
            if 'Number' in item:
                current_task = await taskManager(item['taskNumber'], item['Current Type'])
                choices += [interactions.Choice(
                    name=f"{item['Team name']} ({current_task['task']}) Current tile: {item['Current Tile']}",
                    value=str(item['Number']))]

    await ctx.populate(choices)


async def player_points(counted, tasknumber, team_name, server_id):
    total_points = 0
    with open(f"data/new_events.json", 'r') as jsonfile:
        tasks = json.load(jsonfile)
    if tasknumber != 0:
        assigned = tasks.get(str(tasknumber))
        assigned['taskNumber'] = tasknumber
    for task_key, task in tasks.items():
        if str(task['difficulty']).lower() == "hard":
            total_points = 8000
        elif str(task['difficulty']).lower() == "elite":
            if team_name.lower() == "tumeken":
                total_points = (6000 * 1.50)
            else:
                total_points = 6000
        elif str(task['difficulty']).lower() == "medium":
            total_points = 4000
        elif str(task['difficulty']).lower() == "easy":
            total_points = 2000
    required = await taskQuantity(team_name, tasknumber, server_id)
    # Divide the total points for the assigned task difficulty by the required quantity for that task
    points_per = int(total_points / required)
    # this is the amount of points per piece of the task
    earned = points_per * counted
    return earned


@bot.command(
    name="add_items",
    description="Re-adds items to the team's current progress towards a 'part' completion.",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="team",
            description="Name of team",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="item_string",
            description="What item are you adding to their current progress?",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def add_items(ctx, team: str = "", item_string: str = ""):
    if ctx.guild_id == 1131575888937504798:
        server_id = 616498757441421322
    else:
        server_id = 616498757441421322
    fp = f"data/{server_id}/events/lost_lands.json"
    if os.path.exists(fp):
        with open(fp, 'r') as jsonfile:
            current_data = json.load(jsonfile)
    for item in current_data:
        if 'Mercy Rule' not in item:
            if 'Number' in item:
                if item['Team name'].lower() == team.lower():
                    item['taskItemsObtained'].append({'item': item_string, 'player': 'any', 'team': item['Number']})
                    current_progress = item['taskItemsObtained']
    with open(fp, 'w') as jsonf:
        json.dump(current_data, jsonf, indent=4)
    await ctx.send(f"Added the item to the team's current progress. Current items: \n> {current_progress}")


@bot.command(
    name="find_task",
    description="Search the task list for a matching name (to find IDs, etc)",
    options=[
        interactions.Option(
            name="query",
            description="What item/task are you looking for?",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def find_task_data(ctx, query):
    with open(f"data/new_events.json", 'r') as jsonfile:
        tasks = json.load(jsonfile)
    found_matches = []
    for task_key, task in tasks.items():
        if query.lower() in task['task'].lower():
            task_with_key = task.copy()
            task_with_key['taskNumber'] = task_key
            found_matches.append(task_with_key)
    if not found_matches:
        await ctx.send(f"There were no matching tasks found for '{query}'.")
    else:
        message_string = ""
        for match in found_matches:
            message_string += f"Task Number: {match['taskNumber']}, Task: {match['task']}, Quantity: {match['quantity']}, NPC: {match['npc']}, Difficulty: {match['difficulty']}\n"
        await ctx.send(message_string)


async def taskManager(tasknumber, current_rune):
    global waiting_rolls
    ## stored tasks here and return a task based on its numerical value
    ## a team will be sent to this function with a tasknumber of 0 if they've completed their previous task already.
    ## This means we will need to assign a new, random task for the team based on their current rune
    with open(f"data/new_events.json", 'r') as jsonfile:
        tasks = json.load(jsonfile)
    ##Handle glowing/cracked elsewhere in our code.
    if "glowing_" in current_rune or "cracked_" in current_rune:
        current_rune = current_rune.replace("glowing_", "").replace("cracked_", "")
    if tasknumber != 0 and tasknumber != "0":
        assigned = tasks.get(str(tasknumber))
        assigned['taskNumber'] = tasknumber
    else:
        easy_tasks = []
        medium_tasks = []
        hard_tasks = []
        elite_tasks = []
        all_tasks = []
        print(current_rune, "is the current rune with #0")
        # create a dict of easy, medium, hard and elite_tasks, along with all_tasks. This stores the numerical task IDs in a list.
        for task_key, task in tasks.items():
            if str(task['difficulty']).lower() == "hard":
                hard_tasks.append(task_key)
            elif str(task['difficulty']).lower() == "elite":
                elite_tasks.append(task_key)
            elif str(task['difficulty']).lower() == "medium":
                medium_tasks.append(task_key)
            elif str(task['difficulty']).lower() == "easy":
                easy_tasks.append(task_key)
            all_tasks.append(task_key)
        if current_rune == "air":
            tasknumber = choice(easy_tasks)
            assigned = tasks.get(str(tasknumber))
        elif current_rune == "water":
            tasknumber = choice(medium_tasks)
            assigned = tasks.get(str(tasknumber))
        elif current_rune == "earth":
            tasknumber = choice(hard_tasks)
            assigned = tasks.get(str(tasknumber))
        elif current_rune == "fire":
            tasknumber = choice(elite_tasks)
            assigned = tasks.get(str(tasknumber))
        if assigned:
            assigned['taskNumber'] = tasknumber
        else:
            assigned = tasks.get(str(tasknumber))
            assigned['taskNumber'] = tasknumber
    return assigned


@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name} with ID: {bot.me.id}")
    await bot.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(name=f"Lost Lands", type=interactions.PresenceActivityType.WATCHING)
            ]
        )
    )
    await send_upkeepmsg()
    send_upkeepmsg.start()
    await send_shop_update()
    send_shop_update.start()
    await grab_pickle()
    store_pickle.start()
    await update_tasks()
    update_tasks.start()


bot.start()