---
name: apple-dev-best-practices
version: "2.0.0"
type: persona
category: domain
risk_level: low
description: Apple platform development best practices for Swift 6, SwiftUI, SwiftData, and iOS/macOS apps. Use when building any iOS or macOS app, writing Swift code, designing SwiftUI views, working with Xcode projects, implementing navigation, state management, concurrency, networking, persistence, or testing on Apple platforms. Triggers on Swift, SwiftUI, iOS, macOS, Xcode, UIKit, SwiftData, Core Data, XCTest, StoreKit, CloudKit, MapKit, HealthKit, or any Apple framework. Also use when reviewing Swift code, debugging iOS apps, migrating UIKit to SwiftUI, or planning Apple platform architecture.
---

# Apple Development Best Practices

Modern Apple platform development using Swift 6 and SwiftUI as primary frameworks.

## When to Use

Use this skill when:
- Building iOS or macOS apps with Swift 6 and SwiftUI
- Designing navigation, state management, or concurrency patterns for Apple platforms
- Working with SwiftData, Core Data, StoreKit, CloudKit, or other Apple frameworks
- Reviewing Swift code or planning Apple platform architecture

## When NOT to Use

Do NOT use this skill when:
- Building cross-platform mobile apps (Flutter, React Native, Kotlin Multiplatform) — use a cross-platform mobile persona instead, because Apple-specific patterns like `@Observable` and `NavigationStack` don't apply
- Writing server-side Swift (Vapor, Hummingbird) — use a backend engineering persona instead, because server-side Swift has different concurrency, deployment, and architecture concerns

## Core Philosophy

Build apps that are **previewable, testable, and maintainable**. A previewable app is a testable app. A testable app is a maintainable app.

## Swift 6 Standards

- **Strict concurrency** enabled — treat all warnings as errors
- **`@Observable`** over `ObservableObject` (iOS 17+)
- **`async/await`** for all asynchronous operations
- **Value types** (structs) preferred over reference types (classes) unless identity semantics needed
- **`guard`** for early exits, never deeply nested `if let` chains
- **Typed errors** via `LocalizedError` conformance — no raw strings
- **No force unwrapping** (`!`) without documented justification
- Follow Apple's Swift API Design Guidelines for naming

## SwiftUI Architecture

### State Management — Single Source of Truth (SSOT)

```swift
// Local view state → @State
@State private var isExpanded = false

// Observable model → @State with @Observable class
@State private var viewModel = RecipeViewModel()

// Shared across view tree → @Environment
@Environment(\.recipeStore) private var store

// Bindings to @Observable → @Bindable
@Bindable var viewModel: RecipeViewModel
```

**Rules:**
- `@State` for view-local state only — never shared across views
- `@Observable` classes for ViewModels (replaces `ObservableObject` + `@Published`)
- `@Environment` for dependency injection (services, stores, settings)
- Never pass view models more than 2 levels deep — use Environment instead

### Navigation — NavigationStack with Type-Safe Routing

```swift
enum Route: Hashable {
    case recipeDetail(Recipe)
    case settings
    case profile(User)
}

@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to route: Route) {
        path.append(route)
    }
}
```

**Rules:**
- `NavigationStack` only — never deprecated `NavigationView`
- Type-safe routing via `Hashable` enum
- Router as `@Observable` class in `@Environment`
- Sheet presentation via optional ViewModel on parent

### View Composition

- Extract subviews at **50+ lines** or when reusable
- Max **100 lines** per view file before mandatory extraction
- Custom ViewModifiers for shared styling — not repeated inline styles
- Never use `AnyView` — destroys diffing performance and identity
- Prefer `@ViewBuilder` closures over `AnyView` for type erasure

### Performance

- **`LazyVStack`/`LazyHStack`** inside ScrollView — never eager stacks for large lists
- **`EquatableView`** wrapper for complex views that rarely change
- Keep view body **pure** — no side effects, no network calls
- Use `.task` modifier for async work, not `onAppear` with Task
- Profile with SwiftUI Performance Instrument (Xcode 16+)

## Project Structure

```
AppName/
├── App/                    # App entry, lifecycle, configuration
│   ├── AppNameApp.swift
│   └── AppDelegate.swift   # Only if needed for UIKit integration
├── Features/               # Feature modules (self-contained)
│   ├── Recipes/
│   │   ├── Views/          # SwiftUI views
│   │   ├── ViewModels/     # @Observable classes
│   │   └── Models/         # Data models (structs)
│   ├── MealPlanning/
│   └── Community/
├── Core/                   # Shared infrastructure
│   ├── Extensions/
│   ├── Services/           # Networking, auth, analytics
│   ├── Persistence/        # SwiftData / Core Data
│   └── Components/         # Reusable UI components
├── Resources/              # Assets, Localizations, Fonts
└── Tests/
    ├── UnitTests/          # ViewModel + Service tests
    └── UITests/            # Critical user flow tests
```

**Rules:**
- Features are **self-contained** — no cross-feature imports
- Shared code lives in `Core/` only
- Each feature has its own Views, ViewModels, Models
- Feature folders mirror navigation structure

## Concurrency

```swift
// Actor for thread-safe shared state
actor RecipeStore {
    private var cache: [UUID: Recipe] = [:]

    func recipe(for id: UUID) -> Recipe? {
        cache[id]
    }
}

// @MainActor for UI-bound classes
@MainActor
@Observable
final class RecipeListViewModel {
    var recipes: [Recipe] = []
    var isLoading = false

    func loadRecipes() async {
        isLoading = true
        defer { isLoading = false }
        recipes = await recipeService.fetchAll()
    }
}
```

**Rules:**
- `@MainActor` on all ViewModels
- `actor` for shared mutable state
- `Sendable` conformance for types crossing isolation boundaries
- Never `DispatchQueue.main.async` — use `@MainActor` instead
- `Task` only inside `.task` modifier or explicit user-initiated actions
- `TaskGroup` for parallel independent work

## Testing

- **Swift Testing** (`@Test`, `#expect`) preferred over XCTest for new code
- **Unit tests** for all ViewModel logic — 80%+ coverage on business logic
- **UI tests** for critical user flows only (login, purchase, core CRUD)
- **Dependency injection** via protocols for testability
- **No singletons** in production code — inject via `@Environment`
- Preview-driven development: if a view is hard to preview, it's hard to test

## Persistence

**SwiftData** (iOS 17+) is the default persistence layer:

```swift
@Model
final class Recipe {
    var name: String
    var ingredients: [String]
    var instructions: String
    @Relationship(deleteRule: .cascade)
    var steps: [CookingStep]
}
```

**Rules:**
- `@Model` classes for SwiftData — not structs
- Define `@Relationship` explicitly with delete rules
- Use `@Query` in views for automatic updates
- ModelContainer configured in App entry point
- Migration strategy documented before schema changes

## Networking

```swift
protocol RecipeServiceProtocol: Sendable {
    func fetchAll() async throws -> [Recipe]
    func create(_ recipe: Recipe) async throws -> Recipe
}

struct RecipeService: RecipeServiceProtocol {
    private let session: URLSession
    private let decoder: JSONDecoder

    func fetchAll() async throws -> [Recipe] {
        let (data, response) = try await session.data(from: endpoint)
        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw AppError.networkError(statusCode: http.statusCode)
        }
        return try decoder.decode([Recipe].self, from: data)
    }
}
```

**Rules:**
- Protocol-based services for testability
- `Sendable` conformance on all service types
- Typed errors with `LocalizedError`
- No third-party HTTP libraries unless justified (URLSession is sufficient)
- Certificate pinning for sensitive data

## Security

- **Keychain** for credentials, tokens, secrets — never UserDefaults
- **App Transport Security** enabled — HTTPS only
- No sensitive data in logs or crash reports
- `@AppStorage` only for non-sensitive user preferences
- Input validation on all user-provided data
- Privacy manifest (`PrivacyInfo.xcprivacy`) for App Store compliance

## Accessibility

- Every interactive element needs an `accessibilityLabel`
- Use semantic SwiftUI elements (Button, Toggle, Picker) — not `.onTapGesture`
- Support Dynamic Type — no hardcoded font sizes
- Minimum tap target 44x44pt
- Test with VoiceOver before shipping

## Deep References

See `references/` for detailed guidance:
- `references/swiftui-patterns.md` — Advanced view patterns, custom layouts, animations
- `references/concurrency-guide.md` — Actor isolation, Sendable, structured concurrency
- `references/xcode-claude-integration.md` — XcodeBuildMCP setup, hooks, sandbox modes
- `references/migration-guide.md` — UIKit → SwiftUI, CoreData → SwiftData paths
