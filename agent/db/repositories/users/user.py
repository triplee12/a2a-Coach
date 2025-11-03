from typing import Optional
from uuid import UUID
from asyncpg import UniqueViolationError
from databases import Database
from fastapi import HTTPException, status
from agent.core.logger import logger
from agent.db.repositories.base import BaseRepository

CREATE_USER_QUERY = """
    INSERT INTO users (
        telex_user_id,
        name,
        email
    ) VALUES (
        :telex_user_id,
        :name,
        :email
    ) RETURNING *;
"""

GET_USER_BY_EMAIL_QUERY = """
    SELECT * FROM users WHERE email = :email;
"""

GET_USER_BY_TELEX_ID_QUERY = """
    SELECT * FROM users WHERE telex_user_id = :telex_user_id;
"""

DELETE_USER_QUERY = """
    DELETE FROM users WHERE id = :id;
"""


class UserRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db)
        logger.info("Initializing UserRepository")

    async def create_user(self, telex_user_id: str, name: str, email: str) -> dict:
        try:
            logger.info("Creating user with telex id: %s", telex_user_id)
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                return existing_user

            user = await self.db.fetch_one(
                CREATE_USER_QUERY,
                values={"telex_user_id": telex_user_id, "name": name, "email": email},
            )

            if not user:
                logger.warning("Error while creating user by telex id: %s", telex_user_id)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Error while creating user"
                )

            logger.info("Created user with telex id: %s", telex_user_id)
            return user
        except UniqueViolationError as uve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            ) from uve
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        logger.info("Getting user by email: %s", email)
        try:
            user = await self.db.fetch_one(
                GET_USER_BY_EMAIL_QUERY,
                values={"email": email}
            )

            if not user:
                logger.warning("User not found by email: %s", email)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info("Got user by email: %s", email)
            return user
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_user_by_telex_id(self, telex_user_id: str) -> Optional[dict]:
        logger.info("Getting user by telex id: %s", telex_user_id)
        try:
            user = await self.db.fetch_one(
                GET_USER_BY_TELEX_ID_QUERY,
                values={"telex_user_id": telex_user_id}
            )

            if not user:
                logger.warning("User not found by telex id: %s", telex_user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info("Got user by telex id: %s", telex_user_id)
            return user
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def delete_user(self, user_id: UUID) -> bool:
        logger.info("Deleting user with id: %s", user_id)
        try:
            deleted = await self.db.execute(DELETE_USER_QUERY, values={"id": user_id})
            if not deleted:
                logger.warning("User not found with id: %s", user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            logger.info("Deleted user with id: %s", user_id)
            return True
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
