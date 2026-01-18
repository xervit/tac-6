# Feature: Add Query and SQL Header to Exported CSV

## Metadata
issue_number: `9`
adw_id: `71f548c7`
issue_json: `{"number":9,"title":"Add Query and SQL header to exported CSV","body":"When exporting a query result to a csv file add the 'Query' and 'SQL' values at the top of the page of the exported csv"}`

## Feature Description
This feature enhances the existing CSV export functionality for query results by adding metadata headers at the top of the exported file. When a user exports query results to CSV, the file will now include the original natural language query and the generated SQL statement as header rows before the actual data. This provides context about what query produced the results, making the exported files more self-documenting and useful for sharing or archival purposes.

## User Story
As a user exporting query results
I want to see the original query and SQL statement at the top of my CSV file
So that I can remember what query produced these results when viewing the file later

## Problem Statement
Currently, when users export query results as CSV, they only get the raw data without any context about what query produced it. If a user exports multiple query results or revisits an exported file later, they have no way to know what natural language query or SQL statement generated that data. This makes the exported files less useful for documentation, auditing, or sharing purposes.

## Solution Statement
Modify the `/api/export-results` endpoint and the client-side `exportResults` function to include the natural language query and SQL statement as header rows in the exported CSV. The format will be:
```
Query,<natural language query>
SQL,<sql statement>
<blank row>
<column headers>
<data rows>
```

This approach:
1. Keeps the CSV parseable by placing metadata in clearly labeled rows
2. Uses a blank row separator for visual clarity
3. Requires minimal changes to existing architecture
4. Maintains backward compatibility (optional parameters)

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Contains the `/api/export-results` endpoint that generates CSV content. This file needs to be modified to accept and include the query and SQL metadata in the CSV output.
- `app/server/core/data_models.py` - Contains the `ExportResultsRequest` Pydantic model. This needs to be updated to include optional `query` and `sql` fields.
- `app/client/src/api/client.ts` - Contains the `exportResults` function that sends export requests to the server. This needs to be updated to pass the query and SQL parameters.
- `app/client/src/main.ts` - Contains the `displayResults` function which sets up the download button click handler. This needs to pass the query and SQL values to the export function.
- `app/server/tests/test_export.py` - Contains existing unit tests for export functionality. New tests need to be added for the query/SQL header feature.
- `app_docs/feature-f80ea819-one-click-table-exports.md` - Reference documentation for the existing export feature.
- `.claude/commands/test_e2e.md` - Reference for understanding how to create E2E test files.
- `.claude/commands/e2e/test_one_click_exports.md` - Reference E2E test for export functionality patterns.

### New Files
- `.claude/commands/e2e/test_csv_query_headers.md` - New E2E test file to validate the query and SQL headers appear in exported CSV files.

## Implementation Plan
### Phase 1: Foundation
1. Update the `ExportResultsRequest` data model to include optional `query` and `sql` fields
2. This establishes the contract between frontend and backend for the new feature

### Phase 2: Core Implementation
1. Modify the `/api/export-results` endpoint to write query and SQL metadata rows before the data headers when provided
2. Update the client-side `exportResults` API function to accept and pass query and SQL parameters
3. Modify the download button click handler in `displayResults` to pass the query and SQL values to the export function

### Phase 3: Integration
1. Add unit tests for the new functionality in `test_export.py`
2. Create an E2E test to validate the complete user flow
3. Verify backward compatibility - exports without query/SQL should still work

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test File
- Create `.claude/commands/e2e/test_csv_query_headers.md` following the format of existing E2E test files
- Define test steps that:
  1. Navigate to the application
  2. Load sample data (users)
  3. Run a query (e.g., "Show me all users")
  4. Click the download button for query results
  5. Verify the downloaded CSV contains the Query and SQL headers at the top
- Include success criteria and screenshot requirements

### Task 2: Update ExportResultsRequest Data Model
- Edit `app/server/core/data_models.py`
- Add optional `query` and `sql` fields to `ExportResultsRequest`:
  ```python
  query: Optional[str] = Field(None, description="Original natural language query")
  sql: Optional[str] = Field(None, description="Generated SQL statement")
  ```

### Task 3: Modify Server Export Endpoint
- Edit `app/server/server.py` in the `export_results` function
- When writing CSV content, check if `request.query` or `request.sql` are provided
- If provided, write them as the first rows in the format:
  ```
  Query,<query value>
  SQL,<sql value>
  <blank row>
  ```
- Then continue with the existing column headers and data rows

### Task 4: Update Client API Function
- Edit `app/client/src/api/client.ts`
- Modify the `exportResults` function signature to accept optional `query` and `sql` parameters:
  ```typescript
  async exportResults(
    columns: string[],
    results: Record<string, unknown>[],
    filename?: string,
    query?: string,
    sql?: string
  ): Promise<void>
  ```
- Include these fields in the JSON body sent to the server

### Task 5: Update Download Button Handler
- Edit `app/client/src/main.ts` in the `displayResults` function
- Modify the download button onclick handler to pass `query` and `response.sql` to `api.exportResults`:
  ```typescript
  downloadButton.onclick = () => api.exportResults(
    response.columns,
    response.results,
    undefined,  // filename
    query,      // natural language query
    response.sql // SQL statement
  );
  ```

### Task 6: Add Unit Tests
- Edit `app/server/tests/test_export.py`
- Add new test cases in `TestResultsExportEndpoint`:
  1. `test_export_results_with_query_and_sql_headers` - verify headers appear when query and sql are provided
  2. `test_export_results_with_only_query_header` - verify works with only query provided
  3. `test_export_results_with_only_sql_header` - verify works with only sql provided
  4. `test_export_results_without_headers_backward_compatible` - verify existing behavior without query/sql

### Task 7: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test that CSV output includes Query row when `query` is provided
- Test that CSV output includes SQL row when `sql` is provided
- Test that CSV output includes blank separator row after metadata headers
- Test that CSV properly escapes query and SQL values containing commas or quotes
- Test backward compatibility - exports without query/sql work as before

### Edge Cases
- Query containing commas (should be properly quoted in CSV)
- Query containing quotes (should be properly escaped)
- SQL containing special characters
- Very long query or SQL strings
- Empty query or SQL strings (should be omitted from output)
- Only query provided (no sql)
- Only sql provided (no query)

## Acceptance Criteria
- When exporting query results, the CSV file includes a "Query" row at the top with the original natural language query
- When exporting query results, the CSV file includes a "SQL" row below the Query row with the generated SQL statement
- A blank row separates the metadata headers from the column headers
- Standard CSV escaping is applied to query and SQL values
- The feature is backward compatible - exports without query/sql parameters still work
- All existing unit tests pass
- New unit tests cover the query/sql header functionality
- TypeScript compiles without errors
- Frontend build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_csv_query_headers.md` to validate this functionality works end-to-end

## Notes
- The Query and SQL headers are only relevant for query result exports (not table exports), since table exports don't have an associated query
- Consider future enhancement: add a checkbox or option in the UI to toggle whether to include metadata headers
- The CSV format with metadata rows at the top is a common pattern and should be parseable by most CSV readers that allow skipping header rows
- The implementation uses Python's csv module which handles proper RFC 4180 escaping automatically
