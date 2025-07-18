<template>
  <div class="auth-wrapper d-flex flex-column align-center justify-center fill-height pa-4">
    <div style="margin-bottom: 19vh; width:100%">
      <!-- Логотип и название -->
      <div class="mb-6 text-center">
        <div class="text-h5 font-weight-bold" style="letter-spacing:1px;">Проект SmartLearning</div>
      </div>
      <!-- Карточка авторизации -->
      <v-card class="mx-auto" width="100%" max-width="400" elevation="8">
        <v-card-text>
          <v-form @submit.prevent="login" ref="formRef" validate-on="submit">
            <v-text-field v-model="form.username" label="Пользователь" type="email" :rules="[rules.required]"
              prepend-inner-icon="mdi-account" autocomplete="username" required />
            <v-text-field v-model="form.password" label="Пароль" type="password" :rules="[rules.required]"
              prepend-inner-icon="mdi-lock" autocomplete="current-password" required />
            <v-btn :loading="loading" color="primary" type="submit" class="mt-4" block>
              Войти
            </v-btn>
            <v-alert v-if="serverErrorMessage" type="error" class="mt-3" dense>{{ serverErrorMessage }}</v-alert>
          </v-form>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import rules from "@/common/helpers/rules";

// Импорт сервиса для работы с JWT (получение access/refresh токена)
import jwtService from "@/services/jwt/jwt.service"

// Импорт и инициализация роутера
import { useRouter } from 'vue-router'
const router = useRouter()

// Импорт и инициализация стора авторизации
import { useAuthStore } from '@/stores'
const authStore = useAuthStore()

// Элемент формы
const formRef = ref();
// Сообщение об ошибке авторизации
const serverErrorMessage = ref('')
// Индикатор загрузки
const loading = ref(false)

// Локальное состояние формы
const form = reactive({
  username: "",
  password: "",
});

/**
  Авторизация пользователя
 */
const login = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  loading.value = true
  const credentials = {
    username: form.username,
    password: form.password,
  }
  serverErrorMessage.value = null

  const responseMessage = await authStore.login(credentials)
  loading.value = false

  if (responseMessage !== 'success') {
    serverErrorMessage.value = responseMessage;
    return
  }
  await authStore.getMe();
  await router.push({ path: "/" });
}

/**
 * При монтировании компонента:
 * Если accessToken есть и пользователь уже аутентифицирован —
 * сразу перекинуть на dashboard, чтобы не показывать форму входа
 */
onMounted(async () => {
  const accessToken = jwtService.getAccessToken();
  if (accessToken && authStore.isAuthenticated) {
    router.push({ path: "/" });
  }
})
</script>


<style scoped>
.auth-wrapper {
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
}

@media (max-width: 600px) {
  .auth-wrapper .v-card {
    max-width: 100vw !important;
    width: 100vw !important;
    border-radius: 0 !important;
  }

  .auth-wrapper {
    padding: 0 !important;
  }
}
</style>