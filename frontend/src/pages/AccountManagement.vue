<template>
  <div class="section-box">
    <h3>账号管理</h3>
    <el-table :data="accounts" style="margin-top:16px" @row-click="openDetail">
      <el-table-column prop="username" label="账号名" />
      <el-table-column prop="roleLabel" label="权限" width="160" />
      <el-table-column prop="order_prefix" label="订单ID字段" width="140" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" text @click.stop="openDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-dialog v-model="detailVisible" width="500px" title="账号编辑">
    <el-form :model="editForm" label-width="120px">
      <el-form-item label="账号名">
        <el-input v-model="editForm.username" disabled />
      </el-form-item>
      <el-form-item label="权限">
        <el-select v-model="editForm.role">
          <el-option label="业务员" value="sales" />
          <el-option label="产品配置员" value="product_manager" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
      <el-form-item label="订单ID字段">
        <el-input v-model="editForm.order_prefix" placeholder="如 SA" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="editForm.password" type="password" placeholder="留空则不修改" />
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="editForm.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="detailVisible = false">取消</el-button>
      <el-button type="danger" @click="removeAccount">删除</el-button>
      <el-button type="primary" @click="saveAccount">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";

const accounts = ref([]);
const detailVisible = ref(false);
const editForm = reactive({
  id: null,
  username: "",
  role: "sales",
  order_prefix: "",
  password: "",
  is_active: true
});

const mapRole = (role) => (role === "sales" ? "业务员" : role === "product_manager" ? "产品配置员" : "管理员");

const loadAccounts = async () => {
  const { data } = await axios.get("/api/admin/users");
  accounts.value = data.map((item) => ({
    ...item,
    roleLabel: mapRole(item.role)
  }));
};

const openDetail = (row) => {
  editForm.id = row.id;
  editForm.username = row.username;
  editForm.role = row.role;
  editForm.order_prefix = row.order_prefix || "";
  editForm.password = "";
  editForm.is_active = row.is_active;
  detailVisible.value = true;
};

const saveAccount = async () => {
  await axios.put(`/api/admin/users/${editForm.id}`, {
    role: editForm.role,
    order_prefix: editForm.order_prefix,
    password: editForm.password || null,
    is_active: editForm.is_active
  });
  ElMessage.success("账号已更新");
  detailVisible.value = false;
  await loadAccounts();
};

const removeAccount = async () => {
  await axios.delete(`/api/admin/users/${editForm.id}`);
  ElMessage.success("账号已删除");
  detailVisible.value = false;
  await loadAccounts();
};

onMounted(loadAccounts);
</script>
