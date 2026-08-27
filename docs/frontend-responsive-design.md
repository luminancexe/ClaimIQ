# Frontend Responsive Design & Layout Verification

## 1. Viewport Breakpoints

The ClaimIQ interface is built using responsive Tailwind grid and flexbox primitives verified across 5 standard viewport profiles:

| Profile | Width | Layout Adaptation |
|---|---|---|
| **Mobile Phone** | `375px` | Sidebar collapses to drawer overlay; metric cards stack in 1 column; data tables enable horizontal scroll |
| **Tablet** | `768px` | Metric cards stack in 2 columns; navigation drawer toggle available; charts scale dynamically |
| **Small Desktop** | `1024px` | Persistent sidebar collapses or expands; grid switches to 3–4 columns; full table headers visible |
| **Desktop Console** | `1440px` | Standard multi-column operations dashboard; side-by-side charts and data tables |
| **Large Control Room** | `1920px` | Maximized workspace with max-width container centering content with high data density |

---

## 2. Table & Chart Adaptability
- **Horizontal Scroll Protection**: All `DataTable` components are wrapped in overflow containers (`overflow-x-auto`) to eliminate horizontal page breakages on narrow viewports.
- **Recharts Responsiveness**: All charts use `ResponsiveContainer` with fluid widths (`100%`) and bounded vertical heights (220px to 320px).
