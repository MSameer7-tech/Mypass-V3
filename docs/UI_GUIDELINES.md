# MyPass UI Design System & Guideline Specification

## 1. Grid, Layout & Spatial Boundaries

| UI Region | Fixed / Elastic Width | Padding / Margins | Radius / Border |
| :--- | :--- | :--- | :--- |
| **Sidebar** | `240px` (Fixed) | `16px 12px` | Right border `1px solid #1E2028` |
| **Vault List Column** | `320px – 340px` (Calibrated) | `16px` Horizontal | Right border `1px solid #1E2028` |
| **Details Inspector** | `560px` (Elastic) | `24px` | Borderless canvas |
| **Vault Card** | Height `74px` | `16px` Horizontal, `12px` Vertical | `12px` radius |
| **Buttons & Field Inputs** | Height `40px` | `12px` Horizontal | `8px` radius |
| **Spatial Rhythm System** | Base Unit `8px` | Gap multipliers: `4px`, `8px`, `16px`, `24px`, `32px` |

---

## 2. Palette & Design Tokens (Dark Mode First)

All components must reference CSS variables defined in `:root` / `.dark`. No ad-hoc hex values allowed in JSX/CSS components.

```css
:root {
  --background: #0F1015;
  --surface-sidebar: #14151B;
  --surface-panel: #181920;
  --surface-card: #1E202A;
  --surface-card-hover: #262834;
  --surface-card-selected: #2D303E;
  
  --border-subtle: #232532;
  --border-focus: #3B82F6;
  
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  
  --accent: #3B82F6;
  --accent-hover: #2563EB;
  --accent-glowing: rgba(59, 130, 246, 0.25);
  
  --danger: #EF4444;
  --danger-surface: rgba(239, 68, 68, 0.15);
  --success: #10B981;
  --success-surface: rgba(16, 185, 129, 0.15);
  --warning: #F59E0B;
  --warning-surface: rgba(245, 158, 11, 0.15);
}
```

---

## 3. Motion & Animation Tokens (Framer Motion)

| Interactivity Target | Transition Duration | Easing / Spring |
| :--- | :--- | :--- |
| **Hover & Active States** | `100ms` | `easeInOut` |
| **Dropdown / Context Menus** | `150ms` | `type: "spring", stiffness: 400, damping: 25` |
| **Dialog & Modal Overlays** | `220ms` | `type: "spring", stiffness: 350, damping: 28` |
| **Screen Unlocking Transition** | `300ms` | `easeInOut` |

---

## 4. Typography & Iconography Rules

- **Primary Font**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `SF Pro Display`, `sans-serif`.
- **Title (Inspector)**: `20px` Bold (`700`), Line height `1.2`.
- **Headline (Card Title)**: `14px` SemiBold (`600`), Line height `1.3`.
- **Body / Field Value**: `13px` Regular (`400`), Line height `1.4`.
- **Caption / Timestamp**: `12px` Muted (`400`), Line height `1.4`.
- **Iconography**: `Lucide React` icons exclusively. No plain emojis, no ad-hoc inline SVGs.
