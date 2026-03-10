'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { GameState, Card, CardColor, Difficulty, Player } from '@/lib/types';
import { createDeck, shuffleDeck, dealHands } from '@/lib/deck';
import { canPlayCard, calculateHandPoints } from '@/lib/rules';
import { getAIMove, chooseColorForAI } from '@/lib/ai';

// ─── Pure state-transition helpers ───────────────────────────────────────────

/** Reshuffle the discard pile into the draw pile when the draw pile runs out */
function ensureDrawPile(state: GameState): GameState {
  if (state.drawPile.length > 0) return state;
  if (state.discardPile.length <= 1) return state; // nothing to reshuffle

  const top = state.discardPile[state.discardPile.length - 1];
  // Reset wild cards back to 'wild' colour before reshuffling
  const reshuffled = shuffleDeck(
    state.discardPile.slice(0, -1).map((c) =>
      c.value === 'wild' || c.value === 'wild4' ? { ...c, color: 'wild' as const } : c,
    ),
  );
  return { ...state, drawPile: reshuffled, discardPile: [top] };
}

/** Draw `count` cards for a player, reshuffling if needed */
function drawCardsForPlayer(state: GameState, playerIndex: number, count: number): GameState {
  let s = { ...state };
  const players = s.players.map((p) => ({ ...p, hand: [...p.hand] }));

  for (let i = 0; i < count; i++) {
    s = ensureDrawPile({ ...s, players });
    if (s.drawPile.length === 0) break;
    players[playerIndex].hand.push(s.drawPile[0]);
    s = { ...s, drawPile: s.drawPile.slice(1) };
  }

  return { ...s, players };
}

/** Advance to the next player given direction */
function nextPlayerIndex(players: number, current: number, direction: 1 | -1): number {
  return (current + direction + players) % players;
}

/**
 * Apply the effect of the played card and advance the turn.
 * `chosenColor` is required when card.value is 'wild' or 'wild4'.
 */
function applyEffect(state: GameState, card: Card, chosenColor?: CardColor): GameState {
  const n = state.players.length;
  let s = { ...state };
  const effectiveColor = chosenColor ?? card.color;
  s.currentColor = effectiveColor;

  const nextIdx = nextPlayerIndex(n, s.currentPlayerIndex, s.direction);

  switch (card.value) {
    case 'skip': {
      const skipped = state.players[nextIdx].name;
      s.currentPlayerIndex = nextPlayerIndex(n, nextIdx, s.direction);
      s.message = `${skipped} was skipped!`;
      break;
    }
    case 'reverse': {
      s.direction = (s.direction * -1) as 1 | -1;
      if (n === 2) {
        // With 2 players Reverse acts like Skip — same player goes again
        s.currentPlayerIndex = state.currentPlayerIndex;
        s.message = `Reversed — play again!`;
      } else {
        s.currentPlayerIndex = nextPlayerIndex(n, state.currentPlayerIndex, s.direction);
        s.message = `Direction reversed!`;
      }
      break;
    }
    case 'draw2': {
      s = drawCardsForPlayer(s, nextIdx, 2);
      const skipped2 = state.players[nextIdx].name;
      s.currentPlayerIndex = nextPlayerIndex(n, nextIdx, s.direction);
      s.message = `${skipped2} draws 2 and is skipped!`;
      break;
    }
    case 'wild4': {
      s = drawCardsForPlayer(s, nextIdx, 4);
      const skipped4 = state.players[nextIdx].name;
      s.currentPlayerIndex = nextPlayerIndex(n, nextIdx, s.direction);
      s.message = `${skipped4} draws 4! Color: ${effectiveColor}`;
      break;
    }
    case 'wild': {
      s.currentPlayerIndex = nextIdx;
      s.message = `Wild! Color changed to ${effectiveColor}`;
      break;
    }
    default: {
      s.currentPlayerIndex = nextIdx;
      break;
    }
  }

  return s;
}

/**
 * Remove the card from the player's hand, place it on the discard pile,
 * then apply effects. Returns the new state.
 */
function executePlay(
  state: GameState,
  playerIndex: number,
  cardIndex: number,
  chosenColor?: CardColor,
): GameState {
  const player = state.players[playerIndex];
  const card = player.hand[cardIndex];
  const newHand = player.hand.filter((_, i) => i !== cardIndex);
  const newPlayers = state.players.map((p, i) =>
    i === playerIndex ? { ...p, hand: newHand } : p,
  );

  let s: GameState = {
    ...state,
    players: newPlayers,
    discardPile: [...state.discardPile, card],
  };

  // ── Win condition ──────────────────────────────────────────────────────────
  if (newHand.length === 0) {
    const pointsGained = newPlayers
      .filter((_, i) => i !== playerIndex)
      .reduce((sum, p) => sum + calculateHandPoints(p.hand), 0);

    return {
      ...s,
      phase: 'game-over',
      winner: player,
      scores: {
        ...state.scores,
        [player.id]: (state.scores[player.id] ?? 0) + pointsGained,
      },
      message: `${player.name} wins! +${pointsGained} pts`,
    };
  }

  // UNO call
  if (newHand.length === 1) {
    s.message = `UNO! ${player.name} has one card left!`;
  }

  // Wild cards need a colour — human triggers picking-color phase; AI supplies colour directly
  if ((card.value === 'wild' || card.value === 'wild4') && !chosenColor) {
    return { ...s, phase: 'picking-color', currentColor: 'wild' };
  }

  return applyEffect(s, card, chosenColor);
}

// ─── Initial state factory ────────────────────────────────────────────────────

const DIFFICULTY_CONFIG: Record<Difficulty, { aiCount: number }> = {
  easy: { aiCount: 1 },
  medium: { aiCount: 2 },
  hard: { aiCount: 3 },
};

function buildInitialState(difficulty: Difficulty): GameState {
  const { aiCount } = DIFFICULTY_CONFIG[difficulty];
  const playerCount = aiCount + 1;

  let deck = shuffleDeck(createDeck());
  const { hands, remaining } = dealHands(deck, playerCount);

  // First discard card must not be a wild
  let startIdx = remaining.findIndex((c) => c.value !== 'wild' && c.value !== 'wild4');
  const startCard = remaining[startIdx];
  const drawPile = remaining.filter((_, i) => i !== startIdx);

  const players: Player[] = [
    { id: 'human', name: 'You', type: 'human', hand: hands[0] },
    ...Array.from({ length: aiCount }, (_, i) => ({
      id: `ai-${i}`,
      name: `CPU ${i + 1}`,
      type: 'ai' as const,
      hand: hands[i + 1],
      difficulty,
    })),
  ];

  return {
    players,
    currentPlayerIndex: 0,
    direction: 1,
    drawPile,
    discardPile: [startCard],
    currentColor: startCard.color,
    phase: 'playing',
    winner: null,
    message: "Your turn — play a card!",
    scores: Object.fromEntries(players.map((p) => [p.id, 0])),
    round: 1,
  };
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export interface UnoGameAPI {
  gameState: GameState | null;
  /** Card the human just drew that they may optionally play */
  drawnCard: Card | null;
  /** Whether it is the human player's turn */
  isHumanTurn: boolean;
  startGame: (difficulty: Difficulty) => void;
  /** Human plays a card from their hand by index */
  playCard: (cardIndex: number) => void;
  /** Human draws from the draw pile */
  drawCard: () => void;
  /** Human chooses to play the card they just drew */
  playDrawnCard: () => void;
  /** Human passes after drawing */
  passTurn: () => void;
  /** Human picks a colour after playing a wild */
  pickColor: (color: CardColor) => void;
  resetGame: () => void;
}

export function useUnoGame(): UnoGameAPI {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [drawnCard, setDrawnCard] = useState<Card | null>(null);
  const aiTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isHumanTurn =
    !!gameState &&
    gameState.phase === 'playing' &&
    gameState.players[gameState.currentPlayerIndex]?.type === 'human';

  // ── Start / reset ──────────────────────────────────────────────────────────
  const startGame = useCallback((difficulty: Difficulty) => {
    if (aiTimerRef.current) clearTimeout(aiTimerRef.current);
    setDrawnCard(null);
    setGameState(buildInitialState(difficulty));
  }, []);

  const resetGame = useCallback(() => {
    if (aiTimerRef.current) clearTimeout(aiTimerRef.current);
    setGameState(null);
    setDrawnCard(null);
  }, []);

  // ── Human plays a card ─────────────────────────────────────────────────────
  const playCard = useCallback(
    (cardIndex: number) => {
      if (!gameState || !isHumanTurn) return;
      const { players, currentPlayerIndex, discardPile, currentColor } = gameState;
      const card = players[currentPlayerIndex].hand[cardIndex];
      const topCard = discardPile[discardPile.length - 1];
      if (!canPlayCard(card, topCard, currentColor)) return;

      setDrawnCard(null);
      setGameState((prev) => (prev ? executePlay(prev, currentPlayerIndex, cardIndex) : prev));
    },
    [gameState, isHumanTurn],
  );

  // ── Human draws a card ─────────────────────────────────────────────────────
  const drawCard = useCallback(() => {
    if (!gameState || !isHumanTurn || drawnCard) return;
    const { currentPlayerIndex, discardPile, currentColor } = gameState;

    setGameState((prev) => {
      if (!prev) return prev;
      const next = drawCardsForPlayer(prev, currentPlayerIndex, 1);
      const newCard = next.players[currentPlayerIndex].hand.at(-1)!;
      const topCard = prev.discardPile[prev.discardPile.length - 1];

      if (canPlayCard(newCard, topCard, prev.currentColor)) {
        // Let the player decide whether to play or pass
        setDrawnCard(newCard);
        return next;
      }

      // Can't play — pass the turn
      return {
        ...next,
        currentPlayerIndex: nextPlayerIndex(
          next.players.length,
          currentPlayerIndex,
          next.direction,
        ),
        message: `${prev.players[currentPlayerIndex].name} drew and passed`,
      };
    });
  }, [gameState, isHumanTurn, drawnCard]);

  // ── Human plays the just-drawn card ───────────────────────────────────────
  const playDrawnCard = useCallback(() => {
    if (!gameState || !drawnCard) return;
    const { currentPlayerIndex, players } = gameState;
    const cardIdx = players[currentPlayerIndex].hand.findIndex((c) => c.id === drawnCard.id);
    if (cardIdx === -1) return;
    setDrawnCard(null);
    setGameState((prev) =>
      prev ? executePlay(prev, currentPlayerIndex, cardIdx) : prev,
    );
  }, [gameState, drawnCard]);

  // ── Human passes after drawing ────────────────────────────────────────────
  const passTurn = useCallback(() => {
    if (!gameState || !drawnCard) return;
    setDrawnCard(null);
    setGameState((prev) => {
      if (!prev) return prev;
      const { currentPlayerIndex, players, direction } = prev;
      return {
        ...prev,
        currentPlayerIndex: nextPlayerIndex(players.length, currentPlayerIndex, direction),
        message: `${players[currentPlayerIndex].name} drew and passed`,
      };
    });
  }, [gameState, drawnCard]);

  // ── Human picks colour for wild ───────────────────────────────────────────
  const pickColor = useCallback(
    (color: CardColor) => {
      if (!gameState || gameState.phase !== 'picking-color') return;
      const card = gameState.discardPile[gameState.discardPile.length - 1];
      setGameState((prev) => {
        if (!prev || prev.phase !== 'picking-color') return prev;
        return applyEffect({ ...prev, phase: 'playing' }, card, color);
      });
    },
    [gameState],
  );

  // ── AI auto-play ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (!gameState || gameState.phase !== 'playing') return;
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (currentPlayer.type !== 'ai') return;

    const delay = 900 + Math.random() * 600;

    aiTimerRef.current = setTimeout(() => {
      setGameState((prev) => {
        if (!prev || prev.phase !== 'playing') return prev;
        const player = prev.players[prev.currentPlayerIndex];
        if (player.type !== 'ai') return prev;

        const { cardIndex, chosenColor } = getAIMove(
          prev,
          prev.currentPlayerIndex,
          player.difficulty!,
        );

        if (cardIndex === null) {
          // AI draws
          const drawn = drawCardsForPlayer(prev, prev.currentPlayerIndex, 1);
          const newCard = drawn.players[prev.currentPlayerIndex].hand.at(-1)!;
          const topCard = prev.discardPile[prev.discardPile.length - 1];

          if (canPlayCard(newCard, topCard, drawn.currentColor)) {
            const drawnIdx = drawn.players[prev.currentPlayerIndex].hand.length - 1;
            const col =
              newCard.value === 'wild' || newCard.value === 'wild4'
                ? chooseColorForAI(drawn.players[prev.currentPlayerIndex].hand)
                : undefined;
            return executePlay(drawn, prev.currentPlayerIndex, drawnIdx, col);
          }

          // Can't play drawn card — pass
          return {
            ...drawn,
            currentPlayerIndex: nextPlayerIndex(
              drawn.players.length,
              prev.currentPlayerIndex,
              drawn.direction,
            ),
            message: `${player.name} drew and passed`,
          };
        }

        return executePlay(prev, prev.currentPlayerIndex, cardIndex, chosenColor);
      });
    }, delay);

    return () => {
      if (aiTimerRef.current) clearTimeout(aiTimerRef.current);
    };
  }, [gameState?.currentPlayerIndex, gameState?.phase]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    gameState,
    drawnCard,
    isHumanTurn,
    startGame,
    playCard,
    drawCard,
    playDrawnCard,
    passTurn,
    pickColor,
    resetGame,
  };
}
