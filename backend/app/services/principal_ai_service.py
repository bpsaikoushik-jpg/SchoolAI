from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_client, AIClient
from app.ai import prompts
from app.services.principal_analytics_service import PrincipalAnalyticsService
from app.services.prediction_engine_service import PredictionEngineService

ATTENDANCE_RISK_THRESHOLD = 75.0
SCORE_RISK_THRESHOLD = 55.0


class PrincipalAIService:
    """School-wide AI analytics: bundles PrincipalAnalyticsService output,
    flags at-risk classes/subjects, and produces an AI-written executive
    summary + recommended actions."""

    def __init__(self, db: AsyncSession, ai_client: Optional[AIClient] = None):
        self.db = db
        self.analytics = PrincipalAnalyticsService(db)
        self.predictions = PredictionEngineService(db)
        self.ai = ai_client or get_ai_client()

    async def _detect_risks(self, school_id: UUID, class_performance: list) -> list[dict]:
        risks = []
        for c in class_performance:
            if c.get("average_score") is not None and c["average_score"] < SCORE_RISK_THRESHOLD:
                risks.append({
                    "type": "class_low_performance",
                    "class_id": c["class_id"],
                    "class_name": c["class_name"],
                    "average_score": c["average_score"],
                })
        school_prediction = await self.predictions.predict_school_performance(school_id)
        if school_prediction.get("predicted_average_score") is not None and school_prediction["predicted_average_score"] < SCORE_RISK_THRESHOLD:
            risks.append({"type": "school_predicted_decline", **school_prediction})
        return risks

    async def full_analytics(self, school_id: UUID) -> dict:
        school_performance = await self.analytics.school_performance(school_id)
        class_performance = await self.analytics.class_performance(school_id)
        subject_performance = await self.analytics.subject_performance(school_id)
        teacher_performance = await self.analytics.teacher_performance(school_id)
        ai_usage = await self.analytics.ai_usage_stats(school_id)
        risks = await self._detect_risks(school_id, class_performance)

        payload = {
            "school_performance": school_performance,
            "class_performance": class_performance,
            "subject_performance": subject_performance,
            "teacher_performance": teacher_performance,
            "ai_usage": ai_usage,
            "risk_flags": risks,
        }

        messages = prompts.principal_ai_recommendations_messages(payload)
        completion = await self.ai.complete(messages, temperature=0.5)

        return {
            "data": payload,
            "ai_recommendations": completion.content,
        }
