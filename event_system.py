##################################################################################################
###                                                                                            ###
###                                 DropTracker Event Bot                                      ###
###                                     + Quart API                                            ###
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

from utils.db.database import Database
from core.item import Item

database = Database()


## Define all the items that are
# used inside the Lost Lands event using the Item class
def define_items():
    usable_items = {}
    items_to_add = [
        # Re-rolls
        {"itemid": 0, "name": "reroll", "full_name": "Re-roll",
         "description": "Re-rolls the task that has been currently assigned.",
         "emoji": "🔄",
         "item_type": "misc", "movement": 0, "max_held": 1, "cooldown": 5},
        # Dinh's bulwark
        {"itemid": 1, "name": "dinhs", "full_name": "Dinh's Bulwark",
         "description": "Prevents your team from being affected by movement-related items or abilities.\n"
                        "Expires after one use.",
         "emoji": ":game_die:", "item_type": "defensive",
         "movement": 0},
    ]
    for item_data in items_to_add:
        item = Item(**item_data)
        usable_items[item.name] = item

    return usable_items


items = define_items()


class LostLandsManager:
    def __init__(self):
        self.database = database
        self.games = {}  # Key: game_id, Value: game details
        self.players = {}  # Key: player_id, Value: player details
        self.teams = {}  # Key: team_id, Value: team details
        self.items = items

        asyncio.run(self.load_data_from_db())

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

    async def write_log(self, log_type, name, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
           INSERT INTO logs (log_type, name, message, timestamp)
           VALUES (%s, %s, %s, %s)"""
        await self.database.send_query(query, (log_type, name, message, timestamp))

    async def create_game(self, game_id, game_params):
        game_exists = await self.database.fetch_data("SELECT game_id FROM games WHERE game_id = %s", (game_id,))
        if game_exists:
            raise ValueError("Game already exists")
        await self.database.send_query(
            "INSERT INTO games (game_id, game_params, state) VALUES (%s, %s, 'waiting')",
            (game_id, game_params)
        )
        self.games[game_id] = {'game_id': game_id, 'game_params': game_params, 'state': 'waiting'}
        return f"Game {game_id} created"

    async def register_player(self, game_id, player_id, team_id=None):
        player_exists = await self.database.fetch_data("SELECT player_id FROM players "
                                                       "WHERE player_id = %s AND game_id = %s",
                                                       (player_id, game_id,))
        if player_exists:
            raise ValueError("Player already registered")
        if team_id:
            await self.database.send_query(
                "INSERT INTO players (player_id, game_id, team_id) VALUES (%s, %s, %s)",
                (player_id, game_id, team_id)
            )
        else:
            await self.database.send_query(
                "INSERT INTO players (player_id, game_id) VALUES (%s, %s)",
                (player_id, game_id)
            )
        self.players[player_id] = {'player_id': player_id, 'game_id': game_id, 'team_id': team_id}
        return f"Player {player_id} registered to game {game_id}"

    async def create_team(self, team_id, game_id):
        team_exists = await self.database.fetch_data("SELECT team_id FROM teams WHERE team_id = %s", (team_id,))
        if team_exists:
            raise ValueError("Team already exists")
        await self.database.send_query(
            "INSERT INTO teams (team_id, game_id) VALUES (%s, %s)",
            (team_id, game_id)
        )
        self.teams[team_id] = {'team_id': team_id, 'game_id': game_id}
        return f"Team {team_id} created for game {game_id}"

    async def assign_player_to_team(self, player_id, team_id):
        await self.database.send_query(
            "UPDATE players SET team_id = %s WHERE player_id = %s",
            (team_id, player_id)
        )
        return f"Player {player_id} assigned to team {team_id}"

    async def update_game_state(self, game_id, new_state):
        await self.database.send_query(
            "UPDATE games SET state = %s WHERE game_id = %s",
            (new_state, game_id)
        )
        return f"Game {game_id} updated to state {new_state}"

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
            return False, "The item you were given or tried to give was not found"
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
                    return False, f"You are already holding too many items of this type! ({new_item.type})"
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
