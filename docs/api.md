# API

Base URL: `https://your-domain.example`

## Auth

- `POST /auth/register`
- `POST /auth/login`

Body:

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Sync

`GET /sync`

Header:

```text
Authorization: Bearer <token>
```

## Server config

`GET /server-config`

Response:

```json
{
  "app_name": "Shopping List",
  "external_url": "https://shopping.example.com",
  "allow_registration": true,
  "setup_completed": true
}
```

## Lists

- `POST /lists` - создать список.
- `POST /lists/{list_id}/share` - открыть доступ другому зарегистрированному пользователю.

## Items

- `POST /lists/{list_id}/items` - добавить покупку.
- `PATCH /items/{item_id}` - изменить покупку или отметку.
- `DELETE /items/{item_id}` - удалить покупку.
