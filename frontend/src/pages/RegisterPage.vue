<template>
  <div class="login-page">
    <div class="login-card">
      <h1>注册账号</h1>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.name" placeholder="姓名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.username" placeholder="账号" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="form.role" placeholder="选择角色">
            <el-option label="业务员" value="sales" />
            <el-option label="产品配置员" value="product_manager" />
            <el-option label="财务" value="finance" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.confirm" type="password" placeholder="确认密码" />
        </el-form-item>
        <el-button type="primary" class="full" @click="handleRegister">提交注册</el-button>
      </el-form>
      <div class="login-footer">
        <span>{{ error }}</span>
        <el-button type="text" @click="$router.push('/login')">返回登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import axios from "axios";

const form = reactive({
  name: "",
  username: "",
  role: "sales",
  password: "",
  confirm: ""
});
const error = ref("");

const handleRegister = async () => {
  if (!form.name || !form.username || !form.password || !form.confirm) {
    error.value = "请完整填写信息";
    return;
  }
  if (form.password !== form.confirm) {
    error.value = "两次密码不一致";
    return;
  }
  try {
    await axios.post("/api/auth/register", {
      name: form.name,
      username: form.username,
      role: form.role,
      password: form.password
    });
    error.value = "注册成功，等待管理员审核";
  } catch (err) {
    error.value = err?.response?.data?.detail || "注册失败";
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, #1f2937, #0f172a);
}

.login-card {
  background: #fff;
  padding: 40px;
  border-radius: 20px;
  width: min(420px, 90vw);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.3);
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  color: #16a34a;
}

.full {
  width: 100%;
}
</style>
