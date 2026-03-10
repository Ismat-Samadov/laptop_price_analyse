'use client';

import { motion } from 'framer-motion';
import { Difficulty } from '@/lib/types';
import { useLocalStorage } from '@/hooks/useLocalStorage';

const DIFFICULTIES: {
  key: Difficulty;
  label: string;
  desc: string;
  opponents: string;
  color: string;
  gradient: string;
}[] = [
  {
    key: 'easy',
    label: 'Easy',
    desc: 'One sleepy CPU. Perfect for learning.',
    opponents: '1 CPU (Easy)',
    color: 'text-emerald-300',
    gradient: 'from-emerald-600/30 to-emerald-900/20 border-emerald-500/40 hover:border-emerald-400',
  },
  {
    key: 'medium',
    label: 'Medium',
    desc: 'Two cunning CPUs. A real challenge.',
    opponents: '2 CPUs (Medium)',
    color: 'text-yellow-300',
    gradient: 'from-yellow-600/30 to-yellow-900/20 border-yellow-500/40 hover:border-yellow-400',
  },
  {
    key: 'hard',
    label: 'Hard',
    desc: 'Three ruthless CPUs. Good luck.',
    opponents: '3 CPUs (Hard)',
    color: 'text-red-300',
    gradient: 'from-red-600/30 to-red-900/20 border-red-500/40 hover:border-red-400',
  },
];

interface GameStartScreenProps {
  onStart: (difficulty: Difficulty) => void;
}

export default function GameStartScreen({ onStart }: GameStartScreenProps) {
  const [bestScore] = useLocalStorage<number>('uno-best-score', 0);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-violet-600/20 rounded-full blur-[80px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-red-600/15 rounded-full blur-[100px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex flex-col items-center gap-8 max-w-md w-full"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0.7, rotate: -10 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 18 }}
          className="relative"
        >
          <div className="w-28 h-28 rounded-full bg-gradient-to-br from-red-500 via-yellow-400 to-blue-500 flex items-center justify-center shadow-[0_0_60px_rgba(239,68,68,0.5)] rotate-12">
            <span className="text-white font-black text-4xl drop-shadow-lg -rotate-12">UNO</span>
          </div>
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-white/20"
            animate={{ rotate: 360 }}
            transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
          />
        </motion.div>

        <div className="text-center">
          <h1 className="text-5xl font-black text-white tracking-tight drop-shadow-lg">
            UNO
          </h1>
          <p className="text-white/40 text-sm mt-1 tracking-widest uppercase">The Card Game</p>
          {bestScore > 0 && (
            <p className="text-yellow-400/70 text-xs mt-2">🏆 Best score: {bestScore} pts</p>
          )}
        </div>

        {/* Difficulty cards */}
        <div className="w-full flex flex-col gap-3">
          <p className="text-white/40 text-xs text-center uppercase tracking-widest mb-1">
            Select Difficulty
          </p>
          {DIFFICULTIES.map(({ key, label, desc, opponents, color, gradient }, i) => (
            <motion.button
              key={key}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + i * 0.1 }}
              whileHover={{ scale: 1.03, x: 4 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onStart(key)}
              className={`
                w-full rounded-xl p-4 border bg-gradient-to-r ${gradient}
                flex items-center justify-between
                transition-all duration-200 text-left backdrop-blur-sm
              `}
            >
              <div>
                <p className={`font-black text-lg ${color}`}>{label}</p>
                <p className="text-white/50 text-sm">{desc}</p>
              </div>
              <div className="text-right">
                <p className="text-white/40 text-xs">{opponents}</p>
                <span className="text-white/30 text-lg">→</span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Quick rules */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-white/25 text-xs text-center max-w-xs leading-relaxed"
        >
          Match the colour or number · Play specials to shake it up<br />
          First to empty their hand wins · Call UNO on your last card!
        </motion.div>
      </motion.div>
    </div>
  );
}
