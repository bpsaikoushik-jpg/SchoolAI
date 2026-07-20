from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import TokenPayload
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).where(User.email == token_data.sub))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return user


async def get_own_student_profile_id(db: AsyncSession, user: User):
    """Resolve the StudentProfile.id that belongs to this user, or None."""
    from app.models.profiles import StudentProfile
    result = await db.execute(select(StudentProfile.id).where(StudentProfile.user_id == user.id))
    row = result.first()
    return row[0] if row else None


async def get_own_parent_profile_id(db: AsyncSession, user: User):
    from app.models.profiles import ParentProfile
    result = await db.execute(select(ParentProfile.id).where(ParentProfile.user_id == user.id))
    row = result.first()
    return row[0] if row else None


async def get_own_teacher_profile_id(db: AsyncSession, user: User):
    from app.models.profiles import TeacherProfile
    result = await db.execute(select(TeacherProfile.id).where(TeacherProfile.user_id == user.id))
    row = result.first()
    return row[0] if row else None


async def authorize_student_data_access(
    student_id,
    db: AsyncSession,
    user: User,
) -> None:
    """Enforces the SchoolAI data-access rule for anything scoped to a
    single student: Students -> own data only. Parents -> own children
    only. Teachers/Principal/Admin/Founder -> as already trusted elsewhere
    in this codebase (role-gated, not per-student ownership-gated - matching
    the existing Teacher Insights / Principal Analytics endpoints)."""
    if user.role == UserRole.STUDENT:
        own_id = await get_own_student_profile_id(db, user)
        if own_id is None or own_id != student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only access their own data")
        return

    if user.role == UserRole.PARENT:
        from app.repositories.family import ParentStudentLinkRepository
        parent_id = await get_own_parent_profile_id(db, user)
        if parent_id is None or not await ParentStudentLinkRepository(db).is_linked(parent_id, student_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parents can only access their own children's data")
        return

    if user.role in (UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER):
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


async def resolve_target_student_id(student_id, db: AsyncSession, user: User):
    """Used by AI Mentor / Prediction endpoints where student_id is optional
    in the request body/query (students default to themselves)."""
    if student_id is None:
        if user.role == UserRole.STUDENT:
            own_id = await get_own_student_profile_id(db, user)
            if own_id is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student profile found for this account")
            return own_id
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="student_id is required for this role")

    await authorize_student_data_access(student_id, db, user)
    return student_id
