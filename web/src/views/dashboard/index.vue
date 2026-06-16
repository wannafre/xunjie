<template>
  <div class="dashboard-container">
    <!-- Welcome Section -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-box">
        <el-avatar :size="64" :src="userStore.avatar || defaultAvatar" class="welcome-avatar" />
        <div class="welcome-text">
          <h3>欢迎回来，{{ userStore.username }}！</h3>
          <p>{{ userStore.introduction || '祝你今天过得愉快！' }}</p>
        </div>
      </div>
    </el-card>

    <!-- Stats Grid -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in stats" :key="index">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-wrapper" :style="{ backgroundColor: stat.bgColor }">
            <el-icon :size="24" :style="{ color: stat.color }">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">{{ stat.title }}</div>
            <div class="stat-value">{{ stat.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Content Area -->
    <el-row :gutter="20" class="content-row">
      <el-col :span="16">
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>项目概览</span>
            </div>
          </template>
          <div class="project-info">
            <p><strong>迅捷后台管理系统模板</strong> 采用现代化技术栈开发：</p>
            <ul>
              <li><strong>后端：</strong> FastAPI + SQLAlchemy (Async) + Pydantic v2</li>
              <li><strong>前端：</strong> Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus</li>
              <li><strong>管理：</strong> Git 统一版本控制仓</li>
            </ul>
            <p class="desc">
              该模板提供了极佳的开发体验与高性能基础。你可以直接在 `app/api` 下编写后端业务逻辑，在 `web/src/views` 下扩展前端页面。
            </p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="shortcut-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>快捷链接</span>
            </div>
          </template>
          <div class="shortcut-list">
            <a href="http://127.0.0.1:8000/docs" target="_blank" class="shortcut-item">
              <el-icon :size="20"><Document /></el-icon>
              <span>Swagger API 文档</span>
            </a>
            <a href="https://fastapi.tiangolo.com/" target="_blank" class="shortcut-item">
              <el-icon :size="20"><Link /></el-icon>
              <span>FastAPI 官方文档</span>
            </a>
            <a href="https://cn.vuejs.org/" target="_blank" class="shortcut-item">
              <el-icon :size="20"><Link /></el-icon>
              <span>Vue 3 官方文档</span>
            </a>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../store/user'
import { User, Monitor, Tickets, Connection, Document, Link } from '@element-plus/icons-vue'

const userStore = useUserStore()
const defaultAvatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'

const stats = ref([
  {
    title: '系统访问量',
    value: '12,543',
    icon: Monitor,
    color: '#3b82f6',
    bgColor: 'rgba(59, 130, 246, 0.1)'
  },
  {
    title: '活跃用户',
    value: '1,024',
    icon: User,
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.1)'
  },
  {
    title: '数据增量',
    value: '384',
    icon: Tickets,
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)'
  },
  {
    title: '系统依赖数',
    value: '12',
    icon: Connection,
    color: '#8b5cf6',
    bgColor: 'rgba(139, 92, 246, 0.1)'
  }
])
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-card {
  border: none;
  background: linear-gradient(135deg, #e0e7ff 0%, #e8eaff 100%);
  border-radius: 12px;
}

.welcome-box {
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-avatar {
  border: 4px solid #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.welcome-text h3 {
  margin: 0 0 6px 0;
  font-size: 20px;
  color: #1e1b4b;
}

.welcome-text p {
  margin: 0;
  font-size: 14px;
  color: #4f46e5;
}

.stats-row {
  margin-top: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  height: 100px;
}

:deep(.stat-card .el-card__body) {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 10px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.content-row {
  margin-top: 10px;
}

.info-card, .shortcut-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.card-header {
  font-weight: 600;
  color: #1e293b;
}

.project-info {
  line-height: 1.8;
  color: #334155;
}

.project-info ul {
  padding-left: 20px;
  margin: 10px 0;
}

.project-info li {
  margin-bottom: 6px;
}

.desc {
  font-size: 14px;
  color: #64748b;
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #6366f1;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f8fafc;
  color: #334155;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.shortcut-item:hover {
  background-color: #e0e7ff;
  color: #4f46e5;
  border-color: #c7d2fe;
}
</style>
