/**
 * Core motion tokens for MyPass.
 * These centralize all timing and easing values to ensure a consistent, 
 * native-feeling desktop experience across the application.
 */

export const MOTION_TOKENS = {
  // Interaction durations (in seconds for Framer Motion)
  duration: {
    press: 0.1,         // 100ms - Buttons, fast feedback
    hover: 0.15,        // 150ms - Subtle lift, color transition
    toggle: 0.2,        // 200ms - Toggles, dropdowns, popovers
    transition: 0.25,   // 250ms - Modals, page transitions, theme shifts
    stateChange: 0.3,   // 300ms - Major state changes (Lock/Unlock)
  },

  // Easing curves
  ease: {
    out: "easeOut",
    inOut: "easeInOut",
  },

  // Standard spring configurations for physical-feeling components
  spring: {
    subtle: { type: "spring", stiffness: 400, damping: 30 },
    snappy: { type: "spring", stiffness: 450, damping: 25 },
  }
} as const;
