<template>
  <PageHeader
    title="货物出库"
    subtitle="从当前库存中选择货物并执行出库"
  >
    <template #icon>
      <ArrowUpIcon />
    </template>
  </PageHeader>

  <OutboundForm />
</template>

<script setup>
import PageHeader from '../components/layout/PageHeader.vue'
import OutboundForm from '../components/forms/OutboundForm.vue'
import { ArrowUpIcon } from '../components/icons'
</script>
