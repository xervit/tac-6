# E2E Test: CSV Query and SQL Headers

Test that exported CSV files include the original query and SQL statement as header rows.

## User Story

As a user exporting query results
I want to see the original query and SQL statement at the top of my CSV file
So that I can remember what query produced these results when viewing the file later

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

9. Enter the query: "Show me all users"
10. Click the Query button
11. Wait for results to appear
12. Take a screenshot of the query results
13. **Verify** results display shows both the Query and SQL

14. Click the download button for query results
15. **Verify** CSV file download initiates
16. **Verify** the downloaded CSV contains:
    - First row starts with "Query," followed by the natural language query
    - Second row starts with "SQL," followed by the generated SQL statement
    - Third row is blank (separator)
    - Fourth row contains the column headers
    - Subsequent rows contain the data
17. Take a screenshot after download verification

18. Run a second query: "Show users older than 25"
19. Click the Query button
20. Wait for results to appear
21. Click the download button for the new results
22. **Verify** the new CSV contains the updated Query and SQL headers
23. Take a screenshot of final state

## Success Criteria
- Download button appears for query results
- Clicking results download button initiates CSV file download
- CSV file contains "Query,<natural language query>" as the first row
- CSV file contains "SQL,<sql statement>" as the second row
- A blank row separates the metadata from the column headers
- Column headers appear after the blank row
- Data rows follow the column headers
- Special characters in query or SQL are properly CSV-escaped
- 5 screenshots are taken
