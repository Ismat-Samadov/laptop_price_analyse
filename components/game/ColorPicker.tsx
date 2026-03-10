'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { CardColor } from '@/lib/types';

const COLORS: { color: CardColor; label: string; bg: string; glow: string }[] = [
  { color: 'red',    label: 'Red',    bg: 'bg-red-500',     glow: 'shadow-[0_0_20px_rgba(239,68,68,0.7)]' },
  { color: 'blue',   label: 'Blue',   bg: 'bg-blue-500',    glow: 'shadow-[0_0_20px_rgba(59,130,246,0.7)]' },
  { color: 'green',  label: 'Green',  bg: 'bg-emerald-500', glow: 'shadow-[0_0_20px_rgba(52,211,153,0.7)]' },
  { color: 'yellow', label: 'Yellow', bg: 'bg-yellow-400',  glow: 'shadow-[0_0_20px_rgba(234,179,8,0.7)]' },
];

interface ColorPickerProps {
  open: boolean;
  onPick: (color: CardColor) => void;
}

export default function ColorPicker({ open, onPick }: ColorPickerProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.7, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.7, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 24 }}
            className="bg-gray-900/90 border border-white/10 rounded-2xl p-8 flex flex-col items-center gap-6 max-w-sm w-full mx-4"
          >
            <h2 className="text-white text-2xl font-black tracking-wide">Choose a Color</h2>

            <div className="grid grid-cols-2 gap-4 w-full">
              {COLORS.map(({ color, label, bg, glow }) => (
                <motion.button
                  key={color}
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.93 }}
                  onClick={() => onPick(color)}
                  className={`
                    ${bg} ${glow}
                    rounded-xl py-4 px-6 text-white font-bold text-lg
                    border-2 border-white/20 transition-all duration-150
                    flex items-center justify-center gap-2
                  `}
                >
                  {label}
                </motion.button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
