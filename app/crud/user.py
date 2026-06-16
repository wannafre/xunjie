import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Retrieve user by primary key ID.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Retrieve user by unique username.
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Create a new user with hashed password and custom generated salt.
    """
    salt = user_in.salt or "".join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_password = get_password_hash(user_in.password, salt)
    
    # Exclude plain password and override salt/hashed_password
    user_data = user_in.model_dump(exclude={"password", "salt"})
    db_user = User(**user_data, hashed_password=hashed_password, salt=salt)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    """
    Update user attributes. Regenerates salt if password is changed.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        new_salt = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = get_password_hash(update_data["password"], new_salt)
        db_user.hashed_password = hashed_password
        db_user.salt = new_salt
        del update_data["password"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
