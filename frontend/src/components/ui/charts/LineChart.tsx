import { useId } from 'react';

export interface LineChartDatum {
  label: string;
  value: number;
}

interface LineChartProps {
  data: LineChartDatum[];
  height?: number;
  tint?: string;
}

// Small dependency-free line/area chart, sized for dashboard cards.
export function LineChart({ data, height = 200, tint = 'var(--color-brand-500)' }: LineChartProps) {
  const gradId = useId();
  const width = 600;
  const padY = 16;
  const max = Math.max(...data.map((d) => d.value), 1);
  const min = Math.min(...data.map((d) => d.value), 0);
  const range = max - min || 1;
  const stepX = width / Math.max(data.length - 1, 1);

  const points = data.map((d, i) => {
    const x = i * stepX;
    const y = padY + (1 - (d.value - min) / range) * (height - padY * 2);
    return [x, y] as const;
  });

  const linePath = points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x},${y}`).join(' ');
  const areaPath = `${linePath} L${width},${height} L0,${height} Z`;

  return (
    <div className="w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ height }} preserveAspectRatio="none">
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={tint} stopOpacity="0.35" />
            <stop offset="100%" stopColor={tint} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={areaPath} fill={`url(#${gradId})`} stroke="none" />
        <path d={linePath} fill="none" stroke={tint} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        {points.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={3.5} fill="var(--surface-raised)" stroke={tint} strokeWidth={2} />
        ))}
      </svg>
      <div className="mt-1 flex justify-between text-[11px] text-text-muted">
        {data.map((d) => <span key={d.label}>{d.label}</span>)}
      </div>
    </div>
  );
}
