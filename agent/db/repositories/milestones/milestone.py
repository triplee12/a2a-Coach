from typing import Optional
from uuid import UUID
from asyncpg import UniqueViolationError
from databases import Database
from fastapi import HTTPException, status
from agent.core.logger import logger
from agent.db.repositories.base import BaseRepository

CREATE_MILESTONE_QUERY = """
    INSERT INTO milestones (
        goal_id,
        title,
        due_date,
        completed
    ) VALUES (
        :goal_id,
        :title,
        :due_date,
        :completed
    ) RETURNING *;
"""

GET_MILESTONES_BY_GOAL_ID_QUERY = """
    SELECT * FROM milestones WHERE goal_id = :goal_id
    ORDER BY created_at DESC
    LIMIT :limit
    OFFSET :offset;
"""

GET_MILESTONE_BY_ID_QUERY = """
    SELECT * FROM milestones WHERE id = :id AND goal_id = :goal_id;
"""

DELETE_MILESTONE_QUERY = """
    DELETE FROM milestones WHERE id = :id AND goal_id = :goal_id;
"""

UPDATE_MILESTONE_QUERY = """
    UPDATE milestones SET
        title = :title,
        due_date = :due_date,
        completed = :completed
    WHERE id = :id AND goal_id = :goal_id RETURNING *;
"""

UPDATE_MILESTONE_STATUS_QUERY = """
    UPDATE milestones SET
        completed = :completed
    WHERE id = :id AND goal_id = :goal_id RETURNING *;
"""


class MilestoneRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db)
        logger.info("Initializing MilestoneRepository")

    async def create_milestone(
        self, goal_id: UUID, title: str,
        due_date: Optional[str], completed: bool
    ) -> dict:
        logger.info("Creating milestone for goal with id: %s", goal_id)
        try:
            milestone = await self.db.fetch_one(
                CREATE_MILESTONE_QUERY,
                values={"goal_id": goal_id, "title": title, "due_date": due_date, "completed": completed}
            )
            if not milestone:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Error while creating milestone"
                )
            logger.info("Created milestone for goal with id: %s", goal_id)
            return milestone
        except UniqueViolationError as uve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Milestone with title already exists"
            ) from uve
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_milestones_by_goal_id(self, goal_id: UUID) -> list:
        logger.info("Getting milestones for goal with id: %s", goal_id)
        try:
            milestones = await self.db.fetch_all(
                GET_MILESTONES_BY_GOAL_ID_QUERY,
                values={"goal_id": goal_id}
            )
            logger.info("Got milestones for goal with id: %s", goal_id)
            return milestones
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def get_milestone_by_id(self, goal_id: UUID, milestone_id: UUID) -> Optional[dict]:
        logger.info("Getting milestone with id: %s for goal with id: %s", milestone_id, goal_id)
        try:
            milestone = await self.db.fetch_one(
                GET_MILESTONE_BY_ID_QUERY,
                values={"id": milestone_id, "goal_id": goal_id}
            )
            if not milestone:
                logger.warning("Milestone not found with id: %s for goal with id: %s", milestone_id, goal_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Milestone not found"
                )
            logger.info("Got milestone with id: %s for goal with id: %s", milestone_id, goal_id)
            return milestone
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def delete_milestone(self, goal_id: UUID, milestone_id: UUID) -> bool:
        logger.info("Deleting milestone with id: %s for goal with id: %s", milestone_id, goal_id)
        try:
            deleted = await self.db.execute(
                DELETE_MILESTONE_QUERY, values={"id": milestone_id, "goal_id": goal_id}
            )
            if not deleted:
                logger.warning("Milestone not found with id: %s for goal with id: %s", milestone_id, goal_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Milestone not found"
                )
            logger.info("Deleted milestone with id: %s for goal with id: %s", milestone_id, goal_id)
            return True
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def update_milestone(
        self, goal_id: UUID, milestone_id: UUID,
        title: str, due_date: Optional[str], completed: bool
    ) -> dict:
        logger.info("Updating milestone with id: %s for goal with id: %s", milestone_id, goal_id)
        try:
            milestone = await self.db.fetch_one(
                UPDATE_MILESTONE_QUERY,
                values={
                    "id": milestone_id, "goal_id": goal_id,
                    "title": title, "due_date": due_date,
                    "completed": completed
                }
            )
            if not milestone:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Error while updating milestone"
                )
            logger.info("Updated milestone with id: %s for goal with id: %s", milestone_id, goal_id)
            return milestone
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e

    async def update_milestone_status(self, goal_id: UUID, milestone_id: UUID, completed: bool) -> dict:
        logger.info("Updating milestone status with id: %s for goal with id: %s", milestone_id, goal_id)
        try:
            milestone = await self.db.fetch_one(
                UPDATE_MILESTONE_STATUS_QUERY,
                values={"id": milestone_id, "goal_id": goal_id, "completed": completed}
            )
            if not milestone:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Error while updating milestone status"
                )
            logger.info("Updated milestone status with id: %s for goal with id: %s", milestone_id, goal_id)
            return milestone
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
