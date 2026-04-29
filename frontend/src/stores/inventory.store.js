import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  checkProduct,
  createInbound,
  createOutbound,
  createStorageLocation,
  getBootstrap,
  updateProduct,
  deleteProduct
} from '../services/api'
import { normalizeText } from '../utils/format'

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function normalizeBootstrap(data) {
  return {
    locations: Array.isArray(data?.locations) ? data.locations : [],
    products: Array.isArray(data?.products) ? data.products : [],
    transactions: Array.isArray(data?.transactions) ? data.transactions : []
  }
}

function deriveLastLocation(products, locations) {
  const latestProduct = [...products].find((product) => product.storageLocation)
  if (latestProduct?.storageLocation) {
    return latestProduct.storageLocation
  }

  return locations[0]?.name || ''
}

function normalizeQuantity(value) {
  const quantity = Number.parseInt(value, 10)
  return Number.isFinite(quantity) && quantity > 0 ? quantity : 1
}

function startOfDay(dateString) {
  if (!dateString) return null
  const date = new Date(`${dateString}T00:00:00`)
  return Number.isNaN(date.getTime()) ? null : date.getTime()
}

function endOfDay(dateString) {
  if (!dateString) return null
  const date = new Date(`${dateString}T23:59:59`)
  return Number.isNaN(date.getTime()) ? null : date.getTime()
}

export const useInventoryStore = defineStore('inventory', () => {
  const locations = ref([])
  const products = ref([])
  const transactions = ref([])
  const lastInboundLocation = ref('')
  const isReady = ref(false)
  const errorMessage = ref('')

  const locationOptions = computed(() =>
    [...locations.value].sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  )
  const productOptions = computed(() =>
    [...products.value].sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  )
  const recentProducts = computed(() =>
    [...products.value].sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)))
  )
  const recentTransactions = computed(() =>
    [...transactions.value].sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)))
  )
  const lowStockProducts = computed(() =>
    productOptions.value.filter((product) => product.quantity > 0 && product.quantity <= 10)
  )

  const summary = computed(() => ({
    totalProducts: products.value.length,
    totalQuantity: products.value.reduce((sum, product) => sum + product.quantity, 0),
    totalLocations: locationOptions.value.length,
    totalTransactions: transactions.value.length
  }))

  const locationStats = computed(() =>
    locationOptions.value
      .map((location) => {
        const items = products.value.filter((product) => product.storageLocation === location.name)
        return {
          storageLocation: location.name,
          productCount: items.length,
          totalQuantity: items.reduce((sum, item) => sum + item.quantity, 0)
        }
      })
      .filter((row) => row.productCount > 0)
  )

  async function loadBootstrap() {
    isReady.value = false
    errorMessage.value = ''

    try {
      const data = normalizeBootstrap(await getBootstrap())
      locations.value = data.locations
      products.value = data.products
      transactions.value = data.transactions
      lastInboundLocation.value = deriveLastLocation(products.value, locations.value)
      errorMessage.value = ''
    } catch (error) {
      locations.value = []
      products.value = []
      transactions.value = []
      lastInboundLocation.value = ''
      errorMessage.value = error instanceof Error ? error.message : '加载后端数据失败'
    } finally {
      isReady.value = true
    }
  }

  async function refresh() {
    await loadBootstrap()
  }

  async function addStorageLocation(name) {
    const trimmed = normalizeText(name)
    if (!trimmed) {
      return { success: false, message: '请输入存储位置名称' }
    }

    try {
      const result = await createStorageLocation(trimmed)
      await refresh()
      return {
        success: Boolean(result.success ?? true),
        message: result.message || '存储位置添加成功',
        location: trimmed
      }
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : '添加失败' }
    }
  }

  async function inboundProduct(payload) {
    const name = normalizeText(payload?.name)
    const quantity = normalizeQuantity(payload?.quantity)
    const storageLocation = normalizeText(payload?.storageLocation)
    const note = normalizeText(payload?.note)

    if (!name) {
      return { success: false, message: '请填写货物名称' }
    }

    try {
      const result = await createInbound({
        name,
        quantity,
        storageLocation,
        note
      })
      await refresh()
      return {
        success: true,
        message: result.message || `货物 ${name} 已入库 ${quantity} 件`,
        productId: result.productId
      }
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : '入库失败' }
    }
  }

  async function outboundProduct(payload) {
    const productId = Number.parseInt(payload?.productId, 10)
    const quantity = normalizeQuantity(payload?.quantity)
    const targetLocation = normalizeText(payload?.targetLocation)
    const note = normalizeText(payload?.note)

    if (!productId) {
      return { success: false, message: '请选择货物' }
    }

    try {
      const result = await createOutbound({
        productId,
        quantity,
        targetLocation,
        note
      })
      await refresh()
      return {
        success: true,
        message: result.message || '出库成功'
      }
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : '出库失败' }
    }
  }

  function getProductById(productId) {
    const id = Number.parseInt(productId, 10)
    return products.value.find((product) => product.id === id) || null
  }

  function getProductsByLocation(locationName) {
    const trimmed = normalizeText(locationName)
    return products.value
      .filter((product) => product.storageLocation === trimmed)
      .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  }

  function getLocationSummary(locationName) {
    const productsInLocation = getProductsByLocation(locationName)
    return {
      storageLocation: normalizeText(locationName),
      productCount: productsInLocation.length,
      totalQuantity: productsInLocation.reduce((sum, product) => sum + product.quantity, 0)
    }
  }

  function searchProducts(filters = {}) {
    const nameKeyword = normalizeText(filters.name).toLowerCase()
    const location = normalizeText(filters.storageLocation)
    const startDate = startOfDay(filters.startDate)
    const endDate = endOfDay(filters.endDate)

    return productOptions.value.filter((product) => {
      if (nameKeyword && !product.name.toLowerCase().includes(nameKeyword)) {
        return false
      }

      if (location && product.storageLocation !== location) {
        return false
      }

      if (startDate || endDate) {
        const productTransactions = transactions.value.filter((transaction) => transaction.productId === product.id)
        if (
          !productTransactions.some((transaction) => {
            const time = new Date(transaction.createdAt).getTime()
            return (!startDate || time >= startDate) && (!endDate || time <= endDate)
          })
        ) {
          return false
        }
      }

      return true
    })
  }

  async function checkProductByName(name) {
    return checkProduct(normalizeText(name))
  }

  async function updateProductInfo(id, payload) {
    try {
      const result = await updateProduct(id, payload)
      await refresh()
      return { success: true, message: result.message || '更新成功' }
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : '更新失败' }
    }
  }

  async function removeProduct(id) {
    try {
      const result = await deleteProduct(id)
      await refresh()
      return { success: true, message: result.message || '删除成功' }
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : '删除失败' }
    }
  }

  loadBootstrap()

  return {
    locations,
    products,
    transactions,
    lastInboundLocation,
    isReady,
    errorMessage,
    locationOptions,
    productOptions,
    recentProducts,
    recentTransactions,
    lowStockProducts,
    summary,
    locationStats,
    loadBootstrap,
    refresh,
    addStorageLocation,
    inboundProduct,
    outboundProduct,
    getProductById,
    getProductsByLocation,
    getLocationSummary,
    searchProducts,
    checkProductByName,
    updateProductInfo,
    removeProduct
  }
})
