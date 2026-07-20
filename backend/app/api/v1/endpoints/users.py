from fastapi import APIRouter, Depends
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.schemas.user import UserInDB

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_user_me(current_user: User = Depends(RoleChecker(allowed_roles=[UserRole.STUDENT, UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER]))):
    return current_user

@router.get("/admin-only")
async def admin_only(current_user: User = Depends(RoleChecker(allowed_roles=[UserRole.ADMIN, UserRole.FOUNDER]))):
    return {"message": "Welcome, Admin/Founder"}

@router.get("/teacher-only")
async def teacher_only(current_user: User = Depends(RoleChecker(allowed_roles=[UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER]))):
    return {"message": "Welcome, Educator"}
