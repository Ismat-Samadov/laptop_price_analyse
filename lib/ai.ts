import { Card, CardColor, Difficulty, GameState } from './types';
import { getPlayableCards } from './rules';

/**
 * Picks the color the AI has the most cards of (to maximise future plays).
 */
export function chooseColorForAI(hand: Card[]): CardColor {
  const counts: Record<string, number> = { red: 0, blue: 0, green: 0, yellow: 0 };
  for (const card of hand) {
    if (card.color !== 'wild') counts[card.color]++;
  }
  const best = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return (best[0] as CardColor) || 'red';
}

/**
 * Returns the card index the AI wants to play, or null to draw.
 * Also returns `chosenColor` when playing a wild.
 */
export function getAIMove(
  state: GameState,
  playerIndex: number,
  difficulty: Difficulty,
): { cardIndex: number | null; chosenColor?: CardColor } {
  const player = state.players[playerIndex];
  const topCard = state.discardPile[state.discardPile.length - 1];
  const playable = getPlayableCards(player.hand, topCard, state.currentColor);

  if (playable.length === 0) return { cardIndex: null };

  let chosen: Card;

  if (difficulty === 'easy') {
    // Easy: random playable card
    chosen = playable[Math.floor(Math.random() * playable.length)];
  } else if (difficulty === 'medium') {
    // Medium: prefer action cards over numbers, save wilds for last
    const actions = playable.filter((c) => ['skip', 'reverse', 'draw2'].includes(c.value));
    const numbers = playable.filter((c) => !isNaN(parseInt(c.value)));
    const wilds = playable.filter((c) => c.value === 'wild' || c.value === 'wild4');

    if (actions.length > 0) chosen = actions[Math.floor(Math.random() * actions.length)];
    else if (numbers.length > 0) chosen = numbers[Math.floor(Math.random() * numbers.length)];
    else chosen = wilds[0];
  } else {
    // Hard: strategic play
    const opponentInDanger = state.players.some(
      (p, i) => i !== playerIndex && p.hand.length <= 2,
    );

    const draw4 = playable.find((c) => c.value === 'wild4');
    const draw2 = playable.find((c) => c.value === 'draw2');
    const skip = playable.find((c) => c.value === 'skip');
    const reverse = playable.find((c) => c.value === 'reverse');
    const wilds = playable.filter((c) => c.value === 'wild');
    const numbers = playable.filter((c) => !isNaN(parseInt(c.value)));

    if (opponentInDanger) {
      // Be aggressive when opponent is close to winning
      chosen = draw4 || draw2 || skip || reverse || numbers[0] || wilds[0] || playable[0];
    } else if (player.hand.length <= 3) {
      // Conserve action cards when close to winning, dump high-value cards first
      chosen = numbers[0] || playable.find((c) => c.value === 'skip') || playable[0];
    } else {
      // Normal play: dump numbers, save action & wild cards for when needed
      chosen = numbers[Math.floor(Math.random() * Math.max(numbers.length, 1))]
        || playable[0];
    }
  }

  const cardIndex = player.hand.findIndex((c) => c.id === chosen.id);
  const chosenColor =
    chosen.value === 'wild' || chosen.value === 'wild4'
      ? chooseColorForAI(player.hand)
      : undefined;

  return { cardIndex, chosenColor };
}
