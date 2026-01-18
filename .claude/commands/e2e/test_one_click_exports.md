# E2E Test: One Click Table Exports

Test one-click CSV export functionality for both database tables and query results.

## User Story

As a user
I want to export tables and query results as CSV files with a single click
So that I can easily save and share my data for offline analysis or external use

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Upload Data button
   - Available Tables section

5. Load the "users" sample data by clicking "Upload Data" button
6. Click on the "Users" sample data button to load sample data
7. Wait for table to appear in Available Tables section
8. Take a screenshot showing the loaded table
9. **Verify** download button (down arrow icon) appears to the LEFT of the × remove button for the users table
10. Click the download button for the users table
11. **Verify** CSV file download initiates (check for download or blob URL creation)
12. Take a screenshot after clicking download button

13. Enter the query: "Show me all users"
14. Click the Query button
15. Wait for results to appear
16. Take a screenshot of the query results
17. **Verify** download button appears to the LEFT of the Hide button in results section
18. Click the download button for query results
19. **Verify** CSV file download initiates for query results
20. Take a screenshot after clicking results download button

21. Click "Hide" button to verify existing functionality still works
22. Take a screenshot of the final state

## Success Criteria
- Download button appears to the LEFT of the × button for each available table
- Download button appears to the LEFT of the Hide button in query results
- Clicking table download button initiates CSV file download
- Clicking results download button initiates CSV file download
- All existing functionality continues to work (query execution, results display, hide button)
- 6 screenshots are taken
