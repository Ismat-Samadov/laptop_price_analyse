// ─── Card & Game Types ────────────────────────────────────────────────────────

export type CardColor = 'red' | 'blue' | 'green' | 'yellow' | 'wild';

export type CardValue =
  | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
  | 'skip' | 'reverse' | 'draw2' | 'wild' | 'wild4';

export interface Card {
  id: string;
  color: CardColor;
  value: CardValue;
}

export type PlayerType = 'human' | 'ai';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type Direction = 1 | -1;
export type GamePhase = 'playing' | 'picking-color' | 'game-over';

export interface Player {
  id: string;
  name: string;
  type: PlayerType;
  hand: Card[];
  difficulty?: Difficulty;
}

export interface GameState {
  players: Player[];
  currentPlayerIndex: number;
  direction: Direction;
  drawPile: Card[];
  discardPile: Card[];
  /** Effective color (important for wild cards) */
  currentColor: CardColor;
  phase: GamePhase;
  winner: Player | null;
  message: string;
  /** Cumulative scores across rounds */
  scores: Record<string, number>;
  round: number;
}

export interface GameSettings {
  difficulty: Difficulty;
}
