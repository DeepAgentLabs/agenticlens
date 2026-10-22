---
name: Clinical Intelligence Daylight
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#3f4850'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#707881'
  outline-variant: '#bfc7d2'
  surface-tint: '#006398'
  primary: '#006194'
  on-primary: '#ffffff'
  primary-container: '#007bb9'
  on-primary-container: '#fdfcff'
  inverse-primary: '#93ccff'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#006948'
  on-tertiary: '#ffffff'
  tertiary-container: '#00855d'
  on-tertiary-container: '#f5fff7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
  mono-metric:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-md: 1.5rem
  gutter-lg: 2rem
  margin: 1rem
  margin-md: 1.5rem
  margin-lg: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
---

## Brand & Style

This design system is engineered for enterprise healthcare environments where high-stakes clinical workflows interface directly with ambient AI observability. It resolves the tension between dense, mission-critical telemetry and the serene, distraction-free clarity required by chief medical officers, informaticists, and clinical operations executives.

The design movement bridges **Corporate Precision** and **Clinical Modernism**. It rejects the noisy neon gradients and dark skins of generic developer consoles in favor of an authoritative, luminous "Daylight" canvas. The aesthetic draws upon the surgical accuracy of diagnostic imaging equipment and the frictionless micro-typographic hierarchy of high-end financial architecture (such as Stripe and Linear). 

Every interaction must project stability, institutional trust, and sovereign precision. The UI evokes clinical calm, eliminating cognitive fatigue during long hospital shifts and deep telemetry investigations. Micro-interactions are deliberate and crisp, signaling operational integrity and real-time validation without gimmicks.

## Colors

The daylight color architecture uses high-reflectance, cool-spectrum porcelain surfaces to maximize legibility across varying hospital lighting environments. Colors are categorized strictly by semantic tier:

* **Foundations & Slate Neutrals**: 
  * App Canvas: `#F8FAFC` (Slate 50) establishes a clean foundation.
  * Container & Surface White: `#FFFFFF` (Pure White) houses cards, data grids, and modals.
  * Structural Borders: `#E2E8F0` (Slate 200) for standard card lines; `#CBD5E1` (Slate 300) for focused dividers and active input perimeters.
  * Text Dominance: `#0F172A` (Slate 900) for primary data and high-contrast labels; `#334155` (Slate 700) for body narrative; `#64748B` (Slate 500) for metadata, table column headers, and inactive states.

* **Primary & Secondary (AI Intelligence Engine)**:
  * Primary Sapphire/Cyan (`#0284C7`): Used for ambient AI inference states, active data-stream triggers, and core navigation indicators.
  * Deep Secondary Blue (`#2563EB`): Applied to primary high-confidence operational action items, deep interactive charts, and system selection anchors.

* **Clinical Semantic Accents**:
  * Clinical Emerald (`#059669` base, `#ECFDF5` background tint): Reserved for validated algorithmic confidence, automated pipeline approvals, and positive compliance status.
  * Alert Amber (`#D97706` base, `#FFFBEB` background tint): Designates Human-in-the-Loop (HITL) triage requests, latency warnings, and schema reconciliation requirements.
  * Crimson Risk (`#DC2626` base, `#FEF2F2` background tint): Exclusively signals critical SLA breaches, clinical hallucination flags, or dropped patient events.

## Typography

Typography prioritizes tabular legibility and rapid scanning under operational stress. Plus Jakarta Sans handles high-level module architecture and top-level clinical metrics, providing balanced geometry and an approachable yet authoritative posture. Inter provides the underlying infrastructure for continuous clinical notes, pipeline traces, dense observation tables, and form inputs.

Numerical data, token telemetry metrics, patient encounter IDs, and latency readouts must always enforce tabular numbers (`tnum`) and slashed zeros via OpenType features (`font-feature-settings: "cv02", "cv03", "cv04", "cv11", "tnum" 1`). Never apply heavy display weights to body text; let contrast be governed by Slate tonal shifts (`#0F172A` vs `#64748B`) rather than aggressive font-weight swings.

## Layout & Spacing

The architecture operates on a baseline 4px/8px hybrid grid system designed for expansive clinical cockpit dashboards while remaining responsive across handheld mobile tablet carts.

* **Grid Mechanics**: A 12-column fluid grid system with structural gutters scaling from `1rem` on compact displays up to `2rem` on ultra-wide clinical monitors (`1440px+`). Outer canvas margin pins at `2.5rem` on enterprise desktop monitors to prevent edge-to-edge eye travel.
* **Component Padding Rhythm**: High data density requires strict spatial discipline. Internal card pads utilize `space-xl` (`1.5rem`) for section wrappers and `space-md` (`0.75rem`) for dense cell clusters and metric readouts.
* **Reflow Directives**:
  * **Desktop (1280px+)**: Primary navigation remains persistent in an 80px compressed rail or 240px expanded navigation hierarchy. Observability timelines and streaming patient transcription run side-by-side in a multi-pane split.
  * **Tablet (768px - 1279px)**: Side-by-side operational panes collapse into stacked drawers with accessible segment switchers.
  * **Mobile (< 768px)**: Strict 1-column flow with persistent fixed bottom navigation; data tables convert to summary cards with deep links to full telemetry views.

## Elevation & Depth

This system avoids deep blur drops, heavy drop shadows, or opaque black overlays. Depth is rendered primarily through **Tonal Surface Layering** paired with calibrated, single-pixel slate borders and razor-sharp micro-shadows.

* **Surface Tiering**:
  * Level 0 (Base Canvas): `#F8FAFC`
  * Level 1 (Primary Surface / Cards): `#FFFFFF` bounded by a 1px border of `#E2E8F0`.
  * Level 2 (Floating Popovers / Tooltips / Dropdowns): `#FFFFFF` bounded by `#CBD5E1` with a micro-offset shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
  * Level 3 (Critical Modals / Sliding Drawers): `#FFFFFF` elevated with `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)`.

* **The Ambient Light Edge**:
  Elevated card components incorporate an internal white highlight border: `box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 1)`. This creates a tactile, medical-grade hardware feel that gives components physical presence without visual clutter.

## Shapes

The system enforces a **Soft (Level 1)** geometric standard. This geometry strikes an intentional balance: sharp enough to communicate mathematical rigour and clinical compliance, yet rounded enough to maintain a contemporary, humanized software feel.

* **Base Radius (0.25rem / 4px)**: Applied to table cells, inline chips, status indicators, and micro-form inputs.
* **Medium Radius (0.375rem / 6px)**: Applied to buttons, segmented controls, standard text fields, and list group selections.
* **Large Radius (0.5rem / 8px)**: Applied to primary content modules, KPI display panels, flyout tooltips, and data grid cards.
* **Pill Geometry (9999px)**: Strictly preserved for runtime state badges, machine learning confidence score pills, and hit-counter labels.

## Components

### Buttons
* **Primary**: `#0284C7` background, solid white text, subtle top-edge bevel via `inset 0 1px 0 rgba(255, 255, 255, 0.2)`. Hover shifts to `#0369A1`. Height: 36px (compact desktop) or 44px (touch clinical carts).
* **Secondary**: Pure `#FFFFFF` surface with a 1px `#E2E8F0` border, text in `#334155`. Hover transitions background to `#F8FAFC` and border to `#CBD5E1`.
* **Destructive**: `#FEF2F2` background, 1px border in `#FCA5A5`, text in `#DC2626`. Hover changes to `#DC2626` background with solid white text.

### Interactive Chips & Confidence Pills
* **Confidence Pill (AI Observation)**: Rendered in full-rounded format (`9999px`). Background: `#F0F9FF`, text: `#0369A1`, border: `1px solid #BAE6FD`. Displays a trailing percentage dot (e.g., "99.4% Verified") paired with a 6px status light.
* **HITL Triage Chip**: Background: `#FFFBEB`, text: `#B45309`, border: `1px solid #FDE68A`. Used for records awaiting physician sign-off.

### Tables & Data Grids
* Tables are the centerpiece of the observability experience. 
* Headers: `#F8FAFC` background, height 36px, typography `label-sm` (`#64748B`), uppercase with `0.05em` letter-spacing. Bottom border `1px solid #CBD5E1`.
* Rows: `#FFFFFF` base, height 44px. Alternating hover fill `#F8FAFC`. Active selection row highlights with `#F0F9FF` background and a 2px left border accent in `#0284C7`. Cell padding: horizontal `1rem`, vertical `0.5rem`.

### Form Inputs & Selectors
* Inputs feature a pure `#FFFFFF` background with a 1px border in `#CBD5E1`. Height: 36px. Typography: `body-md` in `#0F172A`. Placeholder: `#94A3B8`.
* Focus State: Border transitions to `#0284C7` with a non-blur focus ring: `0 0 0 1px #0284C7`.

### Selection Controls (Checkboxes & Radios)
* Square checkboxes (4px radius) and round radios (full circle) measuring 16x16px. Inactive state: 1.5px border in `#CBD5E1`. Checked state: Background fills `#0284C7` displaying a crisp white micro-tick.

### Cards & Telemetry Containers
* Crisp `#FFFFFF` surface enclosed by a 1px border of `#E2E8F0`. 
* Card Header: Dedicated 48px height with flex alignment, dividing the content body with a 1px bottom border of `#F1F5F9`.
* Header typography: `headline-sm` with optional right-aligned micro-actions and latency timestamp counters.