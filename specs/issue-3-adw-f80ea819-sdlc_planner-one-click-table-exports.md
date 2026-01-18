# Feature: One Click Table Exports

## Metadata
issue_number: `3`
adw_id: `f80ea819`
issue_json: `{"number":3,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality for both database tables and query results. Users will be able to download any available table as a CSV file by clicking a download button next to the table name. Similarly, after running a query, users can export the query results as a CSV file with a single click. This provides a seamless way to extract data from the application for further analysis or sharing.

## User Story
As a user of the Natural Language SQL Interface
I want to export tables and query results as CSV files with a single click
So that I can easily save and share my data for offline analysis or external use

## Problem Statement
Currently, users can upload data, query it using natural language, and view results, but there is no way to export data back out of the application. Users who want to save their query results or download an entire table must manually copy data, which is error-prone and time-consuming for large datasets.

## Solution Statement
Implement two new server endpoints for CSV export and add download buttons to the UI:
1. A `GET /api/table/{table_name}/export` endpoint that exports an entire table as CSV
2. A `POST /api/export-results` endpoint that exports query results as CSV
3. A download button (↓ icon) placed to the left of the × remove button for each table
4. A download button placed to the left of the Hide button for query results

Both exports will trigger immediate file downloads with appropriate filenames (table name or "query-results" with timestamps).

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Main FastAPI server where new export endpoints will be added (follows existing endpoint patterns)
- `app/server/core/data_models.py` - Pydantic models for request/response types; add ExportResultsRequest model
- `app/server/core/sql_security.py` - Security utilities for validating table names and executing queries safely
- `app/server/core/sql_processor.py` - SQL execution utilities used to fetch table data
- `app/client/src/main.ts` - Main client application; add download buttons to displayTables() and displayResults() functions
- `app/client/src/api/client.ts` - API client; add exportTable() and exportResults() methods
- `app/client/src/style.css` - Styles for new download buttons
- `app/client/src/types.d.ts` - TypeScript type definitions; add ExportResultsRequest interface
- `app/server/tests/` - Directory for server tests; add test_export.py for export endpoint tests
- `.claude/commands/test_e2e.md` - E2E test runner instructions (read to understand how to create E2E tests)
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file (read to understand E2E test format)

### New Files
- `app/server/tests/test_export.py` - Unit tests for the new export endpoints
- `.claude/commands/e2e/test_one_click_exports.md` - E2E test file for validating export functionality

## Implementation Plan
### Phase 1: Foundation
Set up the backend infrastructure for CSV exports:
- Create the Pydantic request model for export results endpoint
- Implement CSV generation utility function
- Add the table export endpoint with proper security validation
- Add the query results export endpoint

### Phase 2: Core Implementation
Implement the client-side functionality:
- Add API client methods for export endpoints
- Update TypeScript types for export requests
- Add download button to table display (left of × icon)
- Add download button to results section (left of Hide button)
- Implement file download triggering logic
- Style the new download buttons consistently

### Phase 3: Integration
Test and validate the complete feature:
- Write unit tests for export endpoints
- Create E2E test file for export functionality
- Run full test suite to ensure no regressions
- Verify download behavior in browser

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` to understand E2E test runner
- Read `.claude/commands/e2e/test_basic_query.md` as an example E2E test
- Create `.claude/commands/e2e/test_one_click_exports.md` with test steps that:
  - Navigate to the application
  - Load sample data (users table)
  - Verify download button appears next to table × icon
  - Click download button for table export
  - Verify CSV file download initiates
  - Run a query to get results
  - Verify download button appears in results section (left of Hide button)
  - Click download button for results export
  - Verify CSV file download initiates
  - Take screenshots at key verification points

### Task 2: Add Pydantic Request Model
- Edit `app/server/core/data_models.py`
- Add `ExportResultsRequest` model with:
  - `columns: List[str]` - column names for CSV header
  - `results: List[Dict[str, Any]]` - the query result rows
  - `filename: Optional[str]` - optional custom filename

### Task 3: Implement Table Export Endpoint
- Edit `app/server/server.py`
- Add `GET /api/table/{table_name}/export` endpoint
- Use `validate_identifier()` to validate table_name
- Use `check_table_exists()` to verify table exists
- Execute `SELECT * FROM [table_name]` using `execute_query_safely()`
- Convert results to CSV format using Python's csv module with StringIO
- Return as `StreamingResponse` with:
  - `media_type="text/csv"`
  - `Content-Disposition: attachment; filename="{table_name}.csv"`
- Add proper error handling and logging

### Task 4: Implement Results Export Endpoint
- Edit `app/server/server.py`
- Add `POST /api/export-results` endpoint
- Accept `ExportResultsRequest` body
- Validate columns list is not empty
- Generate CSV from columns and results using csv module
- Return as `StreamingResponse` with:
  - `media_type="text/csv"`
  - `Content-Disposition: attachment; filename="{filename or 'query-results'}.csv"`
- Add proper error handling and logging

### Task 5: Add TypeScript Types
- Edit `app/client/src/types.d.ts`
- Add `ExportResultsRequest` interface matching the Pydantic model

### Task 6: Add API Client Methods
- Edit `app/client/src/api/client.ts`
- Add `exportTable(tableName: string): Promise<void>` method
  - Fetch from `/api/table/{tableName}/export`
  - Create blob from response
  - Trigger download using temporary anchor element
- Add `exportResults(columns: string[], results: Record<string, unknown>[], filename?: string): Promise<void>` method
  - POST to `/api/export-results` with request body
  - Create blob from response
  - Trigger download using temporary anchor element

### Task 7: Add Download Button Styles
- Edit `app/client/src/style.css`
- Add `.download-table-button` class styled similarly to `.remove-table-button`
  - Consistent sizing and hover effects
  - Position to appear left of remove button
- Add `.download-results-button` class for the results download button
  - Style to match the toggle button aesthetic
- Add `.table-actions` container class for grouping table action buttons
- Add `.results-actions` container class for grouping results action buttons

### Task 8: Add Download Button to Tables Display
- Edit `app/client/src/main.ts` in the `displayTables()` function (around line 288)
- Create a container div with class `table-actions` to hold both buttons
- Create download button element:
  - Class: `download-table-button`
  - innerHTML: `&#8681;` (↓ down arrow icon)
  - title: `Download as CSV`
  - onclick: call `api.exportTable(table.name)`
- Insert download button to the LEFT of the existing remove button
- Wrap both buttons in the `table-actions` container

### Task 9: Add Download Button to Results Display
- Edit `app/client/src/main.ts` in the `displayResults()` function
- Find where the toggle (Hide) button is referenced
- Create a container div with class `results-actions` to hold both buttons
- Create download button element:
  - Class: `download-results-button`
  - innerHTML: `&#8681;` (↓ down arrow icon) or text "Download"
  - title: `Download results as CSV`
  - onclick: call `api.exportResults(response.columns, response.results)`
- Insert download button to the LEFT of the Hide button
- Store results data in a way accessible to the download handler

### Task 10: Write Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py`
- Test table export endpoint:
  - Test successful export returns CSV with correct headers
  - Test export of non-existent table returns 404
  - Test SQL injection in table name is blocked
- Test results export endpoint:
  - Test successful export with valid data
  - Test export with empty columns returns error
  - Test export with empty results returns CSV with headers only
- Use pytest fixtures for test database setup

### Task 11: Run Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate no TypeScript errors
- `cd app/client && bun run build` - Run frontend build to validate the feature compiles correctly
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_one_click_exports.md` test file to validate export functionality works end-to-end

## Testing Strategy
### Unit Tests
- Test table export endpoint returns valid CSV format
- Test table export with special characters in table name
- Test results export with various data types (strings, numbers, nulls)
- Test export endpoints return proper Content-Disposition headers
- Test error handling for invalid requests

### Edge Cases
- Export table with no rows (should return CSV with headers only)
- Export table with unicode characters in data
- Export results with null values (should render as empty string in CSV)
- Export table name with spaces or special characters (validate identifier blocks these)
- Very large table export (streaming response handles memory efficiently)
- Results with columns containing commas or quotes (proper CSV escaping)

## Acceptance Criteria
- Download button (↓ icon) appears to the LEFT of the × button for each available table
- Download button appears to the LEFT of the Hide button in the query results section
- Clicking table download button initiates a CSV file download named `{table_name}.csv`
- Clicking results download button initiates a CSV file download named `query-results.csv`
- Downloaded CSV files contain correct headers matching column names
- Downloaded CSV files contain all data rows properly formatted
- Export works for tables with various data types (text, numbers, dates)
- All existing functionality continues to work (no regressions)
- All server tests pass
- TypeScript compilation succeeds with no errors
- Frontend build succeeds
- E2E test validates export functionality works correctly

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_one_click_exports.md` E2E test file to validate this functionality works.

## Notes
- The download icon `&#8681;` (↓) is a Unicode down arrow that matches the existing icon-based UI pattern using HTML entities
- CSV generation uses Python's built-in csv module for proper escaping and RFC 4180 compliance
- StreamingResponse is used for exports to handle large datasets efficiently without loading everything into memory
- The client triggers downloads by creating a temporary anchor element with blob URL, which works across all modern browsers
- A previous implementation of this feature existed in commit d6d79a2 but was reverted - this plan follows similar patterns but with complete specification
- Consider future enhancement: Add format selection (CSV, JSON, Excel) in a dropdown menu
