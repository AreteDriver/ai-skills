# SwiftUI Patterns Reference

## Table of Contents
- Custom View Modifiers
- Preference Keys
- Custom Layouts
- Animations & Transitions
- Sheet & Modal Patterns
- List & Grid Patterns
- Search & Filtering
- Anti-Patterns to Avoid

---

## Custom View Modifiers

Use for repeated styling across views:

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .shadow(radius: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// Usage
RecipeCard(recipe: recipe)
    .cardStyle()
```

## Preference Keys

For child-to-parent communication (e.g., scroll offset, size reporting):

```swift
struct ScrollOffsetKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

// Child reports
GeometryReader { geo in
    Color.clear
        .preference(key: ScrollOffsetKey.self, 
                     value: geo.frame(in: .named("scroll")).minY)
}

// Parent reads
.onPreferenceChange(ScrollOffsetKey.self) { offset in
    headerOpacity = min(1, max(0, offset / 200))
}
```

## Custom Layouts (iOS 16+)

```swift
struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrange(proposal: proposal, subviews: subviews)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrange(proposal: proposal, subviews: subviews)
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(
                x: bounds.minX + position.x,
                y: bounds.minY + position.y
            ), proposal: .unspecified)
        }
    }
}

// Usage — tag cloud, ingredient chips
FlowLayout(spacing: 6) {
    ForEach(recipe.tags, id: \.self) { tag in
        TagChip(tag)
    }
}
```

## Animations & Transitions

```swift
// Matched geometry for shared element transitions
@Namespace private var animation

// In list
RecipeCard(recipe: recipe)
    .matchedGeometryEffect(id: recipe.id, in: animation)

// In detail
RecipeImage(recipe: recipe)
    .matchedGeometryEffect(id: recipe.id, in: animation)

// Phase animations (iOS 17+)
PhaseAnimator([false, true]) { phase in
    Image(systemName: "heart.fill")
        .scaleEffect(phase ? 1.2 : 1.0)
        .foregroundStyle(phase ? .red : .gray)
}

// Spring animations for natural feel
withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
    isExpanded.toggle()
}
```

## Sheet & Modal Patterns

Parent ViewModel owns child state:

```swift
@MainActor
@Observable
final class RecipeListViewModel {
    var editingRecipe: Recipe?
    var showingNewRecipe = false
    
    func edit(_ recipe: Recipe) {
        editingRecipe = recipe
    }
}

// View
.sheet(item: $viewModel.editingRecipe) { recipe in
    RecipeEditView(recipe: recipe)
}
.sheet(isPresented: $viewModel.showingNewRecipe) {
    NewRecipeView()
}
```

## List & Grid Patterns

```swift
// Lazy list with sections
List {
    ForEach(groupedRecipes.keys.sorted(), id: \.self) { category in
        Section(category) {
            ForEach(groupedRecipes[category] ?? []) { recipe in
                RecipeRow(recipe: recipe)
            }
        }
    }
}
.listStyle(.insetGrouped)

// Adaptive grid
LazyVGrid(columns: [GridItem(.adaptive(minimum: 160), spacing: 12)], spacing: 12) {
    ForEach(recipes) { recipe in
        RecipeCard(recipe: recipe)
    }
}

// Pull to refresh
.refreshable {
    await viewModel.loadRecipes()
}
```

## Search & Filtering

```swift
@MainActor
@Observable
final class RecipeSearchViewModel {
    var searchText = ""
    var selectedTags: Set<String> = []
    
    var filteredRecipes: [Recipe] {
        recipes.filter { recipe in
            (searchText.isEmpty || recipe.name.localizedCaseInsensitiveContains(searchText))
            && (selectedTags.isEmpty || !selectedTags.isDisjoint(with: Set(recipe.tags)))
        }
    }
}

// View
.searchable(text: $viewModel.searchText, prompt: "Search recipes")
.searchSuggestions {
    ForEach(viewModel.recentSearches, id: \.self) { term in
        Text(term).searchCompletion(term)
    }
}
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Do This Instead |
|---|---|---|
| `AnyView` | Destroys view identity, kills diffing | `@ViewBuilder`, `Group`, conditional modifiers |
| `onAppear { Task { ... } }` | No cancellation, can fire multiple times | `.task { ... }` modifier (auto-cancels) |
| Network calls in view body | Fires on every re-render | `.task` or ViewModel `loadData()` |
| `@StateObject` with `@Published` | Legacy pattern, unnecessary overhead | `@State` + `@Observable` class |
| Giant monolithic views | Unpreviewable, untestable | Extract at 50+ lines |
| Hardcoded colors/fonts | Breaks Dark Mode, Dynamic Type | Semantic colors, `.font(.body)` |
| `GeometryReader` at top level | Proposes zero size upward | Use inside `overlay` or `background` |
| Passing ViewModels through init chain | Tight coupling, deep prop drilling | `@Environment` injection |
