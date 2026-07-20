import { useState } from 'react';
import { FileText, FileSpreadsheet, Download, Loader2 } from 'lucide-react';
import { Card, CardHeader, Spinner } from '../ui';
import { useReportTypes, useExportReport } from '../../hooks/useReports';
import type { ExportFormat, ReportType } from '../../types/reports';

const FORMATS: { format: ExportFormat; label: string; icon: typeof FileText }[] = [
  { format: 'pdf', label: 'PDF', icon: FileText },
  { format: 'excel', label: 'Excel', icon: FileSpreadsheet },
  { format: 'csv', label: 'CSV', icon: Download },
];

/** Shared by the Founder and Principal "Reports Overview" pages. Reuses the
 * same /reports endpoints for both - the backend scopes rows to the caller's
 * school (Principal) or the whole organization (Founder/Admin) automatically,
 * so this component doesn't need to know which portal it's rendered in. */
export function ReportExportPanel({ accent }: { accent: string }) {
  const { data: reportTypes, isLoading } = useReportTypes();
  const exportReport = useExportReport();
  const [pending, setPending] = useState<`${ReportType}:${ExportFormat}` | null>(null);
  const [failed, setFailed] = useState<`${ReportType}:${ExportFormat}` | null>(null);

  const handleExport = (reportType: ReportType, format: ExportFormat) => {
    const key = `${reportType}:${format}` as const;
    setPending(key);
    setFailed(null);
    exportReport.mutate(
      { reportType, format },
      {
        onError: () => setFailed(key),
        onSettled: () => setPending(null),
      }
    );
  };

  return (
    <Card padded={false}>
      <div className="p-4">
        <CardHeader
          title="Export Reports"
          subtitle="Download a full report as PDF, Excel, or CSV. Data is pulled live at export time."
        />

        {isLoading ? (
          <Spinner />
        ) : (
          <div className="divide-y divide-border-subtle">
            {(reportTypes ?? []).map((rt) => (
              <div key={rt.value} className="flex flex-col gap-3 py-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-text-primary">{rt.label}</p>
                  <p className="text-xs text-text-muted">{rt.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  {FORMATS.map(({ format, label, icon: Icon }) => {
                    const key = `${rt.value}:${format}` as const;
                    const isPending = pending === key;
                    return (
                      <button
                        key={format}
                        type="button"
                        onClick={() => handleExport(rt.value, format)}
                        disabled={isPending}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-border-subtle px-3 py-1.5 text-xs font-medium text-text-primary transition-colors hover:bg-sunken/60 disabled:opacity-60"
                        style={{ borderColor: `color-mix(in srgb, ${accent} 30%, transparent)` }}
                      >
                        {isPending ? <Loader2 size={13} className="animate-spin" /> : <Icon size={13} />}
                        {label}
                      </button>
                    );
                  })}
                </div>
                {failed === `${rt.value}:pdf` || failed === `${rt.value}:excel` || failed === `${rt.value}:csv` ? (
                  <p className="text-xs text-red-500 sm:hidden">Export failed. Try again.</p>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
