from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import check_permissions
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.crud import user as crud_user

router = APIRouter()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:add"))
):
    """
    Create a new user.
    """
    existing_user = await crud_user.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return await crud_user.create_user(db, user_in)

@router.get("/", response_model=List[UserOut])
async def list_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    nickname: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:list"))
):
    """
    Get users list with optional search filters.
    """
    return await crud_user.get_all_users(db, skip=skip, limit=limit, username=username, nickname=nickname, status=status)

@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:query"))
):
    """
    Get user details.
    """
    db_user = await crud_user.get_user_by_id(db, user_id)
    if not db_user or db_user.del_flag == "2":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:edit"))
):
    """
    Update user.
    """
    db_user = await crud_user.get_user_by_id(db, user_id)
    if not db_user or db_user.del_flag == "2":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await crud_user.update_user(db, db_user, user_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:remove"))
):
    """
    Delete user.
    """
    success = await crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
