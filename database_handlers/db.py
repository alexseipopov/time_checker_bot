import os
import asyncpg
import logging


db_connection = os.getenv("DATABASE_URL")
logging.basicConfig(level=logging.INFO)


async def get_id_by_tg_id(tg_id):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            id = await connection.fetchval(f'''
                SELECT id FROM users WHERE user_id = {tg_id}
            ''')
        return dict(id)['id']
    except Exception as e:
        logging.exception(e)
        return None


async def get_last_period_by_id(user_id):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            last_period = await connection.fetchval(f'''
                SELECT id FROM periods WHERE user_id = {user_id} AND end_date is NULL ORDER BY id DESC LIMIT 1
            ''')
            if not last_period:
                await connection.execute(f'''
                    INSERT INTO periods (user_id) VALUES ({user_id})
                ''')
                last_period = await connection.fetchval(f'''
                    SELECT id FROM periods WHERE user_id = {user_id} ORDER BY id DESC LIMIT 1
                ''')
        return dict(last_period)['id']
    except Exception as e:
        logging.exception(e)
        return None


async def insert_new_hours_count(tg_id, hours_count, date):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            user_id = await get_id_by_tg_id(tg_id)
            period_id = await get_last_period_by_id(user_id)
            await connection.execute(f'''
                INSERT INTO hours (user_id, period_id, date, hours_count) 
                VALUES ({user_id}, {period_id}, {date}, {hours_count})
            ''')
    except Exception as e:
        logging.exception(e)


async def close_period(tg_id):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            user_id = await get_id_by_tg_id(tg_id)
            period_id = await get_last_period_by_id(user_id)
            await connection.execute(f'''
                UPDATE periods SET end_date = NOW() WHERE id = {period_id}
            ''')
    except Exception as e:
        logging.exception(e)

