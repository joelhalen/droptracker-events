import aiomysql
import yaml


class Database:
    def __init__(self, config_path='cfg/config.yaml'):
        self.config = self.load_config(config_path)
        self.db = 'events'
        self.port = 3306

    @staticmethod
    def load_config(config_path):
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)

    async def get_database_connection(self):
        return await aiomysql.connect(
            host=self.config['database_host'],
            port=self.port,
            user=self.config['database_user'],
            password=self.config['database_pass'],
            db=self.db
        )

    async def fetch_data(self, query, args=()):
        async with await self.get_database_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                result = await cur.fetchall()
        return result

    async def send_query(self, query, args=()):
        try:
            async with await self.get_database_connection() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(query, args)
                    if cur.rowcount > 0:
                        await conn.commit()  # Commit the transaction if changes were made
                        return True
                    else:
                        return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    async def init_database(self):
        games_table = """
        CREATE TABLE IF NOT EXISTS games (
            game_id VARCHAR(255) PRIMARY KEY,
            game_params TEXT,
            state VARCHAR(50)
        );
        """

        players_table = """
        CREATE TABLE IF NOT EXISTS players (
            player_id VARCHAR(255) PRIMARY KEY,
            game_id VARCHAR(255),
            team_id VARCHAR(255),
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        );
        """

        teams_table = """
        CREATE TABLE IF NOT EXISTS teams (
            team_id VARCHAR(255) PRIMARY KEY,
            game_id VARCHAR(255),
            players TEXT,
            inventory TEXT,
            currentTile INTEGER,
            lastTile INTEGER,
            effects TEXT,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        );
        """

        await self.send_query(games_table)
        await self.send_query(players_table)
        await self.send_query(teams_table)
