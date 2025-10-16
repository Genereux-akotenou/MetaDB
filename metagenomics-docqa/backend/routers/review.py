from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..auth import get_current_user
from ..database import get_db
from ..models import QAItem, QAStatus, Annotation, User
from ..schemas import QAOut, AnnotationIn, AnnotationOut


router = APIRouter()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    total_qas = db.query(QAItem).count()
    pending_qas = db.query(QAItem).filter(QAItem.status == QAStatus.pending).count()
    ready_qas = db.query(QAItem).filter(QAItem.status == QAStatus.ready).count()
    rejected_qas = db.query(QAItem).filter(QAItem.status == QAStatus.rejected).count()
    
    return {
        "total": total_qas,
        "pending": pending_qas,
        "ready": ready_qas,
        "rejected": rejected_qas
    }


@router.get("/pending", response_model=List[Dict[str, Any]])
def list_pending(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    items = db.query(QAItem).filter(QAItem.status == QAStatus.pending).all()
    result = []
    for item in items:
        annotations = db.query(Annotation).filter(Annotation.qa_item_id_fk == item.id).all()
        annotators = []
        for ann in annotations:
            user = db.query(User).filter(User.id == ann.annotated_by_user_id).first()
            if user:
                annotators.append({
                    "name": user.full_name or user.email,
                    "date": ann.created_at.isoformat(),
                    "score": ann.score
                })
        
        result.append({
            "id": item.id,
            "chunk_id": item.chunk_id_fk,
            "question": item.question,
            "answer": item.answer,
            "status": item.status.value,
            "created_at": item.created_at.isoformat(),
            "annotators": annotators
        })
    return result


@router.post("/annotate", response_model=AnnotationOut)
def annotate(payload: AnnotationIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    qa = db.query(QAItem).filter(QAItem.id == payload.qa_item_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="QA not found")
    ann = Annotation(
        qa_item_id_fk=qa.id,
        edited_question=payload.edited_question,
        edited_answer=payload.edited_answer,
        score=payload.score,
        comment=payload.comment,
        validated=payload.validated,
        annotated_by_user_id=user.id,
    )
    if payload.validated and payload.score >= 0.7:
        qa.status = QAStatus.ready
    elif payload.validated and payload.score < 0.3:
        qa.status = QAStatus.rejected
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return ann


