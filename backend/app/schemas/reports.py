from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel


class ReportType(str, Enum):
    """Every report the Reports module can produce. `assignments` and
    `homework` intentionally resolve to the same builder (Homework *is*
    the assignments model in this schema - see AssignmentSubmission on
    the Homework model), and `results` resolves to the same builder as
    `exams` (Result rows are already folded into the exams rollup used
    by both the Principal and Founder analytics pages)."""

    STUDENTS = "students"
    TEACHERS = "teachers"
    SCHOOLS = "schools"
    ATTENDANCE = "attendance"
    HOMEWORK = "homework"
    ASSIGNMENTS = "assignments"
    EXAMS = "exams"
    RESULTS = "results"
    ORGANIZATION = "organization"


class ExportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportTypeOut(BaseModel):
    value: str
    label: str
    description: str


class ReportColumn(BaseModel):
    key: str
    label: str


class ReportSummaryItem(BaseModel):
    label: str
    value: Any


class ReportBundleOut(BaseModel):
    report_type: str
    title: str
    scope: str  # "organization" (Founder/Admin) or a school name (Principal)
    generated_at: datetime
    summary: List[ReportSummaryItem] = []
    columns: List[ReportColumn]
    rows: List[Dict[str, Any]]
