const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

async function request(path, options = {}) {
  const hasBody = Object.prototype.hasOwnProperty.call(options, 'body')
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
  let response

  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        ...(hasBody && !isFormData ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {})
      },
      ...options
    })
  } catch {
    throw new Error('后端未启动或无法连接，请先启动 FastAPI 后端')
  }

  const text = await response.text()
  const data = text ? JSON.parse(text) : null

  if (!response.ok) {
    const message = data?.detail || data?.message || '请求失败'
    throw new Error(message)
  }

  return data
}

export function login(username, password) {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  })
}

export function getBootstrap() {
  return request('/bootstrap')
}

export function getStorageLocations() {
  return request('/storage-locations')
}

export function createStorageLocation(name) {
  return request('/storage-locations', {
    method: 'POST',
    body: JSON.stringify({ name })
  })
}

export function createInbound(payload) {
  return request('/inbound', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function createOutbound(payload) {
  return request('/outbound', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function searchProducts(params) {
  const query = new URLSearchParams()

  if (params?.name) query.set('name', params.name)
  if (params?.storageLocation) query.set('storage_location', params.storageLocation)
  if (params?.startDate) query.set('start_date', params.startDate)
  if (params?.endDate) query.set('end_date', params.endDate)

  const suffix = query.toString() ? `?${query.toString()}` : ''
  return request(`/search${suffix}`)
}

export function getTransactions() {
  return request('/transactions')
}

export function getLocationStats() {
  return request('/location-stats')
}

export function getLocationDetail(storageLocation) {
  return request(`/location-stats/${encodeURIComponent(storageLocation)}`)
}

export function checkProduct(name) {
  return request('/check-product', {
    method: 'POST',
    body: JSON.stringify({ name })
  })
}

export function updateProduct(id, payload) {
  return request(`/products/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}

export function deleteProduct(id) {
  return request(`/products/${id}`, {
    method: 'DELETE'
  })
}

export function createReceiptImport(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request('/receipt-imports', {
    method: 'POST',
    body: formData
  })
}

export function getReceiptImports() {
  return request('/receipt-imports')
}

export function getReceiptImport(importId) {
  return request(`/receipt-imports/${importId}`)
}

export function updateReceiptImport(importId, payload) {
  return request(`/receipt-imports/${importId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}

export function confirmReceiptImport(importId) {
  return request(`/receipt-imports/${importId}/confirm`, {
    method: 'POST'
  })
}
