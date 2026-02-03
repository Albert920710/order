<template>
  <div class="section-box">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
      <div style="display:flex;gap:12px;align-items:center">
        <el-input v-model="keyword" placeholder="搜索客户" style="max-width:220px" />
      </div>
      <div style="display:flex;gap:12px;align-items:center">
        <el-button type="primary" @click="dialogVisible = true">新建客户</el-button>
        <el-button @click="toggleSelectAll">批量选择</el-button>
        <el-button type="danger" :disabled="!selected.length" @click="deleteSelected">删除选中</el-button>
      </div>
    </div>
    <el-table
      ref="tableRef"
      :data="filteredCustomers"
      style="margin-top:20px"
      @selection-change="selected = $event"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="full_name" label="客户全称" />
      <el-table-column prop="name" label="客户名" width="160" />
      <el-table-column prop="country" label="国家" width="100" />
      <el-table-column prop="customerTypeLabel" label="客户类型" width="160" />
      <el-table-column prop="assignedLabel" label="分配业务员" />
    </el-table>
  </div>

  <el-dialog v-model="dialogVisible" title="新建客户" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item label="客户名">
        <el-input v-model="form.name" placeholder="客户名" />
      </el-form-item>
      <el-form-item label="国家缩写">
        <el-input v-model="form.country" placeholder="如 CA / RU" />
      </el-form-item>
      <el-form-item label="客户类型">
        <el-select v-model="form.customer_type" placeholder="选择类型">
          <el-option label="渠道代理商 (Distributor/Agent)" value="distributor_agent" />
          <el-option label="直客/个人 (Direct/Personal)" value="direct_personal" />
          <el-option label="内部账户 (Internal)" value="internal" />
        </el-select>
      </el-form-item>
      <el-form-item label="分配业务员">
        <el-select v-model="form.assigned_user_ids" multiple placeholder="选择业务员">
          <el-option
            v-for="salesUser in salesUsers"
            :key="salesUser.id"
            :label="salesUser.name || salesUser.username"
            :value="salesUser.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveCustomer">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";

const customers = ref([]);
const salesUsers = ref([]);
const selected = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const tableRef = ref(null);
const form = reactive({
  name: "",
  country: "",
  customer_type: "distributor_agent",
  assigned_user_ids: []
});

const typeLabelMap = {
  distributor_agent: "渠道代理商 (Distributor/Agent)",
  direct_personal: "直客/个人 (Direct/Personal)",
  internal: "内部账户 (Internal)"
};

const loadCustomers = async () => {
  const { data } = await axios.get("/api/customers");
  customers.value = data.map((customer) => ({
    ...customer,
    customerTypeLabel: typeLabelMap[customer.customer_type] || customer.customer_type,
    assignedLabel: (customer.assigned_users || [])
      .map((user) => user.name || user.username)
      .join(", ")
  }));
};

const loadSalesUsers = async () => {
  const { data } = await axios.get("/api/customers/sales-users");
  salesUsers.value = data;
};

const resetForm = () => {
  form.name = "";
  form.country = "";
  form.customer_type = "distributor_agent";
  form.assigned_user_ids = [];
};

const saveCustomer = async () => {
  if (!form.name || !form.country) {
    ElMessage.warning("请填写客户名与国家缩写");
    return;
  }
  await axios.post("/api/customers", {
    name: form.name,
    country: form.country,
    customer_type: form.customer_type,
    assigned_user_ids: form.assigned_user_ids
  });
  ElMessage.success("客户已创建");
  dialogVisible.value = false;
  resetForm();
  await loadCustomers();
};

const toggleSelectAll = () => {
  tableRef.value?.toggleAllSelection();
};

const deleteSelected = async () => {
  const ids = selected.value.map((item) => item.id).filter(Boolean);
  if (!ids.length) return;
  await Promise.all(ids.map((id) => axios.delete(`/api/customers/${id}`)));
  ElMessage.success("已删除选中客户");
  selected.value = [];
  await loadCustomers();
};

const filteredCustomers = computed(() => {
  if (!keyword.value) return customers.value;
  return customers.value.filter(
    (customer) =>
      customer.full_name.includes(keyword.value) ||
      customer.name.includes(keyword.value) ||
      customer.country.includes(keyword.value)
  );
});

onMounted(async () => {
  await loadSalesUsers();
  await loadCustomers();
});
</script>
