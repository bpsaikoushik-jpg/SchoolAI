from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.school import School
from app.models.user import User, UserRole
from app.services.principal_analytics_service import PrincipalAnalyticsService


class FounderService:
    """Backs the Founder Portal's platform-wide school management: list,
    create, edit, activate/deactivate every school on the platform, plus
    the org-wide user directory. Deliberately reuses what already exists
    rather than adding new concepts:

    - "Active" reuses School's existing AuditMixin soft-delete
      (deleted_at is None) instead of a new is_active column.
    - Per-school stats reuse PrincipalAnalyticsService.school_performance,
      the same method the Principal Portal already calls.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics = PrincipalAnalyticsService(db)

    # -----------------------------------------------------------------
    # Schools
    # -----------------------------------------------------------------
    async def list_schools(self, search: Optional[str] = None, include_inactive: bool = True) -> List[dict]:
        query = select(School)
        if not include_inactive:
            query = query.where(School.deleted_at.is_(None))
        if search:
            like = f"%{search.lower()}%"
            query = query.where(func.lower(School.name).like(like))
        query = query.order_by(School.name)
        schools = (await self.db.execute(query)).scalars().all()

        results = []
        for school in schools:
            perf = await self.analytics.school_performance(school.id)
            results.append(self._to_manage_out(school, perf))
        return results

    async def get_school(self, school_id: UUID) -> dict:
        school = await self._get(school_id)
        perf = await self.analytics.school_performance(school_id)
        return self._to_manage_out(school, perf)

    async def create_school(self, payload) -> dict:
        existing = (await self.db.execute(select(School).where(func.lower(School.name) == payload.name.lower()))).scalars().first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A school with this name already exists")

        school = School(name=payload.name, address=payload.address, phone=payload.phone, website=payload.website)
        self.db.add(school)
        await self.db.commit()
        await self.db.refresh(school)

        if payload.principal_email and payload.principal_password:
            existing_user = (await self.db.execute(select(User).where(User.email == payload.principal_email))).scalars().first()
            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")
            principal = User(
                email=payload.principal_email,
                hashed_password=get_password_hash(payload.principal_password),
                full_name=payload.principal_full_name or f"{school.name} Principal",
                role=UserRole.PRINCIPAL,
                school_id=school.id,
            )
            self.db.add(principal)
            await self.db.commit()

        perf = await self.analytics.school_performance(school.id)
        return self._to_manage_out(school, perf)

    async def update_school(self, school_id: UUID, payload) -> dict:
        school = await self._get(school_id)
        data = payload.model_dump(exclude_unset=True)
        for field in ("name", "address", "phone", "website"):
            if field in data:
                setattr(school, field, data[field])
        await self.db.commit()
        await self.db.refresh(school)
        perf = await self.analytics.school_performance(school_id)
        return self._to_manage_out(school, perf)

    async def deactivate_school(self, school_id: UUID) -> dict:
        school = await self._get(school_id)
        school.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(school)
        perf = await self.analytics.school_performance(school_id)
        return self._to_manage_out(school, perf)

    async def activate_school(self, school_id: UUID) -> dict:
        school = await self._get(school_id)
        school.deleted_at = None
        await self.db.commit()
        await self.db.refresh(school)
        perf = await self.analytics.school_performance(school_id)
        return self._to_manage_out(school, perf)

    async def _get(self, school_id: UUID) -> School:
        # Deliberately not filtering on deleted_at here: Founder must be
        # able to look up, edit, and reactivate an inactive school too.
        school = (await self.db.execute(select(School).where(School.id == school_id))).scalars().first()
        if not school:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
        return school

    def _to_manage_out(self, school: School, perf: dict) -> dict:
        return {
            "id": school.id,
            "name": school.name,
            "address": school.address,
            "phone": school.phone,
            "website": school.website,
            "is_active": school.deleted_at is None,
            "created_at": school.created_at,
            "total_students": perf["total_students"],
            "total_teachers": perf["total_teachers"],
            "total_classes": perf["total_classes"],
            "average_score": perf["average_score"],
        }

    # -----------------------------------------------------------------
    # Org-wide user directory (audience for broadcasts, user listing)
    # -----------------------------------------------------------------
    async def list_users(
        self, role: Optional[UserRole] = None, search: Optional[str] = None, skip: int = 0, limit: int = 200,
    ) -> List[dict]:
        query = select(User, School).outerjoin(School, User.school_id == School.id).where(User.deleted_at.is_(None))
        if role:
            query = query.where(User.role == role)
        if search:
            like = f"%{search.lower()}%"
            query = query.where(func.lower(User.full_name).like(like) | func.lower(User.email).like(like))
        query = query.order_by(User.full_name).offset(skip).limit(limit)
        rows = (await self.db.execute(query)).all()

        return [
            {
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "school_id": u.school_id,
                "school_name": s.name if s else None,
            }
            for u, s in rows
        ]
