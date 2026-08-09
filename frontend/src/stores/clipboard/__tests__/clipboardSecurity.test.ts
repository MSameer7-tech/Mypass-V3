import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useClipboardStore } from '../useClipboardStore';

// Mock navigator.clipboard
const mockClipboard = {
  text: "",
  writeText: vi.fn(async (t) => {
    mockClipboard.text = t;
  }),
  readText: vi.fn(async () => mockClipboard.text)
};

Object.assign(navigator, {
  clipboard: mockClipboard
});

describe('12.4.1 Clipboard Security', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockClipboard.text = "";
    mockClipboard.writeText.mockClear();
    mockClipboard.readText.mockClear();
    useClipboardStore.setState({ lastCopiedValue: null, clearTimeoutId: null });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('Clipboard Timeout: clears after configured timeout', async () => {
    const store = useClipboardStore.getState();
    await store.copy('secret_password', 30);
    
    expect(mockClipboard.text).toBe('secret_password');
    expect(useClipboardStore.getState().lastCopiedValue).toBe('secret_password');

    // Fast-forward 29 seconds - should still be there
    vi.advanceTimersByTime(29000);
    expect(mockClipboard.text).toBe('secret_password');

    // Fast-forward 1 more second - should clear
    vi.advanceTimersByTime(1000);
    
    // We need to wait for promises to resolve inside the timer callback
    await vi.runAllTimersAsync();
    
    expect(mockClipboard.text).toBe('');
    expect(useClipboardStore.getState().lastCopiedValue).toBeNull();
  });

  it('Clipboard Overwrite Safety: does not clear unrelated content', async () => {
    const store = useClipboardStore.getState();
    await store.copy('secret_password', 30);
    
    expect(mockClipboard.text).toBe('secret_password');

    // User copies something else externally
    mockClipboard.text = 'unrelated_email@example.com';

    // Fast-forward 30 seconds
    vi.advanceTimersByTime(30000);
    await vi.runAllTimersAsync();

    // The clipboard should NOT be cleared because it no longer matches 'secret_password'
    expect(mockClipboard.text).toBe('unrelated_email@example.com');
    // But the store should still clean up its own state
    expect(useClipboardStore.getState().lastCopiedValue).toBeNull();
  });

  it('Lock Scrubbing: clears immediately on manual lock (clearIfOwned)', async () => {
    const store = useClipboardStore.getState();
    await store.copy('secret_password', 30);
    expect(mockClipboard.text).toBe('secret_password');

    // Simulate lock scrub
    await store.clearIfOwned();
    expect(mockClipboard.text).toBe('');
    expect(useClipboardStore.getState().lastCopiedValue).toBeNull();
  });

  it('App Close Scrub: clears only if owned', async () => {
    const store = useClipboardStore.getState();
    await store.copy('secret_password', 30);
    
    // Simulate close scrub
    await store.clearIfOwned();
    expect(mockClipboard.text).toBe('');

    // Now copy something else
    await store.copy('secret2', 30);
    mockClipboard.text = 'unrelated_content';
    
    // Simulate close scrub again
    await store.clearIfOwned();
    // It should not clear unrelated content
    expect(mockClipboard.text).toBe('unrelated_content');
  });
});
