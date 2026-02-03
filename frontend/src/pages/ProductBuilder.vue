<template>
  <div style="display:grid;grid-template-columns:3fr 1fr;gap:24px">
    <div>
      <div class="section-box">
        <h3>产品基础信息</h3>
        <el-input v-model="form.title" placeholder="产品标题" style="margin-top:12px" />
        <el-input
          v-model="form.shortDescription"
          type="textarea"
          placeholder="产品短描述"
          style="margin-top:12px"
        />
        <div style="display:flex;gap:12px;margin-top:12px">
          <el-input v-model="form.brand" placeholder="品牌" />
          <el-input v-model="form.material" placeholder="材质" />
        </div>
      </div>
      <div class="section-box">
        <h3>上传产品图片</h3>
        <el-upload
          list-type="picture-card"
          :file-list="productImages"
          :http-request="handleProductUpload"
          :on-remove="handleProductRemove"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
        <p>第一张默认作为主图。</p>
      </div>
      <div class="section-box">
        <h3>产品分类</h3>
        <div style="display:flex;gap:12px;align-items:center">
          <el-select v-model="form.category" placeholder="选择分类">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
          <el-button @click="categoryDialog = true">新建分类</el-button>
        </div>
      </div>
      <div class="section-box">
        <h3>基础价格</h3>
        <el-input-number v-model="form.basePrice" :min="0" />
      </div>
      <div class="section-box">
        <h3>产品属性配置</h3>
        <div
          v-for="(attribute, index) in form.attributes"
          :key="index"
          class="section-box"
          draggable="true"
          @dragstart="handleAttributeDragStart(index)"
          @dragover.prevent
          @drop="handleAttributeDrop(index)"
        >
          <div style="display:flex;justify-content:space-between;align-items:center">
            <el-input v-model="attribute.name" placeholder="属性名" />
            <div style="display:flex;gap:8px;align-items:center">
              <el-button @click="addOption(attribute)">+ option</el-button>
              <el-button type="danger" plain @click="removeAttribute(index)">删除属性</el-button>
            </div>
          </div>
          <div v-if="expandedAttributes[index]" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px">
            <div
              v-for="(option, optIndex) in visibleOptions(attribute, index)"
              :key="option.uid"
              class="section-box option-card"
              style="width:180px"
              draggable="true"
              @dragstart="handleOptionDragStart(attribute, optIndex)"
              @dragover.prevent
              @drop="handleOptionDrop(attribute, optIndex)"
            >
              <div class="option-toolbar">
                <el-button type="danger" text @click="removeOption(attribute, option)">删除</el-button>
              </div>
              <el-input v-model="option.label" placeholder="选项" />
              <el-input-number v-model="option.price" :min="0" style="margin-top:8px" />
              <el-checkbox v-model="option.isDefault" style="margin-top:8px">默认选中</el-checkbox>
              <el-upload
                list-type="picture-card"
                :limit="1"
                :file-list="option.fileList"
                :http-request="(request) => handleOptionUpload(request, option)"
                :on-remove="() => handleOptionRemove(option)"
                :class="{ 'hide-upload': option.fileList.length >= 1 }"
                style="margin-top:8px"
              />
            </div>
          </div>
          <div v-if="attribute.options.length" style="margin-top:8px">
            <el-button text @click="toggleOptions(index)">
              {{ expandedAttributes[index] ? "收起选项" : `展开选项（共 ${attribute.options.length} 个）` }}
            </el-button>
          </div>
        </div>
        <el-button @click="addAttribute">新增属性</el-button>
      </div>
      <div class="section-box">
        <h3>订单备注</h3>
        <el-checkbox v-model="form.remarkEnabled">启用订单备注</el-checkbox>
      </div>
      <div class="section-box">
        <h3>订单字段设置</h3>
        <el-checkbox v-model="form.distributorEnabled" :true-label="true" :false-label="false">启用代理商</el-checkbox>
        <el-checkbox v-model="form.customOrderCodeEnabled" :true-label="true" :false-label="false" style="margin-left:12px">
          启用自定义订单号
        </el-checkbox>
      </div>
    </div>
    <div>
      <div class="sticky-panel">
        <p>确认信息无误后保存。</p>
        <el-button type="primary" style="width:100%" @click="submitProduct">{{ submitLabel }}</el-button>
      </div>
    </div>
  </div>
  <el-dialog v-model="categoryDialog" title="新建分类">
    <el-input v-model="newCategory" placeholder="分类名" />
    <template #footer>
      <el-button @click="categoryDialog = false">取消</el-button>
      <el-button type="primary" @click="saveCategory">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import { Plus } from "@element-plus/icons-vue";
import { useRoute, useRouter } from "vue-router";

const categoryDialog = ref(false);
const newCategory = ref("");
const categories = ref([]);
const productImages = ref([]);
const optionLimit = 10;
const expandedAttributes = ref([]);
const attributeDragIndex = ref(null);
let optionUid = 0;
const createOption = (overrides = {}) => ({
  uid: optionUid++,
  label: "",
  price: 0,
  imageUrl: "",
  fileList: [],
  isDefault: false,
  ...overrides
});
const route = useRoute();
const router = useRouter();
const productId = computed(() => route.params.id);
const submitLabel = computed(() => (productId.value ? "保存" : "发布"));
const form = reactive({
  title: "",
  shortDescription: "",
  brand: "",
  material: "",
  category: "",
  basePrice: 0,
  images: [],
  remarkEnabled: true,
  distributorEnabled: true,
  customOrderCodeEnabled: true,
  attributes: []
});

const addAttribute = () => {
  form.attributes.push({ name: "", options: [] });
  expandedAttributes.value.push(false);
};

const addOption = (attribute) => {
  attribute.options = [...attribute.options, createOption()];
};

const removeAttribute = (index) => {
  form.attributes.splice(index, 1);
  expandedAttributes.value.splice(index, 1);
};

const removeOption = (attribute, option) => {
  attribute.options = attribute.options.filter((item) => item !== option);
};

const handleAttributeDragStart = (index) => {
  attributeDragIndex.value = index;
};

const handleAttributeDrop = (index) => {
  const fromIndex = attributeDragIndex.value;
  if (fromIndex === null || fromIndex === index) return;
  const updatedAttributes = [...form.attributes];
  const [movedAttribute] = updatedAttributes.splice(fromIndex, 1);
  updatedAttributes.splice(index, 0, movedAttribute);
  form.attributes = updatedAttributes;

  const updatedExpanded = [...expandedAttributes.value];
  const [movedExpanded] = updatedExpanded.splice(fromIndex, 1);
  updatedExpanded.splice(index, 0, movedExpanded);
  expandedAttributes.value = updatedExpanded;
  attributeDragIndex.value = null;
};

const handleOptionDragStart = (attribute, index) => {
  attribute.dragIndex = index;
};

const handleOptionDrop = (attribute, index) => {
  const fromIndex = attribute.dragIndex;
  if (fromIndex === undefined || fromIndex === index) return;
  const updated = [...attribute.options];
  const [moved] = updated.splice(fromIndex, 1);
  updated.splice(index, 0, moved);
  attribute.options = updated;
  attribute.dragIndex = undefined;
};

const toggleOptions = (index) => {
  expandedAttributes.value[index] = !expandedAttributes.value[index];
};

const visibleOptions = (attribute, index) => {
  if (expandedAttributes.value[index] || attribute.options.length <= optionLimit) {
    return attribute.options;
  }
  return attribute.options.slice(0, optionLimit);
};

const saveCategory = async () => {
  if (!newCategory.value) return;
  await axios.post(`/api/products/categories?name=${encodeURIComponent(newCategory.value)}`);
  newCategory.value = "";
  categoryDialog.value = false;
  await loadCategories();
};

const submitProduct = async () => {
  if (!form.title) {
    ElMessage.warning("请填写产品标题");
    return;
  }
  const payload = {
    title: form.title,
    short_description: form.shortDescription,
    brand: form.brand,
    material: form.material,
    base_price: form.basePrice,
    category_id: form.category || null,
    remark_enabled: Boolean(form.remarkEnabled),
    distributor_enabled: Boolean(form.distributorEnabled),
    custom_order_code_enabled: Boolean(form.customOrderCodeEnabled)
  };
  let targetId = productId.value;
  if (targetId) {
    await axios.put(`/api/products/${targetId}`, payload);
  } else {
    const { data } = await axios.post("/api/products", payload);
    targetId = data.id;
  }
  await axios.post(`/api/products/${targetId}/assets`, {
    images: form.images.map((url, index) => ({
      image_url: url,
      is_primary: index === 0
    })),
    attributes: form.attributes.map((attribute, index) => ({
      name: attribute.name,
      sort_order: index,
      options: attribute.options.map((option) => ({
        label: option.label,
        price_delta: option.price || 0,
        image_url: option.imageUrl || null,
        is_default: option.isDefault
      }))
    }))
  });
  ElMessage.success(targetId && productId.value ? "产品已保存" : "产品已创建");
  if (!productId.value) {
    router.push("/app/products");
  }
};

const loadCategories = async () => {
  const { data } = await axios.get("/api/products/categories");
  categories.value = data;
};

const uploadMedia = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await axios.post("/api/products/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data.url;
};

const handleProductUpload = async ({ file }) => {
  const url = await uploadMedia(file);
  form.images.push(url);
  productImages.value.push({ name: file.name, url });
};

const handleProductRemove = (file) => {
  form.images = form.images.filter((url) => url !== file.url);
};

const handleOptionUpload = async ({ file }, option) => {
  const url = await uploadMedia(file);
  option.imageUrl = url;
  option.fileList = [{ name: file.name, url }];
};

const handleOptionRemove = (option) => {
  option.imageUrl = "";
  option.fileList = [];
};

const loadProduct = async () => {
  if (!productId.value) return;
  const { data } = await axios.get("/api/products");
  const product = data.find((item) => item.id === Number(productId.value));
  if (!product) return;
  form.title = product.title;
  form.shortDescription = product.short_description || "";
  form.brand = product.brand || "";
  form.material = product.material || "";
  form.basePrice = product.base_price || 0;
  form.category = product.category?.id || "";
  form.remarkEnabled = product.remark_enabled ?? true;
  form.distributorEnabled =
    product.distributor_enabled !== undefined ? Boolean(product.distributor_enabled) : true;
  form.customOrderCodeEnabled =
    product.custom_order_code_enabled !== undefined ? Boolean(product.custom_order_code_enabled) : true;
  form.images = product.images?.map((img) => img.image_url) || [];
  productImages.value = product.images?.map((img) => ({ name: img.image_url, url: img.image_url })) || [];
  form.attributes = (product.attributes || []).map((attribute) => ({
    name: attribute.name,
    options: (attribute.options || []).map((option) => ({
      ...createOption({
        label: option.label,
        price: option.price_delta || 0,
        imageUrl: option.image_url || "",
        fileList: option.image_url ? [{ name: option.image_url, url: option.image_url }] : [],
        isDefault: option.is_default || false
      })
    }))
  }));
  expandedAttributes.value = form.attributes.map(() => false);
};

onMounted(async () => {
  await loadCategories();
  await loadProduct();
});
</script>

<style scoped>
:deep(.hide-upload .el-upload--picture-card) {
  display: none;
}

.option-card {
  display: flex;
  flex-direction: column;
}

.option-toolbar {
  display: flex;
  justify-content: flex-end;
  margin: 4px 4px 8px 4px;
}
</style>
