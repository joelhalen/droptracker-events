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
from utils.db.database import Database


database = Database()


class EventManager:
    def __init__(self):
        self.database = database

    async def create_game(self, game_id, game_params):
        game_exists = await self.database.fetch_data("SELECT game_id FROM games WHERE game_id = %s", (game_id,))
        if game_exists:
            raise ValueError("Game already exists")
        await self.database.send_query(
            "INSERT INTO games (game_id, game_params, state) VALUES (%s, %s, 'waiting')",
            (game_id, game_params)
        )
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
        return f"Player {player_id} registered to game {game_id}"

    async def create_team(self, team_id, game_id):
        team_exists = await self.database.fetch_data("SELECT team_id FROM teams WHERE team_id = %s", (team_id,))
        if team_exists:
            raise ValueError("Team already exists")
        await self.database.send_query(
            "INSERT INTO teams (team_id, game_id) VALUES (%s, %s)",
            (team_id, game_id)
        )
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

