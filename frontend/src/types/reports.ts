// Mirrors backend/app/schemas/reports.py

export type ReportType =
  | 'students'
  | 'teachers'
  | 'schools'
  | 'attendance'
  | 'homework'
  | 'assignments'
  | 'exams'
  | 'results'
  | 'organization';

export type ExportFormat = 'pdf' | 'excel' | 'csv';

export interface ReportTypeItem {
  value: ReportType;
  label: string;
  description: string;
}

export interface ReportColumn {
  key: string;
  label: string;
}

export interface ReportSummaryItem {
  label: string;
  value: string | number | boolean | null;
}

export interface ReportBundle {
  report_type: string;
  title: string;
  scope: string;
  generated_at: string;
  summary: ReportSummaryItem[];
  columns: ReportColumn[];
  rows: Record<string, unknown>[];
}
