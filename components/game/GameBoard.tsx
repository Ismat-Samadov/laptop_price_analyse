'use client';

import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { GameState, CardColor, Difficulty } from '@/lib/types';
import { UnoGameAPI } from '@/hooks/useUnoGame';
import { useSound } from '@/hooks/useSound';

import AIHand from './AIHand';
import PlayerHand from './PlayerHand';
import DrawPile from './DrawPile';
import DiscardPile from './DiscardPile';
import ColorPicker from './ColorPicker';
import GameOverModal from './GameOverModal';
import ScoreBoard from './ScoreBoard';

interface GameBoardProps {
  api: UnoGameAPI;
  difficulty: Difficulty;
  onMainMenu: () => void;
}

export default function GameBoard({ api, difficulty, onMainMenu }: GameBoardProps) {
  const {
    gameState,
    drawnCard,
    isHumanTurn,
    playCard,
    drawCard,
    playDrawnCard,
    passTurn,
    pickColor,
    startGame,
  } = api;

  const { soundEnabled, toggleSound, play } = useSound();
  const prevDiscardRef = useRef<string | undefined>(undefined);

  // Play sound when a card is placed on the discard pile
  useEffect(() => {
    if (!gameState) return;
    const topId = gameState.discardPile.at(-1)?.id;
    if (topId && topId !== prevDiscardRef.current) {
      prevDiscardRef.current = topId;
      const card = gameState.discardPile.at(-1)!;
      if (card.value === 'wild' || card.value === 'wild4') play('wild');
      else play('play');
    }
  }, [gameState?.discardPile.length, play]); // eslint-disable-line react-hooks/exhaustive-deps

  // Play win / lose sound
  useEffect(() => {
    if (gameState?.phase === 'game-over' && gameState.winner) {
      if (gameState.winner.type === 'human') play('win');
      else play('lose');
    }
  }, [gameState?.phase, play]); // eslint-disable-line react-hooks/exhaustive-deps

  // UNO call sound
  const prevHandSizeRef = useRef<number | undefined>(undefined);
  useEffect(() => {
    if (!gameState) return;
    const humanPlayer = gameState.players.find((p) => p.type === 'human');
    if (!humanPlayer) return;
    const hs = humanPlayer.hand.length;
    if (prevHandSizeRef.current !== undefined && prevHandSizeRef.current > 1 && hs === 1) {
      play('uno');
    }
    prevHandSizeRef.current = hs;
  }, [gameState?.players, play]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!gameState) return null;

  const {
    players,
    currentPlayerIndex,
    discardPile,
    drawPile,
    currentColor,
    phase,
    winner,
    message,
    scores,
    round,
    direction,
  } = gameState;

  const topCard = discardPile.at(-1)!;
  const humanPlayer = players[0];
  const aiPlayers = players.slice(1);

  // Lay out AI players: 1→top, 2→top+right, 3→left+top+right
  const aiLayout =
    aiPlayers.length === 1
      ? [{ player: aiPlayers[0], position: 'top' as const }]
      : aiPlayers.length === 2
      ? [
          { player: aiPlayers[0], position: 'top' as const },
          { player: aiPlayers[1], position: 'right' as const },
        ]
      : [
          { player: aiPlayers[0], position: 'left' as const },
          { player: aiPlayers[1], position: 'top' as const },
          { player: aiPlayers[2], position: 'right' as const },
        ];

  return (
    <div className="relative min-h-screen w-full flex flex-col overflow-hidden select-none">
      {/* Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_#1a1035_0%,_#0a0a14_70%)] pointer-events-none" />
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-4 pt-3 pb-2 flex-wrap gap-2">
        <ScoreBoard
          players={players}
          scores={scores}
          currentPlayerIndex={currentPlayerIndex}
          round={round}
        />
        <div className="flex items-center gap-2">
          {/* Direction indicator */}
          <motion.span
            animate={{ rotate: direction === 1 ? 0 : 180 }}
            transition={{ type: 'spring' }}
            className="text-white/30 text-lg select-none"
            title="Play direction"
          >
            ↻
          </motion.span>

          {/* Sound toggle */}
          <button
            onClick={() => { toggleSound(); play('click'); }}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white/60 flex items-center justify-center text-sm transition-colors"
            aria-label="Toggle sound"
          >
            {soundEnabled ? '🔊' : '🔇'}
          </button>

          {/* Menu */}
          <button
            onClick={onMainMenu}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white/60 flex items-center justify-center text-sm transition-colors"
            aria-label="Main menu"
          >
            ✕
          </button>
        </div>
      </header>

      {/* AI hands — top row */}
      <div className="relative z-10 flex items-start justify-around px-4 pt-2 pb-2 gap-4 flex-wrap">
        {aiLayout
          .filter(({ position }) => position === 'top')
          .map(({ player }) => (
            <AIHand
              key={player.id}
              playerName={player.name}
              cardCount={player.hand.length}
              isActive={players.indexOf(player) === currentPlayerIndex}
              position="top"
            />
          ))}
      </div>

      {/* Middle row: left AI · centre piles · right AI */}
      <div className="relative z-10 flex flex-1 items-center justify-between px-4 gap-4 min-h-[160px]">
        {/* Left AI */}
        <div className="hidden sm:flex">
          {aiLayout
            .filter(({ position }) => position === 'left')
            .map(({ player }) => (
              <AIHand
                key={player.id}
                playerName={player.name}
                cardCount={player.hand.length}
                isActive={players.indexOf(player) === currentPlayerIndex}
                position="left"
              />
            ))}
        </div>

        {/* Centre — draw + discard */}
        <div className="flex flex-col items-center gap-4 flex-1">
          {/* Status message */}
          <AnimatePresence mode="wait">
            <motion.p
              key={message}
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="text-white/70 text-sm text-center font-medium min-h-[20px] px-4"
            >
              {message}
            </motion.p>
          </AnimatePresence>

          <div className="flex items-center gap-6">
            <DrawPile
              count={drawPile.length}
              canDraw={isHumanTurn && !drawnCard}
              onDraw={() => { drawCard(); play('draw'); }}
            />
            <DiscardPile topCard={topCard} currentColor={currentColor} />
          </div>
        </div>

        {/* Right AI */}
        <div className="hidden sm:flex">
          {aiLayout
            .filter(({ position }) => position === 'right')
            .map(({ player }) => (
              <AIHand
                key={player.id}
                playerName={player.name}
                cardCount={player.hand.length}
                isActive={players.indexOf(player) === currentPlayerIndex}
                position="right"
              />
            ))}
        </div>
      </div>

      {/* Mobile: left + right AIs below centre */}
      <div className="relative z-10 flex sm:hidden items-center justify-around px-4 pb-2 gap-4 flex-wrap">
        {aiLayout
          .filter(({ position }) => position === 'left' || position === 'right')
          .map(({ player }) => (
            <AIHand
              key={player.id}
              playerName={player.name}
              cardCount={player.hand.length}
              isActive={players.indexOf(player) === currentPlayerIndex}
              position="top"
            />
          ))}
      </div>

      {/* Human hand */}
      <div className="relative z-10 pb-4 px-2 flex flex-col items-center gap-3">
        {/* "Your turn" indicator */}
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold',
          'border transition-all duration-300',
          isHumanTurn
            ? 'bg-white/20 border-white/40 text-white'
            : 'bg-white/5 border-white/10 text-white/30',
        )}>
          {isHumanTurn && (
            <motion.span
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ repeat: Infinity, duration: 0.9 }}
              className="w-2 h-2 rounded-full bg-green-400 inline-block"
            />
          )}
          🧑 {humanPlayer.name}
          {isHumanTurn && ' — Your turn!'}
        </div>

        <PlayerHand
          hand={humanPlayer.hand}
          topCard={topCard}
          currentColor={currentColor}
          isActive={isHumanTurn}
          drawnCard={drawnCard}
          onPlayCard={playCard}
          onPlayDrawn={playDrawnCard}
          onPass={passTurn}
          onDraw={() => { drawCard(); play('draw'); }}
        />
      </div>

      {/* Colour picker overlay */}
      <ColorPicker
        open={phase === 'picking-color'}
        onPick={(color) => { pickColor(color); play('click'); }}
      />

      {/* Game over modal */}
      <GameOverModal
        open={phase === 'game-over'}
        winner={winner}
        scores={scores}
        players={players}
        round={round}
        onNewRound={() => startGame(difficulty)}
        onMainMenu={onMainMenu}
      />
    </div>
  );
}
