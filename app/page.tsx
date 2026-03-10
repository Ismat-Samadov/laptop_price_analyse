'use client';

import { useState } from 'react';
import { Difficulty } from '@/lib/types';
import { useUnoGame } from '@/hooks/useUnoGame';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import GameStartScreen from '@/components/game/GameStartScreen';
import GameBoard from '@/components/game/GameBoard';

export default function Home() {
  const api = useUnoGame();
  const [activeDifficulty, setActiveDifficulty] = useState<Difficulty | null>(null);
  const [, setBestScore] = useLocalStorage<number>('uno-best-score', 0);

  // Track best score when a round ends
  if (
    api.gameState?.phase === 'game-over' &&
    api.gameState.winner?.type === 'human'
  ) {
    const humanScore = api.gameState.scores['human'] ?? 0;
    setBestScore((prev) => Math.max(prev, humanScore));
  }

  function handleStart(difficulty: Difficulty) {
    setActiveDifficulty(difficulty);
    api.startGame(difficulty);
  }

  function handleMainMenu() {
    api.resetGame();
    setActiveDifficulty(null);
  }

  if (!api.gameState || !activeDifficulty) {
    return <GameStartScreen onStart={handleStart} />;
  }

  return (
    <GameBoard
      api={api}
      difficulty={activeDifficulty}
      onMainMenu={handleMainMenu}
    />
  );
}
