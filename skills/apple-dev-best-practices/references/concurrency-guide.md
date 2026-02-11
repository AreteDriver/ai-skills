# Swift Concurrency Guide

## Table of Contents
- Actor Isolation Model
- Sendable Conformance
- Structured Concurrency
- Task Management
- Common Pitfalls
- Migration from GCD

---

## Actor Isolation Model

### Global Actors

```swift
// @MainActor — UI thread
@MainActor
@Observable
final class RecipeViewModel {
    var recipes: [Recipe] = []
    
    // This runs on main actor automatically
    func updateUI(with recipes: [Recipe]) {
        self.recipes = recipes
    }
    
    // Explicitly hop off main actor for heavy work
    nonisolated func processImage(_ data: Data) async -> UIImage? {
        // Runs on cooperative thread pool
        await ImageProcessor.process(data)
    }
}
```

### Custom Actors

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]
    private var inProgress: [URL: Task<UIImage?, Error>] = [:]
    
    func image(for url: URL) async throws -> UIImage? {
        // Check cache first
        if let cached = cache[url] { return cached }
        
        // Deduplicate in-flight requests
        if let existing = inProgress[url] {
            return try await existing.value
        }
        
        // Start new fetch
        let task = Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            return UIImage(data: data)
        }
        inProgress[url] = task
        
        let image = try await task.value
        cache[url] = image
        inProgress[url] = nil
        return image
    }
}
```

## Sendable Conformance

Types that cross actor boundaries must be `Sendable`:

```swift
// Value types are automatically Sendable
struct Recipe: Sendable, Codable, Identifiable {
    let id: UUID
    var name: String
    var ingredients: [String]
}

// Reference types must prove safety
final class RecipeService: Sendable {
    // All stored properties must be immutable or Sendable
    let session: URLSession  // URLSession is Sendable
    let baseURL: URL         // URL is Sendable
}

// @unchecked Sendable — use sparingly with locking
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]
    
    func get(_ key: String) -> Any? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}
```

**Rules:**
- Structs with all Sendable properties: automatically Sendable
- Final classes with immutable Sendable properties: conform explicitly
- Classes with mutable state: use `actor` or `@unchecked Sendable` with locking
- Never use `@unchecked Sendable` to silence warnings without actual thread safety

## Structured Concurrency

### TaskGroup for Parallel Work

```swift
func loadDashboard() async throws -> Dashboard {
    async let recipes = recipeService.fetchRecent()
    async let mealPlan = mealPlanService.fetchCurrent()
    async let shoppingList = shoppingService.fetchList()
    
    // All three run in parallel, await together
    return try await Dashboard(
        recipes: recipes,
        mealPlan: mealPlan,
        shoppingList: shoppingList
    )
}

// Dynamic parallelism
func loadImages(for recipes: [Recipe]) async -> [UUID: UIImage] {
    await withTaskGroup(of: (UUID, UIImage?).self) { group in
        for recipe in recipes {
            group.addTask {
                let image = try? await imageCache.image(for: recipe.imageURL)
                return (recipe.id, image)
            }
        }
        
        var results: [UUID: UIImage] = [:]
        for await (id, image) in group {
            if let image { results[id] = image }
        }
        return results
    }
}
```

### Task Cancellation

```swift
// .task modifier auto-cancels when view disappears
.task {
    await viewModel.loadRecipes()
}

// Check cancellation in long-running work
func processLargeDataset(_ items: [Item]) async throws {
    for item in items {
        try Task.checkCancellation()  // Throws if cancelled
        await process(item)
    }
}

// Cooperative cancellation
func pollForUpdates() async {
    while !Task.isCancelled {
        await fetchUpdates()
        try? await Task.sleep(for: .seconds(30))
    }
}
```

## Common Pitfalls

| Pitfall | Problem | Solution |
|---|---|---|
| `Task { }` in `onAppear` | No cancellation, can fire twice | `.task { }` modifier |
| `DispatchQueue.main.async` | Bypasses actor isolation | `@MainActor`, `MainActor.run {}` |
| `@Sendable` closure captures | Non-Sendable type in concurrent closure | Make type Sendable or copy needed data |
| Unstructured Tasks everywhere | Memory leaks, zombie tasks | Prefer structured concurrency |
| `.task(id:)` missing | Task doesn't restart when dependency changes | Add `id` parameter matching the dependency |

## Migration from GCD

| GCD Pattern | Swift Concurrency Equivalent |
|---|---|
| `DispatchQueue.main.async { }` | `await MainActor.run { }` or `@MainActor` |
| `DispatchQueue.global().async { }` | `Task { }` or `Task.detached { }` |
| `DispatchGroup` | `async let` or `TaskGroup` |
| `DispatchSemaphore` | `AsyncStream`, `AsyncChannel` |
| `DispatchQueue (serial)` | `actor` |
| `NSLock` / `os_unfair_lock` | `actor` (preferred) or `Mutex` (iOS 18+) |
| Completion handlers | `async throws -> T` |
| Delegate callbacks | `AsyncStream` or `AsyncSequence` |
