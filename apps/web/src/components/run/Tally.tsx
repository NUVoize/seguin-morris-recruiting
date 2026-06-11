'use client';

import {useEffect, useRef, useState} from 'react';

/** Count-up number — celebrates the end of a run without confetti noise. */
function CountUp({value, duration = 900}: {value: number; duration?: number}) {
  const [display, setDisplay] = useState(0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || value === 0) {
      setDisplay(value);
      return;
    }
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(Math.round(eased * value));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [value, duration]);

  return <>{display}</>;
}

export interface TallyStat {
  key: string;
  label: string;
  value: number;
  accent?: boolean;
}

/** Completion strip: big condensed numbers, small labels. */
export function Tally({stats}: {stats: TallyStat[]}) {
  return (
    <div className="sm-rise grid grid-cols-3 divide-x divide-steel-800 rounded-xl border border-steel-800 bg-steel-800/40">
      {stats.map((s) => (
        <div key={s.key} className="px-5 py-4 text-center">
          <p
            className={
              'font-display text-4xl font-bold tabular-nums ' +
              (s.accent ? 'text-ember' : 'text-steel-100')
            }
          >
            <CountUp value={s.value} />
          </p>
          <p className="mt-1 text-[11px] font-medium uppercase tracking-wider text-steel-400">
            {s.label}
          </p>
        </div>
      ))}
    </div>
  );
}
