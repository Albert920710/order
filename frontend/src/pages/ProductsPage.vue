<template>
  <div class="section-box">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
      <div style="display:flex;gap:12px;align-items:center">
        <el-input v-model="keyword" placeholder="搜索产品" style="max-width:220px" />
      </div>
      <div style="display:flex;gap:12px;align-items:center">
        <el-button type="primary" @click="$router.push('/app/products/new')">新建产品</el-button>
        <el-button @click="toggleSelectAll">批量选择</el-button>
        <el-button type="danger" :disabled="!selected.length" @click="deleteSelected">删除选中</el-button>
        <el-button :disabled="!selected.length" @click="copySelected">复制选中</el-button>
      </div>
    </div>
    <el-table ref="tableRef" :data="filteredProducts" style="margin-top:20px" @row-click="goDetail" @selection-change="selected = $event">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="title" label="产品" />
      <el-table-column prop="categoryName" label="分类" width="160" />
      <el-table-column prop="base_price" label="基础价格" width="120" />
      <el-table-column label="操作" width="120">
        <template #default>
          <el-button type="primary" text>查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const products = ref([]);
const keyword = ref("");
const selected = ref([]);
const tableRef = ref(null);

const goDetail = (row) => {
  if (!row?.id) return;
  router.push(`/app/products/${row.id}`);
};

const loadProducts = async () => {
  const { data } = await axios.get("/api/products");
  products.value = data.map((product) => ({
    ...product,
    categoryName: product.category?.name || "-"
  }));
};

const filteredProducts = computed(() => {
  if (!keyword.value) return products.value;
  return products.value.filter((product) => product.title.includes(keyword.value));
});

const toggleSelectAll = () => {
  tableRef.value?.toggleAllSelection();
};

const deleteSelected = async () => {
  const ids = selected.value.map((item) => item.id).filter(Boolean);
  if (!ids.length) return;
  await Promise.all(ids.map((id) => axios.delete(`/api/products/${id}`)));
  ElMessage.success("已删除选中产品");
  selected.value = [];
  await loadProducts();
};

const copySelected = async () => {
  const targets = selected.value.filter((item) => item.id);
  if (!targets.length) return;
  for (const product of targets) {
    const payload = {
      title: `${product.title} 复制`,
      short_description: product.short_description || "",
      brand: product.brand || "",
      material: product.material || "",
      base_price: product.base_price || 0,
      category_id: product.category?.id || null,
      remark_enabled: Boolean(product.remark_enabled ?? true),
      distributor_enabled: Boolean(product.distributor_enabled ?? true),
      custom_order_code_enabled: Boolean(product.custom_order_code_enabled ?? true)
    };
    const { data } = await axios.post("/api/products", payload);
    await axios.post(`/api/products/${data.id}/assets`, {
      images: (product.images || []).map((img) => ({
        image_url: img.image_url,
        is_primary: img.is_primary
      })),
      attributes: (product.attributes || []).map((attribute, index) => ({
        name: attribute.name,
        sort_order: attribute.sort_order ?? index,
        options: (attribute.options || []).map((option) => ({
          label: option.label,
          price_delta: option.price_delta || 0,
          image_url: option.image_url || null,
          is_default: option.is_default || false
        }))
      }))
    });
  }
  ElMessage.success("已复制选中产品");
  selected.value = [];
  await loadProducts();
};

onMounted(loadProducts);
</script>
