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

from app.models.dict import DictType, DictData

async def seed_default_users(db: AsyncSession) -> None:
    """
    Seeds default menus, buttons, roles, dicts, and admin/editor accounts if they don't already exist.
    """
    try:
        # 1. 确保核心菜单存在
        menu_items = [
            {"name": "用户管理", "perms": "system:user:list", "path": "user", "order": 1},
            {"name": "角色管理", "perms": "system:role:list", "path": "role", "order": 2},
            {"name": "菜单管理", "perms": "system:menu:list", "path": "menu", "order": 3},
            {"name": "字典管理", "perms": "system:dict:list", "path": "dict", "order": 4},
        ]
        
        menus_by_name = {}
        for item in menu_items:
            res = await db.execute(select(Menu).filter(Menu.menu_name == item["name"], Menu.menu_type == "C"))
            menu_obj = res.scalars().first()
            if not menu_obj:
                menu_obj = Menu(
                    menu_name=item["name"],
                    menu_type="C",
                    perms=item["perms"],
                    path=item["path"],
                    order_num=item["order"],
                    parent_id=0,
                    status="0",
                    visible="0"
                )
                db.add(menu_obj)
                await db.commit()
                await db.refresh(menu_obj)
            menus_by_name[item["name"]] = menu_obj

        # 2. 确保各菜单下的按钮/接口权限存在
        button_definitions = {
            "用户管理": [
                {"name": "用户查询", "perms": "system:user:query"},
                {"name": "用户新增", "perms": "system:user:add"},
                {"name": "用户修改", "perms": "system:user:edit"},
                {"name": "用户删除", "perms": "system:user:remove"},
                {"name": "重置密码", "perms": "system:user:resetPwd"},
            ],
            "角色管理": [
                {"name": "角色查询", "perms": "system:role:query"},
                {"name": "角色新增", "perms": "system:role:add"},
                {"name": "角色修改", "perms": "system:role:edit"},
                {"name": "角色删除", "perms": "system:role:remove"},
            ],
            "菜单管理": [
                {"name": "菜单查询", "perms": "system:menu:query"},
                {"name": "菜单新增", "perms": "system:menu:add"},
                {"name": "菜单修改", "perms": "system:menu:edit"},
                {"name": "菜单删除", "perms": "system:menu:remove"},
            ],
            "字典管理": [
                {"name": "字典查询", "perms": "system:dict:query"},
                {"name": "字典新增", "perms": "system:dict:add"},
                {"name": "字典修改", "perms": "system:dict:edit"},
                {"name": "字典删除", "perms": "system:dict:remove"},
            ],
        }

        for parent_name, buttons in button_definitions.items():
            parent_menu = menus_by_name[parent_name]
            for btn in buttons:
                res = await db.execute(
                    select(Menu).filter(Menu.perms == btn["perms"], Menu.parent_id == parent_menu.id)
                )
                btn_obj = res.scalars().first()
                if not btn_obj:
                    btn_obj = Menu(
                        menu_name=btn["name"],
                        menu_type="F",
                        perms=btn["perms"],
                        parent_id=parent_menu.id,
                        status="0",
                        visible="0",
                        order_num=0
                    )
                    db.add(btn_obj)
        await db.commit()

        # 获取当前所有的 Menu 记录以分配给 admin
        res_all_menus = await db.execute(select(Menu))
        all_menus = res_all_menus.scalars().all()

        # 3. 种子初始化角色，并建立角色-菜单关联
        res_roles = await db.execute(select(Role))
        all_roles = res_roles.scalars().all()
        admin_role = None
        editor_role = None
        
        if not all_roles:
            admin_role = Role(role_name="管理员", role_key="admin", status="0")
            editor_role = Role(role_name="编辑者", role_key="editor", status="0")
            
            # 管理员角色关联全部菜单/按钮权限
            admin_role.menus = all_menus
            
            # 编辑者角色关联“用户管理”菜单权限及用户查询权限
            user_mgmt_menu = [m for m in all_menus if m.perms in ["system:user:list", "system:user:query"]]
            editor_role.menus = user_mgmt_menu
                
            db.add(admin_role)
            db.add(editor_role)
            await db.commit()
            await db.refresh(admin_role)
            await db.refresh(editor_role)
            logger.info("Default roles seeded successfully.")
        else:
            admin_role = [r for r in all_roles if r.role_key == "admin"][0]
            # 确保管理员拥有所有最新菜单/按钮的关联
            admin_role.menus = all_menus
            db.add(admin_role)
            await db.commit()

        # 4. 种子初始化系统默认用户，并绑定角色
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
            
        # 5. 种子初始化字典类型与数据
        res_dict = await db.execute(select(DictType))
        all_dicts = res_dict.scalars().all()
        if not all_dicts:
            dict_types = [
                DictType(dict_name="用户性别", dict_type="sys_user_sex", status="0", remark="用户性别列表"),
                DictType(dict_name="系统状态", dict_type="sys_normal_disable", status="0", remark="系统正常/停用状态列表")
            ]
            db.add_all(dict_types)
            await db.commit()
            
            dict_datas = [
                DictData(dict_sort=1, dict_label="男", dict_value="0", dict_type="sys_user_sex", list_class="primary", is_default="Y", status="0"),
                DictData(dict_sort=2, dict_label="女", dict_value="1", dict_type="sys_user_sex", list_class="danger", is_default="N", status="0"),
                DictData(dict_sort=3, dict_label="未知", dict_value="2", dict_type="sys_user_sex", list_class="info", is_default="N", status="0"),
                
                DictData(dict_sort=1, dict_label="正常", dict_value="0", dict_type="sys_normal_disable", list_class="primary", is_default="Y", status="0"),
                DictData(dict_sort=2, dict_label="停用", dict_value="1", dict_type="sys_normal_disable", list_class="danger", is_default="N", status="0")
            ]
            db.add_all(dict_datas)
            await db.commit()
            logger.info("Default dictionary types and data seeded successfully.")
            
    except Exception as e:
        logger.error(f"Error seeding default users, roles, and menus: {e}")


