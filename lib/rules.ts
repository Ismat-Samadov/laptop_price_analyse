import { Card, CardColor } from './types';

/** Returns true when `card` can be played on top of `topCard` given `currentColor` */
export function canPlayCard(card: Card, topCard: Card, currentColor: CardColor): boolean {
  if (card.value === 'wild' || card.value === 'wild4') return true;
  if (card.color === currentColor) return true;
  if (card.value === topCard.value) return true;
  return false;
}

/** Filters a hand to cards that are currently playable */
export function getPlayableCards(hand: Card[], topCard: Card, currentColor: CardColor): Card[] {
  return hand.filter((c) => canPlayCard(c, topCard, currentColor));
}

/**
 * Calculates the point value of a hand (used for scoring when an opponent wins).
 * Number cards = face value, action cards = 20, wilds = 50.
 */
export function calculateHandPoints(hand: Card[]): number {
  return hand.reduce((total, card) => {
    if (card.value === 'wild' || card.value === 'wild4') return total + 50;
    if (['skip', 'reverse', 'draw2'].includes(card.value)) return total + 20;
    return total + parseInt(card.value, 10);
  }, 0);
}
