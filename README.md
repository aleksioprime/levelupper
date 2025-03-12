# Платформа образовательных курсов


## Запуск для разработчика

Скачайте репозиторий:
```
git clone https://github.com/aleksioprime/hyperspectrus.git
cd hyperspectrus
```

Запустите сервис локально:
```
docker-compose -p hyperspectrus up -d --build
```

Если выходит ошибка `exec /usr/src/app/entrypoint.sh: permission denied`, то нужно вручную установить флаг выполнения для entrypoint.sh в локальной системе:
```
chmod +x backend/entrypoint.sh
chmod +x auth/entrypoint.sh
```