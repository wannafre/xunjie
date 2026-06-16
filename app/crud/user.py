import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.models.user import User
from app.models.role import Role
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
    Create a new user with hashed password, custom generated salt, and associated Roles.
    """
    salt = user_in.salt or "".join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_password = get_password_hash(user_in.password, salt)
    
    # Exclude roles, password, and salt from direct instantiation
    user_data = user_in.model_dump(exclude={"password", "salt", "roles"})
    db_user = User(**user_data, password=hashed_password, salt=salt)
    
    # Query Role objects and assign to relationship
    if user_in.roles:
        res = await db.execute(select(Role).filter(Role.role_key.in_(user_in.roles)))
        db_user.roles = res.scalars().all()
        
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    """
    Update user attributes, hashes password if changed, and maps role_key strings to Role objects.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Handle password and salt update
    if "password" in update_data and update_data["password"]:
        new_salt = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = get_password_hash(update_data["password"], new_salt)
        db_user.password = hashed_password
        db_user.salt = new_salt
        del update_data["password"]


    # Handle roles conversion
    if "roles" in update_data:
        role_keys = update_data["roles"]
        if role_keys:
            res = await db.execute(select(Role).filter(Role.role_key.in_(role_keys)))
            db_user.roles = res.scalars().all()
        else:
            db_user.roles = []
        del update_data["roles"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
