'use client';

import clsx from 'clsx';

/**
 * Circular fit-score ring. Color encodes the band the backend already
 * uses (>=80 strong, >=50 promising, below = needs review).
 */
export function ScoreRing({
  score,
  size = 34,
  stroke = 3.5,
  className
}: {
  score: number;
  size?: number;
  stroke?: number;
  className?: string;
}) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  const offset = c * (1 - pct / 100);
  const color = pct >= 80 ? 'text-ok' : pct >= 50 ? 'text-ember' : 'text-steel-400';

  return (
    <span
      className={clsx('relative inline-flex shrink-0 items-center justify-center', className)}
      style={{width: size, height: size}}
      aria-label={`Score ${score}/100`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          className="stroke-steel-100"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className={clsx('stroke-current transition-[stroke-dashoffset] duration-700', color)}
        />
      </svg>
      <span
        className={clsx(
          'absolute font-mono font-semibold tabular-nums',
          size >= 56 ? 'text-lg' : 'text-[10.5px]',
          color
        )}
      >
        {score}
      </span>
    </span>
  );
}
