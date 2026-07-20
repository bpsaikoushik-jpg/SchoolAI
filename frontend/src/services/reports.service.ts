import api from './api';
import type { ReportType, ReportTypeItem, ReportBundle, ExportFormat } from '../types/reports';

// ---------------------------------------------------------------------------
// Reports module (Founder: organization-wide, Principal: own school)
// ---------------------------------------------------------------------------
export async function fetchReportTypes(): Promise<ReportTypeItem[]> {
  const { data } = await api.get<ReportTypeItem[]>('/reports/types');
  return data;
}

export async function fetchReport(reportType: ReportType): Promise<ReportBundle> {
  const { data } = await api.get<ReportBundle>(`/reports/${reportType}`);
  return data;
}

const EXTENSIONS: Record<ExportFormat, string> = { pdf: 'pdf', excel: 'xlsx', csv: 'csv' };

export async function downloadReportExport(reportType: ReportType, format: ExportFormat): Promise<void> {
  const { data } = await api.get(`/reports/${reportType}/export`, {
    params: { format },
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = `${reportType}-report.${EXTENSIONS[format]}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
