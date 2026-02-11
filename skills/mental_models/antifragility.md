# Antifragility

Some systems don't just survive stress — they get stronger from it. The opposite of fragile isn't robust; it's antifragile.

## The Triad

- **Fragile:** harmed by volatility, disorder, stress. Wants predictability. (A glass.)
- **Robust:** unaffected by volatility. Survives but doesn't improve. (A rock.)
- **Antifragile:** benefits from volatility, disorder, stress. Gets stronger. (Your immune system, muscles, evolution.)

## Design Principles

- **Barbell strategy:** combine extreme safety with small, high-upside bets. Avoid the middle (moderate risk, moderate return).
- **Optionality:** prefer positions with limited downside and unlimited upside. Options, not obligations.
- **Small reversible bets:** many small experiments beat one large irreversible commitment.
- **Skin in the game:** systems without feedback from consequences become fragile.
- **Via negativa:** improve by removing (fragilities, risks, clutter) more than by adding.

## Application

- **Software:** chaos engineering (Netflix's Chaos Monkey) makes systems antifragile — inject failures to force resilience
- **Teams:** teams that practice incident response get better at it. Teams that avoid incidents get worse.
- **Career:** diverse experience portfolio with small bets on new skills > single specialized bet
- **Architecture:** microservices with circuit breakers are more antifragile than monoliths — one failure strengthens the system's ability to handle the next
