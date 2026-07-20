export interface BarChartDatum {
  label: string;
  value: number;
}

interface BarChartProps {
  data: BarChartDatum[];
  height?: number;
  tint?: string;
  valueSuffix?: string;
}

// Small dependency-free bar chart, sized for dashboard cards.
export function BarChart({ data, height = 220, tint = 'var(--color-brand-500)', valueSuffix = '' }: BarChartProps) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="w-full" style={{ height }}>
      <div className="flex h-full items-end gap-3">
        {data.map((d) => {
          const pct = (d.value / max) * 100;
          return (
            <div key={d.label} className="group flex flex-1 flex-col items-center gap-2">
              <div className="relative flex w-full flex-1 items-end justify-center">
                <span className="pointer-events-none absolute -top-6 rounded-md bg-overlay px-1.5 py-0.5 text-[11px] font-medium text-text-primary opacity-0 shadow-md transition-opacity group-hover:opacity-100">
                  {d.value}{valueSuffix}
                </span>
                <div
                  className="w-full rounded-t-lg transition-all duration-500"
                  style={{ height: `${pct}%`, minHeight: 4, background: `linear-gradient(180deg, ${tint}, color-mix(in srgb, ${tint} 35%, transparent))` }}
                />
              </div>
              <span className="text-[11px] text-text-muted">{d.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
