from typing import Optional
from uuid import UUID
from asyncpg import UniqueViolationError
from databases import Database
from fastapi import HTTPException, status
from agent.core.logger import logger
from agent.db.repositories.base import BaseRepository

CREATE_GOAL_QUERY = """
    INSERT INTO goals (
        user_id,
        title,
        description,
        status
    ) VALUES (
        :user_id,
        :title,
        :description,
        :status
    ) RETURNING *;
"""

GET_GOALS_BY_USER_ID_QUERY = """
    SELECT * FROM goals WHERE user_id = :user_id;
"""

DELETE_GOAL_QUERY = """
    DELETE FROM goals WHERE id = :id AND user_id = :user_id;
"""

GET_GOAL_BY_ID_QUERY = """
    SELECT * FROM goals WHERE id = :id AND user_id = :user_id;
"""

UPDATE_GOAL_QUERY = """
    UPDATE goals SET
        title = :title,
        description = :description,
        status = :status
    WHERE id = :id AND user_id = :user_id
    RETURNING *;
"""

UPDATE_GOAL_STATUS_QUERY = """
    UPDATE goals SET
        status = :status
    WHERE id = :id AND user_id = :user_id
    RETURNING *;
"""


class GoalRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db)
        logger.info("Initializing GoalRepository")

    async def create_goal(self, user_id: UUID, title: str, description: str, _status: str) -> dict:
        try:
            logger.info("Creating goal for user with id: %s", user_id)
            goal = await self.db.fetch_one(
                CREATE_GOAL_QUERY,
                values={"user_id": user_id, "title": title, "description": description, "status": _status},
            )

            if not goal:
                logger.warning("Error while creating goal for user with id: %s", user_id)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Error while creating goal"
                )

            logger.info("Created goal for user with id: %s", user_id)
            return goal
        except UniqueViolationError as uve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal already exists"
            ) from uve
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_goals_by_user_id(self, user_id: UUID) -> list:
        logger.info("Getting goals for user with id: %s", user_id)
        try:
            goals = await self.db.fetch_all(GET_GOALS_BY_USER_ID_QUERY, values={"user_id": user_id})
            logger.info("Got goals for user with id: %s", user_id)
            return goals
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def delete_goal(self, user_id: UUID, goal_id: UUID) -> bool:
        logger.info("Deleting goal with id: %s for user with id: %s", goal_id, user_id)
        try:
            deleted = await self.db.execute(DELETE_GOAL_QUERY, values={"id": goal_id, "user_id": user_id})
            if not deleted:
                logger.warning("Goal not found with id: %s for user with id: %s", goal_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )
            logger.info("Deleted goal with id: %s for user with id: %s", goal_id, user_id)
            return True
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_goal_by_id(self, user_id: UUID, goal_id: UUID) -> Optional[dict]:
        logger.info("Getting goal with id: %s for user with id: %s", goal_id, user_id)
        try:
            goal = await self.db.fetch_one(GET_GOAL_BY_ID_QUERY, values={"id": goal_id, "user_id": user_id})
            if not goal:
                logger.warning("Goal not found with id: %s for user with id: %s", goal_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )
            logger.info("Got goal with id: %s for user with id: %s", goal_id, user_id)
            return goal
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def update_goal(self, user_id: UUID, goal_id: UUID, title: str, description: str, _status: str) -> dict:
        logger.info("Updating goal with id: %s for user with id: %s", goal_id, user_id)
        try:
            goal = await self.db.fetch_one(
                UPDATE_GOAL_QUERY,
                values={
                    "id": goal_id, "user_id": user_id,
                    "title": title, "description": description,
                    "status": _status
                }
            )
            if not goal:
                logger.warning("Goal not found with id: %s for user with id: %s", goal_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )
            logger.info("Updated goal with id: %s for user with id: %s", goal_id, user_id)
            return goal
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def update_goal_status(self, user_id: UUID, goal_id: UUID, _status: str) -> dict:
        logger.info("Updating goal status with id: %s for user with id: %s", goal_id, user_id)
        try:
            goal = await self.db.fetch_one(
                UPDATE_GOAL_STATUS_QUERY,
                values={"id": goal_id, "user_id": user_id, "status": _status}
            )
            if not goal:
                logger.warning("Goal not found with id: %s for user with id: %s", goal_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found"
                )
            logger.info("Updated goal status with id: %s for user with id: %s", goal_id, user_id)
            return goal
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
