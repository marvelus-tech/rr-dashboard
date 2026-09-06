# Style Contract — Rank & Rent Dashboard

**Updated:** 2026-09-06  
**Status:** Locked for current iteration

## Design Principle
This dashboard is a light, paper-and-ink craft tool for evaluating website landlord opportunities. It is NOT a dark SaaS app, NOT a flashy consumer interface, NOT a purple gradient startup product.

## Color Roles

### Foundation
- **Paper** `--bg: #faf8f3` — main background (warm off-white)
- **Surface** `--surface: #ffffff` — card/widget backgrounds
- **Ink** `--text-primary: #1a1a1a` — body copy, headings

### Accent
- **Gold** `--gold: #c9a227` — primary accent for priority, CTAs, active states
- **Gold Soft** `--gold-soft: rgba(201, 162, 39, 0.08)` — backgrounds for selected/active chips
- **Border** `--border: rgba(139, 119, 89, 0.12)` — default dividers and card edges

### Utility
- **Green** `--green: #2d7d46` — positive signals (recurring service, excellent scores)
- **Danger** `--danger: #b54242` — warnings, penalties
- **Secondary Text** `--text-secondary: #5c5c5c` — labels, metadata
- **Tertiary Text** `--text-tertiary: #8a8a8a` — less important info

## Typography

### Families
- **Display:** `Playfair Display` — headings, large numbers
- **Body:** `Plus Jakarta Sans` — UI text, data labels, buttons

### Scale (modular, 1.125 ratio base)
- **XL:** 52px / 600 weight — page title
- **L:** 40px / 600 weight — KPI numbers
- **M:** 24px / 600 weight — card titles (niche name)
- **Base:** 17px / 400 weight — subtitles, descriptions
- **SM:** 14px / 500 weight — metric labels
- **XS:** 13px / 500 weight — buttons, filters
- **XXS:** 11px / 700 weight — eyebrow, badges

### Rules
- Use `Playfair Display` for numerals and headings to create editorial hierarchy
- Use `Plus Jakarta Sans` for UI controls, labels, and data
- Maintain optical balance: large numbers need less tracking, small caps need more

## Spacing (8px grid)
- **Micro:** 4px — tight pairs (icon + label)
- **XS:** 8px — related items within a group
- **SM:** 12px — between distinct UI elements
- **Base:** 16px — comfortable reading separation
- **M:** 20px — group-to-group spacing
- **L:** 28px — card internal padding
- **XL:** 48px — section separation

## Radius
- **Pills:** `100px` — filter chips, badges
- **SM:** `12px` — small widgets, dropdowns
- **Base:** `20px` — cards, stat panels
- **LG:** `24px` — hero panels (if needed)

## Motion Budget

### Allowed
1. **Chip press:** scale(0.97) + opacity 0.7 for 150ms
2. **Card hover:** translateY(-3px) over 300ms cubic-bezier(0.34, 1.56, 0.64, 1)
3. **Dropdown open:** opacity 0→1 + translateY(-8px→0) over 200ms ease-out

### Forbidden
- Scale-from-zero entrances (feels gimmicky)
- Rotation or skew (breaks craft aesthetic)
- Parallax or scroll-driven (too playful)
- Long multi-step choreography (>500ms)

### Accessibility
- **ALWAYS** wrap animated elements in `@media (prefers-reduced-motion: no-preference)`
- Provide instant fallback (no animation) when user prefers reduced motion

## Anti-Cliché Blocklist

These patterns are **banned** to maintain editorial craft identity:

❌ Purple-to-pink gradients  
❌ Inter as the only typeface  
❌ Emoji as icon replacements (🚀💡✨)  
❌ Unsolicited dark mode (light is default)  
❌ Glassmorphism (backdrop-filter blur)  
❌ Neumorphism (soft inner shadows)  
❌ Bento grid layouts (unless user-requested)  
❌ "Premium" pill badges in neon colors  

## Card Density Goal
Each opportunity card should:
- Be scannable at a glance (niche + city + key metrics)
- Use ≤ 200px vertical height on desktop (target: 160-180px)
- Show metrics in a 2×2 or 4-column inline grid (not vertical stack)
- Eliminate empty wells and unnecessary padding
- Reserve whitespace for hierarchy, not decoration

## Breakpoints
- **Mobile:** 320–767px (single column, simplified controls)
- **Tablet:** 768–1023px (2-column grid)
- **Desktop:** 1024px+ (3-column grid, full KPI row)

## Hierarchy Rules
1. **Page title > Subtitle > Date** — clear descending importance
2. **KPI numbers > Labels** — numbers are Playfair Display XL, labels are small caps
3. **Filter chips** — flat until active, then gold background + dark gold text
4. **Card title (niche)** — largest element inside card, Playfair Display M
5. **City** — secondary color, smaller, below niche
6. **Metrics** — dense grid, equal visual weight

## Implementation Notes
- All colors are defined in `:root` CSS variables
- Motion must be opt-in via `prefers-reduced-motion: no-preference`
- Maintain 4.5:1 contrast minimum for WCAG AA
- Test hit targets: minimum 44×44px for interactive elements on mobile
- Avoid inline styles except for dynamic JS-injected values
