import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id
from app.models.user import UserRole, User
from app.services.ai_mentor_service import AIMentorService
from app.services.memory_update_service import MemoryUpdateService
from app.services.prediction_engine_service import PredictionEngineService
from app.services.recommendation_engine_service import RecommendationEngineService
from app.repositories.memory import RecommendationRepository
from app.schemas.mentor import MentorChatRequest, MentorChatResponse, MentorQuizRequest, MentorFlashcardRequest
from app.schemas.memory import ConversationMemoryOut, RecommendationOut

router = APIRouter()

all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=MentorChatResponse)
async def mentor_chat(
    payload: MentorChatRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    student_id = await resolve_target_student_id(payload.student_id, db, user)

    mentor = AIMentorService(db)
    result = await mentor.chat(
        student_id=student_id,
        question=payload.message,
        subject=payload.subject,
        subject_id=payload.subject_id,
        topic=payload.topic,
        mode=payload.mode,
    )

    memory_update = MemoryUpdateService(db)
    await memory_update.log_interaction(
        student_id, payload.message, result["response"], payload.subject_id, payload.topic
    )
    # Heavier re-aggregation (profile/weakness recompute, plan regeneration,
    # weekly/monthly rollups) doesn't need to block the response.
    background_tasks.add_task(memory_update.refresh_profiles_and_recommendations, student_id)
    background_tasks.add_task(memory_update.bump_daily_progress, student_id, payload.subject, payload.topic)

    return result


@router.post("/stream")
async def mentor_stream(
    payload: MentorChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    student_id = await resolve_target_student_id(payload.student_id, db, user)
    mentor = AIMentorService(db)
    memory_update = MemoryUpdateService(db)

    async def event_generator():
        collected = []
        async for chunk in mentor.stream_chat(student_id, payload.message, payload.subject, payload.topic, payload.mode):
            collected.append(chunk)
            yield f"data: {json.dumps({'delta': chunk})}\n\n"

        full_response = "".join(collected)
        await memory_update.log_interaction(student_id, payload.message, full_response, payload.subject_id, payload.topic)
        await memory_update.bump_daily_progress(student_id, payload.subject, payload.topic)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# History / recommendations
# ---------------------------------------------------------------------------
@router.get("/history", response_model=list[ConversationMemoryOut])
async def mentor_history(
    student_id: Optional[UUID] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    from app.services.student_memory_service import StudentMemoryService
    return await StudentMemoryService(db).get_conversations(target, limit)


@router.get("/recommendations", response_model=list[RecommendationOut])
async def mentor_recommendations(
    student_id: Optional[UUID] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await RecommendationRepository(db).get_by_student(target, type)


# ---------------------------------------------------------------------------
# Study / revision plans (AI-narrated on top of the Recommendation Engine)
# ---------------------------------------------------------------------------
@router.get("/study-plan")
async def mentor_study_plan(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await AIMentorService(db).study_plan_with_narrative(target)


@router.get("/revision-plan")
async def mentor_revision_plan(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await AIMentorService(db).revision_plan_with_narrative(target)


@router.get("/motivation")
async def mentor_motivation(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return {"message": await AIMentorService(db).motivation_message(target)}


@router.get("/daily-goal")
async def mentor_daily_goal(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await AIMentorService(db).daily_learning_goal(target)


# ---------------------------------------------------------------------------
# Quiz generation
# ---------------------------------------------------------------------------
@router.post("/quiz")
async def mentor_quiz(
    payload: MentorQuizRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(payload.student_id, db, user)
    return await AIMentorService(db).generate_quiz(target, payload.subject, payload.topic, payload.num_questions, payload.difficulty)


@router.post("/flashcards")
async def mentor_flashcards(
    payload: MentorFlashcardRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(payload.student_id, db, user)
    return await AIMentorService(db).generate_flashcards(target, payload.subject, payload.topic, payload.count)


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------
@router.get("/predictions")
async def mentor_predictions(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await PredictionEngineService(db).student_prediction_bundle(target)
