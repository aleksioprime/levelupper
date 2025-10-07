FROM --platform=linux/amd64 node:20-bullseye AS builder

# Устанавливаем рабочий каталог контейнера
WORKDIR /usr/src/app

# Позволяет запускать vite и другие инструменты напрямую
ENV PATH /app/node_modules/.bin:$PATH
ENV NODE_OPTIONS=--trace-deprecation

# Внедряем все переменные окружения, которые нам понадобятся
ARG VITE_LOGGING
ARG VITE_SERVICE_URL

# Предоставлем переменную готовому контейнеру
ENV VITE_LOGGING=$VITE_LOGGING
ENV VITE_SERVICE_URL=$VITE_SERVICE_URL

# Копируем файлы пакетов в контейнер и устанавливаем их
COPY app/package.json ./
RUN npm install

# Копируем все файлы фронтенда
COPY app ./

FROM builder AS dev
CMD ["npm", "run", "dev", "--", "--host"]

FROM builder AS prod-builder
RUN npm run build

FROM nginx:1.29 AS prod

RUN apt update && apt install -y certbot python3-certbot-nginx
RUN mkdir -p /var/www/certbot

COPY --from=prod-builder /usr/src/app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]