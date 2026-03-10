'use client';

import { useState, useCallback, useEffect } from 'react';

/**
 * useState that is persisted in localStorage.
 * SSR-safe: defaults to `initialValue` on the server / first render.
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, React.Dispatch<React.SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const stored = window.localStorage.getItem(key);
      return stored !== null ? (JSON.parse(stored) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore write errors (e.g. private mode quota)
    }
  }, [key, value]);

  return [value, setValue];
}
