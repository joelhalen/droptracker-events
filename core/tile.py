
## Defines a tile inside the game board

class Tile:
    def __init__(self, location: int):
        self.location = location
        self.effects = {}
        self.type = ""

    def set_type(self, tile_type):
        self.type = tile_type

    def set_effect(self, effect_name, effect_value, team_id, player_id):
        self.effects[effect_name] = {"value": effect_value,
                                     "team_id": team_id,
                                     "player_id": player_id}

    def clear_effect(self, effect_name):
        self.effects[effect_name] = {}

    def clear_all_effects(self):
        self.effects = {}
