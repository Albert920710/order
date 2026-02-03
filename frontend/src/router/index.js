import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import LoginPage from "../pages/LoginPage.vue";
import RegisterPage from "../pages/RegisterPage.vue";
import DashboardLayout from "../pages/DashboardLayout.vue";
import SalesDashboard from "../pages/SalesDashboard.vue";
import OrdersPage from "../pages/OrdersPage.vue";
import OrderDetailPage from "../pages/OrderDetailPage.vue";
import ProductsPage from "../pages/ProductsPage.vue";
import ProductBuilder from "../pages/ProductBuilder.vue";
import CategoriesPage from "../pages/CategoriesPage.vue";
import AdminPanel from "../pages/AdminPanel.vue";
import AccountManagement from "../pages/AccountManagement.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/login" },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },
    {
      path: "/app",
      component: DashboardLayout,
      children: [
        { path: "sales", component: SalesDashboard },
        { path: "orders", component: OrdersPage },
        { path: "orders/:id", component: OrderDetailPage },
        { path: "products", component: ProductsPage },
        { path: "products/new", component: ProductBuilder },
        { path: "products/:id", component: ProductBuilder },
        { path: "categories", component: CategoriesPage },
        { path: "admin", component: AdminPanel },
        { path: "accounts", component: AccountManagement }
      ]
    }
  ]
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.path.startsWith("/app") && !auth.isAuthenticated) {
    return "/login";
  }
  return true;
});

export default router;
