import logging
from html import escape
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .csrf import create_csrf_token, require_csrf_token, require_same_origin
from .database import get_db
from .models import ServerSetting, User
from .rate_limit import check_rate_limit
from .security import hash_password, verify_password


router = APIRouter()
logger = logging.getLogger(__name__)


def get_server_settings(db: Session) -> ServerSetting:
    server_settings = db.get(ServerSetting, 1)
    if server_settings is None:
        server_settings = ServerSetting(id=1)
        db.add(server_settings)
        db.flush()
    return server_settings


def has_admin_user(db: Session) -> bool:
    return db.scalar(select(User.id).where(User.is_admin.is_(True)).limit(1)) is not None


def verify_admin(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.lower(), User.is_admin.is_(True)))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def render_setup_page(
    server_settings: ServerSetting,
    needs_admin_creation: bool,
    message: str = "",
    csrf_token: str = "",
) -> str:
    csrf_token = csrf_token or create_csrf_token()
    admin_title = "Создание администратора" if needs_admin_creation else "Вход администратора"
    password_extra = """
              <label for="admin_password_confirm">Повторите пароль администратора</label>
              <input id="admin_password_confirm" name="admin_password_confirm" type="password" required minlength="8" autocomplete="new-password" />
    """ if needs_admin_creation else ""
    password_autocomplete = "new-password" if needs_admin_creation else "current-password"

    return f"""
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Настройка списка покупок</title>
        <style>
          :root {{
            color-scheme: light;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
          body {{ margin: 0; background: #f6f7f9; color: #1f2933; }}
          main {{ max-width: 680px; margin: 0 auto; padding: 32px 18px; }}
          section {{
            background: #ffffff;
            border: 1px solid #dde3ea;
            border-radius: 8px;
            padding: 24px;
          }}
          h1 {{ margin: 0 0 8px; font-size: 28px; }}
          h2 {{ margin: 22px 0 8px; font-size: 18px; }}
          p {{ margin: 0 0 20px; color: #52616f; line-height: 1.5; }}
          label {{ display: block; margin: 14px 0 6px; font-weight: 650; }}
          input[type="email"], input[type="text"], input[type="password"], input[type="url"] {{
            box-sizing: border-box;
            width: 100%;
            min-height: 44px;
            border: 1px solid #b8c4d0;
            border-radius: 6px;
            padding: 10px 12px;
            font: inherit;
          }}
          .row {{ display: flex; gap: 10px; align-items: center; margin-top: 14px; }}
          .row input {{ width: 18px; height: 18px; }}
          button {{
            margin-top: 22px;
            min-height: 44px;
            border: 0;
            border-radius: 6px;
            background: #2364aa;
            color: white;
            padding: 0 18px;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
          }}
          .message {{
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 6px;
            background: #e7f5ec;
            color: #14532d;
          }}
          code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
        </style>
      </head>
      <body>
        <main>
          <section>
            <h1>Настройка списка покупок</h1>
            <p>Настройте сервер и учетную запись администратора.</p>
            {f'<div class="message">{escape(message)}</div>' if message else ''}
            <form method="post" action="/setup">
              <input type="hidden" name="csrf_token" value="{escape(csrf_token)}" />
              <h2>{admin_title}</h2>
              <label for="admin_email">Email администратора</label>
              <input id="admin_email" name="admin_email" type="email" required maxlength="255" autocomplete="username" />

              <label for="admin_password">Пароль администратора</label>
              <input id="admin_password" name="admin_password" type="password" required minlength="8" autocomplete="{password_autocomplete}" />
              {password_extra}

              <h2>Настройки сервера</h2>
              <label for="app_name">Название приложения</label>
              <input id="app_name" name="app_name" type="text" value="{escape(server_settings.app_name)}" required maxlength="80" />

              <label for="external_url">Внешний HTTPS-адрес</label>
              <input id="external_url" name="external_url" type="url" value="{escape(server_settings.external_url)}" placeholder="https://shopping.example.com" required maxlength="255" />

              <label class="row" for="allow_registration">
                <input id="allow_registration" name="allow_registration" type="checkbox" value="true" {"checked" if server_settings.allow_registration else ""} />
                Разрешить регистрацию новых пользователей
              </label>

              <button type="submit">Сохранить настройки</button>
            </form>
            <p style="margin-top: 18px;">Публичная конфигурация доступна по адресу <code>/server-config</code>.</p>
          </section>
        </main>
      </body>
    </html>
    """


@router.get("/setup", response_class=HTMLResponse)
def setup_page(message: str = "", db: Session = Depends(get_db)):
    server_settings = get_server_settings(db)
    display_message = "Настройки сохранены" if message == "saved" else message
    return render_setup_page(
        server_settings,
        needs_admin_creation=not has_admin_user(db),
        message=display_message,
        csrf_token=create_csrf_token(),
    )


@router.post("/setup")
def save_setup(
    request: Request,
    admin_email: str = Form(...),
    admin_password: str = Form(...),
    admin_password_confirm: str = Form(default=""),
    app_name: str = Form(...),
    external_url: str = Form(...),
    allow_registration: bool = Form(default=False),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    require_same_origin(request)
    require_csrf_token(csrf_token)
    check_rate_limit(request, "setup", admin_email, limit=8, window_seconds=60)
    needs_admin_creation = not has_admin_user(db)
    email = admin_email.strip().lower()
    server_settings = get_server_settings(db)

    if len(admin_password) < 8:
        return HTMLResponse(
            render_setup_page(server_settings, needs_admin_creation, "Пароль администратора слишком короткий"),
            status_code=400,
        )

    if needs_admin_creation:
        if admin_password != admin_password_confirm:
            return HTMLResponse(
                render_setup_page(server_settings, needs_admin_creation, "Пароли администратора не совпадают"),
                status_code=400,
            )
        if db.scalar(select(User.id).where(User.email == email)):
            return HTMLResponse(
                render_setup_page(server_settings, needs_admin_creation, "Этот email уже зарегистрирован"),
                status_code=409,
            )
        try:
            password_hash = hash_password(admin_password)
        except Exception:
            logger.exception("Could not hash administrator password")
            return HTMLResponse(
                render_setup_page(server_settings, needs_admin_creation, "Не удалось подготовить пароль администратора"),
                status_code=500,
            )
        db.add(User(email=email, password_hash=password_hash, is_admin=True))
    elif verify_admin(db, email, admin_password) is None:
        return HTMLResponse(
            render_setup_page(server_settings, needs_admin_creation, "Неверный email или пароль администратора"),
            status_code=403,
        )

    normalized_url = external_url.strip().rstrip("/")
    if not normalized_url.startswith("https://"):
        return HTMLResponse(
            render_setup_page(server_settings, needs_admin_creation, "Внешний адрес должен начинаться с https://"),
            status_code=400,
        )

    server_settings.app_name = app_name.strip()
    server_settings.external_url = normalized_url
    server_settings.allow_registration = allow_registration
    server_settings.setup_completed = True
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not save server setup")
        return HTMLResponse(
            render_setup_page(server_settings, needs_admin_creation, "Не удалось сохранить настройки. Проверьте логи контейнера API."),
            status_code=500,
        )

    return RedirectResponse(url="/setup?message=saved", status_code=303)
