<template>
  <div class="section-box">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
      <div style="display:flex;gap:12px;align-items:center">
        <el-input v-model="keyword" placeholder="订单号 / 产品名" style="width:240px" />
        <el-button @click="search">搜索</el-button>
      </div>
      <div>
        <el-button type="danger" :disabled="!selected.length">批量删除</el-button>
        <el-button @click="exportSelected" :disabled="!selected.length">导出选中订单</el-button>
        <el-button @click="exportAll">导出全部订单</el-button>
      </div>
    </div>
    <el-table :data="orders" style="margin-top:20px" @selection-change="selected = $event">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="orderCode" label="订单号" width="220" />
      <el-table-column prop="date" label="下单日期" width="160" />
      <el-table-column prop="product" label="产品" />
      <el-table-column prop="customOrderCode" label="自定义订单号" width="160" />
      <el-table-column prop="total" label="总价" width="120" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" text @click="openDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:center;margin-top:16px">
      <el-pagination background layout="prev, pager, next" :page-size="50" :total="orders.length" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const keyword = ref("");
const selected = ref([]);
const orders = ref([]);
const router = useRouter();
const rawOrders = ref([]);

const loadOrders = async () => {
  const { data } = await axios.get("/api/orders");
  rawOrders.value = data;
  orders.value = data.map((order) => ({
    orderCode: order.order_code,
    date: new Date(order.created_at).toLocaleDateString(),
    product: order.product?.title || "-",
    total: `¥${order.total_price}`,
    id: order.id,
    distributor: order.distributor || "",
    customOrderCode: order.custom_order_code || ""
  }));
};

const search = async () => {
  await loadOrders();
  if (!keyword.value) return;
  orders.value = orders.value.filter(
    (order) =>
      order.orderCode.includes(keyword.value) ||
      order.product.includes(keyword.value)
  );
};

const openDetail = (row) => {
  if (!row?.id) return;
  router.push(`/app/orders/${row.id}`);
};

onMounted(loadOrders);

const buildCsv = (records) => {
  const headers = [
    "业务员",
    "代理商",
    "下单日期",
    "订单号",
    "自定义订单号",
    "产品名称",
    "产品品牌",
    "材质",
    "订单备注"
  ];
  const attributeHeaders = new Set();
  records.forEach((order) => {
    (order.items || []).forEach((item) => attributeHeaders.add(item.attribute_name));
  });
  const attributeList = Array.from(attributeHeaders);
  const allHeaders = [...headers, ...attributeList];
  const rows = records.map((order) => {
    const base = [
      order.sales?.name || order.sales?.username || "",
      order.distributor || "",
      new Date(order.created_at).toLocaleDateString(),
      order.order_code,
      order.custom_order_code || "",
      order.product?.title || "",
      order.product?.brand || "",
      order.product?.material || "",
      order.remark_text || ""
    ];
    const attrs = attributeList.map((name) => {
      const item = (order.items || []).find((entry) => entry.attribute_name === name);
      return item ? item.option_label : "";
    });
    return [...base, ...attrs];
  });
  return [allHeaders, ...rows]
    .map((row) => row.map((cell) => `"${String(cell ?? "").replace(/\"/g, '""')}"`).join(","))
    .join("\n");
};

const downloadCsv = (content, filename) => {
  const blob = new Blob([`\uFEFF${content}`], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const exportSelected = () => {
  const ids = new Set(selected.value.map((item) => item.id));
  const records = rawOrders.value.filter((order) => ids.has(order.id));
  const csv = buildCsv(records);
  downloadCsv(csv, "selected-orders.csv");
};

const exportAll = () => {
  const csv = buildCsv(rawOrders.value);
  downloadCsv(csv, "all-orders.csv");
};
</script>
