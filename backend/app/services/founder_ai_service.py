from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_client, AIClient
from app.ai import prompts
from app.services.founder_analytics_service import FounderAnalyticsService

SCORE_RISK_THRESHOLD = 55.0


class FounderAIService:
    """Organization-wide AI analytics for the Founder Portal. Mirrors
    PrincipalAIService's pattern (bundle analytics, flag risks, produce an
    AI-written executive summary) but scoped across every school instead
    of a single one."""

    def __init__(self, db: AsyncSession, ai_client: Optional[AIClient] = None):
        self.db = db
        self.analytics = FounderAnalyticsService(db)
        self.ai = ai_client or get_ai_client()

    def _detect_risks(self, school_performance: list) -> list[dict]:
        risks = []
        for s in school_performance:
            if s.get("average_score") is not None and s["average_score"] < SCORE_RISK_THRESHOLD:
                risks.append({
                    "type": "school_low_performance",
                    "school_id": s["school_id"],
                    "school_name": s["school_name"],
                    "average_score": s["average_score"],
                })
        return risks

    async def full_analytics(self) -> dict:
        org_overview = await self.analytics.org_overview()
        school_performance = await self.analytics.school_performance()
        role_breakdown = await self.analytics.role_breakdown()
        attendance_today = await self.analytics.attendance_overview()
        risks = self._detect_risks(school_performance)

        payload = {
            "org_overview": org_overview,
            "school_performance": school_performance,
            "role_breakdown": role_breakdown,
            "attendance_today": attendance_today,
            "risk_flags": risks,
        }

        messages = prompts.founder_ai_recommendations_messages(payload)
        completion = await self.ai.complete(messages, temperature=0.5)

        return {
            "data": payload,
            "ai_recommendations": completion.content,
        }
