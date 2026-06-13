from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ClientOperation


def get_client_operation(db: Session, user_id: int, client_operation_id: str) -> ClientOperation | None:
    return db.scalar(
        select(ClientOperation).where(
            ClientOperation.user_id == user_id,
            ClientOperation.client_operation_id == client_operation_id,
        )
    )


def add_client_operation(
    db: Session,
    user_id: int,
    client_operation_id: str,
    operation_type: str,
    response_json: str,
    temp_id: str = "",
    resource_id: int | None = None,
) -> None:
    db.add(
        ClientOperation(
            user_id=user_id,
            client_operation_id=client_operation_id,
            operation_type=operation_type,
            temp_id=temp_id,
            resource_id=resource_id,
            response_json=response_json,
        )
    )
