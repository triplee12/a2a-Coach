from typing import Optional
from uuid import UUID
from databases import Database
from fastapi import HTTPException, status
from agent.core.logger import logger
from agent.db.repositories.base import BaseRepository

CREATE_MESSAGE_QUERY = """
    INSERT INTO messages (
        user_id,
        telex_sender_id,
        text
    ) VALUES (
        :user_id,
        :telex_sender_id,
        :text
    ) RETURNING *;
"""

GET_MESSAGES_BY_USER_ID_QUERY = """
    SELECT * FROM messages
    WHERE user_id = :user_id
    ORDER BY created_at DESC
    LIMIT :limit
    OFFSET :offset;
"""

GET_MESSAGE_BY_ID_QUERY = """
    SELECT * FROM messages WHERE id = :id AND user_id = :user_id;
"""

DELETE_MESSAGE_QUERY = """
    DELETE FROM messages WHERE id = :id AND user_id = :user_id;
"""


class MessageRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db)
        logger.info("Initializing MessageRepository")

    async def create_message(self, user_id: UUID, telex_sender_id: str, text: str) -> dict:
        logger.info("Creating message for user with id: %s", user_id)
        try:
            message = await self.db.execute(
                CREATE_MESSAGE_QUERY,
                values={"user_id": user_id, "telex_sender_id": telex_sender_id, "text": text}
            )
            if not message:
                logger.warning("Message not created for user with id: %s", user_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Message not created"
                )
            logger.info("Created message for user with id: %s", user_id)
            return message
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
    
    async def get_messages_by_user_id(self, user_id: UUID, limit: int, offset: int) -> list:
        logger.info("Getting messages for user with id: %s", user_id)
        try:
            messages = await self.db.fetch_all(
                GET_MESSAGES_BY_USER_ID_QUERY,
                values={"user_id": user_id, "limit": limit, "offset": offset}
            )
            if not messages:
                logger.warning("No messages found for user with id: %s", user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No messages found"
                )
            logger.info("Got messages for user with id: %s", user_id)
            return messages
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
    
    async def get_message_by_id(self, user_id: UUID, message_id: UUID) -> Optional[dict]:
        logger.info("Getting message with id: %s for user with id: %s", message_id, user_id)
        try:
            message = await self.db.fetch_one(GET_MESSAGE_BY_ID_QUERY, values={"id": message_id, "user_id": user_id})
            if not message:
                logger.warning("Message not found with id: %s for user with id: %s", message_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Message not found"
                )
            logger.info("Got message with id: %s for user with id: %s", message_id, user_id)
            return message
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
    
    async def delete_message(self, user_id: UUID, message_id: UUID) -> bool:
        logger.info("Deleting message with id: %s for user with id: %s", message_id, user_id)
        try:
            deleted = await self.db.execute(DELETE_MESSAGE_QUERY, values={"id": message_id, "user_id": user_id})
            if not deleted:
                logger.warning("Message not found with id: %s for user with id: %s", message_id, user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Message not found"
                )
            logger.info("Deleted message with id: %s for user with id: %s", message_id, user_id)
            return True
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            ) from e
