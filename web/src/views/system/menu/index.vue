<template>
  <div class="menu-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">菜单管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="输入关键字搜索"
              clearable
              :prefix-icon="Search"
              class="search-input"
              @input="handleSearch"
            />
            <el-button type="primary" :icon="Plus" @click="handleCreate" class="add-btn">
              新增记录
            </el-button>
          </div>
        </div>
      </template>

      <!-- Menu Table (Supports tree grid) -->
      <el-table
        v-loading="loading"
        :data="filteredTableData"
        row-key="id"
        border
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        class="menu-table"
      >
        <el-table-column prop="menu_name" label="菜单名称" min-width="180" />
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="scope">
            <el-icon v-if="scope.row.icon && scope.row.icon !== '#'"><component :is="getIconComponent(scope.row.icon)" /></el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_num" label="排序" width="80" align="center" />
        <el-table-column prop="perms" label="权限标识" min-width="150" show-overflow-tooltip />
        <el-table-column prop="path" label="路由地址" min-width="150" show-overflow-tooltip />
        <el-table-column prop="component" label="组件路径" min-width="150" show-overflow-tooltip />
        <el-table-column prop="menu_type" label="类型" width="90" align="center">
          <template #default="scope">
            <el-tag :type="getTypeTag(scope.row.menu_type)" size="small">
              {{ getTypeLabel(scope.row.menu_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'" size="small">
              {{ scope.row.status === '0' ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleUpdate(scope.row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Menu Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增菜单' : '编辑菜单'"
      width="600px"
      align-center
    >
      <el-form :model="menuForm" :rules="formRules" ref="menuFormRef" label-width="100px">
        <el-form-item label="上级菜单">
          <el-tree-select
            v-model="menuForm.parent_id"
            :data="treeSelectData"
            :props="{ label: 'menu_name', value: 'id', children: 'children' }"
            placeholder="选择上级菜单 (不选默认为顶级目录)"
            check-strictly
            clearable
            class="full-width"
          />
        </el-form-item>

        <el-form-item label="菜单类型" prop="menu_type">
          <el-radio-group v-model="menuForm.menu_type">
            <el-radio value="M">目录</el-radio>
            <el-radio value="C">菜单</el-radio>
            <el-radio value="F">按钮/接口</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="菜单名称" prop="menu_name">
          <el-input v-model="menuForm.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>

        <el-form-item label="显示顺序" prop="order_num">
          <el-input-number v-model="menuForm.order_num" :min="0" class="full-width" />
        </el-form-item>

        <el-form-item label="菜单图标" v-if="menuForm.menu_type !== 'F'">
          <el-select v-model="menuForm.icon" placeholder="请选择菜单图标" clearable filterable class="full-width">
            <el-option
              v-for="item in iconOptions"
              :key="item"
              :label="item"
              :value="item"
            >
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-icon><component :is="getIconComponent(item)" /></el-icon>
                <span>{{ item }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="路由地址" prop="path" v-if="menuForm.menu_type !== 'F'">
          <el-input v-model="menuForm.path" placeholder="请输入路由地址" />
        </el-form-item>

        <el-form-item label="组件路径" prop="component" v-if="menuForm.menu_type === 'C'">
          <el-input v-model="menuForm.component" placeholder="请输入组件路径 (如: system/user/index)" />
        </el-form-item>

        <el-form-item label="权限标识" prop="perms">
          <el-input v-model="menuForm.perms" placeholder="请输入权限标识 (如: system:user:list)" />
        </el-form-item>

        <el-form-item label="显示状态" v-if="menuForm.menu_type !== 'F'">
          <el-radio-group v-model="menuForm.visible">
            <el-radio value="0">显示</el-radio>
            <el-radio value="1">隐藏</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="菜单状态">
          <el-radio-group v-model="menuForm.status">
            <el-radio value="0">正常</el-radio>
            <el-radio value="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="menuForm.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import request from '../../../utils/request'
import { deepClone, listToTree } from '../../../utils'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<any[]>([])
const treeSelectData = ref<any[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const menuFormRef = ref<FormInstance>()

const iconOptions = ref([
  'Setting', 'User', 'Avatar', 'List', 'Key', 'Notebook', 'Folder', 'Document', 
  'Odometer', 'Monitor', 'Bell', 'Search', 'Plus', 'Edit', 'Delete', 'Operation',
  'Grid', 'Menu', 'Location', 'Cpu'
])

const menuForm = reactive({
  id: undefined,
  parent_id: 0,
  menu_name: '',
  menu_type: 'M',
  order_num: 0,
  path: '',
  component: '',
  perms: '',
  icon: '#',
  visible: '0',
  status: '0',
  remark: ''
})

const formRules = reactive<FormRules>({
  menu_name: [{ required: true, message: '菜单名称不能为空', trigger: 'blur' }],
  menu_type: [{ required: true, message: '菜单类型不能为空', trigger: 'change' }]
})

// Resolve Element Plus Icon component dynamically
function getIconComponent(iconName: string) {
  return (ElementPlusIcons as any)[iconName] || null
}

const getTypeLabel = (type: string) => {
  if (type === 'M') return '目录'
  if (type === 'C') return '菜单'
  return '按钮/接口'
}

const getTypeTag = (type: string) => {
  if (type === 'M') return 'primary'
  if (type === 'C') return 'success'
  return 'warning'
}

// Flat search logic matching keywords in menu names
const filteredTableData = computed(() => {
  if (!searchQuery.value) return tableData.value
  const query = searchQuery.value.toLowerCase()
  
  const filterNode = (nodes: any[]): any[] => {
    return nodes
      .map(node => {
        const matched = node.menu_name.toLowerCase().includes(query) || 
                        (node.perms && node.perms.toLowerCase().includes(query)) ||
                        (node.path && node.path.toLowerCase().includes(query))
        
        let children: any[] = []
        if (node.children && node.children.length > 0) {
          children = filterNode(node.children)
        }
        
        if (matched || children.length > 0) {
          return { ...node, children }
        }
        return null
      })
      .filter((n): n is any => n !== null)
  }
  
  return filterNode(tableData.value)
})

// Fetch all menus from database
async function getList() {
  loading.value = true
  try {
    const res: any = await request.get('/menu/tree')
    tableData.value = res || []
    
    // Construct tree options for parent menu selection (excluding buttons)
    const rawMenus: any = await request.get('/menu/')
    const menuOptions = (rawMenus || []).filter((item: any) => item.menu_type !== 'F')
    treeSelectData.value = [
      { id: 0, menu_name: '主类目', children: listToTree(menuOptions) }
    ]
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // Computed filter handles search reactively
}

function resetForm() {
  Object.assign(menuForm, {
    id: undefined,
    parent_id: 0,
    menu_name: '',
    menu_type: 'M',
    order_num: 0,
    path: '',
    component: '',
    perms: '',
    icon: '#',
    visible: '0',
    status: '0',
    remark: ''
  })
}

function handleCreate() {
  resetForm()
  dialogType.value = 'create'
  dialogVisible.value = true
}

function handleUpdate(row: any) {
  resetForm()
  Object.assign(menuForm, deepClone(row))
  // parent_id should be integer
  menuForm.parent_id = Number(menuForm.parent_id) || 0
  dialogType.value = 'update'
  dialogVisible.value = true
}

async function submitForm() {
  if (!menuFormRef.value) return
  await menuFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const payload = { ...menuForm }
        if (!payload.parent_id) {
          payload.parent_id = 0
        }
        
        if (dialogType.value === 'create') {
          await request.post('/menu/', payload)
          ElMessage.success('新增菜单成功')
        } else {
          await request.put(`/menu/${payload.id}`, payload)
          ElMessage.success('修改菜单成功')
        }
        dialogVisible.value = false
        getList()
      } catch (err) {
        console.error(err)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除菜单 "${row.menu_name}" 吗？`, '警告', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await request.delete(`/menu/${row.id}`)
    ElMessage.success('删除成功')
    getList()
  } catch (err) {
    if (err !== 'cancel') {
      console.error(err)
    }
  }
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.menu-container {
  height: 100%;
}

.box-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 240px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  box-shadow: none !important;
  transition: all 0.2s;
}

:deep(.el-input__wrapper.is-focus) {
  background-color: #ffffff;
  border-color: #1890ff;
}

.add-btn {
  border-radius: 8px;
  background-color: #1890ff;
  border: none;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(24, 144, 255, 0.2);
}

.add-btn:hover {
  background-color: #40a9ff;
}

.menu-table {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
}

.full-width {
  width: 100%;
}

:deep(.el-table th) {
  background-color: #f8fafc !important;
  color: #475569;
  font-weight: 600;
}

:deep(.el-dialog) {
  border-radius: 16px;
}
</style>
