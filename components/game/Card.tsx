'use client';

import { motion } from 'framer-motion';
import clsx from 'clsx';
import { Card as CardType } from '@/lib/types';

// ─── Colour mappings ──────────────────────────────────────────────────────────

const COLOR_BG: Record<string, string> = {
  red:    'bg-gradient-to-br from-red-500 to-red-700',
  blue:   'bg-gradient-to-br from-blue-500 to-blue-700',
  green:  'bg-gradient-to-br from-emerald-500 to-emerald-700',
  yellow: 'bg-gradient-to-br from-yellow-400 to-yellow-600',
  wild:   'bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400',
};

const COLOR_BORDER: Record<string, string> = {
  red:    'border-red-400',
  blue:   'border-blue-400',
  green:  'border-emerald-400',
  yellow: 'border-yellow-300',
  wild:   'border-purple-400',
};

const COLOR_SHADOW: Record<string, string> = {
  red:    'shadow-[0_0_20px_rgba(239,68,68,0.55)]',
  blue:   'shadow-[0_0_20px_rgba(59,130,246,0.55)]',
  green:  'shadow-[0_0_20px_rgba(52,211,153,0.55)]',
  yellow: 'shadow-[0_0_20px_rgba(234,179,8,0.55)]',
  wild:   'shadow-[0_0_20px_rgba(168,85,247,0.55)]',
};

const COLOR_TEXT: Record<string, string> = {
  red:    'text-red-200',
  blue:   'text-blue-200',
  green:  'text-emerald-200',
  yellow: 'text-yellow-100',
  wild:   'text-white',
};

// ─── Symbol rendering ─────────────────────────────────────────────────────────

function cardLabel(value: string): string {
  switch (value) {
    case 'skip':    return '⊘';
    case 'reverse': return '↺';
    case 'draw2':   return '+2';
    case 'wild':    return '★';
    case 'wild4':   return '+4';
    default:        return value;
  }
}

// ─── Props ────────────────────────────────────────────────────────────────────

interface CardProps {
  card: CardType;
  /** Highlight as playable (human hand) */
  isPlayable?: boolean;
  /** Currently selected / active */
  isSelected?: boolean;
  /** Compact — used for draw pile stack indicator */
  isBack?: boolean;
  onClick?: () => void;
  className?: string;
  layoutId?: string;
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function Card({
  card,
  isPlayable = false,
  isSelected = false,
  isBack = false,
  onClick,
  className,
  layoutId,
}: CardProps) {
  const col = card.color;

  if (isBack) {
    return (
      <div
        className={clsx(
          'relative rounded-xl border-2 border-gray-600',
          'bg-gradient-to-br from-gray-800 to-gray-900',
          'w-14 h-20 sm:w-16 sm:h-24 flex items-center justify-center',
          'shadow-lg',
          className,
        )}
      >
        {/* UNO back pattern */}
        <div className="w-8 h-12 sm:w-10 sm:h-16 rounded-lg bg-gradient-to-br from-red-600 to-yellow-500 opacity-80 flex items-center justify-center rotate-12">
          <span className="text-white font-black text-xs sm:text-sm -rotate-12 drop-shadow">UNO</span>
        </div>
      </div>
    );
  }

  const label = cardLabel(card.value);

  return (
    <motion.div
      layoutId={layoutId}
      whileHover={isPlayable ? { y: -10, scale: 1.05 } : undefined}
      whileTap={isPlayable ? { scale: 0.95 } : undefined}
      animate={isSelected ? { y: -14, scale: 1.08 } : {}}
      transition={{ type: 'spring', stiffness: 300, damping: 22 }}
      onClick={isPlayable ? onClick : undefined}
      className={clsx(
        'relative rounded-xl border-2 select-none flex-shrink-0',
        'w-14 h-20 sm:w-16 sm:h-24 md:w-18 md:h-28',
        'transition-shadow duration-200',
        COLOR_BG[col],
        COLOR_BORDER[col],
        isPlayable
          ? [COLOR_SHADOW[col], 'cursor-pointer ring-2 ring-white/20']
          : 'opacity-70 cursor-default',
        isSelected && 'ring-4 ring-white/60',
        className,
      )}
    >
      {/* Corner labels */}
      <span
        className={clsx(
          'absolute top-1 left-1.5 font-black leading-none',
          'text-xs sm:text-sm',
          COLOR_TEXT[col],
          'drop-shadow-md',
        )}
      >
        {label}
      </span>
      <span
        className={clsx(
          'absolute bottom-1 right-1.5 font-black leading-none rotate-180',
          'text-xs sm:text-sm',
          COLOR_TEXT[col],
          'drop-shadow-md',
        )}
      >
        {label}
      </span>

      {/* Center oval */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          className={clsx(
            'w-9 h-6 sm:w-10 sm:h-7 rounded-full',
            'bg-white/15 backdrop-blur-sm border border-white/25',
            'flex items-center justify-center',
            'rotate-[-25deg]',
          )}
        >
          <span
            className={clsx(
              'font-black text-white drop-shadow-lg',
              'text-sm sm:text-base rotate-[25deg]',
              label.length > 2 ? 'text-xs sm:text-sm' : '',
            )}
          >
            {label}
          </span>
        </div>
      </div>

      {/* Playable glow pulse */}
      {isPlayable && (
        <motion.div
          className={clsx(
            'absolute inset-0 rounded-xl opacity-0',
            COLOR_SHADOW[col],
          )}
          animate={{ opacity: [0, 0.5, 0] }}
          transition={{ repeat: Infinity, duration: 1.6, ease: 'easeInOut' }}
        />
      )}
    </motion.div>
  );
}
