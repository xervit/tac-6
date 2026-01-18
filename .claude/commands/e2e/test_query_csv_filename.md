# E2E Test: Query-Based CSV Filename

Test that exported CSV files are named based on the natural language query text.

## User Story

As a user
I want my exported query results to be named after the query I ran
So that I can easily identify and organize my downloaded CSV files

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
13. **Verify** download button appears in the results section
14. Inspect the download button's onclick handler or hover over it
15. **Verify** clicking the download button would produce a filename containing "show_me_all_users" (sanitized version of the query)
16. Click the download button for query results
17. **Verify** the downloaded file is named with a sanitized version of the query (e.g., "show_me_all_users.csv")
18. Take a screenshot after clicking download button

19. Enter a new query: "Find products with price greater than 50"
20. Click the Query button
21. Wait for results to appear
22. Take a screenshot of the new query results
23. Click the download button for the new query results
24. **Verify** the downloaded file is named with the new sanitized query (e.g., "find_products_with_price_greater_than_50.csv")
25. Take a screenshot after clicking second download button

26. Click "Hide" button to verify existing functionality still works
27. Take a screenshot of the final state

## Success Criteria
- Download button appears in query results section
- Clicking download button initiates CSV file download with query-based filename
- Filename is sanitized (spaces replaced with underscores, special characters removed)
- Different queries produce different filenames
- Empty or invalid queries fall back to "query-results" as filename
- All existing functionality continues to work (query execution, results display, hide button)
- 7 screenshots are taken
