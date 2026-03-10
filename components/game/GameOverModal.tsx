'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Player } from '@/lib/types';
import confetti from 'canvas-confetti';
import { useEffect } from 'react';

interface GameOverModalProps {
  open: boolean;
  winner: Player | null;
  scores: Record<string, number>;
  players: Player[];
  round: number;
  onNewRound: () => void;
  onMainMenu: () => void;
}

function ScoreRow({ player, score, isWinner }: { player: Player; score: number; isWinner: boolean }) {
  return (
    <div className={`flex items-center justify-between rounded-lg px-4 py-2 ${isWinner ? 'bg-yellow-500/20 border border-yellow-500/40' : 'bg-white/5'}`}>
      <span className="text-white font-semibold">
        {isWinner && '👑 '}{player.name}
      </span>
      <span className="text-yellow-300 font-bold">{score} pts</span>
    </div>
  );
}

export default function GameOverModal({
  open,
  winner,
  scores,
  players,
  round,
  onNewRound,
  onMainMenu,
}: GameOverModalProps) {
  const humanWon = winner?.type === 'human';

  useEffect(() => {
    if (open && humanWon) {
      // Burst confetti when the player wins
      const end = Date.now() + 2000;
      const burst = () => {
        confetti({ particleCount: 60, spread: 80, origin: { x: Math.random(), y: 0.3 } });
        if (Date.now() < end) requestAnimationFrame(burst);
      };
      burst();
    }
  }, [open, humanWon]);

  return (
    <AnimatePresence>
      {open && winner && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.6, opacity: 0, y: 40 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.6, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
            className="bg-gray-900/95 border border-white/10 rounded-2xl p-8 max-w-sm w-full mx-4 flex flex-col gap-6"
          >
            {/* Result headline */}
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1, rotate: [0, -10, 10, -5, 5, 0] }}
                transition={{ delay: 0.2, type: 'spring' }}
                className="text-5xl mb-2"
              >
                {humanWon ? '🎉' : '😞'}
              </motion.div>
              <h2 className={`text-3xl font-black ${humanWon ? 'text-yellow-300' : 'text-gray-300'}`}>
                {humanWon ? 'You Win!' : `${winner.name} Wins!`}
              </h2>
              <p className="text-white/50 text-sm mt-1">Round {round}</p>
            </div>

            {/* Score table */}
            <div className="flex flex-col gap-2">
              <p className="text-white/50 text-xs uppercase tracking-wider mb-1">Scores</p>
              {players.map((p) => (
                <ScoreRow
                  key={p.id}
                  player={p}
                  score={scores[p.id] ?? 0}
                  isWinner={p.id === winner.id}
                />
              ))}
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-3">
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={onNewRound}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-lg transition-all"
              >
                Next Round
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={onMainMenu}
                className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold transition-all"
              >
                Main Menu
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
