##################################################################################################
###                                                                                            ###
###                                Lost Lands Event System                                     ###
###                                                                                            ###
###                           This bot was written by @joelhalen                               ###
###                                     joelhalen.net                                          ###
###                              https://www.droptracker.io                                    ###
###                                                                                            ###
###                             Copyright DropTracker.io 2024                                  ###
###                                 All Rights Reserved.                                       ###
###                                                                                            ###
###     Please maintain the above copyright notice in redistributions or modifications.        ###
##################################################################################################
import asyncio
import datetime

import discord
import interactions
from interactions import ChannelType, Permissions, Overwrite

from utils.db.database import Database
from core.item import Item

database = Database()


## Define all the items that are
# used inside the Lost Lands event using the Item class
def define_items():
    usable_items = {}
    items_to_add = [
        ## TODO : Public-facing images for all items in the shop
        # Re-rolls
        {"itemid": 0, "name": "reroll", "full_name": "Re-roll",
         "cost": 5,
         "description": "Re-rolls the task that has been currently assigned.",
         "emoji": "🔄",
         "image_url": "https://www.droptracker.io/img/dt-logo.png",
         "item_type": "misc", "movement": 0, "max_held": 1, "cooldown": 5},
        # Dinh's bulwark
        {"itemid": 1, "name": "dinhs", "full_name": "Dinh's Bulwark",
         "cost": 7,
         "description": "Prevents your team from being affected by movement-related items or abilities.\n"
                        "Expires after one use.",
         "emoji": ":game_die:", "item_type": "defensive",
         "image_url": "https://www.droptracker.io/img/dt-logo.png",
         "movement": 0},
    ]
    for item_data in items_to_add:
        item = Item(**item_data)
        usable_items[item.name] = item

    return usable_items


items = define_items()


class LostLandsManager:
    def __init__(self, bot):
        self.database = database
        self.games = {}
        self.players = {}
        self.teams = {}
        self.items = items
        self.use_database = False
        self.bot = bot

    async def async_init(self):
        await self.load_data_from_db()

    async def load_data_from_db(self):
        await self.load_games()
        await self.load_players()
        await self.load_teams()

    async def load_games(self):
        games = await self.database.fetch_data("SELECT * FROM games")
        for game in games:
            self.games[game['game_id']] = game

    async def load_players(self):
        players = await self.database.fetch_data("SELECT * FROM players")
        for player in players:
            self.players[player['player_id']] = player

    async def load_teams(self):
        teams = await self.database.fetch_data("SELECT * FROM teams")
        for team in teams:
            self.teams[team['team_id']] = team

    async def write_log(self, name, message, log_type: str = "DEBUG"):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
           INSERT INTO logs (log_type, name, message, timestamp)
           VALUES (%s, %s, %s, %s)"""
        print(f"[{timestamp}] {log_type} - {name} - {message}")
        if self.use_database:
            await self.database.send_query(query, (log_type, name, message, timestamp))

    async def create_game(self, game_id, game_params, server_id):
        game_exists = await self.database.fetch_data("SELECT game_id FROM games WHERE game_id = %s", (game_id,))
        if game_exists:
            raise ValueError("Game already exists")
        self.games[game_id] = {'game_id': game_id, 'server_id': server_id, 'game_params': game_params,
                               'state': 'waiting'}
        await self.write_log(f"Game Creation", f"Game {game_id} + created")
        if self.use_database:
            await self.database.send_query(
                "INSERT INTO games (game_id, server_id, game_params, state) VALUES (%s, %s, %s, 'waiting')",
                (game_id, server_id, game_params)
            )
        return self.games[game_id]

    async def register_player(self, game_id, player_id, team_id=None):
        player_exists = await self.database.fetch_data("SELECT player_id FROM players "
                                                       "WHERE player_id = %s AND game_id = %s",
                                                       (player_id, game_id,))
        if player_exists:
            raise ValueError("Player already registered")
        if self.use_database:
            if team_id:
                await self.database.send_query(
                    "INSERT INTO players (player_id, game_id, team_id) VALUES (%s, %s, %s)",
                    (player_id, game_id, team_id)
                )
                ## TODO : update teams player row with new player
            else:
                await self.database.send_query(
                    "INSERT INTO players (player_id, game_id) VALUES (%s, %s)",
                    (player_id, game_id)
                )
        self.players[player_id] = {'player_id': player_id, 'game_id': game_id, 'team_id': team_id}
        await self.write_log(f"Player Registration", f"Player {player_id} signed up for the event")
        return True

    async def create_team(self, team_id, game_id):
        team_exists = await self.database.fetch_data("SELECT team_id FROM teams WHERE team_id = %s", (team_id,))
        if team_exists:
            raise ValueError("Team already exists")
        if self.use_database:
            await self.database.send_query(
                "INSERT INTO teams (team_id, game_id, thread_id, role_id) VALUES (%s, %s, 0, 0)",
                (team_id, game_id)
            )
        self.teams[team_id] = {'team_id': team_id, 'game_id': game_id, 'thread_id': 0, 'role_id': 0}

        await self.write_log(f"Team Creation", f"Team {team_id} created in game {game_id}")
        return self.teams[team_id]

    async def assign_player_to_team(self, player_id, team_id, game_id):
        if self.use_database:
            await self.database.send_query(
                "UPDATE players SET team_id = %s WHERE player_id = %s AND game_id = %s",
                (team_id, player_id, game_id)
            )

        await self.write_log(f"Team Assigned", f"Player {player_id} has been "
                                               f"assigned to {team_id} in game {game_id}")
        return self.players[player_id]

    async def update_game_state(self, game_id, new_state):
        if self.use_database:
            await self.database.send_query(
                "UPDATE games SET state = %s WHERE game_id = %s",
                (new_state, game_id)
            )
        self.games[game_id]["state"] = new_state
        await self.write_log(f"State Change", f"Game {game_id}'s game state was updated: {new_state}")
        return self.games[game_id]["state"]

    async def give_item(self, individual: bool, targ_id: int, item: str, reason: str = "None provided"):
        new_item = None
        if item in self.items:
            new_item = self.items[item]
        else:
            for item in self.items:
                if item.name == item:
                    new_item = self.items[item]
                elif item.full_name == item:
                    new_item = self.items[item]
        if new_item is None:
            await self.write_log("give_item",
                                 "Item not found",
                                 f"{new_item} was not found in the item list: {self.items}")
            return False, "not found"

        else:
            if individual:
                if self.players[targ_id]['items'].count(new_item) > new_item.max_held:
                    await self.write_log("WARNING",
                                         "Too many items",
                                         f"{self.players[targ_id]['player_name']} was "
                                         f"given {new_item.full_name} but did not have "
                                         f"enough space in their inventory. "
                                         f"Held/Max: "
                                         f"{self.players[targ_id]['items'].count(new_item)}/{new_item.max_held}")
                    return False, f"Too many!"
                self.players[targ_id]['items'].append(new_item)
            else:
                if self.players[targ_id]['items'].count(new_item) > new_item.max_held:
                    await self.write_log("WARNING",
                                         "Too many items",
                                         f"{self.teams[targ_id]['team_name']} was "
                                         f"given {new_item.full_name} but did not have "
                                         f"enough space in their inventory. "
                                         f"Held/Max: "
                                         f"{self.teams[targ_id]['items'].count(new_item)}/{new_item.max_held}")
                    return False, f"Your team is already holding too many items of this type! ({new_item.type})"
                self.teams[targ_id]['items'].append(new_item)

    async def start_game_cmd(self, game_id):
        event_start_message = f"Event starting message to sent to users!! :)"
        if game_id not in self.games:
            return False
        try:
            self.games[game_id]["state"] = "p.op1.team.active"
            player_ct = 0
            for player in self.players:
                player_ct += 1
                if player["game_id"] == game_id:
                    if player['guild_id'] != "none":
                        member_object = await interactions.get(self.bot, interactions.Member,
                                                               object_id=player['player_id'],
                                                               parent_id=player['guild_id'])
                        await member_object.send(event_start_message)
                    else:
                        user_object = await interactions.get(self.bot, interactions.User,
                                                             object_id=int(player['player_id']))
                        await user_object.send(event_start_message)

            await self.write_log("Event marked as starting",
                                 f"{game_id} has been started. {player_ct} players notified.")
            await self.start_game(game_id, player_ct)
        except Exception as e:
            print(f"Error: {e}")

    async def start_game(self, game_id, player_ct):
        if self.games[game_id]["state"] != "p.op1.team.active":
            return False
        self.games[game_id]["state"] = f"1.team.starting.{player_ct}"
        ll_category = None
        try:
            server_object = await interactions.get(self.bot, interactions.Guild,
                                                   object_id=self.games[game_id]['server_id'])
            if "Lost Lands Event" not in [channel.name for channel in server_object.channels]:
                ll_category = await server_object.create_channel(name="Lost Lands Event",
                                                                 type=ChannelType.GUILD_CATEGORY)
            else:
                for channel in server_object.channels:
                    if channel.name == "Lost Lands Event":
                        ll_category = channel
        except Exception:
            print("Unable to complete the request to start a game"
                  "for an unknown reason...")
            return
        if ll_category is None:
            return False
        for team in self.teams:

            if team["game_id"] == game_id:
                try:
                    team_thread = await ll_category.create_thread(team['name'],
                                                                  type=ChannelType.GUILD_PRIVATE_THREAD,
                                                                  invitable=False,
                                                                  reason="Event beginning")
                    self.teams[team]['thread_id'] = team_thread.id
                    allow_permissions = Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES
                    team_role = discord.utils.get(server_object.roles, name=team['name'])
                    await team_thread.permissions.(team_role, read_messages=True, send_messages=True)

                    await team_thread.send(f"Hey <@&{self.teams[team]['role_id']}!\n"
                                           f"This is your private team channel for the **Lost Lands** event!")
                except Exception as e:
                    print("Unable to properly create the team thread")
