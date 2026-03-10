'use client';

import clsx from 'clsx';
import { Player } from '@/lib/types';

interface ScoreBoardProps {
  players: Player[];
  scores: Record<string, number>;
  currentPlayerIndex: number;
  round: number;
}

export default function ScoreBoard({ players, scores, currentPlayerIndex, round }: ScoreBoardProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap justify-center">
      <span className="text-white/40 text-xs font-semibold uppercase tracking-widest">
        Round {round}
      </span>

      {players.map((p, i) => (
        <div
          key={p.id}
          className={clsx(
            'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold',
            'border transition-all duration-300',
            i === currentPlayerIndex
              ? 'bg-white/20 border-white/40 text-white'
              : 'bg-white/5 border-white/10 text-white/50',
          )}
        >
          {p.type === 'human' ? '🧑' : '🤖'}
          <span>{p.name}</span>
          <span className="text-yellow-300 font-bold">{scores[p.id] ?? 0}</span>
        </div>
      ))}
    </div>
  );
}
