import os
import asyncpg
import logging


db_connection = os.getenv("DATABASE_URL")
logging.basicConfig(level=logging.INFO)


async def get_id_by_tg_id(tg_id):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            id = await connection.fetch(f'''
                SELECT id FROM users WHERE user_id = {tg_id}
            ''')
            logging.info(f"User {tg_id} has id {id}")
        return id[0]['id']
    except Exception as e:
        logging.exception(e)
        return None


async def get_last_period_by_id(user_id):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            last_period = await connection.fetch(f'''
                SELECT id FROM periods WHERE user_id = {user_id} AND end_date is NULL ORDER BY id DESC LIMIT 1
            ''')
            if not last_period:
                await connection.execute(f'''
                    INSERT INTO periods (user_id) VALUES ({user_id})
                ''')
                last_period = await connection.fetch(f'''
                    SELECT id FROM periods WHERE user_id = {user_id} ORDER BY id DESC LIMIT 1
                ''')
        return last_period[0]['id']
    except Exception as e:
        logging.exception(e)
        return None


async def insert_new_hours_count(tg_id, hours_count, date):
    logging.info(f"Inserting new hours count: {tg_id}, {hours_count}, {date}")
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            user_id = await get_id_by_tg_id(tg_id)
            period_id = await get_last_period_by_id(user_id)
            date_check = await connection.fetch(f'''
                SELECT id FROM hours WHERE user_id = {user_id} AND period_id = {period_id} AND date = '{date}'
            ''')
            if date_check:
                logging.info(f"User {tg_id} already have hours count for {date}")
                return False
            await connection.execute(f'''
                INSERT INTO hours (user_id, period_id, date, hours_count) 
                VALUES ({user_id}, {period_id}, '{date}', {hours_count})
            ''')
            logging.info(f"User {tg_id} successfully inserted new hours count for {date}")
            return True
    except Exception as e:
        logging.exception(e)
        return False


async def update_description(tg_id, description, date):
    logging.info(f"Updating description: {tg_id}, {description}, {date}")
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            user_id = await get_id_by_tg_id(tg_id)
            period_id = await get_last_period_by_id(user_id)
            await connection.execute(f'''
                UPDATE hours SET description = '{description}' WHERE user_id = {user_id} AND period_id = {period_id} AND date = '{date}'
            ''')
            logging.info(f"User {tg_id} successfully updated description for {date}")
            return True
    except Exception as e:
        logging.exception(e)
        return False


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


async def insert_new_user(tg_id):
    logging.info(f"User {tg_id} try add to database.")
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            user_id = await connection.fetch(f'''
                SELECT id FROM users WHERE user_id = {tg_id}
            ''')
            if not user_id:
                await connection.execute(f'''
                    INSERT INTO users (user_id) VALUES ({tg_id})
                ''')
                logging.info(f"User {tg_id} added to database.")
                return True
            else:
                logging.info(f"User {tg_id} already exists in database.")
                return False
    except Exception as e:
        logging.exception(e)
        return False
