<template>
  <div class="section-box">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
      <h3>分类管理</h3>
      <el-button type="primary" @click="openCreate">新增分类</el-button>
    </div>
    <el-table :data="categories" style="margin-top:20px">
      <el-table-column prop="name" label="分类名" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button text type="primary" @click="editCategory(row)">编辑</el-button>
          <el-button text type="danger" @click="removeCategory(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-dialog v-model="editVisible" :title="editMode === 'create' ? '新增分类' : '编辑分类'">
    <el-input v-model="editName" placeholder="分类名" />
    <template #footer>
      <el-button @click="editVisible = false">取消</el-button>
      <el-button type="primary" @click="saveEdit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";

const categories = ref([]);
const editVisible = ref(false);
const editName = ref("");
const editTarget = ref(null);
const editMode = ref("create");

const loadCategories = async () => {
  const { data } = await axios.get("/api/products/categories");
  categories.value = data;
};

const openCreate = () => {
  editMode.value = "create";
  editTarget.value = null;
  editName.value = "";
  editVisible.value = true;
};

const editCategory = (row) => {
  editMode.value = "edit";
  editTarget.value = row;
  editName.value = row.name;
  editVisible.value = true;
};

const saveEdit = async () => {
  if (!editName.value) return;
  if (editMode.value === "create") {
    await axios.post(`/api/products/categories?name=${encodeURIComponent(editName.value)}`);
    ElMessage.success("分类已新增");
  } else if (editTarget.value) {
    await axios.put(`/api/products/categories/${editTarget.value.id}?name=${encodeURIComponent(editName.value)}`);
    ElMessage.success("分类已更新");
  }
  editVisible.value = false;
  await loadCategories();
};

const removeCategory = async (row) => {
  await axios.delete(`/api/products/categories/${row.id}`);
  ElMessage.success("分类已删除");
  await loadCategories();
};

onMounted(loadCategories);
</script>
