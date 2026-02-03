<template>
  <div class="app-shell">
    <aside class="sidebar">
      <h2>订单系统</h2>
      <div class="nav-section">
        <router-link to="/app/sales" v-if="role === 'sales' || role === 'admin'">欢迎</router-link>
        <router-link to="/app/orders" v-if="role === 'sales' || role === 'admin'">订单管理</router-link>
        <router-link
          to="/app/products"
          v-if="role !== 'sales'"
          :class="{ 'router-link-active': isProductsActive }"
        >
          产品列表
        </router-link>
        <router-link to="/app/products/new" v-if="role !== 'sales'">新建产品</router-link>
        <router-link to="/app/categories" v-if="role !== 'sales'">分类管理</router-link>
        <router-link to="/app/customers" v-if="role === 'admin' || role === 'finance'">客户管理</router-link>
        <router-link to="/app/accounts" v-if="role === 'admin'">账号管理</router-link>
        <router-link to="/app/admin" v-if="role === 'admin'">管理员中心</router-link>
      </div>
    </aside>
    <div class="content">
      <header class="header">
        <div>
          <strong>欢迎，{{ username }}</strong>
          <div style="font-size:12px;color:#6b7280">上次登录：{{ lastLogin }}</div>
        </div>
        <div style="display:flex;gap:12px;align-items:center">
          <el-button @click="goProfile">用户面板</el-button>
          <el-button type="danger" @click="logout">退出</el-button>
        </div>
      </header>
      <main style="padding:24px;flex:1">
        <router-view />
      </main>
      <footer style="text-align:center;padding:16px;color:#9ca3af;margin-top:auto">
        Copyright © 2026 Design By Albert.
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

axios.defaults.headers.common.Authorization = `Bearer ${auth.token}`;

const role = computed(() => auth.role);
const username = computed(() => auth.username || "用户");
const lastLogin = computed(() => new Date().toLocaleString());
const isProductsActive = computed(
  () => route.path.startsWith("/app/products") && route.path !== "/app/products/new"
);

const logout = () => {
  auth.logout();
  router.push("/login");
};

const goProfile = () => {
  router.push("/app/sales");
};
</script>
