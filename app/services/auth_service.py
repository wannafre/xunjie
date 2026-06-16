from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import logging

from app.models.user import User
from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate
from app.core.security import verify_password

logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by checking username and password hash.
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password, user.salt):
        return None
    return user

async def seed_default_users(db: AsyncSession) -> None:
    """
    Seeds default admin and editor accounts if they don't already exist.
    """
    try:
        # Check if admin exists
        admin_user = await get_user_by_username(db, "admin")
        if not admin_user:
            admin_in = UserCreate(
                username="admin",
                password="123456",
                roles=["admin"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                introduction="I am a super administrator"
            )
            await create_user(db, admin_in)
            logger.info("Default 'admin' user created successfully.")

        # Check if editor exists
        editor_user = await get_user_by_username(db, "editor")
        if not editor_user:
            editor_in = UserCreate(
                username="editor",
                password="123456",
                roles=["editor"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                introduction="I am an editor"
            )
            await create_user(db, editor_in)
            logger.info("Default 'editor' user created successfully.")
            
    except Exception as e:
        logger.error(f"Error seeding default users: {e}")
