from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from app.models.user import User
from app.models.chat import Message
from app.schemas.chat import MessageCreate, MessageRead
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=MessageRead, summary="Відправити повідомлення")
def send_message(
        msg: MessageCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    receiver = db.query(User).filter(User.id == msg.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    message = Message(
        sender_id=current_user.id,
        receiver_id=msg.receiver_id,
        content=msg.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageRead(id=message.id, sender_id=message.sender_id, receiver_id=message.receiver_id,
                       timestamp=message.timestamp, content=message.content)


@router.get("/messages/{user_id}", response_model=list[MessageRead],
            summary="Отримати історію повідомлень з користувачем")
def get_messages(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    return [MessageRead(id=message.id, sender_id=message.sender_id, receiver_id=message.receiver_id,
                        content=message.content, timestamp=message.timestamp) for message in messages]
