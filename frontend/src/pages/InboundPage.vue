<template>
  <div class="page-container">
    <PageHeader
      title="货物入库"
      subtitle="录入新货物或补充现有仓储位置"
    >
      <template #icon>
        <ArrowDownIcon />
      </template>
    </PageHeader>

    <InboundForm />
  </div>
</template>

<script setup>
import PageHeader from '../components/layout/PageHeader.vue'
import InboundForm from '../components/forms/InboundForm.vue'
import { ArrowDownIcon } from '../components/icons'
</script>
