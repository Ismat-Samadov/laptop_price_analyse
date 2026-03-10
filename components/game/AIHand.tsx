'use client';

import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import Card from './Card';

interface AIHandProps {
  playerName: string;
  cardCount: number;
  isActive: boolean;
  /** Position: top, left, right */
  position?: 'top' | 'left' | 'right';
}

export default function AIHand({ playerName, cardCount, isActive, position = 'top' }: AIHandProps) {
  const isVertical = position === 'left' || position === 'right';

  return (
    <div
      className={clsx(
        'flex flex-col items-center gap-2',
        isActive && 'drop-shadow-[0_0_12px_rgba(255,255,255,0.3)]',
      )}
    >
      {/* Player label */}
      <div
        className={clsx(
          'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold',
          'border transition-all duration-300',
          isActive
            ? 'bg-white/20 border-white/50 text-white'
            : 'bg-white/5 border-white/10 text-white/40',
        )}
      >
        {isActive && (
          <motion.span
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ repeat: Infinity, duration: 1 }}
            className="w-2 h-2 rounded-full bg-green-400 inline-block"
          />
        )}
        {playerName}
        <span className="ml-1 opacity-60">({cardCount})</span>
      </div>

      {/* Face-down cards — show up to 7 stacked */}
      <div
        className={clsx(
          'flex',
          isVertical ? 'flex-col' : 'flex-row',
          'items-center',
        )}
      >
        <AnimatePresence mode="popLayout">
          {Array.from({ length: Math.min(cardCount, 7) }).map((_, i) => (
            <motion.div
              key={i}
              layout
              initial={{ opacity: 0, scale: 0.6 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.6 }}
              transition={{ duration: 0.2, delay: i * 0.02 }}
              style={{
                marginLeft: isVertical ? 0 : i === 0 ? 0 : -28,
                marginTop: isVertical && i > 0 ? -28 : 0,
                zIndex: i,
              }}
            >
              <Card
                card={{ id: `back-${i}`, color: 'wild', value: 'wild' }}
                isBack
                className="w-12 h-17 sm:w-14 sm:h-20"
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* +N overflow indicator */}
        {cardCount > 7 && (
          <div className="ml-1 text-white/60 text-xs font-bold">+{cardCount - 7}</div>
        )}
      </div>
    </div>
  );
}
