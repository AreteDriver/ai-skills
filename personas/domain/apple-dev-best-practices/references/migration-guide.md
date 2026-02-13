# Migration Guide

## Table of Contents
- UIKit → SwiftUI Migration
- CoreData → SwiftData Migration
- Combine → async/await Migration
- ObservableObject → @Observable Migration
- Common Migration Gotchas

---

## UIKit → SwiftUI Migration

### Strategy: Incremental, Not Big-Bang

Migrate feature by feature, not the whole app at once. SwiftUI and UIKit coexist well.

### Hosting SwiftUI in UIKit

```swift
// Embed SwiftUI view in UIKit view controller
let swiftUIView = RecipeDetailView(recipe: recipe)
let hostingController = UIHostingController(rootView: swiftUIView)
navigationController?.pushViewController(hostingController, animated: true)
```

### Hosting UIKit in SwiftUI

```swift
// Wrap UIKit view for SwiftUI
struct CameraPreview: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let previewView = CameraPreviewView()
        return previewView
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {}
}

// Wrap UIKit view controller
struct ImagePickerView: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator { Coordinator(self) }
}
```

### Migration Priority Order

1. **Settings/Preferences screens** — Simple forms, lowest risk
2. **Detail views** — Display-heavy, good SwiftUI fit
3. **List views** — SwiftUI List is excellent
4. **Navigation structure** — Migrate after views are stable
5. **Complex custom UI** — Last, may need UIViewRepresentable bridges

### Claude Gotcha: Legacy API Confusion

Claude often suggests UIKit APIs when SwiftUI equivalents exist. Common confusions:

| Claude Suggests (UIKit) | Use This (SwiftUI) |
|---|---|
| `UINavigationController` | `NavigationStack` |
| `UITableView` | `List` |
| `UICollectionView` | `LazyVGrid` / `LazyHGrid` |
| `UIAlertController` | `.alert()` modifier |
| `UIActivityViewController` | `ShareLink` |
| `UISearchController` | `.searchable()` modifier |
| `UIRefreshControl` | `.refreshable {}` |

---

## CoreData → SwiftData Migration

### Side-by-Side Comparison

| CoreData | SwiftData |
|---|---|
| `NSManagedObject` subclass | `@Model` class |
| `NSPersistentContainer` | `ModelContainer` |
| `NSManagedObjectContext` | `ModelContext` |
| `NSFetchRequest` / `FetchedResultsController` | `@Query` |
| `.xcdatamodeld` file | Swift code only |
| Manual migration mapping | `VersionedSchema` + `SchemaMigrationPlan` |

### Migration Steps

```swift
// 1. Define SwiftData models alongside CoreData
@Model
final class Recipe {
    var name: String
    var instructions: String
    @Relationship(deleteRule: .cascade)
    var ingredients: [Ingredient]
    
    init(name: String, instructions: String) {
        self.name = name
        self.instructions = instructions
        self.ingredients = []
    }
}

// 2. Create migration utility
struct CoreDataMigrator {
    let coreDataContext: NSManagedObjectContext
    let swiftDataContext: ModelContext
    
    func migrateRecipes() async throws {
        let request: NSFetchRequest<CDRecipe> = CDRecipe.fetchRequest()
        let cdRecipes = try coreDataContext.fetch(request)
        
        for cdRecipe in cdRecipes {
            let recipe = Recipe(
                name: cdRecipe.name ?? "",
                instructions: cdRecipe.instructions ?? ""
            )
            swiftDataContext.insert(recipe)
        }
        try swiftDataContext.save()
    }
}

// 3. Versioned schema for future migrations
enum RecipeSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] {
        [Recipe.self, Ingredient.self]
    }
}
```

---

## Combine → async/await Migration

| Combine | async/await |
|---|---|
| `publisher.sink { }` | `for await value in stream { }` |
| `Just(value)` | Direct return |
| `Future { }` | `async` function |
| `PassthroughSubject` | `AsyncStream.makeStream()` |
| `CurrentValueSubject` | `@Observable` property |
| `publisher.map { }` | `stream.map { }` or plain transform |
| `.receive(on: DispatchQueue.main)` | `@MainActor` |
| `AnyCancellable` | `Task` (cancel via `.task` modifier) |

---

## ObservableObject → @Observable Migration

```swift
// BEFORE (iOS 14-16)
class RecipeViewModel: ObservableObject {
    @Published var recipes: [Recipe] = []
    @Published var isLoading = false
}

struct RecipeListView: View {
    @StateObject private var viewModel = RecipeViewModel()
    // ...
}

// AFTER (iOS 17+)
@Observable
final class RecipeViewModel {
    var recipes: [Recipe] = []  // No @Published needed
    var isLoading = false
}

struct RecipeListView: View {
    @State private var viewModel = RecipeViewModel()  // @State, not @StateObject
    // ...
}
```

Key changes:
- `@Observable` replaces `ObservableObject` conformance
- No `@Published` needed — all properties auto-observed
- `@State` replaces `@StateObject` for ownership
- `@Bindable` replaces `@ObservedObject` for bindings
- `@Environment` works directly with `@Observable` classes

---

## Common Migration Gotchas

1. **Swift Concurrency + Swift 5.x compiled frameworks**: Libraries not yet compiled with Swift 6 will trigger Sendable warnings. Use `@preconcurrency import` as temporary workaround.

2. **SwiftData + CloudKit**: SwiftData's CloudKit integration is less mature than CoreData's. Test sync thoroughly before migrating if you use CloudKit.

3. **`.pbxproj` corruption**: When adding SwiftUI files via Claude Code, create the file but add to the Xcode project manually. Never let AI tools modify .pbxproj.

4. **Preview crashes after migration**: SwiftData previews need their own in-memory ModelContainer. Always configure previews with `.modelContainer(for: Recipe.self, inMemory: true)`.

5. **Keypath observation differences**: `@Observable` uses Swift macros for fine-grained observation. Views only re-render when *accessed* properties change, unlike `@Published` which triggered on *any* property change. This is better but can surprise you if you expect side effects.
