<template>
  <el-container class="app-wrapper">
    <!-- Light-themed Premium Sidebar with Collapse state -->
    <el-aside :width="isCollapse ? '64px' : '256px'" class="sidebar-container">
      <div class="logo-container">
        <!-- Logo shield matching screenshot -->
        <div class="logo-icon-box">
          <svg viewBox="0 0 24 24" width="20" height="20" class="logo-shield">
            <path fill="currentColor" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path fill="white" d="M12 4.3l5.5 2.1v4.8c0 4-4.2 7.1-5.5 8.1-1.3-1-5.5-4.1-5.5-8.1V6.4L12 4.3z"/>
            <path fill="currentColor" d="M11 7h2v5h-2zm0 6h2v2h-2z"/>
          </svg>
        </div>
        <span class="logo-text" v-if="!isCollapse">安全监测系统</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        class="el-menu-vertical"
        text-color="#595959"
        active-text-color="#1890ff"
        background-color="#ffffff"
        router
      >
        <!-- Static Dashboard Item -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>
            <span>首页 (Dashboard)</span>
          </template>
        </el-menu-item>

        <!-- Dynamic Menus fetched from backend -->
        <template v-for="menu in menuList" :key="menu.id">
          <!-- With child items / Submenu -->
          <el-sub-menu 
            v-if="menu.children && menu.children.length > 0" 
            :index="String(menu.id)"
          >
            <template #title>
              <el-icon>
                <component :is="getMenuIcon(menu)" />
              </el-icon>
              <span>{{ menu.menu_name }}</span>
            </template>

            <el-menu-item 
              v-for="child in menu.children" 
              :key="child.id"
              :index="resolvePath(child.path)"
            >
              <el-icon>
                <component :is="getMenuIcon(child)" />
              </el-icon>
              <template #title>
                <span>{{ child.menu_name }}</span>
              </template>
            </el-menu-item>
          </el-sub-menu>

          <!-- Single Menu Item -->
          <el-menu-item 
            v-else 
            :index="resolvePath(menu.path)"
          >
            <el-icon>
              <component :is="getMenuIcon(menu)" />
            </el-icon>
            <template #title>
              <span>{{ menu.menu_name }}</span>
            </template>
          </el-menu-item>
        </template>
      </el-menu>

      <!-- Sidebar footer matching screenshot V1.0.0 -->
      <div class="sidebar-footer" v-if="!isCollapse">
        <span>系统版本 V1.0.0</span>
      </div>
    </el-aside>

    <el-container class="main-container">
      <!-- White top header -->
      <el-header class="header-container">
        <div class="header-left">
          <!-- Fold/Unfold button to toggle sidebar -->
          <el-icon class="fold-btn" @click="isCollapse = !isCollapse">
            <component :is="isCollapse ? Expand : Fold" />
          </el-icon>
          <div class="breadcrumbs">
            <span class="breadcrumb-prefix">轨道交通安全监测系统</span>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ currentRouteTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <!-- Header search box -->
          <div class="header-search">
            <el-input
              placeholder="搜索菜单或功能"
              :prefix-icon="Search"
              size="small"
              class="search-bar"
            />
          </div>

          <!-- Notification bell -->
          <el-badge is-dot class="notice-badge">
            <el-icon class="notice-icon"><Bell /></el-icon>
          </el-badge>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="avatar-wrapper">
              <el-avatar :size="32" :src="userStore.avatar || defaultAvatar" />
              <span class="username">{{ userStore.username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { 
  Odometer, ArrowDown, Fold, Expand, Search, Bell, Folder, Document, List, User, Avatar, Key, Notebook, Location, Cpu, Monitor
} from '@element-plus/icons-vue'
import * as ElementPlusIcons from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const defaultAvatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'

const menuList = ref<any[]>([])
const isCollapse = ref(false)

const activeMenu = computed(() => {
  return route.path
})

const currentRouteTitle = computed(() => {
  return (route.meta.title as string) || '首页'
})

// Dynamically resolve icon components
function getIconComponent(iconName: string) {
  return (ElementPlusIcons as any)[iconName] || null
}

// Fallback logic for dynamic menu icons based on keywords in menu names
function getMenuIcon(menu: any) {
  if (menu.icon && menu.icon !== '#') {
    const comp = getIconComponent(menu.icon)
    if (comp) return comp
  }
  
  const name = menu.menu_name
  if (name.includes('用户')) return User
  if (name.includes('角色')) return Avatar
  if (name.includes('菜单')) return List
  if (name.includes('权限')) return Key
  if (name.includes('字典')) return Notebook
  if (name.includes('路')) return Location
  if (name.includes('设备')) return Cpu
  if (name.includes('监测') || name.includes('可视化') || name.includes('监控')) return Monitor
  
  return menu.children && menu.children.length > 0 ? Folder : Document
}

// Ensure correct route index formats (e.g. '/menu')
function resolvePath(path: string) {
  if (!path) return '/'
  return path.startsWith('/') ? path : '/' + path
}

// Fetch dynamic menus from server
async function fetchMenus() {
  try {
    const res: any = await request.get('/menu/tree')
    menuList.value = res || []
  } catch (err) {
    console.error('Failed to load menus', err)
  }
}

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    await userStore.logout()
    ElMessage.success('已安全退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('个人中心模块开发中')
  }
}

onMounted(() => {
  fetchMenus()
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f0f2f5;
}

/* Light Theme Sidebar styles matching screenshot */
.sidebar-container {
  background-color: #ffffff;
  color: #595959;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #f0f0f0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.015);
  transition: width 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  overflow: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.logo-icon-box {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  background-color: #1890ff;
  color: white;
  border-radius: 8px;
  margin-right: 12px;
  box-shadow: 0 4px 10px rgba(24, 144, 255, 0.2);
  flex-shrink: 0;
}

.logo-shield {
  display: block;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.el-menu-vertical {
  border-right: none;
  flex-grow: 1;
}

:deep(.el-menu-item) {
  height: 40px;
  line-height: 40px;
  margin: 4px 0;
  color: #4e5969;
}

:deep(.el-menu-item:hover) {
  background-color: #f2f3f5 !important;
  color: #4e5969;
}

:deep(.el-menu-item.is-active) {
  background-color: #e8f1ff !important;
  color: #165dff !important;
  font-weight: 500;
  border-left: 2px solid #165dff;
}

:deep(.el-sub-menu__title) {
  height: 40px;
  line-height: 40px;
  margin: 4px 0;
  color: #4e5969;
}

:deep(.el-sub-menu__title:hover) {
  background-color: #f2f3f5 !important;
  color: #4e5969;
}

.sidebar-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #bfbfbf;
  flex-shrink: 0;
}

/* Header container */
.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header-container {
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.fold-btn {
  font-size: 20px;
  color: #4e5969;
  cursor: pointer;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-prefix {
  color: #86909c;
}

.breadcrumb-separator {
  color: #e5e6eb;
}

.breadcrumb-current {
  color: #1d2129;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-search {
  width: 200px;
}

.search-bar :deep(.el-input__wrapper) {
  border-radius: 4px;
  background-color: #f2f3f5;
  border: none;
  box-shadow: none !important;
}

.notice-icon {
  font-size: 20px;
  color: #4e5969;
  cursor: pointer;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.username {
  font-size: 14px;
  color: #4e5969;
  font-weight: 500;
}

.app-main {
  flex-grow: 1;
  padding: 24px;
  overflow-y: auto;
}

/* Page transit animations */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.2s ease-out;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-15px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(15px);
}
</style>
