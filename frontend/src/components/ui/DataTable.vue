<template>
  <div class="table-shell">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :style="{ width: column.width || 'auto' }">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!data.length">
          <td :colspan="columns.length">
            <slot name="empty">
              <div class="empty-state empty-state-inline">
                <p class="empty-state-title">{{ emptyTitle }}</p>
                <p v-if="emptyDescription" class="empty-state-description">{{ emptyDescription }}</p>
              </div>
            </slot>
          </td>
        </tr>
        <tr v-for="(row, index) in data" :key="getRowKey(row, index)">
          <td v-for="column in columns" :key="column.key">
            <slot :name="column.key" :row="row" :index="index">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  emptyTitle: {
    type: String,
    default: '暂无数据'
  },
  emptyDescription: {
    type: String,
    default: ''
  },
  rowKey: {
    type: String,
    default: ''
  }
})

function getRowKey(row, index) {
  if (props.rowKey && row?.[props.rowKey] !== undefined) {
    return row[props.rowKey]
  }

  return index
}
</script>
