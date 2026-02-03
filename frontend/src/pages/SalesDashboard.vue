<template>
  <div>
    <div class="section-box">
      <h2>欢迎页面</h2>
      <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:16px">
        <div class="section-box" style="flex:1;min-width:200px">
          <strong>账号角色</strong>
          <div>{{ roleLabel }}</div>
        </div>
        <div class="section-box" style="flex:1;min-width:200px">
          <strong>当前下单数量</strong>
          <div>{{ orderCount }}</div>
        </div>
        <div class="section-box" style="flex:1;min-width:200px">
          <strong>上次登录地点</strong>
          <div>内网</div>
        </div>
      </div>
    </div>
    <div class="section-box">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h3>立即下单</h3>
        <el-button type="primary" @click="modalVisible = true">立即下单</el-button>
      </div>
      <p>通过弹窗选择产品，完成属性配置后即可下单。</p>
    </div>
    <el-dialog v-model="modalVisible" width="80%" title="产品下单" draggable class="modal-scroll">
      <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;align-items:center">
        <el-input v-model="keyword" placeholder="产品名称 / 关键词 / SKU" style="max-width:280px" />
        <el-button @click="searchByKeyword">搜索</el-button>
        <el-upload :show-file-list="false" :auto-upload="false" :on-change="handleProductImageSelect">
          <el-button>上传图片搜索</el-button>
        </el-upload>
        <span v-if="productSearchFileName" style="font-size:12px;color:#6b7280">{{ productSearchFileName }}</span>
        <el-button :disabled="!productSearchFile" @click="searchByImage">图片搜索</el-button>
        <el-button text v-if="isProductSearchActive" @click="clearProductSearch">清除搜索</el-button>
      </div>
      <div class="card-grid">
        <div class="product-card" v-for="product in visibleProducts" :key="product.id" @click="selectProduct(product)">
          <img :src="product.image" alt="" />
          <div class="info">
            <div class="badge">{{ product.category }}</div>
            <div>{{ product.title }}</div>
          </div>
        </div>
      </div>
      <div style="display:flex;justify-content:center;margin-top:16px">
        <el-pagination background layout="prev, pager, next" :page-size="20" :total="visibleProducts.length" />
      </div>
      <template #footer>
        <el-button @click="modalVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="detailVisible" width="70%" title="产品详情" draggable class="modal-scroll">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
        <div>
          <img :src="activeImage" alt="" style="width:100%;border-radius:16px" />
          <div style="display:flex;gap:8px;margin-top:12px">
            <img
              v-for="image in selectedProduct.images"
              :key="image"
              :src="image"
              style="width:60px;height:60px;object-fit:cover;border-radius:10px;cursor:pointer"
              @click="activeImage = image"
            />
          </div>
        </div>
        <div>
          <span class="badge">{{ selectedProduct.category }}</span>
          <h3>{{ selectedProduct.title }}</h3>
          <div style="margin-bottom:12px">属性选配（必填）</div>
          <div v-for="attribute in selectedProduct.attributes" :key="attribute.id" style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
              <span style="font-size:13px;color:#6b7280">{{ attribute.name }}</span>
              <el-button v-if="attributeHasImages(attribute)" text @click="openImageSearch(attribute)">
                图片搜索属性
              </el-button>
            </div>
            <div v-if="attributeHasImages(attribute)" style="display:flex;gap:8px;flex-wrap:wrap">
              <div
                v-for="option in visibleAttributeOptions(attribute)"
                :key="option.id"
                :style="optionStyle(attribute.id, option.id)"
                @click="selectedOptions[attribute.id] = option.id"
              >
                <img :src="option.image_url" alt="" style="width:48px;height:48px;object-fit:cover;border-radius:8px" />
                <div style="font-size:12px;text-align:center">{{ option.label }}</div>
              </div>
            </div>
            <el-select v-else v-model="selectedOptions[attribute.id]" placeholder="请选择">
              <el-option
                v-for="option in visibleAttributeOptions(attribute)"
                :key="option.id"
                :label="option.label"
                :value="option.id"
              />
            </el-select>
          </div>
          <div v-if="selectedProduct.remark_enabled" style="margin-top:12px">
            <div style="margin-bottom:6px;font-size:13px;color:#6b7280">订单备注</div>
            <el-input v-model="remarkText" type="textarea" placeholder="备注信息" />
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
          <div v-if="selectedProduct.distributor_enabled || selectedProduct.custom_order_code_enabled" style="margin-top:12px">
            <div v-if="selectedProduct.distributor_enabled" style="margin-bottom:8px">
              <el-select v-model="distributor" placeholder="选择客户" filterable>
                <el-option
                  v-for="customer in customers"
                  :key="customer.id"
                  :label="customer.full_name"
                  :value="customer.full_name"
                />
              </el-select>
            </div>
            <div v-if="selectedProduct.custom_order_code_enabled" style="margin-bottom:8px">
              <el-input v-model="customOrderCode" placeholder="自定义订单号" />
            </div>
          </div>
          <div style="margin-top:16px;display:flex;gap:12px;align-items:center">
            <el-input-number v-model="qty" :min="1" />
            <el-button type="primary" @click="placeOrder">下单</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
    <el-dialog v-model="imageSearchVisible" width="60%" title="图片搜索属性" draggable class="modal-scroll">
      <div v-if="searchAttribute">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:12px;flex-wrap:wrap">
          <el-upload :show-file-list="false" :auto-upload="false" :on-change="handleAttributeSearchSelect">
            <el-button>上传图片搜索</el-button>
          </el-upload>
          <span v-if="attributeSearchFileName" style="font-size:12px;color:#6b7280">{{ attributeSearchFileName }}</span>
          <el-button :disabled="!attributeSearchFile" @click="handleAttributeSearchUpload">图片搜索</el-button>
          <el-button type="primary" style="margin-left:auto" @click="confirmImageSelection">保存</el-button>
        </div>
        <div v-if="searchError" style="margin-bottom:8px;color:#f43f5e">{{ searchError }}</div>
        <div class="card-grid">
          <div
            v-for="option in visibleSearchResults"
            :key="option.id"
            class="product-card"
            style="cursor:pointer"
            @click="toggleOption(option.id)"
          >
            <img :src="option.image_url" alt="" />
            <div class="info">
              <div>{{ option.label }}</div>
              <el-checkbox v-model="selectedSearchOptions" :label="option.id">选择</el-checkbox>
            </div>
          </div>
        </div>
        <div v-if="searchResults.length > optionLimit" style="margin-top:12px">
          <el-button text @click="searchExpanded = !searchExpanded">
            {{ searchExpanded ? "收起选项" : `展开全部（已折叠 ${searchResults.length - optionLimit} 个）` }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import { useAuthStore } from "../stores/auth";
import { Plus } from "@element-plus/icons-vue";

const auth = useAuthStore();
const roleLabel = computed(() => (auth.role === "sales" ? "业务员" : auth.role));
const orderCount = ref(0);
const modalVisible = ref(false);
const detailVisible = ref(false);
const keyword = ref("");
const selectedOptions = ref({});
const qty = ref(1);
const activeImage = ref("");
const remarkText = ref("");
const remarkFiles = ref([]);
const distributor = ref("");
const customOrderCode = ref("");
const imageSearchVisible = ref(false);
const searchAttribute = ref(null);
const searchResults = ref([]);
const productSearchFile = ref(null);
const productSearchFileName = ref("");
const attributeSearchFile = ref(null);
const attributeSearchFileName = ref("");
const searchError = ref("");
const optionLimit = 10;
const searchExpanded = ref(false);
const selectedSearchOptions = ref([]);
const customers = ref([]);

const productList = ref([]);
const productMatches = ref([]);

const isProductSearchActive = computed(() => productMatches.value.length > 0);
const visibleProducts = computed(() => (isProductSearchActive.value ? productMatches.value : productList.value));
const selectedProduct = ref(productList.value[0]);

const searchByKeyword = () => {
  if (!keyword.value) return;
  const filtered = productList.value.filter((product) => product.title.includes(keyword.value));
  if (filtered.length) {
    productMatches.value = filtered;
    selectedProduct.value = filtered[0];
    activeImage.value = filtered[0].images?.[0] || "";
  } else {
    productMatches.value = [];
  }
};

const handleProductImageSelect = (uploadFile) => {
  productSearchFile.value = uploadFile.raw;
  productSearchFileName.value = uploadFile.name;
};

const clearProductSearch = () => {
  productMatches.value = [];
  keyword.value = "";
  productSearchFile.value = null;
  productSearchFileName.value = "";
};

const selectProduct = (product) => {
  selectedProduct.value = product;
  activeImage.value = product.images?.[0] || "";
  selectedOptions.value = {};
  distributor.value = "";
  customOrderCode.value = "";
  (product.attributes || []).forEach((attribute) => {
    const defaultOption = attribute.options?.find((option) => option.is_default);
    if (defaultOption) {
      selectedOptions.value[attribute.id] = defaultOption.id;
    }
  });
  remarkText.value = "";
  remarkFiles.value = [];
  detailVisible.value = true;
};

const placeOrder = async () => {
  const requiredAttributes = selectedProduct.value.attributes || [];
  const selectedIds = requiredAttributes.map((attribute) => selectedOptions.value[attribute.id]).filter(Boolean);
  if (requiredAttributes.length && selectedIds.length !== requiredAttributes.length) {
    ElMessage.warning("请完成所有属性选择");
    return;
  }
  try {
    await axios.post("/api/orders", {
      product_id: selectedProduct.value.id,
      qty: qty.value,
      selected_options: selectedIds,
      distributor: distributor.value,
      custom_order_code: customOrderCode.value,
      remark_text: remarkText.value,
      remark_images: remarkFiles.value.map((file) => file.url)
    });
    ElMessage.success("下单成功");
    detailVisible.value = false;
    modalVisible.value = false;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "下单失败");
  }
};

const attributeHasImages = (attribute) => attribute.options?.some((option) => option.image_url);

const visibleAttributeOptions = (attribute) => {
  return attribute.options || [];
};

const optionStyle = (attributeId, optionId) => ({
  borderRadius: "10px",
  border:
    Number(selectedOptions.value[attributeId]) === optionId ? "2px solid #111827" : "1px solid #e5e7eb",
  padding: "6px",
  cursor: "pointer"
});

const openImageSearch = (attribute) => {
  searchAttribute.value = attribute;
  searchResults.value = attribute.options || [];
  searchExpanded.value = false;
  selectedSearchOptions.value = [];
  attributeSearchFile.value = null;
  attributeSearchFileName.value = "";
  searchError.value = "";
  imageSearchVisible.value = true;
};

const toggleOption = (optionId) => {
  if (selectedSearchOptions.value.includes(optionId)) {
    selectedSearchOptions.value = selectedSearchOptions.value.filter((id) => id !== optionId);
  } else {
    selectedSearchOptions.value = [optionId];
  }
};

const confirmImageSelection = () => {
  if (searchAttribute.value && selectedSearchOptions.value.length) {
    const selectedId = Number(selectedSearchOptions.value[0]);
    const selectedMatch = searchResults.value.find((option) => Number(option.id) === selectedId);
    let targetOption = selectedMatch;
    if (selectedMatch && searchAttribute.value) {
      const options = searchAttribute.value.options || [];
      targetOption =
        options.find((option) => option.image_url && option.image_url === selectedMatch.image_url) ||
        options.find((option) => option.label === selectedMatch.label) ||
        selectedMatch;
    }
    selectedOptions.value[searchAttribute.value.id] = Number(targetOption?.id || selectedId);
    searchAttribute.value = null;
    selectedSearchOptions.value = [];
    searchResults.value = [];
  } else {
    searchAttribute.value = null;
    selectedSearchOptions.value = [];
    searchResults.value = [];
  }
  imageSearchVisible.value = false;
};

const visibleSearchResults = computed(() => {
  if (searchExpanded.value || searchResults.value.length <= optionLimit) {
    return searchResults.value;
  }
  return searchResults.value.slice(0, optionLimit);
});

const handleAttributeSearchSelect = (uploadFile) => {
  attributeSearchFile.value = uploadFile.raw;
  attributeSearchFileName.value = uploadFile.name;
  searchError.value = "";
};

const handleAttributeSearchUpload = async () => {
  if (!attributeSearchFile.value) return;
  searchError.value = "";
  const formData = new FormData();
  formData.append("file", attributeSearchFile.value);
  try {
    const { data } = await axios.post("/api/search/image", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    if (data.matches?.length) {
      const attributeOptions = searchAttribute.value?.options || [];
      const optionById = new Map(attributeOptions.map((option) => [option.id, option]));
      const optionByImage = new Map(
        attributeOptions.filter((option) => option.image_url).map((option) => [option.image_url, option])
      );
      const optionByLabel = new Map(attributeOptions.map((option) => [option.label, option]));
      const mapped = [];
      data.matches.forEach((match) => {
        if (match.type !== "option") return;
        const resolved =
          optionById.get(match.id) ||
          (match.image_url ? optionByImage.get(match.image_url) : undefined) ||
          (match.label ? optionByLabel.get(match.label) : undefined);
        if (resolved) {
          mapped.push({
            id: resolved.id,
            label: resolved.label,
            image_url: resolved.image_url,
            price_delta: resolved.price_delta
          });
        }
      });
      if (mapped.length) {
        const unique = new Map(mapped.map((option) => [option.id, option]));
        searchResults.value = Array.from(unique.values());
      } else {
        searchResults.value = attributeOptions;
        searchError.value = "未找到匹配结果，已显示当前属性全部选项";
      }
    } else if (searchAttribute.value) {
      searchResults.value = searchAttribute.value.options || [];
      searchError.value = "未找到匹配结果，已显示当前属性全部选项";
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "图片搜索失败");
    searchError.value = "图片搜索失败，请重试";
  }
};

const searchByImage = async () => {
  if (!productSearchFile.value) return;
  const formData = new FormData();
  formData.append("file", productSearchFile.value);
  try {
    const { data } = await axios.post("/api/search/image", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    const productIds = data.matches
      ?.filter((match) => match.type === "product" && match.product_id)
      .map((match) => match.product_id);
    if (productIds?.length) {
      const filtered = productList.value.filter((product) => productIds.includes(product.id));
      productMatches.value = filtered;
      if (filtered.length) {
        selectedProduct.value = filtered[0];
        activeImage.value = filtered[0].images?.[0] || "";
      }
    } else {
      productMatches.value = [];
      ElMessage.warning("未找到匹配的产品");
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "图片搜索失败");
  }
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

const loadOrdersCount = async () => {
  const { data } = await axios.get("/api/orders");
  if (auth.role === "admin") {
    orderCount.value = data.length;
  } else {
    orderCount.value = data.filter((order) => order.sales?.username === auth.username).length;
  }
};

const loadProducts = async () => {
  const { data } = await axios.get("/api/products");
  productList.value = data.map((product) => ({
    id: product.id,
    title: product.title,
    category: product.category?.name || "-",
    images: product.images?.map((img) => img.image_url) || [],
    attributes: product.attributes || [],
    remark_enabled: product.remark_enabled,
    distributor_enabled: product.distributor_enabled ?? true,
    custom_order_code_enabled: product.custom_order_code_enabled ?? true,
    image: product.images?.find((img) => img.is_primary)?.image_url || product.images?.[0]?.image_url || ""
  }));
  productMatches.value = [];
  if (productList.value.length) {
    selectedProduct.value = productList.value[0];
    activeImage.value = productList.value[0].images?.[0] || "";
  }
};

const loadCustomers = async () => {
  const { data } = await axios.get("/api/customers/assigned");
  customers.value = data;
};

onMounted(async () => {
  await loadOrdersCount();
  await loadProducts();
  await loadCustomers();
});
</script>

<style scoped>
:deep(.modal-scroll .el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
