# 🃏 UNO — The Card Game

A full-stack, browser-based UNO card game built with **Next.js 15**, **TypeScript** (strict), and **Tailwind CSS**. Features a dark neon/glassmorphism visual theme, animated card play, AI opponents at three difficulty tiers, synthesized sound effects, and a complete implementation of classic UNO rules.

---

## ✨ Features

- **Complete UNO rules** — number matching, color matching, Skip, Reverse, Draw Two, Wild, Wild Draw Four
- **3 difficulty levels** — Easy (1 CPU), Medium (2 CPUs), Hard (3 CPUs) — each with smarter AI strategy
- **AI auto-play** — opponents play automatically with natural thinking delays
- **Color picker** — animated modal for choosing the active color after a Wild card
- **Synthesized sound effects** — Web Audio API (no external audio files) with on/off toggle
- **Confetti celebration** — canvas-confetti burst when the player wins
- **Persistent scores** — round scores accumulate; best score saved to localStorage
- **Responsive layout** — works on mobile, tablet, and desktop without horizontal scrolling
- **Framer Motion animations** — card deal, play, draw, and modal transitions
- **Neon glassmorphism theme** — dark background, colored card glows, pulsing highlights
- **Themed SVG favicon**
- **Vercel-ready** — zero extra configuration needed

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript 5 (strict mode) |
| Styling | Tailwind CSS v3 |
| Animations | Framer Motion |
| Sound | Web Audio API (synthesized, no files) |
| Confetti | canvas-confetti |
| State | React hooks (`useState`, `useEffect`, `useCallback`) |
| Persistence | `localStorage` via custom hook |

---

## 🎮 Controls

### Desktop (mouse)
| Action | Input |
|---|---|
| Play a card | Click the card |
| Draw a card | Click the draw pile |
| Play drawn card | Click **Play** in the prompt |
| Pass turn | Click **Pass** in the prompt |
| Pick color (wild) | Click a color button in the modal |

### Mobile (touch)
All actions are touch-friendly large tap targets. No keyboard required.

---

## 📐 Project Structure

```
├── app/
│   ├── layout.tsx              # Root layout & metadata
│   ├── page.tsx                # Main page (start screen ↔ game board)
│   └── globals.css             # Global styles
├── components/
│   ├── game/
│   │   ├── Card.tsx            # Single UNO card (front & back)
│   │   ├── PlayerHand.tsx      # Human player's hand
│   │   ├── AIHand.tsx          # AI face-down hand
│   │   ├── DrawPile.tsx        # Draw pile with click-to-draw
│   │   ├── DiscardPile.tsx     # Discard pile with flip animation
│   │   ├── ColorPicker.tsx     # Wild color selection modal
│   │   ├── GameOverModal.tsx   # End-of-round overlay
│   │   ├── ScoreBoard.tsx      # Header score display
│   │   ├── GameStartScreen.tsx # Difficulty selection screen
│   │   └── GameBoard.tsx       # Main game layout
│   └── ui/
│       └── Button.tsx          # Reusable animated button
├── hooks/
│   ├── useUnoGame.ts           # Core game state machine
│   ├── useSound.ts             # Web Audio synthesizer
│   └── useLocalStorage.ts      # SSR-safe localStorage hook
├── lib/
│   ├── types.ts                # All TypeScript interfaces & enums
│   ├── deck.ts                 # Deck creation, shuffling, dealing
│   ├── rules.ts                # Card legality & scoring helpers
│   └── ai.ts                   # AI move selection (easy / medium / hard)
└── public/
    └── favicon.svg             # Themed SVG favicon
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd uno

# 2. Install dependencies
npm install

# 3. Start the dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ Deploy to Vercel

```bash
# Install Vercel CLI (once)
npm i -g vercel

# Deploy from project root
vercel
```

Or push to GitHub and connect the repo at [vercel.com](https://vercel.com) — it will auto-deploy on every push with no extra configuration.

---

## 📜 UNO Rules Reference

| Card | Effect |
|---|---|
| 0–9 | Match by number or color |
| Skip | Next player loses their turn |
| Reverse | Reverses play direction (acts as Skip in 2-player) |
| Draw Two | Next player draws 2 cards and is skipped |
| Wild | Play on anything; choose any color |
| Wild Draw Four | Next player draws 4 and is skipped; you choose color |

- If you cannot play, draw one card; if it is playable you may play it, otherwise pass.
- First player to empty their hand wins the round.
- Points are tallied from losers' remaining cards (numbers = face value, actions = 20, wilds = 50).

---

## 📄 License

MIT
