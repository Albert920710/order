<template>
  <div>
    <div class="section-box">
      <h3>用户审批</h3>
      <el-table :data="users" style="margin-top:16px">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="username" label="账号" />
        <el-table-column prop="roleLabel" label="角色" width="160" />
        <el-table-column prop="approvedLabel" label="状态" width="120" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" text :disabled="row.is_approved" @click="approve(row)">同意注册</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="section-box">
      <h3>图片索引</h3>
      <p>索引用于图片搜索，产品新增后可触发全量索引。</p>
      <div style="display:flex;gap:16px;align-items:center">
        <el-button type="primary" :loading="indexLoading" @click="triggerIndex">开始索引</el-button>
      </div>
      <div v-if="indexStatus" style="margin-top:8px;color:#6b7280">{{ indexStatus }}</div>
      <div v-if="indexTotal !== null" style="margin-top:8px;color:#6b7280">本次索引图片：{{ indexTotal }} 张</div>
      <div v-if="indexError" style="margin-top:8px;color:#f43f5e">{{ indexError }}</div>
      <el-progress v-if="indexProgress > 0" :percentage="indexProgress" style="margin-top:8px" />
    </div>
    <div class="section-box">
      <h3>操作日志</h3>
      <el-table :data="pagedLogs" style="margin-top:16px">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="action" label="操作" />
        <el-table-column prop="detail" label="详细" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
      <div style="display:flex;justify-content:center;margin-top:16px">
        <el-pagination
          background
          layout="prev, pager, next"
          :page-size="20"
          :total="logs.length"
          @current-change="page = $event"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";

const users = ref([]);
const logs = ref([]);
const page = ref(1);
const indexStatus = ref("");
const indexTotal = ref(null);
const indexProgress = ref(0);
const indexLoading = ref(false);
const indexError = ref("");

const loadUsers = async () => {
  const { data } = await axios.get("/api/admin/users");
  users.value = data.map((user) => ({
    ...user,
    roleLabel: user.role === "sales" ? "业务员" : user.role === "product_manager" ? "产品配置员" : "管理员",
    approvedLabel: user.is_approved ? "已通过" : "待审核"
  }));
};

const loadLogs = async () => {
  const { data } = await axios.get("/api/admin/logs");
  const { data: users } = await axios.get("/api/admin/users");
  logs.value = data.map((log) => ({
    ...log,
    name: users.find((user) => user.id === log.user_id)?.name || log.role
  }));
};

const approve = async (row) => {
  await axios.post(`/api/admin/users/${row.id}/approve`);
  ElMessage.success("已通过审核");
  await loadUsers();
};

const triggerIndex = async () => {
  indexStatus.value = "索引中...";
  indexProgress.value = 30;
  indexError.value = "";
  indexLoading.value = true;
  try {
    const { data } = await axios.post("/api/search/index");
    indexTotal.value = data.total_images ?? 0;
    indexProgress.value = data.status === "completed" ? 100 : 0;
    if (data.status === "completed") {
      indexStatus.value = data.message || "索引完成";
      ElMessage.success(indexStatus.value);
    } else {
      indexStatus.value = data.message || "索引失败";
      indexError.value = indexStatus.value;
      ElMessage.error(indexStatus.value);
    }
  } catch (error) {
    indexProgress.value = 0;
    indexStatus.value = "索引失败";
    indexError.value = error?.response?.data?.detail || "索引失败，请稍后重试";
    ElMessage.error(indexError.value);
  } finally {
    indexLoading.value = false;
  }
};

onMounted(() => {
  loadUsers();
  loadLogs();
});

const pagedLogs = computed(() => {
  const start = (page.value - 1) * 20;
  return logs.value.slice(start, start + 20);
});
</script>
