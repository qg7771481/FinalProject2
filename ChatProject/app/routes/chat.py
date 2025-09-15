from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from app.models.user import User
from app.models.chat import Message
from app.schemas.chat import MessageCreate, MessageRead
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/send",
    response_model=MessageRead,
    summary="Відправити повідомлення",
    description="""
Надсилає повідомлення від **поточного авторизованого користувача** іншому користувачу.

- Перевіряє, чи існує отримувач (`receiver_id`).
- Якщо отримувача не знайдено — повертає помилку `404`.
- Якщо все добре — створює повідомлення і повертає його дані.
""",
    responses={
        200: {
            "description": "Повідомлення успішно надіслано",
            "model": MessageRead
        },
        401: {"description": "Неавторизований запит (немає або неправильний токен)"},
        404: {"description": "Отримувача не знайдено"},
    },
)
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


@router.get(
    "/messages/{user_id}",
    response_model=list[MessageRead],
    summary="Отримати історію повідомлень з користувачем",
    description="""
Повертає список усіх повідомлень між **поточним користувачем** та користувачем з `user_id`.

- Повертає повідомлення у хронологічному порядку (`timestamp`).
- Не включає повідомлення, що не стосуються цих двох користувачів.
""",
    responses={
        200: {
            "description": "Список повідомлень між користувачами",
            "model": list[MessageRead]
        },
        401: {"description": "Неавторизований запит (немає або неправильний токен)"},
        404: {"description": "Повідомлень з цим користувачем не знайдено (повертає порожній список)"},
    },
)
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
