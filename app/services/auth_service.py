from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import logging

from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
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
    if not verify_password(password, user.password, user.salt):
        return None
    return user

async def seed_default_users(db: AsyncSession) -> None:
    """
    Seeds default menus, roles, and admin/editor accounts if they don't already exist.
    """
    try:
        # 1. 种子初始化菜单/按钮/接口权限
        res_menus = await db.execute(select(Menu))
        all_menus = res_menus.scalars().all()
        if not all_menus:
            menu_list = [
                Menu(menu_name="用户管理", menu_type="C", perms="system:user:list", path="user", order_num=1),
                Menu(menu_name="角色管理", menu_type="C", perms="system:role:list", path="role", order_num=2),
                Menu(menu_name="菜单管理", menu_type="C", perms="system:menu:list", path="menu", order_num=3),
            ]
            db.add_all(menu_list)
            await db.commit()
            for m in menu_list:
                await db.refresh(m)
            all_menus = menu_list
            logger.info("Default menus seeded successfully.")

        # 2. 种子初始化角色，并建立角色-菜单关联
        res_roles = await db.execute(select(Role))
        all_roles = res_roles.scalars().all()
        admin_role = None
        editor_role = None
        
        if not all_roles:
            admin_role = Role(role_name="管理员", role_key="admin", status="0")
            editor_role = Role(role_name="编辑者", role_key="editor", status="0")
            
            # 管理员角色关联全部菜单权限
            admin_role.menus = all_menus
            
            # 编辑者角色关联“用户管理”菜单权限
            user_mgmt_menu = [m for m in all_menus if m.menu_name == "用户管理"]
            if user_mgmt_menu:
                editor_role.menus = user_mgmt_menu
                
            db.add(admin_role)
            db.add(editor_role)
            await db.commit()
            await db.refresh(admin_role)
            await db.refresh(editor_role)
            logger.info("Default roles seeded successfully.")
        else:
            admin_role = [r for r in all_roles if r.role_key == "admin"][0]
            editor_role = [r for r in all_roles if r.role_key == "editor"][0]

        # 3. 种子初始化系统默认用户，并绑定角色
        admin_user = await get_user_by_username(db, "admin")
        if not admin_user:
            admin_in = UserCreate(
                username="admin",
                nickname="超级管理员",
                password="123456",
                roles=["admin"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                remark="I am a super administrator"
            )
            await create_user(db, admin_in)
            logger.info("Default 'admin' user created successfully.")

        editor_user = await get_user_by_username(db, "editor")
        if not editor_user:
            editor_in = UserCreate(
                username="editor",
                nickname="普通编辑员",
                password="123456",
                roles=["editor"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                remark="I am an editor"
            )
            await create_user(db, editor_in)
            logger.info("Default 'editor' user created successfully.")
            
    except Exception as e:
        logger.error(f"Error seeding default users, roles, and menus: {e}")


