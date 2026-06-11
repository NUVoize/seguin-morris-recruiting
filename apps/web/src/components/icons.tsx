import type {SVGProps} from 'react';
import type {AgentType} from '@/lib/api';

/**
 * Monoline icon set — single 1.7px stroke, 24px grid.
 * Hand-rolled so we add zero dependencies. Consistent with the
 * industrial console identity (no emojis anywhere).
 */

type IconProps = SVGProps<SVGSVGElement> & {size?: number};

function Base({size = 16, children, ...rest}: IconProps & {children: React.ReactNode}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      {...rest}
    >
      {children}
    </svg>
  );
}

export function IconRadar(p: IconProps) {
  return (
    <Base {...p}>
      <circle cx="11" cy="11" r="7" />
      <path d="m21 21-4.3-4.3" />
      <circle cx="11" cy="11" r="2.5" />
    </Base>
  );
}

export function IconSchool(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M2.5 9.5 12 4.5l9.5 5L12 14.5z" />
      <path d="M6.5 12v5c0 1.2 2.5 2.5 5.5 2.5s5.5-1.3 5.5-2.5v-5" />
      <path d="M21.5 9.5V15" />
    </Base>
  );
}

export function IconFunnel(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M3.5 4.5h17l-6.5 8v6l-4 2v-8z" />
    </Base>
  );
}

export function IconShield(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M12 3.5 5 6v5.5c0 4.4 3 7.6 7 9 4-1.4 7-4.6 7-9V6z" />
      <path d="m9 11.5 2.2 2.2L15.5 9" />
    </Base>
  );
}

export function IconTarget(p: IconProps) {
  return (
    <Base {...p}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </Base>
  );
}

export function IconArrowRight(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M4 12h16" />
      <path d="m14 6 6 6-6 6" />
    </Base>
  );
}

export function IconPin(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z" />
      <circle cx="12" cy="10" r="2.5" />
    </Base>
  );
}

export function IconMail(p: IconProps) {
  return (
    <Base {...p}>
      <rect x="3" y="5.5" width="18" height="13" rx="2" />
      <path d="m3.5 7 8.5 6 8.5-6" />
    </Base>
  );
}

export function IconPhone(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M5 4h4l1.5 4.5-2.2 1.6a13 13 0 0 0 5.6 5.6l1.6-2.2L20 15v4a1.5 1.5 0 0 1-1.6 1.5C10.3 19.9 4.1 13.7 3.5 5.6A1.5 1.5 0 0 1 5 4z" />
    </Base>
  );
}

export function IconLink(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M10 14a4.5 4.5 0 0 0 6.4.4l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.4 1.4" />
      <path d="M14 10a4.5 4.5 0 0 0-6.4-.4l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.4-1.4" />
    </Base>
  );
}

export function IconCheck(p: IconProps) {
  return (
    <Base {...p}>
      <path d="m4.5 12.5 5 5L19.5 7" />
    </Base>
  );
}

export function IconClock(p: IconProps) {
  return (
    <Base {...p}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7v5.2l3.4 2" />
    </Base>
  );
}

export function IconX(p: IconProps) {
  return (
    <Base {...p}>
      <path d="m6 6 12 12M18 6 6 18" />
    </Base>
  );
}

export function IconBolt(p: IconProps) {
  return (
    <Base {...p}>
      <path d="M13 2.5 4.5 13.5H11l-1 8 8.5-11H12z" />
    </Base>
  );
}

export const AGENT_ICONS: Partial<Record<AgentType, (p: IconProps) => React.JSX.Element>> = {
  employment_source: IconRadar,
  school_pipeline: IconSchool,
  lead_enrichment: IconFunnel,
  candidate_vetting: IconShield,
  fit_ranking: IconTarget
};
