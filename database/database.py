import os
import asyncpg


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool:
            return

        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable not found.")

        self.pool = await asyncpg.create_pool(database_url)

        print("✅ Connected to PostgreSQL")

        await self.create_tables()

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("🔒 Database connection closed.")

    async def create_tables(self):
        async with self.pool.acquire() as conn:

            # -----------------------------
            # Ticket Panels
            # -----------------------------
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ticket_panels (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    panel_type TEXT NOT NULL
                );
            """)

            # -----------------------------
            # Tickets
            # -----------------------------
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id SERIAL PRIMARY KEY,
                    channel_id BIGINT NOT NULL,
                    owner_id BIGINT NOT NULL,
                    ticket_type TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # -----------------------------
            # Relationships
            # -----------------------------
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    partner_id BIGINT NOT NULL,
                    relationship_type TEXT NOT NULL
                );
            """)

            # -----------------------------
            # Marriages
            # -----------------------------
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS marriages (
                    id SERIAL PRIMARY KEY,
                    user1_id BIGINT NOT NULL,
                    user2_id BIGINT NOT NULL,
                    married_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        print("✅ Database tables checked.")


db = Database()
