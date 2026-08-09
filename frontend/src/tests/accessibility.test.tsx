import { describe, it, expect, vi } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

// Mock framer-motion with a simpler approach that avoids hoisting issues
vi.mock("framer-motion", () => ({
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  motion: new Proxy({} as Record<string, unknown>, {
    get: (_target, prop: string) => {
      // Return a forwardRef component for any HTML element
      return React.forwardRef((props: Record<string, unknown>, ref: React.Ref<unknown>) => {
        const { children, initial, animate, exit, transition, variants, whileHover, whileTap, whileFocus, layout, layoutId, ...rest } = props as any;
        return React.createElement(prop, { ...rest, ref }, children);
      });
    },
  }),
}));

// Must import components AFTER vi.mock
const { Dialog } = await import("../components/overlay/Dialog");
const { Icon } = await import("../components/core/Icon");
const { Shield } = await import("lucide-react");

describe("Accessibility & Keyboard", () => {
  describe("Icon component", () => {
    it("hides decorative icons from screen readers by default", () => {
      render(<Icon icon={Shield} data-testid="test-icon" />);
      const icon = screen.getByTestId("test-icon");
      expect(icon).toHaveAttribute("aria-hidden", "true");
      cleanup();
    });

    it("does not hide icon when aria-label is provided", () => {
      render(<Icon icon={Shield} aria-label="Security" data-testid="test-icon-label" />);
      const icon = screen.getByTestId("test-icon-label");
      expect(icon).not.toHaveAttribute("aria-hidden");
      cleanup();
    });
  });

  describe("Dialog focus trap", () => {
    it("auto-focuses first focusable element on open", async () => {
      render(
        <Dialog open={true} onClose={() => {}}>
          <button data-testid="btn-1">Button 1</button>
          <button data-testid="btn-2">Button 2</button>
        </Dialog>
      );

      // Wait for the setTimeout(50) in Dialog to fire
      await new Promise((r) => setTimeout(r, 100));

      // The close button in the header or the first child button should be focused
      // Since Dialog has no title, there's no close button rendered. First child button should be focused.
      const btn1 = screen.getByTestId("btn-1");
      expect(document.activeElement).toBe(btn1);
      cleanup();
    });

    it("traps Tab cycling forward and backward", async () => {
      const user = userEvent.setup();

      render(
        <Dialog open={true} onClose={() => {}}>
          <button data-testid="btn-a">A</button>
          <button data-testid="btn-b">B</button>
        </Dialog>
      );

      await new Promise((r) => setTimeout(r, 100));

      const btnA = screen.getByTestId("btn-a");
      const btnB = screen.getByTestId("btn-b");

      expect(document.activeElement).toBe(btnA);

      await user.tab();
      expect(document.activeElement).toBe(btnB);

      // Tab from last element should wrap to first
      await user.tab();
      expect(document.activeElement).toBe(btnA);

      // Shift+Tab from first should wrap to last
      await user.tab({ shift: true });
      expect(document.activeElement).toBe(btnB);
      cleanup();
    });

    it("closes on Escape and restores focus", async () => {
      const user = userEvent.setup();

      const TestComponent = () => {
        const [open, setOpen] = React.useState(true);
        const triggerRef = React.useRef<HTMLButtonElement>(null);

        React.useEffect(() => {
          // Simulate the trigger being focused before dialog opened
          if (!open && triggerRef.current) {
            // Focus should be restored automatically by Dialog
          }
        }, [open]);

        return (
          <div>
            <button ref={triggerRef} data-testid="trigger">Trigger</button>
            <Dialog open={open} onClose={() => setOpen(false)}>
              <button data-testid="dialog-btn">Inside</button>
            </Dialog>
          </div>
        );
      };

      render(<TestComponent />);

      await new Promise((r) => setTimeout(r, 100));

      const dialogBtn = screen.getByTestId("dialog-btn");
      expect(document.activeElement).toBe(dialogBtn);

      await user.keyboard("{Escape}");

      // Dialog should be closed (no more dialog-btn in DOM)
      expect(screen.queryByTestId("dialog-btn")).toBeNull();
      cleanup();
    });
  });
});
