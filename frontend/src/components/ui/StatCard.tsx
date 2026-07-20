import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Card } from './Card';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: { value: string; direction: 'up' | 'down' };
  tint?: string; // e.g. 'var(--color-role-student)'
  index?: number;
}

export function StatCard({ label, value, icon: Icon, trend, tint, index = 0 }: StatCardProps) {
  const accent = tint ?? 'var(--color-brand-500)';
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.35 }}
    >
      <Card className="relative overflow-hidden">
        <div
          className="absolute inset-x-0 top-0 h-0.5"
          style={{ background: accent }}
        />
        <div className="flex items-start justify-between">
          <div
            className="grid h-10 w-10 place-items-center rounded-xl"
            style={{ background: `color-mix(in srgb, ${accent} 14%, transparent)`, color: accent }}
          >
            <Icon size={20} />
          </div>
          {trend && (
            <span
              className={cn(
                'inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium',
                trend.direction === 'up'
                  ? 'bg-emerald-500/10 text-emerald-500'
                  : 'bg-rose-500/10 text-rose-500'
              )}
            >
              {trend.direction === 'up' ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
              {trend.value}
            </span>
          )}
        </div>
        <p className="mt-4 text-sm font-medium text-text-secondary">{label}</p>
        <p className="mt-1 text-2xl font-semibold tracking-tight text-text-primary">{value}</p>
      </Card>
    </motion.div>
  );
}
