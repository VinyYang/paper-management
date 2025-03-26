from sqlalchemy.orm import Session
from ..models import Note
from typing import List, Optional
from ..schemas.note import NoteCreate, NoteUpdate

def create_note(db: Session, note: NoteCreate, user_id: int) -> Note:
    db_note = Note(**note.dict(), user_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note(db: Session, note_id: int) -> Optional[Note]:
    return db.query(Note).filter(Note.id == note_id).first()

def get_user_notes(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    paper_id: Optional[int] = None
) -> List[Note]:
    query = db.query(Note).filter(Note.user_id == user_id)
    if paper_id:
        query = query.filter(Note.paper_id == paper_id)
    return query.offset(skip).limit(limit).all()

def update_note(db: Session, note_id: int, note: NoteUpdate) -> Optional[Note]:
    db_note = get_note(db, note_id)
    if not db_note:
        return None
    
    update_data = note.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> bool:
    db_note = get_note(db, note_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True

def get_public_notes(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Note]:
    return db.query(Note).filter(Note.is_public == True).offset(skip).limit(limit).all() 