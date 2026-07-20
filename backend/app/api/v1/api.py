from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    student_memory,
    learning_engine,
    teacher_insights,
    principal_analytics,
    mentor,
    teacher_ai,
    parent_ai,
    principal_ai,
    principal,
    academic,
    attendance,
    homework,
    exams,
    notifications,
    calendar,
    founder,
    founder_analytics,
    founder_ai,
    reports,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(student_memory.router, prefix="/memory", tags=["ai-memory"])
api_router.include_router(learning_engine.router, prefix="/learning", tags=["ai-learning-engine"])
api_router.include_router(teacher_insights.router, prefix="/teacher-insights", tags=["teacher-insights"])
api_router.include_router(principal_analytics.router, prefix="/principal-analytics", tags=["principal-analytics"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["ai-mentor"])
api_router.include_router(teacher_ai.router, prefix="/teacher", tags=["teacher-ai"])
api_router.include_router(parent_ai.router, prefix="/parent", tags=["parent-ai"])
api_router.include_router(principal_ai.router, prefix="/principal", tags=["principal-ai"])
api_router.include_router(principal.router, prefix="/principal", tags=["principal-management"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(homework.router, prefix="/homework", tags=["homework"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(founder.router, prefix="/founder", tags=["founder-management"])
api_router.include_router(founder_analytics.router, prefix="/founder-analytics", tags=["founder-analytics"])
api_router.include_router(founder_ai.router, prefix="/founder-ai", tags=["founder-ai"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
