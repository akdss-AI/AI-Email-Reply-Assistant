from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user

from models.user import User
from models.session import Session as SessionModel
from models.message import Message

from schemas.message import MessageCreate, EmailReply

from services.groq import (
    draft_email_reply,
    GroqServiceError,
    GroqQuotaError,
    GroqOutputError,
    GroqScopeError,
)


router = APIRouter()


@router.post(
    "/sessions/{session_id}/messages",
    response_model=EmailReply
)
def create_message(
    session_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    try:

        # 1. Call Groq
        ai_result = draft_email_reply(
            incoming_email=message.incoming_email,
            instruction=message.instruction,
            tone=message.tone
        )

        # 2. Handle out-of-scope request
        if not ai_result.in_scope:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ai_result.refusal
                or "This service only drafts email replies."
            )

        # 3. Build public email reply 
        ai_reply = EmailReply(
            in_scope=ai_result.in_scope,
            subject=ai_result.subject,
            greeting=ai_result.greeting,
            body=ai_result.body,
            closing=ai_result.closing,
            refusal=ai_result.refusal or ""  # uses empty string if refusal is None
        )


        # 4. Create user message
        user_message = Message(
            session_id=session.id,
            role="user",
            content={
                "incoming_email": message.incoming_email,
                "instruction": message.instruction,
                "tone": message.tone
            }
        )

        # 5. Create assistant message
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=ai_reply.model_dump()
        )

        # 6. Add both
        db.add(user_message)
        db.add(assistant_message)

        # 7. Commit ONCE
        db.commit()

        db.refresh(user_message)
        db.refresh(assistant_message)

        return ai_reply

    except HTTPException:
        db.rollback()
        raise
    

    except GroqScopeError as e:
        db.rollback()

        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
         )

    except GroqQuotaError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI request limit reached. Please try again later."
        )

    except GroqOutputError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned an invalid response."
        )

    except GroqServiceError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable. Please try again later."
        )

    except Exception as e:
        db.rollback()
        print("ACTUAL MESSAGE ERROR:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
@router.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session ownership
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.id == session_id,
            SessionModel.user_id == current_user.id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages