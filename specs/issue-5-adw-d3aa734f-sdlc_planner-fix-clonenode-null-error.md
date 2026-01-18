# Bug: Fix cloneNode null error on subsequent queries

## Metadata
issue_number: `5`
adw_id: `d3aa734f`
issue_json: `{"number":5,"title":"Cannot read properties of null","body":"/bug \n\n\"Show all products\" is generated correctly to the following SQL syntax: \n\n\"SELECT * FROM products LIMIT 100;\"\n\nResulting in the following error:\n\n\"Cannot read properties of null (reading 'cloneNode')\""}`

## Bug Description
When executing a natural language query such as "Show all products", the SQL is correctly generated as `SELECT * FROM products LIMIT 100;`. However, subsequent query executions result in a JavaScript error: `Cannot read properties of null (reading 'cloneNode')`. The first query execution works correctly and displays results, but any subsequent query execution crashes with this null reference error. This makes the application unusable after the first successful query without a page refresh.

## Problem Statement
The `displayResults()` function in `app/client/src/main.ts` permanently removes the `#toggle-results` button from the DOM after the first query execution. When a second query is executed, the function tries to find this button using `document.getElementById('toggle-results')`, which returns `null` because the element no longer exists. The code then attempts to call `cloneNode()` on this null reference, causing the error.

## Solution Statement
Refactor the `displayResults()` function to preserve the toggle button's existence in the DOM across multiple query executions. Instead of replacing the toggle button with an actions container on each call, the code should:
1. Check if the actions container already exists before creating/manipulating elements
2. Either keep the toggle button with its original ID, or properly manage the toggle button state without removing it from the DOM

The fix should ensure the toggle button (or its replacement) maintains proper accessibility for subsequent queries while keeping the download and hide/show functionality intact.

## Steps to Reproduce
1. Navigate to the application at http://localhost:5173
2. Load sample data (e.g., "Product Inventory")
3. Enter a natural language query like "Show all products"
4. Click the Query button - results display successfully
5. Enter another query (e.g., "Show products with price greater than 50")
6. Click the Query button again
7. **Observe**: JavaScript error "Cannot read properties of null (reading 'cloneNode')" in the console, and the query results do not update

## Root Cause Analysis
The bug is located in `app/client/src/main.ts` lines 236-250 in the `displayResults()` function:

```typescript
// Move the toggle button into the actions container
const toggleButton = document.getElementById('toggle-results') as HTMLButtonElement;

// Clone the toggle button to remove old event listeners
const newToggleButton = toggleButton.cloneNode(true) as HTMLButtonElement;
newToggleButton.addEventListener('click', () => {
  resultsContainer.style.display = resultsContainer.style.display === 'none' ? 'block' : 'none';
  newToggleButton.textContent = resultsContainer.style.display === 'none' ? 'Show' : 'Hide';
});

// Replace the old toggle button with the new one in the actions container
actionsContainer.appendChild(newToggleButton);

// Replace the old toggle button in the DOM
toggleButton.parentNode?.replaceChild(actionsContainer, toggleButton);
```

**Root cause sequence:**
1. First query execution: `getElementById('toggle-results')` finds the button, clones it, and then replaces the original button with `actionsContainer`. The cloned button inside `actionsContainer` has no ID attribute anymore (cloneNode copies the element but the original with ID is removed).
2. Second query execution: `getElementById('toggle-results')` returns `null` because the element with that ID was replaced/removed from the DOM.
3. Line 240 calls `toggleButton.cloneNode(true)` on `null`, throwing the error.

## Relevant Files
Use these files to fix the bug:

- `app/client/src/main.ts` - Contains the `displayResults()` function (lines 184-251) where the bug occurs. This is the primary file that needs to be modified.
- `app/client/index.html` - Contains the original HTML structure including the `#toggle-results` button (lines 32-39). Understanding the original structure helps ensure the fix maintains proper DOM structure.
- `.claude/commands/test_e2e.md` - E2E test runner instructions for understanding how to run E2E tests.
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test to understand the test format.

### New Files
- `.claude/commands/e2e/test_consecutive_queries.md` - New E2E test file to validate that consecutive queries work without errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Fix the toggle button handling in displayResults()
- Open `app/client/src/main.ts`
- Locate the `displayResults()` function (starts at line 184)
- Refactor lines 213-250 to properly handle the toggle button and actions container:
  - Check if a `results-actions` container already exists in the results header
  - If it exists, clear and reuse it instead of creating a new one
  - Create a new toggle button dynamically instead of relying on `getElementById('toggle-results')`
  - Do NOT use `replaceChild` to replace the toggle button - instead, append the actions container after the h2 element
  - Ensure the toggle button functionality (hide/show results) works correctly
  - Ensure the download button is properly added when there are results
- The fix should handle both first-time and subsequent query executions

### 2. Verify the HTML structure is preserved
- Ensure the original `#toggle-results` button in `index.html` (line 35) is either:
  - Left intact and hidden/unused (simplest approach), OR
  - Removed from HTML if the new approach doesn't need it
- The results header should contain the h2 and the actions container with toggle button

### 3. Create E2E test for consecutive queries
- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_complex_query.md` to understand the E2E test format
- Create a new E2E test file at `.claude/commands/e2e/test_consecutive_queries.md` that validates:
  - First query executes successfully and displays results
  - Second query executes successfully without errors
  - Third query executes successfully to confirm the fix is robust
  - Hide/Show toggle button works after multiple queries
  - Download button appears and functions correctly after multiple queries
- Include appropriate screenshots for each query execution

### 4. Run validation commands
- Execute all validation commands listed below to ensure the bug is fixed with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate no backend regressions
- `cd app/client && bun tsc --noEmit` - Run TypeScript type checking to validate no type errors
- `cd app/client && bun run build` - Run frontend build to validate the build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_consecutive_queries.md` to validate consecutive queries work

## Notes
- The fix should be minimal and surgical - only modify what's necessary to fix the bug
- The cloneNode approach was originally used to remove old event listeners, but a better approach is to create fresh elements each time or properly manage event listeners
- Consider using `removeEventListener` or creating new button elements directly instead of cloning
- The download button functionality should continue to work with the new approach
- Test both scenarios: queries with results (shows download button) and queries with no results (no download button)
