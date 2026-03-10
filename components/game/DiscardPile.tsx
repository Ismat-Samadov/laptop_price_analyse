'use client';

import { AnimatePresence, motion } from 'framer-motion';
import clsx from 'clsx';
import { Card as CardType, CardColor } from '@/lib/types';
import Card from './Card';

const COLOR_GLOW: Record<string, string> = {
  red:    'shadow-[0_0_30px_rgba(239,68,68,0.6)]',
  blue:   'shadow-[0_0_30px_rgba(59,130,246,0.6)]',
  green:  'shadow-[0_0_30px_rgba(52,211,153,0.6)]',
  yellow: 'shadow-[0_0_30px_rgba(234,179,8,0.6)]',
  wild:   'shadow-[0_0_30px_rgba(168,85,247,0.6)]',
};

interface DiscardPileProps {
  topCard: CardType;
  currentColor: CardColor;
}

export default function DiscardPile({ topCard, currentColor }: DiscardPileProps) {
  // When the top card is a wild, show the chosen colour as a ring overlay
  const showColorIndicator = topCard.value === 'wild' || topCard.value === 'wild4';

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={clsx('relative', COLOR_GLOW[currentColor], 'rounded-xl')}>
        <AnimatePresence mode="wait">
          <motion.div
            key={topCard.id}
            initial={{ rotateY: 90, opacity: 0, scale: 0.8 }}
            animate={{ rotateY: 0, opacity: 1, scale: 1 }}
            exit={{ rotateY: -90, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
          >
            <Card card={topCard} />
          </motion.div>
        </AnimatePresence>

        {/* Current-colour badge for wilds */}
        {showColorIndicator && (
          <motion.div
            key={currentColor}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className={clsx(
              'absolute -top-2 -right-2 w-5 h-5 rounded-full border-2 border-white/50',
              {
                'bg-red-500':     currentColor === 'red',
                'bg-blue-500':    currentColor === 'blue',
                'bg-emerald-500': currentColor === 'green',
                'bg-yellow-400':  currentColor === 'yellow',
                'bg-purple-500':  currentColor === 'wild',
              },
            )}
          />
        )}
      </div>
      <span className="text-white/50 text-xs mt-1">Discard</span>
    </div>
  );
}
