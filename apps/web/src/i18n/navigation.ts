import {createNavigation} from 'next-intl/navigation';
import {routing} from './routing';

/**
 * Locale-aware Link, useRouter, redirect, etc.
 * Always import navigation primitives from here, not from 'next/link' or 'next/navigation',
 * so URLs automatically carry the right locale prefix.
 */
export const {Link, redirect, usePathname, useRouter, getPathname} =
  createNavigation(routing);
