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

from utils.db.database import fetch_data, send_query


# Defines a player in the game's memory and
# stores up-to-date information on score, etc
class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    async def get_player_info(self):
        query = "SELECT * FROM players WHERE player_id = %s"
        return await fetch_data(query, (self.player_id,))

    async def add_points(self, points):
        query = "UPDATE players SET points = points + %s WHERE player_id = %s"
        return await send_query(query, (points, self.player_id))

