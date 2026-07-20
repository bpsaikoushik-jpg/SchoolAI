import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.report_service import ReportService
from app.schemas.reports import ReportType, ExportFormat, ReportBundleOut, ReportTypeOut

logger = logging.getLogger("schoolai.reports")

router = APIRouter()

# Reports are available to organization-wide oversight roles (Founder/Admin)
# and to Principals for their own school - the same pair of scopes every
# other dual-scope module in this codebase (Founder/Principal analytics,
# Founder/Principal reports overview pages) already supports.
report_roles = RoleChecker([UserRole.FOUNDER, UserRole.ADMIN, UserRole.PRINCIPAL])

_MEDIA_TYPES = {
    ExportFormat.PDF: "application/pdf",
    ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.CSV: "text/csv",
}
_EXTENSIONS = {
    ExportFormat.PDF: "pdf",
    ExportFormat.EXCEL: "xlsx",
    ExportFormat.CSV: "csv",
}


@router.get("/types", response_model=list[ReportTypeOut])
async def list_report_types(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(report_roles),
):
    return ReportService(db).available_report_types(user)


@router.get("/{report_type}", response_model=ReportBundleOut)
async def get_report(
    report_type: ReportType,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(report_roles),
):
    return await ReportService(db).build_report(report_type, user)


@router.get("/{report_type}/export")
async def export_report(
    report_type: ReportType,
    format: ExportFormat,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(report_roles),
):
    service = ReportService(db)
    bundle = await service.build_report(report_type, user)

    try:
        if format == ExportFormat.PDF:
            content = service.to_pdf(bundle)
        elif format == ExportFormat.EXCEL:
            content = service.to_excel(bundle)
        else:
            content = service.to_csv(bundle)
    except Exception:
        logger.exception("Failed to render %s report as %s", report_type.value, format.value)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate the export. Please try again.",
        )

    filename = f"{report_type.value}-report.{_EXTENSIONS[format]}"
    return Response(
        content=content,
        media_type=_MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
