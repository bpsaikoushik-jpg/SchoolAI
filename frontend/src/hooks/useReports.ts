import { useMutation, useQuery } from '@tanstack/react-query';
import { fetchReportTypes, fetchReport, downloadReportExport } from '../services/reports.service';
import type { ReportType, ExportFormat } from '../types/reports';

export function useReportTypes() {
  return useQuery({ queryKey: ['reports', 'types'], queryFn: fetchReportTypes });
}

export function useReport(reportType: ReportType | null) {
  return useQuery({
    queryKey: ['reports', reportType],
    queryFn: () => fetchReport(reportType as ReportType),
    enabled: reportType !== null,
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: ({ reportType, format }: { reportType: ReportType; format: ExportFormat }) =>
      downloadReportExport(reportType, format),
  });
}
