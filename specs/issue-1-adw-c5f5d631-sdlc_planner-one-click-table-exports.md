# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `c5f5d631`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality to the Natural Language SQL Interface application. Users will be able to export:
1. **Table data**: Download any available table as a CSV file with a single click
2. **Query results**: Download the results of any executed query as a CSV file

The feature requires two new backend API endpoints and UI modifications to add download buttons in the appropriate locations.

## User Story
As a data analyst
I want to export tables and query results as CSV files with a single click
So that I can easily share and analyze data in spreadsheet applications without manual data extraction

## Problem Statement
Currently, users can view data in the application but have no way to export it. If they need to use the data outside the application (in Excel, Google Sheets, or for reporting), they must manually copy and paste data or recreate queries elsewhere. This creates friction in the data analysis workflow and limits the application's utility.

## Solution Statement
Add download buttons to both the Available Tables section and the Query Results section that trigger CSV file downloads:
1. Create a `GET /api/table/{table_name}/export` endpoint that returns table data as a CSV file
2. Create a `POST /api/export-results` endpoint that accepts query results and returns them as a CSV file
3. Add a download button (with appropriate icon) to the left of the × (remove) button for each table in the Available Tables section
4. Add a download button (with appropriate icon) to the left of the Hide button in the Query Results section

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Main FastAPI server where new export endpoints will be added
- `app/server/core/data_models.py` - Pydantic models for request/response types; may need new models for export
- `app/server/core/sql_processor.py` - Contains `execute_sql_safely` function used to query tables
- `app/server/core/sql_security.py` - Security utilities for safe SQL execution; use for table export endpoint
- `app/client/src/main.ts` - Main client TypeScript file where UI logic and button handlers are implemented
- `app/client/src/api/client.ts` - API client with methods for backend communication; needs new export methods
- `app/client/src/types.d.ts` - TypeScript type definitions; may need new types for export responses
- `app/client/src/style.css` - Stylesheet for styling the new download buttons
- `app/client/index.html` - HTML template (likely no changes needed, buttons added dynamically)
- `.claude/commands/test_e2e.md` - E2E test runner documentation to understand how to create E2E tests
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test to follow for creating new E2E test

### New Files
- `.claude/commands/e2e/test_one_click_exports.md` - E2E test file to validate export functionality

## Implementation Plan
### Phase 1: Foundation
- Add new Pydantic models for export responses (if needed)
- Create the table export endpoint (`GET /api/table/{table_name}/export`)
- Create the query results export endpoint (`POST /api/export-results`)
- Write backend unit tests for the new endpoints

### Phase 2: Core Implementation
- Add API client methods for the new export endpoints
- Create the download button UI component with appropriate styling
- Add download button to the Available Tables section (left of × button)
- Add download button to the Query Results section (left of Hide button)
- Implement click handlers that trigger CSV downloads

### Phase 3: Integration
- Test full flow: table export from Available Tables
- Test full flow: query results export after running a query
- Verify CSV files are properly formatted
- Ensure error handling for edge cases (empty results, missing tables)

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format
- Create `.claude/commands/e2e/test_one_click_exports.md` with test steps for:
  - Uploading sample data
  - Verifying download button appears next to table × button
  - Clicking table download button and verifying CSV download
  - Running a query
  - Verifying download button appears next to Hide button
  - Clicking results download button and verifying CSV download
- Include screenshots for each major step

### Task 2: Add Backend Table Export Endpoint
- Open `app/server/server.py`
- Add `from fastapi.responses import StreamingResponse` import
- Create `GET /api/table/{table_name}/export` endpoint that:
  - Validates table name using `validate_identifier`
  - Checks table exists using `check_table_exists`
  - Queries all data from the table using `execute_query_safely`
  - Converts results to CSV format using Python's `csv` module with `io.StringIO`
  - Returns `StreamingResponse` with `media_type="text/csv"` and appropriate `Content-Disposition` header for download
- Add proper error handling (404 for missing table, 500 for internal errors)

### Task 3: Add Backend Query Results Export Endpoint
- Open `app/server/core/data_models.py`
- Add `ExportResultsRequest` model with:
  - `columns: List[str]` - column names
  - `results: List[Dict[str, Any]]` - result data
  - `filename: Optional[str]` - optional custom filename
- Open `app/server/server.py`
- Create `POST /api/export-results` endpoint that:
  - Accepts `ExportResultsRequest` body
  - Converts columns and results to CSV format
  - Returns `StreamingResponse` with CSV data and download headers
- Add proper error handling for empty results

### Task 4: Write Backend Unit Tests
- Open `app/server/tests/` directory (create if needed)
- Create test file `test_export_endpoints.py`
- Write tests for:
  - `GET /api/table/{table_name}/export` with valid table
  - `GET /api/table/{table_name}/export` with invalid/missing table
  - `POST /api/export-results` with valid data
  - `POST /api/export-results` with empty results
  - Verify CSV format is correct (headers, data rows, proper escaping)

### Task 5: Add Frontend API Client Methods
- Open `app/client/src/api/client.ts`
- Add `exportTable(tableName: string): Promise<void>` method that:
  - Constructs URL `${API_BASE_URL}/table/${tableName}/export`
  - Fetches the CSV data
  - Triggers browser download using `URL.createObjectURL` and programmatic anchor click
- Add `exportResults(columns: string[], results: Record<string, any>[], filename?: string): Promise<void>` method that:
  - POSTs to `/export-results` with JSON body
  - Handles the CSV response and triggers download

### Task 6: Add Download Button Styles
- Open `app/client/src/style.css`
- Add `.download-table-button` class styled similarly to `.remove-table-button`:
  - No background, no border
  - Icon size 1.5rem (or appropriate)
  - Hover effect with light background
  - Cursor pointer
- Add `.download-results-button` class styled similarly to `.toggle-button`:
  - Consistent with existing button styling
  - Positioned to the left of Hide button

### Task 7: Add Download Button to Available Tables
- Open `app/client/src/main.ts`
- In the `displayTables` function, locate where `removeButton` is created
- Before `removeButton`, create a `downloadButton`:
  - Use download icon (↓ arrow or appropriate Unicode/SVG icon like ⬇ or use `innerHTML = '&#x2B07;'` or similar)
  - Add class `download-table-button`
  - Set `title = 'Download as CSV'`
  - Add click handler that calls `api.exportTable(table.name)`
- Insert `downloadButton` into `tableHeader` before `removeButton`
- Update the button container to include both buttons with proper spacing

### Task 8: Add Download Button to Query Results
- Open `app/client/src/main.ts`
- In the `displayResults` function, locate where the toggle button is handled
- Store the current query results in a variable accessible to the download handler
- Create a download button:
  - Use download icon consistent with table download button
  - Add class `download-results-button`
  - Set `title = 'Download results as CSV'`
  - Add click handler that calls `api.exportResults(response.columns, response.results)`
- Modify the results header to include the download button left of Hide button
- Note: May need to update `index.html` to add a container for multiple buttons, or create buttons dynamically

### Task 9: Update TypeScript Types (if needed)
- Open `app/client/src/types.d.ts`
- Add any new types if required for export functionality
- Ensure types match backend models

### Task 10: Run Validation Commands
- Run all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint returns valid CSV with correct headers and data
- Test table export endpoint handles missing tables with 404
- Test table export endpoint handles invalid table names with 400
- Test results export endpoint converts JSON to CSV correctly
- Test results export endpoint handles empty results array
- Test CSV escaping for special characters (commas, quotes, newlines)

### Edge Cases
- Empty table (table exists but has no rows)
- Table with special characters in column names
- Query results with null values
- Query results with nested objects (should be stringified)
- Large datasets (ensure streaming works properly)
- Concurrent export requests
- Unicode characters in data

## Acceptance Criteria
- [ ] Download button with appropriate icon appears directly to the left of × button for each table in Available Tables
- [ ] Download button with appropriate icon appears directly to the left of Hide button in Query Results
- [ ] Clicking table download button downloads a CSV file named `{table_name}.csv`
- [ ] Clicking results download button downloads a CSV file (e.g., `query_results.csv`)
- [ ] Downloaded CSV files open correctly in Excel/Google Sheets
- [ ] CSV files contain proper headers matching column names
- [ ] CSV files contain all data rows
- [ ] Special characters (commas, quotes) are properly escaped in CSV
- [ ] Error messages appear if export fails
- [ ] All existing functionality continues to work (no regressions)
- [ ] All unit tests pass
- [ ] E2E test validates the complete export flow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_one_click_exports.md` E2E test file to validate this functionality works
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate no TypeScript errors
- `cd app/client && bun run build` - Run frontend build to validate the feature compiles correctly

## Notes
- Use the standard download icon: ⬇️ (or `&#x2B07;` / `&#8681;` in HTML) for consistency
- Consider using an SVG icon for better rendering across platforms
- The CSV export uses Python's built-in `csv` module which handles proper escaping
- StreamingResponse is used for efficient memory usage with large datasets
- The frontend uses `URL.createObjectURL` with `Blob` for triggering downloads without page navigation
- Future enhancement: Add export format options (JSON, Excel) - out of scope for this feature
