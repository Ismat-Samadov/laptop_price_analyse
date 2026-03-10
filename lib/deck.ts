import { Card, CardColor, CardValue } from './types';

const COLORS: CardColor[] = ['red', 'blue', 'green', 'yellow'];
const NUMBER_VALUES: CardValue[] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
const ACTION_VALUES: CardValue[] = ['skip', 'reverse', 'draw2'];

/**
 * Creates a standard 108-card UNO deck:
 * - 4 colors × (one 0 + two each of 1-9 + two each of skip/reverse/draw2)
 * - 4 Wild + 4 Wild Draw Four
 */
export function createDeck(): Card[] {
  const cards: Card[] = [];
  let id = 0;

  for (const color of COLORS) {
    // One 0 per color
    cards.push({ id: `card-${id++}`, color, value: '0' });

    // Two of each 1-9 and action card
    for (const value of [...NUMBER_VALUES.slice(1), ...ACTION_VALUES]) {
      cards.push({ id: `card-${id++}`, color, value });
      cards.push({ id: `card-${id++}`, color, value });
    }
  }

  // 4 Wild and 4 Wild Draw Four
  for (let i = 0; i < 4; i++) {
    cards.push({ id: `card-${id++}`, color: 'wild', value: 'wild' });
    cards.push({ id: `card-${id++}`, color: 'wild', value: 'wild4' });
  }

  return cards; // 108 cards total
}

/** Fisher-Yates shuffle */
export function shuffleDeck(deck: Card[]): Card[] {
  const shuffled = [...deck];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/** Deal `handSize` cards to each of `playerCount` players */
export function dealHands(
  deck: Card[],
  playerCount: number,
  handSize = 7,
): { hands: Card[][]; remaining: Card[] } {
  const hands: Card[][] = Array.from({ length: playerCount }, () => []);
  let i = 0;

  for (let card = 0; card < handSize; card++) {
    for (let p = 0; p < playerCount; p++) {
      hands[p].push(deck[i++]);
    }
  }

  return { hands, remaining: deck.slice(i) };
}
