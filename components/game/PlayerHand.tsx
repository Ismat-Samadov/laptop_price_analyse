'use client';

import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { Card as CardType, CardColor } from '@/lib/types';
import { canPlayCard } from '@/lib/rules';
import Card from './Card';

interface PlayerHandProps {
  hand: CardType[];
  topCard: CardType;
  currentColor: CardColor;
  isActive: boolean;
  drawnCard: CardType | null;
  onPlayCard: (index: number) => void;
  onPlayDrawn: () => void;
  onPass: () => void;
  onDraw: () => void;
}

export default function PlayerHand({
  hand,
  topCard,
  currentColor,
  isActive,
  drawnCard,
  onPlayCard,
  onPlayDrawn,
  onPass,
  onDraw,
}: PlayerHandProps) {
  return (
    <div className="flex flex-col items-center gap-3 w-full">
      {/* "Just drew" prompt */}
      <AnimatePresence>
        {drawnCard && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 border border-white/20"
          >
            <span className="text-white/80 text-sm">Play drawn card?</span>
            <button
              onClick={onPlayDrawn}
              className="px-3 py-1 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-white text-sm font-semibold transition-colors"
            >
              Play
            </button>
            <button
              onClick={onPass}
              className="px-3 py-1 rounded-lg bg-gray-600 hover:bg-gray-500 text-white text-sm font-semibold transition-colors"
            >
              Pass
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hand cards */}
      <div
        className={clsx(
          'flex flex-row flex-wrap justify-center gap-1 sm:gap-2 px-2',
          'max-w-full overflow-x-auto pb-1',
        )}
      >
        <AnimatePresence mode="popLayout">
          {hand.map((card, i) => {
            const playable =
              isActive && !drawnCard && canPlayCard(card, topCard, currentColor);
            const isDrawn = drawnCard?.id === card.id;

            return (
              <motion.div
                key={card.id}
                layout
                initial={{ opacity: 0, y: 30, scale: 0.7 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.5, y: -20 }}
                transition={{ type: 'spring', stiffness: 280, damping: 22, delay: i * 0.03 }}
              >
                <Card
                  card={card}
                  isPlayable={playable}
                  isSelected={isDrawn}
                  onClick={() => onPlayCard(i)}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Card count badge */}
      <p className="text-white/50 text-xs">
        {hand.length} card{hand.length !== 1 ? 's' : ''}
      </p>
    </div>
  );
}
