<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

watch(
  () => route.name,
  () => {
    document.title = route.meta.title
      ? `SmartLearning - ${route.meta.title}`
      : 'SmartLearning';
  },
  { immediate: true }
)
</script>