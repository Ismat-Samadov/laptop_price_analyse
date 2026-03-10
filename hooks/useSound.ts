'use client';

import { useRef, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';

type SoundType = 'play' | 'draw' | 'win' | 'lose' | 'uno' | 'click' | 'wild';

/** Creates a short synthesized sound using the Web Audio API — no audio files required */
function synthesize(ctx: AudioContext, type: SoundType) {
  const masterGain = ctx.createGain();
  masterGain.connect(ctx.destination);
  masterGain.gain.setValueAtTime(0.25, ctx.currentTime);

  const osc = ctx.createOscillator();
  const env = ctx.createGain();
  osc.connect(env);
  env.connect(masterGain);

  const t = ctx.currentTime;

  switch (type) {
    case 'play': {
      // Short descending swoosh
      osc.type = 'sine';
      osc.frequency.setValueAtTime(660, t);
      osc.frequency.exponentialRampToValueAtTime(330, t + 0.12);
      env.gain.setValueAtTime(0.4, t);
      env.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
      osc.start(t);
      osc.stop(t + 0.15);
      break;
    }
    case 'draw': {
      // Paper ruffle — noise burst
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(200, t);
      osc.frequency.linearRampToValueAtTime(100, t + 0.1);
      env.gain.setValueAtTime(0.2, t);
      env.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
      osc.start(t);
      osc.stop(t + 0.12);
      break;
    }
    case 'win': {
      // Ascending fanfare
      const freqs = [523, 659, 784, 1047];
      freqs.forEach((freq, i) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g);
        g.connect(masterGain);
        o.type = 'triangle';
        o.frequency.value = freq;
        g.gain.setValueAtTime(0, t + i * 0.1);
        g.gain.linearRampToValueAtTime(0.3, t + i * 0.1 + 0.05);
        g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.1 + 0.25);
        o.start(t + i * 0.1);
        o.stop(t + i * 0.1 + 0.3);
      });
      break;
    }
    case 'lose': {
      // Descending sad notes
      const freqs = [392, 349, 311, 262];
      freqs.forEach((freq, i) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g);
        g.connect(masterGain);
        o.type = 'triangle';
        o.frequency.value = freq;
        g.gain.setValueAtTime(0, t + i * 0.12);
        g.gain.linearRampToValueAtTime(0.25, t + i * 0.12 + 0.05);
        g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.12 + 0.3);
        o.start(t + i * 0.12);
        o.stop(t + i * 0.12 + 0.35);
      });
      break;
    }
    case 'uno': {
      // Two sharp beeps
      [0, 0.15].forEach((offset) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g);
        g.connect(masterGain);
        o.type = 'square';
        o.frequency.value = 880;
        g.gain.setValueAtTime(0.3, t + offset);
        g.gain.exponentialRampToValueAtTime(0.001, t + offset + 0.1);
        o.start(t + offset);
        o.stop(t + offset + 0.12);
      });
      osc.disconnect();
      return;
    }
    case 'wild': {
      // Glittery sweep
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, t);
      osc.frequency.exponentialRampToValueAtTime(880, t + 0.2);
      env.gain.setValueAtTime(0.3, t);
      env.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
      osc.start(t);
      osc.stop(t + 0.22);
      break;
    }
    case 'click': {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, t);
      env.gain.setValueAtTime(0.15, t);
      env.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
      osc.start(t);
      osc.stop(t + 0.06);
      break;
    }
  }
}

export function useSound() {
  const [soundEnabled, setSoundEnabled] = useLocalStorage('uno-sound', true);
  const ctxRef = useRef<AudioContext | null>(null);

  const getCtx = useCallback(() => {
    if (!ctxRef.current || ctxRef.current.state === 'closed') {
      ctxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    if (ctxRef.current.state === 'suspended') {
      ctxRef.current.resume();
    }
    return ctxRef.current;
  }, []);

  const play = useCallback(
    (type: SoundType) => {
      if (!soundEnabled) return;
      try {
        const ctx = getCtx();
        synthesize(ctx, type);
      } catch {
        // Silently ignore audio errors (e.g. browser blocks autoplay)
      }
    },
    [soundEnabled, getCtx],
  );

  const toggleSound = useCallback(() => setSoundEnabled((v) => !v), [setSoundEnabled]);

  return { soundEnabled, toggleSound, play };
}
