'use client';

import { motion } from 'framer-motion';
import clsx from 'clsx';
import Card from './Card';

interface DrawPileProps {
  count: number;
  canDraw: boolean;
  onDraw: () => void;
}

export default function DrawPile({ count, canDraw, onDraw }: DrawPileProps) {
  return (
    <div className="flex flex-col items-center gap-1">
      <motion.button
        onClick={canDraw ? onDraw : undefined}
        whileHover={canDraw ? { scale: 1.08 } : undefined}
        whileTap={canDraw ? { scale: 0.93 } : undefined}
        className={clsx(
          'relative focus:outline-none',
          canDraw ? 'cursor-pointer' : 'cursor-default',
        )}
        aria-label="Draw a card"
      >
        {/* Stack shadow cards */}
        <div className="absolute top-1 left-1 opacity-50">
          <Card card={{ id: 'back-2', color: 'wild', value: 'wild' }} isBack />
        </div>
        <div className="absolute top-0.5 left-0.5 opacity-70">
          <Card card={{ id: 'back-1', color: 'wild', value: 'wild' }} isBack />
        </div>
        <Card card={{ id: 'back-0', color: 'wild', value: 'wild' }} isBack />

        {/* Glowing ring when drawable */}
        {canDraw && (
          <motion.div
            className="absolute inset-0 rounded-xl ring-2 ring-white/40"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ repeat: Infinity, duration: 1.4 }}
          />
        )}
      </motion.button>

      <span className="text-white/50 text-xs mt-1">Draw ({count})</span>
    </div>
  );
}
