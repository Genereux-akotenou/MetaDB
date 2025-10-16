from typing import List, Dict, Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import json

from ..auth import require_role, get_current_user
from ..database import get_db
from ..models import UserRole, QAItem, QAStatus, User, Annotation
from ..schemas import QAOut


router = APIRouter()


@router.get("/ready", response_model=List[Dict[str, Any]])
def list_ready(_user=Depends(require_role(UserRole.provider)), db: Session = Depends(get_db)):
    items = db.query(QAItem).filter(QAItem.status == QAStatus.ready).all()
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "chunk_id": item.chunk_id_fk,
            "question": item.question,
            "answer": item.answer,
            "status": item.status.value,
            "created_at": item.created_at.isoformat()
        })
    return result


@router.get("/export/json")
def export_json(_user=Depends(require_role(UserRole.provider)), db: Session = Depends(get_db)):
    items = db.query(QAItem).filter(QAItem.status == QAStatus.ready).all()
    data = []
    for item in items:
        data.append({
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "created_at": item.created_at.isoformat()
        })
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=ready_qas.json"}
    )


@router.get("/export/csv")
def export_csv(_user=Depends(require_role(UserRole.provider)), db: Session = Depends(get_db)):
    items = db.query(QAItem).filter(QAItem.status == QAStatus.ready).all()
    csv_content = "id,question,answer,created_at\n"
    for item in items:
        csv_content += f"{item.id},\"{item.question.replace('\"', '\"\"')}\",\"{item.answer.replace('\"', '\"\"')}\",{item.created_at.isoformat()}\n"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ready_qas.csv"}
    )


