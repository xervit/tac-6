# Feature: Use Query Value as CSV File Title

## Metadata
issue_number: `11`
adw_id: `236e1481`
issue_json: `{"number":11,"title":"Use Query value as csv file title","body":"When exporting query results to a csv file use the 'Query'  value as title of the csv file instead of 'query-results'."}`

## Feature Description
This feature enhances the CSV export functionality for query results by using the natural language query text as the filename for downloaded CSV files instead of the generic "query-results" filename. This makes it easier for users to identify and organize their exported data files based on what query generated the results.

## User Story
As a user
I want my exported query results to be named after the query I ran
So that I can easily identify and organize my downloaded CSV files

## Problem Statement
Currently, when users export query results to CSV, the file is always named "query-results.csv" regardless of what query was executed. This makes it difficult to organize and identify multiple exported files, especially when users run many different queries and export results throughout a session.

## Solution Statement
Pass the natural language query text from the client to the server when exporting results, and use a sanitized version of that query as the CSV filename. The query will be sanitized to create a valid filename by:
1. Truncating long queries to a reasonable length
2. Replacing spaces with underscores
3. Removing or replacing invalid filename characters
4. Falling back to "query-results" if the query is empty or invalid

## Relevant Files
Use these files to implement the feature:

- `app/client/src/main.ts` - Contains the `displayResults()` function where the download button is created and the `api.exportResults()` call is made. This is where the query text needs to be passed to the export function.
- `app/client/src/api/client.ts` - Contains the `exportResults()` function that calls the backend API and handles the filename parameter. Already supports optional filename, but the client-side download filename logic needs to be updated.
- `app/server/server.py` - Contains the `/api/export-results` endpoint that already accepts an optional `filename` parameter in the request body. No changes needed here.
- `app/server/core/data_models.py` - Contains the `ExportResultsRequest` model which already includes an optional `filename` field. No changes needed here.
- `app/client/src/types.d.ts` - Contains TypeScript type definitions. Already has `ExportResultsRequest` with optional `filename`. No changes needed here.

### New Files
- `.claude/commands/e2e/test_query_csv_filename.md` - E2E test file to validate the new filename behavior works correctly.

## Implementation Plan
### Phase 1: Foundation
Understand the existing export flow:
1. User clicks download button in results section
2. `displayResults()` in `main.ts` calls `api.exportResults(columns, results)`
3. `exportResults()` in `client.ts` sends POST request to `/api/export-results`
4. Server generates CSV and returns with Content-Disposition header
5. Client creates blob and triggers download

The filename parameter already exists in the API but is not being utilized by the client.

### Phase 2: Core Implementation
Modify the client-side code to:
1. Create a utility function to sanitize query text into a valid filename
2. Pass the query text to the `exportResults()` function call in `displayResults()`
3. The `exportResults()` function already sends filename to server

### Phase 3: Integration
The server already handles the filename parameter correctly:
- Uses provided filename if present
- Falls back to "query-results" if not provided
- Appends .csv extension if missing

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Create `.claude/commands/e2e/test_query_csv_filename.md` with test steps that validate:
  - Run a query "Show me all users"
  - Click the download button for results
  - Verify the downloaded filename contains "show_me_all_users" or similar sanitized version
  - Run another query "Find products with price greater than 50"
  - Verify that filename reflects the new query

### Step 2: Add Filename Sanitization Utility
- In `app/client/src/main.ts`, add a utility function `sanitizeFilename(query: string): string` that:
  - Converts to lowercase
  - Truncates to maximum 50 characters (before extension)
  - Replaces spaces with underscores
  - Removes or replaces invalid filename characters: `< > : " / \ | ? *`
  - Falls back to "query-results" if result is empty

### Step 3: Update displayResults Function
- In `app/client/src/main.ts`, modify the `displayResults()` function:
  - The function already receives `query` as a parameter
  - Update the download button onclick handler to pass a sanitized filename:
    ```typescript
    const filename = sanitizeFilename(query);
    downloadButton.onclick = () => api.exportResults(response.columns, response.results, filename);
    ```

### Step 4: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- The server-side functionality is already covered by existing tests for the export endpoint
- No new unit tests needed as this is primarily a UI change passing data that already exists

### Edge Cases
- Empty query string: should fall back to "query-results"
- Very long query: should be truncated to reasonable length
- Query with special characters: should be sanitized properly
- Query with only spaces/punctuation: should fall back to "query-results"

## Acceptance Criteria
- When exporting query results, the CSV filename is based on the natural language query
- Filenames are properly sanitized (no invalid characters)
- Long queries are truncated to a reasonable filename length
- Empty or invalid queries fall back to "query-results"
- All existing export functionality continues to work

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_query_csv_filename.md` to validate this functionality works.
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- The backend API already supports the filename parameter, so no server changes are required
- The client API function `exportResults()` already accepts an optional filename parameter
- This is a minimal change that leverages existing infrastructure
- Future enhancement: Consider adding user preference for filename format (e.g., include timestamp, use SQL instead of query)
