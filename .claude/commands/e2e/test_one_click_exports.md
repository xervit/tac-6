# E2E Test: One Click Table Exports

Test one-click CSV export functionality for tables and query results in the Natural Language SQL Interface application.

## User Story

As a data analyst
I want to export tables and query results as CSV files with a single click
So that I can easily share and analyze data in spreadsheet applications without manual data extraction

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Upload Data button
   - Available Tables section

5. **Verify** the "users" table is shown in Available Tables
6. **Verify** a download button appears to the left of the × (remove) button for the users table
7. Take a screenshot showing the table with download button
8. Click the download button for the users table
9. **Verify** a CSV file download is triggered (check network requests for the export endpoint call)
10. Take a screenshot after clicking download button

11. Enter the query: "Show me all users"
12. Click the Query button
13. **Verify** the query results appear
14. **Verify** a download button appears to the left of the Hide button in the results section
15. Take a screenshot showing the results with download button
16. Click the download button for the query results
17. **Verify** a CSV download is triggered for the results
18. Take a screenshot after clicking results download button

## Success Criteria
- Download button is visible next to × button for each table in Available Tables
- Download button is visible next to Hide button in Query Results section
- Clicking table download button triggers CSV download for that table
- Clicking results download button triggers CSV download for query results
- All existing functionality continues to work (query execution, hide button, etc.)
- 6 screenshots are taken documenting the export flow
