import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from ..models import User
from ..repositories.operations_repo import add_client_operation, get_client_operation


def normalize_client_operation_id(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def replay_client_operation(db: Session, user: User, client_operation_id: str | None):
    client_operation_id = normalize_client_operation_id(client_operation_id)
    if client_operation_id is None:
        return None
    operation = get_client_operation(db, user.id, client_operation_id)
    if operation is None:
        return None
    return json.loads(operation.response_json)


def remember_client_operation(
    db: Session,
    user: User,
    client_operation_id: str | None,
    operation_type: str,
    response,
    temp_id: str | int | None = None,
    resource_id: int | None = None,
) -> None:
    client_operation_id = normalize_client_operation_id(client_operation_id)
    if client_operation_id is None:
        return
    add_client_operation(
        db,
        user_id=user.id,
        client_operation_id=client_operation_id,
        operation_type=operation_type,
        temp_id="" if temp_id is None else str(temp_id),
        resource_id=resource_id,
        response_json=json.dumps(jsonable_encoder(response), ensure_ascii=False),
    )
