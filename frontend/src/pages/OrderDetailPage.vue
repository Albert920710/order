<template>
  <div style="display:grid;grid-template-columns:3fr 1fr;gap:24px">
    <div class="section-box" v-if="order">
      <h3>订单详情</h3>
      <div style="display:flex;gap:16px;align-items:center;margin-top:12px">
        <img :src="order.mainImage" alt="" style="width:120px;height:120px;object-fit:cover;border-radius:12px" />
        <div>
          <p><strong>订单号：</strong>{{ order.orderCode }}</p>
          <p><strong>产品标题：</strong>{{ order.productTitle }}</p>
          <p><strong>产品品牌：</strong>{{ order.brand || '-' }}</p>
          <p><strong>产品分类：</strong>{{ order.category || '-' }}</p>
        </div>
      </div>
      <div style="margin-top:16px">
        <div v-for="attribute in order.attributes" :key="attribute.id" style="margin-bottom:12px">
          <div style="margin-bottom:6px;color:#6b7280">{{ attribute.name }}</div>
          <el-select v-model="selectedOptions[attribute.id]" placeholder="请选择">
            <el-option
              v-for="option in attribute.options"
              :key="option.id"
              :label="option.label"
              :value="option.id"
            />
          </el-select>
        </div>
      </div>
      <div v-if="order?.distributorEnabled" style="margin-top:12px">
        <el-input v-model="distributor" placeholder="代理商" />
      </div>
      <div v-if="order?.customOrderCodeEnabled" style="margin-top:12px">
        <el-input v-model="customOrderCode" placeholder="自定义订单号" />
      </div>
      <div style="margin-top:12px">
        <el-input v-model="remarkText" type="textarea" placeholder="订单备注" />
        <el-upload
          list-type="picture-card"
          multiple
          :file-list="remarkFiles"
          :http-request="handleRemarkUpload"
          :on-remove="handleRemarkRemove"
          style="margin-top:8px"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </div>
      <div style="margin-top:12px">
        <el-input-number v-model="qty" :min="1" />
      </div>
      <div style="margin-top:16px;font-weight:600">总价：¥{{ totalPrice }}</div>
    </div>
    <div>
      <div class="sticky-panel">
        <h3>保存修改</h3>
        <el-button type="primary" style="width:100%" @click="save">保存</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";
import { Plus } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const order = ref(null);
const qty = ref(1);
const distributor = ref("");
const customOrderCode = ref("");
const remarkText = ref("");
const remarkFiles = ref([]);
const selectedOptions = ref({});

const totalPrice = computed(() => {
  if (!order.value) return 0;
  const base = order.value.basePrice || 0;
  const options = order.value.attributes
    .map((attribute) => attribute.options.find((option) => option.id === selectedOptions.value[attribute.id]))
    .filter(Boolean);
  const optionsSum = options.reduce((sum, option) => sum + (option.price_delta || 0), 0);
  return (base + optionsSum) * qty.value;
});

const loadOrder = async () => {
  const { data } = await axios.get("/api/orders");
  const found = data.find((item) => item.id === Number(route.params.id));
  if (!found) {
    router.push("/app/orders");
    return;
  }
  order.value = {
    id: found.id,
    orderCode: found.order_code,
    productTitle: found.product?.title || "-",
    brand: found.product?.brand,
    category: found.product?.category?.name,
    basePrice: found.product?.base_price || 0,
    mainImage: found.product?.images?.find((img) => img.is_primary)?.image_url || found.product?.images?.[0]?.image_url || "",
    attributes: found.product?.attributes || [],
    distributorEnabled: found.product?.distributor_enabled ?? true,
    customOrderCodeEnabled: found.product?.custom_order_code_enabled ?? true
  };
  qty.value = found.qty || 1;
  distributor.value = found.distributor || "";
  customOrderCode.value = found.custom_order_code || "";
  remarkText.value = found.remark_text || "";
  remarkFiles.value = found.remark_image_url
    ? found.remark_image_url.split(",").map((url) => ({ name: url, url }))
    : [];
  selectedOptions.value = {};
  (found.items || []).forEach((item) => {
    const attribute = order.value.attributes.find((attr) => attr.name === item.attribute_name);
    if (!attribute) return;
    const option = attribute.options.find((opt) => opt.label === item.option_label);
    if (option) {
      selectedOptions.value[attribute.id] = option.id;
    }
  });
};

const save = async () => {
  if (!order.value) return;
  const selectedIds = order.value.attributes.map((attribute) => selectedOptions.value[attribute.id]).filter(Boolean);
  await axios.put(`/api/orders/${order.value.id}`, {
    qty: qty.value,
    selected_options: selectedIds,
    distributor: distributor.value,
    custom_order_code: customOrderCode.value,
    remark_text: remarkText.value,
    remark_images: remarkFiles.value.map((file) => file.url)
  });
  ElMessage.success("订单已更新");
  router.push("/app/orders");
};

const uploadMedia = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await axios.post("/api/products/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data.url;
};

const handleRemarkUpload = async ({ file }) => {
  const url = await uploadMedia(file);
  remarkFiles.value.push({ name: file.name, url });
};

const handleRemarkRemove = (file) => {
  remarkFiles.value = remarkFiles.value.filter((item) => item.url !== file.url);
};

onMounted(loadOrder);
</script>
