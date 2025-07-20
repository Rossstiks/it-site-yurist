from typing import Optional, Any
import json
from sqlalchemy.orm import Session
from app.models import AuditLog


def log_action(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    diff: Optional[dict[str, Any]] = None,
    actor_id: Optional[int] = None,
) -> None:
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        diff_json=json.dumps(diff) if diff else None,
        actor_id=actor_id,
    )
    db.add(log)
    db.commit()
