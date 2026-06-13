# Список покупок v1.3.9-project-cleanup

Актуальный публичный релиз Android-приложения и серверной части для самостоятельного размещения.

## Изменения в v1.3.9-project-cleanup

- Это refactor-релиз: пользовательский UX и публичные API-пути сохранены.
- `backend/app/main.py` стал точкой сборки FastAPI-приложения.
- Основные backend endpoints перенесены в router-слой.
- Логика `client_operation_id` вынесена в `services/idempotency_service.py`.
- Работа с таблицей `client_operations` вынесена в `repositories/operations_repo.py`.
- Android-хранилища вынесены из `ShoppingViewModel` в `data/local`.
- `TokenStorage` сохраняет EncryptedSharedPreferences, миграцию старого token и очистку при logout.
- `AppPreferences`, `OfflineQueueStorage` и `ProductCatalogStorage` разгружают ViewModel от прямой работы с SharedPreferences.
- Backend tests расширены до 25 тестов.
- Добавлен документ `docs/architecture.md`.
- Обновлены номера версии Android-приложения и API до `1.3.9`.

## Совместимость

- API-совместимость сохранена.
- UX Android-приложения не менялся.
- Старые Android-клиенты без `client_operation_id` продолжают работать.
- Идемпотентность offline queue из `v1.3.8` сохранена.
- Docker image name, package name, minSdk, targetSdk и env-переменные не менялись.

## Что входит

- Android-приложение для совместных списков покупок.
- Сервер синхронизации на FastAPI и PostgreSQL.
- Веб-мастер первичной настройки сервера по адресу `/setup`.
- Веб-страница администратора по адресу `/admin`.
- Идемпотентная offline-очередь изменений.
- Автоматические миграции базы данных при запуске контейнера API.
- Несколько способов запуска сервера: Docker Compose, сборка напрямую из GitHub, готовый GHCR-образ и TrueNAS Custom App.

## Совместимость Android

- Минимальная версия Android: Android 8.0 Oreo.
- Минимальный API: 26.
- Целевая версия сборки: Android 15, API 35.

## Сервер

Готовый Docker-образ:

```text
ghcr.io/shurshick/shopping-list-api:latest
ghcr.io/shurshick/shopping-list-api:v1.3.9-project-cleanup
```

## Проверки

```bash
python -m pytest backend/tests -q
cd android
./gradlew assembleDebug --stacktrace
./gradlew assembleRelease --stacktrace
```

## Файлы релиза

- `shopping-list-android-v1.3.9-project-cleanup.apk` - Android-приложение для установки на телефон.
- `shopping-list-server-v1.3.9-project-cleanup.zip` - серверная часть, Docker Compose-файлы и инструкции.
- `shopping-list-source-v1.3.9-project-cleanup.zip` - полный архив исходного кода.
