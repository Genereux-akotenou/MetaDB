from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import UserRole, Chunk, QAItem
from ..pipeline import generate_qas_for_chunk


router = APIRouter()


@router.post("/file")
def upload_raw_file(
    f: UploadFile = File(...),
    _user=Depends(require_role(UserRole.provider)),
    db: Session = Depends(get_db),
):
    # Accept uploaded jsonl of raw chunks with fields: chunk_id, source_url, content
    if not f.filename.endswith((".jsonl", ".json")):
        raise HTTPException(status_code=400, detail="Only .jsonl or .json supported for now")
    content = f.file.read().decode("utf-8", errors="ignore")
    import json

    created, qa_created = 0, 0
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        chunk = Chunk(
            chunk_id=obj.get("chunk_id") or obj.get("id"),
            source_url=obj.get("source_url", ""),
            content=obj.get("content") or obj.get("text") or "",
        )
        if not chunk.content:
            continue
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        created += 1

        # autogenerate QAs via Ollama
        for qa in generate_qas_for_chunk(chunk.content):
            db.add(QAItem(chunk_id_fk=chunk.id, question=qa["question"], answer=qa["answer"]))
            qa_created += 1
        db.commit()

    return {"chunks": created, "qa_generated": qa_created}


