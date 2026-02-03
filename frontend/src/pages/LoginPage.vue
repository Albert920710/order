<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <img src="http://localhost:8000/media/logo.png" alt="logo" />

      </div>
      <h1>希步销售系统</h1>
      <p>欢迎回来，请登录进入系统</p>
      <el-form :model="form" class="login-form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="账号" class="login-input" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" class="login-input" />
        </el-form-item>
        <el-button type="primary" class="full login-button" @click="handleLogin">登录</el-button>
      </el-form>
      <div class="login-footer">
        <span>{{ error }}</span>
        <el-button type="text" @click="$router.push('/register')">注册</el-button>
      </div>
    </div>
    <div class="copyright">Copyright © 2026 Design By Albert.</div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const form = reactive({
  username: "",
  password: ""
});
const error = ref("");

const handleLogin = async () => {
  if (!form.username && !form.password) {
    error.value = "请输入账号密码后登录";
    return;
  }
  if (form.username && !form.password) {
    error.value = "请输入正确的密码后登录";
    return;
  }
  try {
    await auth.login(form.username, form.password);
    router.push("/app/sales");
  } catch (err) {
    error.value = err?.response?.data?.detail || "登录失败";
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, #4f46e5, #0f172a, #22c55e);
  background-size: 200% 200%;
  animation: gradientShift 12s ease infinite;
  position: relative;
}

.login-card {
  background: #fff;
  padding: 32px 36px 28px;
  border-radius: 18px;
  width: min(420px, 92vw);
  box-shadow: 0 30px 70px rgba(15, 23, 42, 0.35);
}

.login-logo {
  width: 120px;
  margin-bottom: 16px;
}

.login-logo img {
  width: 100%;
  height: auto;
  display: block;
}

.login-card h1 {
  margin: 0 0 6px;
  font-size: 22px;
}

.login-form .full {
  width: 100%;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  color: #ef4444;
}

.login-form {
  margin-top: 16px;
}

.login-input :deep(.el-input__wrapper) {
  height: 44px;
  border-radius: 10px;
}

.login-button {
  height: 44px;
  border-radius: 10px;
  font-weight: 600;
  margin-top: 6px;
}

.copyright {
  margin-top: 24px;
  color: #cbd5f5;
  font-size: 12px;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
