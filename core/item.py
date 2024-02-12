class Item:
    def __init__(self, itemid, name, full_name, description, item_type,
                 movement: int, emoji: str, max_held: int = 100,
                 cooldown: int = 3):
        self.id = itemid
        self.name = name
        self.full_name = full_name
        self.movement = movement
        self.description = description
        self.max_held = max_held
        self.cooldown = cooldown
        self.type = item_type
        self.emoji = emoji
