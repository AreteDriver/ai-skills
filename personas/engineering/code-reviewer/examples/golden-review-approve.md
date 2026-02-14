# Golden Example: Clean Approval

This example shows what a review looks like when code is solid and the
reviewer approves with minor suggestions. The key: don't manufacture
issues just to seem thorough.

## Input: PR diff

```typescript
// src/services/cache.ts — Add TTL-based cache invalidation

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

export class TTLCache<T> {
  private store = new Map<string, CacheEntry<T>>();
  private readonly defaultTTL: number;

  constructor(defaultTTLMs: number = 60_000) {
    this.defaultTTL = defaultTTLMs;
  }

  get(key: string): T | undefined {
    const entry = this.store.get(key);
    if (!entry) return undefined;

    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return undefined;
    }

    return entry.value;
  }

  set(key: string, value: T, ttlMs?: number): void {
    this.store.set(key, {
      value,
      expiresAt: Date.now() + (ttlMs ?? this.defaultTTL),
    });
  }

  delete(key: string): boolean {
    return this.store.delete(key);
  }

  clear(): void {
    this.store.clear();
  }

  get size(): number {
    return this.store.size;
  }
}
```

```typescript
// src/services/cache.test.ts

describe("TTLCache", () => {
  let cache: TTLCache<string>;

  beforeEach(() => {
    cache = new TTLCache(100); // 100ms TTL for fast tests
    jest.useFakeTimers();
  });

  afterEach(() => jest.useRealTimers());

  it("stores and retrieves values", () => {
    cache.set("key", "value");
    expect(cache.get("key")).toBe("value");
  });

  it("returns undefined for missing keys", () => {
    expect(cache.get("nope")).toBeUndefined();
  });

  it("expires entries after TTL", () => {
    cache.set("key", "value");
    jest.advanceTimersByTime(101);
    expect(cache.get("key")).toBeUndefined();
  });

  it("supports custom TTL per entry", () => {
    cache.set("short", "value", 50);
    cache.set("long", "value", 200);
    jest.advanceTimersByTime(100);
    expect(cache.get("short")).toBeUndefined();
    expect(cache.get("long")).toBe("value");
  });

  it("deletes entries", () => {
    cache.set("key", "value");
    expect(cache.delete("key")).toBe(true);
    expect(cache.get("key")).toBeUndefined();
  });

  it("reports size", () => {
    cache.set("a", "1");
    cache.set("b", "2");
    expect(cache.size).toBe(2);
  });
});
```

## Expected Review Output

```markdown
## Code Review Summary

### Overview
Well-implemented TTL cache with clean generics and thorough tests. Ready to merge.

### Critical Issues
(none)

### Suggestions
- **src/services/cache.ts:43** — `size` counts expired entries
  - Recommendation: If size is used for monitoring or capacity decisions, consider
    pruning expired entries first. Not blocking since expired entries are cleaned
    on `get()`, but worth noting for future use:
    ```typescript
    get size(): number {
      // Optional: prune expired before counting
      const now = Date.now();
      for (const [key, entry] of this.store) {
        if (now > entry.expiresAt) this.store.delete(key);
      }
      return this.store.size;
    }
    ```

### Nits
- **src/services/cache.ts:10** — `defaultTTLMs` parameter vs `defaultTTL` field
  naming inconsistency. Consider matching them (`defaultTTLMs` for both, since
  it encodes the unit).

### Security Considerations
- No security concerns — this is a local in-memory cache with no external surface

### What's Good
- Generic type parameter makes this reusable across different value types
- Lazy expiration on `get()` avoids the need for background cleanup timers
- Tests use `jest.useFakeTimers()` correctly — no flaky timing-dependent tests
- Good coverage: happy path, missing keys, expiration, custom TTL, deletion

### Testing
- [x] Unit tests cover new functionality
- [x] Edge cases are tested
- [x] No test regressions

**Verdict: approve** — Clean implementation with good test coverage.
```

## Why This Review Is Good

1. **Doesn't manufacture severity** — A style nit stays a nit, a minor suggestion stays a suggestion
2. **Suggestions are genuinely useful** — The `size` observation is a real future footgun
3. **Positive feedback is specific** — "Generic type parameter makes this reusable" is better than "nice code"
4. **Testing checklist reflects reality** — boxes are checked because the tests actually exist
5. **Verdict matches the findings** — No critical issues = approve, period
