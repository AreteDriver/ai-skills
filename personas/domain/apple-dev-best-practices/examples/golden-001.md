# Apple Dev Best Practices Response
## Example Output
```
// Local view state → @State
@State private var isExpanded = false

// Observable model → @State with @Observable class
@State private var viewModel = RecipeViewModel()

// Shared across view tree → @Environment
@Environment(\.recipeStore) private var store

// Bindings to @Observable → @Bindable
@Bindable var viewModel: RecipeViewModel
```
