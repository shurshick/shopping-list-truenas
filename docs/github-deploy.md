# Развертывание серверной части с GitHub

Есть два удобных варианта.

## Вариант 1: запуск готового образа из GitHub Container Registry

Этот вариант не собирает backend на TrueNAS. Сервер скачивает готовый Docker-образ из GitHub.

1. Создайте на GitHub Personal Access Token с правами `read:packages` и доступом на чтение содержимого приватного репозитория.
2. На TrueNAS выполните вход в GitHub Container Registry:

```bash
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u shurshick --password-stdin
```

3. Создайте папку приложения и скачайте compose-файл:

```bash
mkdir -p shopping-list
cd shopping-list
curl -L -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -o docker-compose.yml \
  https://raw.githubusercontent.com/shurshick/shopping-list-truenas/main/docker-compose.ghcr.yml
```

4. Создайте `.env`:

```env
POSTGRES_PASSWORD=long-random-password
JWT_SECRET=another-long-random-secret
API_PORT=8000
APP_VERSION=latest
```

5. Запустите:

```bash
docker compose pull
docker compose up -d
```

6. Откройте мастер:

```text
http://truenas-ip:8000/setup
```

## Вариант 2: clone приватного репозитория и сборка на сервере

Этот вариант собирает backend прямо на TrueNAS из исходников.

```bash
git clone https://github.com/shurshick/shopping-list-truenas.git
cd shopping-list-truenas
cp .env.example .env
```

Заполните `.env`, затем:

```bash
docker compose up -d --build
```

Для приватного репозитория GitHub попросит логин и token вместо пароля.

## Обновление

Для варианта с готовым образом:

```bash
docker compose pull
docker compose up -d
```

Для варианта с clone:

```bash
git pull
docker compose up -d --build
```
