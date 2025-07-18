<template>
  <v-container class="mt-6">

    <!-- Заголовок -->
    <v-card elevation="10" class="mb-8">
      <v-card-title>
        <v-icon class="me-2">mdi-view-dashboard</v-icon>
        Добро пожаловать на EmPolimer!
      </v-card-title>
      <v-card-text>
        <div>Вы вошли как <b>{{ authStore.user?.email }}</b>.</div>
        <div class="d-flex align-center mt-4">
          <v-btn color="error" @click="logout">
            Выйти
          </v-btn>
          <v-spacer />
          <v-btn color="secondary" @click="goToDevices">
            <v-icon start>mdi-cellphone-wireless</v-icon>
            Устройства
          </v-btn>
          <v-btn color="secondary" class="ms-2" @click="goToProfile">
            <v-icon start>mdi-account</v-icon>
            Профиль
          </v-btn>
          <v-btn v-if="canEdit" color="secondary" class="ms-2" @click="goToUsers">
            <v-icon start>mdi-account-group</v-icon>
            Пользователи
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { provide, ref, computed } from 'vue'

const stopSocket = ref(() => {})
provide('stopSocket', stopSocket)

// Инициализация роутера
import { useRouter } from 'vue-router'
const router = useRouter()

// Инициализация стора авторизации
import { useAuthStore } from "@/stores/auth";
const authStore = useAuthStore();

// --- ДРУГИЕ ФУНКЦИИ ---

/**
 * Выход из аккаунта, переход на экран авторизации
 */
const logout = async () => {
  await authStore.logout()
  stopSocket.value && stopSocket.value()
  router.push({ name: 'login' })
}

</script>