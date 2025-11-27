# Component Library Documentation

This document describes the reusable UI components used throughout Dr. Longevity.

## Design Principles

- **Consistency**: All components follow the same visual language
- **Accessibility**: Keyboard navigation, focus states, proper contrast
- **Responsiveness**: Components adapt to mobile/tablet/desktop
- **Simplicity**: No over-engineering - just what's needed

---

## Components

### 1. Metric Card

**Purpose**: Display key performance indicators with optional trends

**Usage:**
```python
st.metric("FTP", "216W", delta="+5W", help="Functional Threshold Power")
```

**Variants:**
- **With positive delta**: Shows green arrow (improvement)
- **With negative delta**: Shows red arrow (decline)
- **With help text**: Hover tooltip for explanation
- **With sparkline**: Add chart below for visual trend

**When to use:**
- KPIs and performance metrics (FTP, VO2 Max)
- Counts and totals (workouts, hours)
- Comparisons (YoY, MoM changes)

**When NOT to use:**
- Long text content
- Raw data tables
- Complex visualizations

**Styling:**
- Background: White card with soft shadow
- Border radius: 16px
- Padding: 1.5rem
- Font size: 2.5rem (metric value)

---

### 2. Tabs

**Purpose**: Navigate between major sections of the app

**Usage:**
```python
tab1, tab2 = st.tabs(["📊 Fitness Metrics", "🏗️ Technical Architecture"])

with tab1:
    st.header("Content")
```

**Design:**
- Container background: Light gray (#f8f9fa)
- Active tab: Blue background with white text
- Hover state: Gray background
- Padding: 1rem × 2rem
- Font size: 1.1rem (bold)

**When to use:**
- Top-level navigation (2-5 sections)
- Mutually exclusive content areas
- Equal-importance sections

**When NOT to use:**
- For steps in a process (use progress indicator)
- More than 5 tabs (consider sidebar navigation)
- Nested navigation (tabs within tabs)

---

### 3. Expander

**Purpose**: Show/hide detailed content to reduce clutter

**Usage:**
```python
with st.expander("ℹ️ Why I Built This App", expanded=True):
    st.markdown("Content here")
```

**Variants:**
- `expanded=True`: Open by default
- `expanded=False`: Collapsed by default

**When to use:**
- Optional explanatory content
- FAQ sections
- Advanced settings
- Secondary information

**When NOT to use:**
- Critical information users must see
- Primary navigation
- Form inputs (should always be visible)

**Styling:**
- Background: White
- Border: 1px solid #E8E8E0
- Border radius: 12px
- Box shadow: Subtle (0 2px 6px rgba(0,0,0,0.04))

---

### 4. Buttons

**Purpose**: Primary and secondary actions

**Usage:**
```python
# Primary action
st.button("📥 Sync Garmin Data", type="primary", use_container_width=True)

# Secondary action
st.button("🔄 Refresh Data", use_container_width=True)
```

**Variants:**
- **Primary**: Blue background, white text (main actions)
- **Secondary**: Transparent with blue border (secondary actions)

**Styling:**
- Border radius: 50px (pill-shaped)
- Padding: 0.75rem × 2rem
- Hover: Lift effect (translateY -1px) + shadow
- Active: Press down (translateY 0)
- Transition: 200ms ease

**When to use:**
- Actions (sync, refresh, submit)
- Navigation to external pages
- Triggering computations

**When NOT to use:**
- For navigation between app sections (use tabs)
- For selections (use radio/selectbox)

---

### 5. Data Tables

**Purpose**: Display tabular data with sorting/filtering

**Usage:**
```python
st.dataframe(
    df[['Date', 'Workout', 'Duration', 'Distance']],
    use_container_width=True,
    hide_index=True,
    height=400
)
```

**Styling:**
- Border radius: 12px
- Box shadow: 0 2px 8px rgba(0,0,0,0.06)
- Max height: 400px (scrollable)

**When to use:**
- Lists of workouts/activities
- Recent logs (food, water)
- Any tabular data > 5 rows

**When NOT to use:**
- Summary statistics (use metrics)
- Key numbers (use metric cards)
- < 5 rows (just display inline)

---

### 6. Charts (Plotly)

**Purpose**: Visualize trends and distributions

**Usage:**
```python
fig = go.Figure()
fig.add_trace(go.Bar(...))
st.plotly_chart(fig, use_container_width=True)
```

**Chart Types Used:**
- **Bar charts**: Zone distribution, time in zones
- **Line charts**: Trends over time (FTP, VO2 Max)
- **Sparklines**: Compact trends in metric cards
- **Pie charts**: Polarized training analysis
- **Heatmaps**: GPS route visualization (Folium)

**Color Palette:**
```python
COLORS = {
    'primary': '#0066CC',
    'secondary': '#FF6B35',
    'zone1': '#3b82f6',  # Blue (easy)
    'zone2': '#10b981',  # Green (endurance)
    'zone3': '#f59e0b',  # Yellow (tempo)
    'zone4': '#f97316',  # Orange (threshold)
    'zone5': '#ef4444',  # Red (VO2 max)
}
```

**When to use:**
- Showing trends over time
- Comparing distributions
- Geographic data

---

### 7. Info/Warning/Error Boxes

**Purpose**: Display contextual messages

**Usage:**
```python
st.info("💡 Two ways to use this app...")
st.success("✅ Sync complete!")
st.warning("⚠️ Data is stale - consider syncing")
st.error("❌ Error connecting to database")
```

**Styling:**
- Border radius: 12px
- No border (background color only)
- Padding: 1.25rem

**Color Meanings:**
- **Info** (blue): Helpful information
- **Success** (green): Completed actions
- **Warning** (yellow): Caution/attention needed
- **Error** (red): Failures/problems

---

## Typography

### Font Family
- **Primary**: Inter (sans-serif) - body text, UI elements
- **Headers**: Inter (bold) - h1, h2, h3

### Font Scale
```python
--font-size-sm: 0.875rem    # 14px - Captions
--font-size-base: 1rem      # 16px - Body text
--font-size-lg: 1.125rem    # 18px - Large text
--font-size-xl: 1.25rem     # 20px - Subheadings
--font-size-2xl: 1.5rem     # 24px - Small headers
--font-size-3xl: 2rem       # 32px - Large headers, metrics
```

### Line Heights
```python
--line-height-tight: 1.2     # Headlines, metrics
--line-height-normal: 1.5    # Subheadings, UI
--line-height-relaxed: 1.6   # Body text
```

---

## Color System

### Primary Colors
```python
Primary: #0066CC      # CTAs, links, active states
Secondary: #FF6B35    # Highlights, accents
Success: #059669      # Positive feedback
Warning: #F59E0B      # Cautions
Danger: #ef4444       # Errors, critical actions
Info: #8B5CF6         # Informational messages
```

### Training Zones
```python
Zone 1: #3b82f6   # Blue - Recovery/Easy
Zone 2: #10b981   # Green - Endurance
Zone 3: #f59e0b   # Yellow - Tempo
Zone 4: #f97316   # Orange - Threshold
Zone 5: #ef4444   # Red - VO2 Max
```

---

## Spacing

### Scale (8px base unit)
```python
--space-xs: 4px       # 0.25rem
--space-sm: 8px       # 0.5rem
--space-md: 16px      # 1rem
--space-lg: 24px      # 1.5rem
--space-xl: 32px      # 2rem
--space-2xl: 48px     # 3rem
```

### Usage
- **Padding inside cards**: 1.5rem (24px)
- **Margin between sections**: 2rem (32px)
- **Gap between columns**: 1rem (16px)
- **Button padding**: 0.75rem × 2rem

---

## Accessibility

### Focus States
All interactive elements have visible focus indicators:
```css
:focus-visible {
    outline: 3px solid #0066CC;
    outline-offset: 2px;
    border-radius: 4px;
}
```

### Keyboard Navigation
- **Tab**: Move forward through interactive elements
- **Shift+Tab**: Move backward
- **Enter/Space**: Activate buttons
- **Arrow keys**: Navigate within components

### Color Contrast
All text meets WCAG AA standards:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- Interactive elements: 3:1 minimum

---

## Responsive Breakpoints

### Mobile (< 768px)
- Single column layout
- Reduced font sizes
- Increased touch targets (min 44×44px)
- Stacked columns

### Tablet/Desktop (≥ 768px)
- Multi-column layouts
- Full typography scale
- Hover states enabled

---

## Best Practices

### Do's ✅
- Use consistent spacing (spacing scale)
- Follow the color system
- Add help text to complex metrics
- Test keyboard navigation
- Keep text readable (line-height: 1.6)

### Don'ts ❌
- Don't create one-off colors
- Don't use hard-coded pixel values
- Don't skip accessibility features
- Don't make text too small (< 14px)
- Don't use more than 3 font sizes on one screen

---

## Contributing

When adding new components:
1. Follow existing patterns
2. Use CSS variables (not hard-coded values)
3. Add documentation to this file
4. Test keyboard navigation
5. Verify color contrast
6. Test on mobile

---

**Last Updated**: November 2025
