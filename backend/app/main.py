from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .database import Base, engine, get_db
from .models import ListMember, ShoppingItem, ShoppingList, User
from .schemas import (
    AuthRequest,
    ItemCreate,
    ItemUpdate,
    ListCreate,
    ShareRequest,
    SyncResponse,
    TokenResponse,
)
from .security import create_access_token, get_current_user, hash_password, verify_password


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping List Sync API", version="0.1.0")


def require_list_access(db: Session, user: User, list_id: int) -> ShoppingList:
    shopping_list = db.scalar(
        select(ShoppingList)
        .join(ListMember, ListMember.list_id == ShoppingList.id)
        .where(ShoppingList.id == list_id, ListMember.user_id == user.id)
    )
    if shopping_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return shopping_list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=TokenResponse)
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email or password")
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/sync", response_model=SyncResponse)
def sync(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lists = db.scalars(
        select(ShoppingList)
        .join(ListMember, ListMember.list_id == ShoppingList.id)
        .where(ListMember.user_id == current_user.id)
        .options(selectinload(ShoppingList.items))
        .order_by(ShoppingList.updated_at.desc())
    ).all()
    return {"lists": lists}


@app.post("/lists")
def create_list(payload: ListCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    shopping_list = ShoppingList(name=payload.name, owner_id=current_user.id)
    db.add(shopping_list)
    db.flush()
    db.add(ListMember(list_id=shopping_list.id, user_id=current_user.id))
    db.commit()
    return {"id": shopping_list.id, "name": shopping_list.name}


@app.post("/lists/{list_id}/share")
def share_list(
    list_id: int,
    payload: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = require_list_access(db, current_user, list_id)
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not db.scalar(select(ListMember).where(ListMember.list_id == shopping_list.id, ListMember.user_id == user.id)):
        db.add(ListMember(list_id=shopping_list.id, user_id=user.id))
        db.commit()
    return {"status": "shared"}


@app.post("/lists/{list_id}/items")
def create_item(
    list_id: int,
    payload: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_list_access(db, current_user, list_id)
    item = ShoppingItem(list_id=list_id, name=payload.name, quantity=payload.quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/items/{item_id}")
def update_item(
    item_id: int,
    payload: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(ShoppingItem).where(ShoppingItem.id == item_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    require_list_access(db, current_user, item.list_id)
    update = payload.model_dump(exclude_unset=True)
    for key, value in update.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/items/{item_id}")
def delete_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(ShoppingItem).where(ShoppingItem.id == item_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    require_list_access(db, current_user, item.list_id)
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
