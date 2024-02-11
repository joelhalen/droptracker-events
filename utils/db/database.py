import aiomysql

async def get_database_connection():
    # Create a connection to your MySQL database
    conn = await aiomysql.connect(host='localhost', port=3306,
                                  user='dtdb', password='0X[y(Ref6YOUW)D)',
                                  db='events')
    return conn


async def fetch_data(query, args=()):
    async with await get_database_connection() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            result = await cur.fetchall()
    return result


async def send_query(query, args=()):
    try:
        async with await get_database_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                # Check if any rows were affected
                if cur.rowcount > 0:
                    await conn.commit()  # Commit the transaction if changes were made
                    return True
                else:
                    return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False