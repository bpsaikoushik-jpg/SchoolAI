from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.founder_service import FounderService
from app.services.founder_analytics_service import FounderAnalyticsService
from app.schemas.founder import (
    SchoolManageOut, SchoolCreateInput, SchoolUpdateInput,
    OrgOverviewOut, RoleBreakdownItem, OrgUserOut,
)

router = APIRouter()

# Founder Portal is platform-wide oversight, not school-scoped, so it's
# gated to Founder/Admin only (Principal is intentionally excluded, same
# as every other school-scoped role is excluded from Principal endpoints).
founder_roles = RoleChecker([UserRole.FOUNDER, UserRole.ADMIN])


# ---------------------------------------------------------------------------
# School management (list / create / edit / activate / deactivate)
# ---------------------------------------------------------------------------
@router.get("/schools", response_model=List[SchoolManageOut])
async def list_schools(
    search: Optional[str] = Query(None),
    include_inactive: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).list_schools(search, include_inactive)


@router.post("/schools", response_model=SchoolManageOut, status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: SchoolCreateInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).create_school(payload)


@router.get("/schools/{school_id}", response_model=SchoolManageOut)
async def get_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).get_school(school_id)


@router.patch("/schools/{school_id}", response_model=SchoolManageOut)
async def update_school(
    school_id: UUID,
    payload: SchoolUpdateInput,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).update_school(school_id, payload)


@router.post("/schools/{school_id}/activate", response_model=SchoolManageOut)
async def activate_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).activate_school(school_id)


@router.post("/schools/{school_id}/deactivate", response_model=SchoolManageOut)
async def deactivate_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).deactivate_school(school_id)


# ---------------------------------------------------------------------------
# Organization overview
# ---------------------------------------------------------------------------
@router.get("/overview", response_model=OrgOverviewOut)
async def org_overview(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).org_overview()


@router.get("/user-breakdown", response_model=List[RoleBreakdownItem])
async def user_breakdown(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).role_breakdown()


# ---------------------------------------------------------------------------
# Org-wide user directory (audience for broadcasts / user listing)
# ---------------------------------------------------------------------------
@router.get("/users", response_model=List[OrgUserOut])
async def list_org_users(
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, le=1000),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderService(db).list_users(role, search, skip, limit)
