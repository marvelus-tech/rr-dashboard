# Style Lock: Readability Rules

## Type & Contrast Standards

### Font Size Minimums
- **Floor:** All UI labels and body text must be ≥12px
- **No 10px text** anywhere in the interface
- **Headers:** Use larger sizes (16px+) for hierarchy

### Color Contrast (WCAG AA)
- `--text-primary`: `#1a1a1a` (dark ink, primary content)
- `--text-secondary`: `#4a4a4a` (body labels, meets 4.5:1 on white)
- `--text-tertiary`: `#5c5c5c` (supporting text, meets 4.5:1)
- `--text-muted`: `#6e6e6e` (de-emphasized content, meets 4.5:1)

### Gold Usage Restrictions
- **Gold (`#c9a227`) must NOT be used for small body text**
- Gold is reserved for:
  - Rules, dividers, and accent lines
  - Dots and indicators
  - Active chip fills
- If gold text is needed:
  - Use `--gold-dark` (`#a88420`) only
  - Minimum 14px font size
  - Always verify contrast

## Animation Lock

### Text Animation Ban
- **NO shimmer effects on text glyphs**
- NO `background-clip: text` / transparent fill on numbers
- Numbers must be solid ink (`--text-primary`)

### Allowed Animations
- 2px accent bar shimmer (structural, not text)
- Card hover lift effects
- Chip press feedback
- All animations must honor `prefers-reduced-motion`

## Card Reading Order (Critical)

Visual scan path must be:
1. **Niche title** (strong) + **City** (with icon)
2. **Hero metrics:** Monthly fee + Lead value (prominent); Avg job / Recurring (secondary)
3. **Quiet score badge** (16px, muted color, not competing with title)
4. **Status control** (single, clear control)
5. **Collapsed sections** (behind `<details>` disclosures):
   - Target Keyword & Actions
   - Score Breakdown
   - Why This Location
   - SEO Metrics
   - Domain Ideas
   - Action Plan

**Goal:** User skims niche → city → fee in under 1 second.

## Metrics Display

### Labels
- Font size: ≥12px
- Case: Sentence case or light tracking (0.03em max)
- Color: `--text-secondary`
- Weight: 600

### Values
- Font family: **Plus Jakarta Sans** (NOT Playfair)
- Font size: 18-20px
- Weight: 600
- `font-variant-numeric: tabular-nums`
- Dense 2×2 or 4-col grid layout

## Typography Hierarchy

### Primary Content
- Niche title: 22px, weight 700, Playfair Display
- City: 14px, weight 500, secondary color
- Metrics values: 20px, weight 600, Plus Jakarta Sans

### Labels & Supporting Text
- Minimum 12px
- Letter-spacing: 0.02-0.03em (not 0.1em screaming caps)
- Secondary or tertiary color for hierarchy

### Action Counter Badges
- Small circular badges (22px): 12px text minimum
- Balance legibility with space constraints

## Motion & Accessibility

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### Interaction Feedback
- Keep chip press
- Keep card hover lift
- Remove infinite shimmer loops on numbers

## Icon & Accent Colors

### Icon Colors
- Icons paired with text (e.g., location pin) must use `--text-secondary` or darker
- NO gold icons on light backgrounds unless ≥16px and serving as visual accent (not paired with small text)
- Icon opacity: 0.8 for subtle presence without disappearing

### Inline Panels & Sections
- NO dark theme colors (`rgba(0,0,0,...)`, `#888`, `#e0e0e0`) in light theme
- All panels use paper/ink: `var(--surface-warm)` background, `var(--text-primary)` values, `var(--text-secondary)` labels
- Border: `var(--border)` (never white/light borders on light backgrounds)

## Mobile Responsiveness

### Filter Bar
- Reduce padding on mobile: 20px → 16px @ 768px, → 12px @ 480px
- Reduce button size: padding 8/18px → 7/14px @ 768px, → 6/12px @ 480px
- Font size: 13px → 12px on mobile

### Stats KPI Bar
- Desktop: 5-column grid
- Tablet (768px): 3-column grid to prevent orphaned items
- Mobile (480px): 2-column grid

## Testing Checklist

Before publishing changes:
- [ ] No text below 12px
- [ ] All body/label colors pass WCAG AA (4.5:1)
- [ ] No shimmer-clipped text on numbers
- [ ] Cards lead with niche + city + fee (visible immediately)
- [ ] Secondary chrome collapsed by default
- [ ] Data and interactions still work
- [ ] Gold text only at ≥14px with verified contrast
- [ ] `prefers-reduced-motion` honored
- [ ] NO dark theme colors in light theme panels
- [ ] Icons use text-secondary (not gold) when paired with text
- [ ] Mobile: filters don't wrap excessively, KPIs distribute well

---

**Last Updated:** 2026-09-06  
**Applies To:** `index.html`, `dashboard.html`
