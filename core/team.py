from utils.db.database import send_query


class Team:
    def __init__(self, team_id):
        self.team_id = team_id

    async def assign_player_to_team(self, player_id):
        query = "UPDATE players SET team_id = %s WHERE player_id = %s"
        return await send_query(query, (self.team_id, player_id))


async def remove_player_from_team(self, player_id):
    query = "UPDATE players SET team_id = NULL WHERE player_id = %s"
    return await send_query(query, (player_id,))