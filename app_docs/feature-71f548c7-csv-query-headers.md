# CSV Export with Query and SQL Headers

**ADW ID:** 71f548c7
**Date:** 2026-01-18
**Specification:** specs/issue-9-adw-71f548c7-sdlc_planner-add-query-sql-csv-headers.md

## Overview

This feature enhances the CSV export functionality to include metadata headers at the top of exported files. When users export query results, the CSV now includes the original natural language query and the generated SQL statement as header rows, making exported files self-documenting and more useful for sharing or archival purposes.

## Screenshots

![Initial Application State](assets/01_initial_state.png)

![Query Results with Metadata Ready for Export](assets/02_query_results_with_metadata.png)

![CSV Download Complete with Query and SQL Headers](assets/03_csv_download_complete.png)

## What Was Built

- Enhanced CSV export data model to accept optional query and SQL metadata
- Modified server export endpoint to write metadata headers at the top of CSV files
- Updated client-side export function to pass query and SQL parameters
- Integrated query and SQL values into the download button handler
- Added comprehensive unit tests for the new functionality
- Created E2E test specification for validating the complete user flow

## Technical Implementation

### Files Modified

- `app/server/core/data_models.py`: Added optional `query` and `sql` fields to `ExportResultsRequest` model
- `app/server/server.py`: Modified `/api/export-results` endpoint to write query and SQL metadata rows before data headers
- `app/client/src/api/client.ts`: Updated `exportResults` function signature to accept optional `query` and `sql` parameters
- `app/client/src/main.ts`: Modified download button handler in `displayResults` to pass query and SQL values
- `app/server/tests/test_export.py`: Added 4 new unit tests covering metadata headers and backward compatibility
- `.claude/commands/e2e/test_csv_query_headers.md`: Created E2E test specification for validating the feature

### Key Changes

- The `ExportResultsRequest` model now includes `query: Optional[str]` and `sql: Optional[str]` fields with proper descriptions
- Server writes metadata rows in the format: `Query,<value>` then `SQL,<value>` followed by a blank separator row before column headers
- Client API function now accepts and passes query and SQL parameters in the request body
- Download button handler passes the original query string and `response.sql` from the query response
- Backward compatible: exports without query/SQL parameters continue to work as before

## How to Use

1. Load sample data or ensure a database is connected
2. Enter a natural language query (e.g., "Show me all users")
3. Click the "Run Query" button to execute the query
4. Once results are displayed, click the "Download" button (down arrow icon)
5. Open the downloaded CSV file - you'll see:
   - Line 1: `Query,<your natural language query>`
   - Line 2: `SQL,<the generated SQL statement>`
   - Line 3: (blank separator row)
   - Line 4+: Column headers and data rows

## Configuration

No configuration required. The feature works automatically when exporting query results. Metadata headers are included whenever both the query string and SQL statement are available in the query response.

## Testing

### Unit Tests

Run server tests with:
```bash
cd app/server && uv run pytest
```

The following test cases validate the feature:
- `test_export_results_with_query_and_sql_headers`: Verifies both Query and SQL headers appear
- `test_export_results_with_only_query_header`: Tests export with only query provided
- `test_export_results_with_only_sql_header`: Tests export with only SQL provided
- `test_export_results_without_headers_backward_compatible`: Ensures backward compatibility

### E2E Testing

The feature includes an E2E test specification at `.claude/commands/e2e/test_csv_query_headers.md` that validates:
- Query execution and result display
- CSV download functionality
- Presence of Query and SQL headers in the exported file
- Proper formatting with blank separator row

## Notes

- CSV escaping is handled automatically by Python's csv module (RFC 4180 compliant)
- Metadata headers are only relevant for query results (not table exports), as table exports don't have an associated query
- The blank separator row improves visual clarity when viewing the CSV
- Future enhancement consideration: add UI option to toggle whether to include metadata headers
- Works with queries containing special characters (commas, quotes) - properly escaped in CSV format
