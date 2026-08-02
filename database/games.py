from database.database import db


# --------------------------------------------------
# GET GAME STATE
# --------------------------------------------------

async def get_game_state(guild_id: int):

    async with db.pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT *
            FROM game_state
            WHERE guild_id = $1
            """,
            guild_id,
        )

        if row:
            return dict(row)

        await conn.execute(
            """
            INSERT INTO game_state (guild_id)
            VALUES ($1)
            """,
            guild_id,
        )

        row = await conn.fetchrow(
            """
            SELECT *
            FROM game_state
            WHERE guild_id = $1
            """,
            guild_id,
        )

        return dict(row)


# --------------------------------------------------
# SAVE COUNTING
# --------------------------------------------------

async def save_counting(
    guild_id: int,
    current_count: int,
    last_counter: int | None,
):

    async with db.pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE game_state

            SET current_count=$2,
                last_counter=$3

            WHERE guild_id=$1
            """,
            guild_id,
            current_count,
            last_counter,
        )


# --------------------------------------------------
# SAVE WORDCHAIN
# --------------------------------------------------

async def save_wordchain(
    guild_id: int,
    last_word: str,
    used_words: list,
    last_counter: int | None,
):

    async with db.pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE game_state

            SET last_word=$2,
                used_words=$3,
                word_last_counter=$4

            WHERE guild_id=$1
            """,
            guild_id,
            last_word,
            used_words,
            last_counter,
        )


# --------------------------------------------------
# SAVE SETTINGS
# --------------------------------------------------

async def save_settings(
    guild_id: int,
    data: dict,
):

    async with db.pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE game_state

            SET counting_channel=$2,
                counting_enabled=$3,
                wordchain_channel=$4,
                wordchain_enabled=$5

            WHERE guild_id=$1
            """,
            guild_id,
            data["counting_channel"],
            data["counting_enabled"],
            data["wordchain_channel"],
            data["wordchain_enabled"],
        )
