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
from utils.db.database import send_query

## For team and player-based inventory management
class Inventory:
    def __init__(self, owner, size: int = 10, name: str = "inventory", max_stock: int = 3):
        # Define the inventory container's owner (team or player, which one)
        # Alongside its max size (max amount of unique items)
        # It's max stock (max amount per item)
        # and the name of the container (inventory, bank, etc)
        self.owner = owner
        self.size = size
        self.max_stock = max_stock
        self.name = name
        self.items = {}

    @staticmethod
    async def add_item_to_player(self, player_id, inventory_name, item_id, quantity):
        query = ("INSERT INTO inventory (player_id, name, "
                 "item_id, quantity) VALUES (%s, %s, %s, %s)")
        self.items[item_id] += quantity
        return await send_query(query, (player_id, inventory_name, item_id, quantity))

    # async def remove_item_from_player(self, item_id, quantity, inventory_name: str = "inventory"):
    #     self.items[item_id] -= quantity
    #     query = ("UPDATE inventory SET quantity = %s WHERE item_id = %s, inventory_name = %s"
    #              "")