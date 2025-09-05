"use client";
import React, { useState, useEffect } from "react";
import { useUiStore } from "../lib/store";
import { Api } from "../lib/api";
import type { AdminOrder, AdminStats, AdminOrderDetail } from "../lib/types";

export default function AdminPanel() {
  const isAdmin = useUiStore((s) => s.isAdmin);
  const adminKey = useUiStore((s) => s.adminKey);
  const [activeTab, setActiveTab] = useState<"dashboard" | "orders" | "customers" | "products">("dashboard");
  const [orders, setOrders] = useState<AdminOrder[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<AdminOrderDetail | null>(null);
  const [orderStatusFilter, setOrderStatusFilter] = useState<string>("");

  if (!isAdmin) {
    return null;
  }

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await Api.getAdminOrders(orderStatusFilter || undefined, 50, 0, adminKey);
      setOrders(data.orders);
    } catch (error) {
      console.error("Failed to load orders:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await Api.getAdminStats(adminKey);
      setStats(data);
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const loadOrderDetail = async (orderId: number) => {
    try {
      const data = await Api.getAdminOrder(orderId, adminKey);
      setSelectedOrder(data);
    } catch (error) {
      console.error("Failed to load order detail:", error);
    }
  };

  const updateOrderStatus = async (orderId: number, newStatus: string) => {
    try {
      await Api.updateAdminOrder(orderId, { status: newStatus }, adminKey);
      await loadOrders();
      if (selectedOrder && selectedOrder.id === orderId) {
        await loadOrderDetail(orderId);
      }
    } catch (error) {
      console.error("Failed to update order:", error);
    }
  };

  useEffect(() => {
    if (activeTab === "dashboard") {
      loadStats();
    } else if (activeTab === "orders") {
      loadOrders();
    }
  }, [activeTab, orderStatusFilter]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency: "RUB",
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ru-RU", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "bg-yellow-100 text-yellow-800";
      case "processing": return "bg-blue-100 text-blue-800";
      case "shipped": return "bg-purple-100 text-purple-800";
      case "delivered": return "bg-green-100 text-green-800";
      case "cancelled": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "pending": return "Ожидает";
      case "processing": return "Обрабатывается";
      case "shipped": return "Отправлен";
      case "delivered": return "Доставлен";
      case "cancelled": return "Отменен";
      default: return status;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Админ-панель</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-3 py-1 rounded-full text-sm ${
              activeTab === "dashboard" ? "bg-neutral-900 text-white" : "bg-neutral-200 text-neutral-900"
            }`}
          >
            Дашборд
          </button>
          <button
            onClick={() => setActiveTab("orders")}
            className={`px-3 py-1 rounded-full text-sm ${
              activeTab === "orders" ? "bg-neutral-900 text-white" : "bg-neutral-200 text-neutral-900"
            }`}
          >
            Заказы
          </button>
          <button
            onClick={() => setActiveTab("customers")}
            className={`px-3 py-1 rounded-full text-sm ${
              activeTab === "customers" ? "bg-neutral-900 text-white" : "bg-neutral-200 text-neutral-900"
            }`}
          >
            Клиенты
          </button>
          <button
            onClick={() => setActiveTab("products")}
            className={`px-3 py-1 rounded-full text-sm ${
              activeTab === "products" ? "bg-neutral-900 text-white" : "bg-neutral-200 text-neutral-900"
            }`}
          >
            Товары
          </button>
        </div>
      </div>

      {activeTab === "dashboard" && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_orders}</div>
              <div className="text-sm text-blue-800">Всего заказов</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{formatCurrency(stats.total_revenue)}</div>
              <div className="text-sm text-green-800">Общая выручка</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{stats.orders_today}</div>
              <div className="text-sm text-purple-800">Заказов сегодня</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {Object.values(stats.orders_by_status).reduce((a, b) => a + b, 0)}
              </div>
              <div className="text-sm text-orange-800">Активных заказов</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Заказы по статусам</h3>
              <div className="space-y-2">
                {Object.entries(stats.orders_by_status).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className="capitalize">{getStatusLabel(status)}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Популярные товары</h3>
              <div className="space-y-2">
                {stats.top_products.map((product, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm">{product.name}</span>
                    <span className="font-semibold text-sm">{product.orders_count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Последние заказы</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Заказ</th>
                    <th className="text-left p-2">Клиент</th>
                    <th className="text-left p-2">Статус</th>
                    <th className="text-left p-2">Сумма</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_orders.map((order) => (
                    <tr key={order.order_no} className="border-b">
                      <td className="p-2 font-mono">{order.order_no}</td>
                      <td className="p-2">{order.customer_email}</td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(order.status)}`}>
                          {getStatusLabel(order.status)}
                        </span>
                      </td>
                      <td className="p-2">{formatCurrency(order.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === "orders" && (
        <div className="space-y-4">
          <div className="flex gap-4 items-center">
            <select
              value={orderStatusFilter}
              onChange={(e) => setOrderStatusFilter(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="">Все статусы</option>
              <option value="pending">Ожидает</option>
              <option value="processing">Обрабатывается</option>
              <option value="shipped">Отправлен</option>
              <option value="delivered">Доставлен</option>
              <option value="cancelled">Отменен</option>
            </select>
            <button
              onClick={loadOrders}
              disabled={loading}
              className="px-4 py-2 bg-neutral-900 text-white rounded-lg disabled:opacity-50"
            >
              {loading ? "Загрузка..." : "Обновить"}
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Заказ</th>
                  <th className="text-left p-2">Дата</th>
                  <th className="text-left p-2">Клиент</th>
                  <th className="text-left p-2">Статус</th>
                  <th className="text-left p-2">Сумма</th>
                  <th className="text-left p-2">Товаров</th>
                  <th className="text-left p-2">Действия</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-mono">{order.order_no}</td>
                    <td className="p-2">{formatDate(order.created_at)}</td>
                    <td className="p-2">
                      <div>
                        <div>{order.customer_email}</div>
                        <div className="text-xs text-gray-500">{order.customer_city}</div>
                      </div>
                    </td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(order.status)}`}>
                        {getStatusLabel(order.status)}
                      </span>
                    </td>
                    <td className="p-2">{formatCurrency(order.total)}</td>
                    <td className="p-2">{order.items_count}</td>
                    <td className="p-2">
                      <button
                        onClick={() => loadOrderDetail(order.id)}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedOrder && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Заказ {selectedOrder.order_no}</h3>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Статус</label>
                  <select
                    value={selectedOrder.status}
                    onChange={(e) => updateOrderStatus(selectedOrder.id, e.target.value)}
                    className="w-full border rounded-lg px-3 py-2"
                  >
                    <option value="pending">Ожидает</option>
                    <option value="processing">Обрабатывается</option>
                    <option value="shipped">Отправлен</option>
                    <option value="delivered">Доставлен</option>
                    <option value="cancelled">Отменен</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Сумма</label>
                  <div className="text-lg font-semibold">{formatCurrency(selectedOrder.total)}</div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Клиент</label>
                <div className="text-sm">
                  <div>{selectedOrder.customer_email}</div>
                  <div className="text-gray-500">{selectedOrder.customer_city}, {selectedOrder.customer_zip}</div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Товары</label>
                <div className="space-y-2">
                  {selectedOrder.items.map((item) => (
                    <div key={item.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-gray-500">{item.sku} • {item.category}</div>
                      </div>
                      <div className="text-right">
                        <div>{item.qty} шт.</div>
                        <div className="font-medium">{formatCurrency(item.price)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
