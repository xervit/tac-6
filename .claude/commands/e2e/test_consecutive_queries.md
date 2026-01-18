# E2E Test: Consecutive Queries

Test that multiple consecutive queries execute without errors (validates fix for cloneNode null error).

## User Story

As a user
I want to run multiple queries in succession
So that I can explore my data without needing to refresh the page

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"

### First Query Execution
4. Enter the query: "Show all products"
5. Take a screenshot of the query input
6. Click the Query button
7. Wait for results to appear
8. **Verify** the results section is visible
9. **Verify** the SQL translation is displayed (should contain "SELECT")
10. **Verify** the results table contains data
11. Take a screenshot of the first query results
12. **Verify** the Hide button is visible
13. **Verify** the Download button is visible

### Second Query Execution
14. Enter the query: "Show products with price greater than 50"
15. Take a screenshot of the second query input
16. Click the Query button
17. Wait for results to appear
18. **Verify** NO JavaScript errors occur (specifically "Cannot read properties of null (reading 'cloneNode')")
19. **Verify** the results section is still visible
20. **Verify** the SQL translation is updated
21. **Verify** the results table shows filtered data
22. Take a screenshot of the second query results
23. **Verify** the Hide button is still functional
24. **Verify** the Download button is still visible

### Third Query Execution
25. Enter the query: "Count total products"
26. Take a screenshot of the third query input
27. Click the Query button
28. Wait for results to appear
29. **Verify** NO JavaScript errors occur
30. **Verify** the results section is still visible
31. **Verify** the SQL translation is updated (should contain "COUNT")
32. Take a screenshot of the third query results

### Toggle Button Functionality
33. Click the Hide button
34. **Verify** results container is hidden
35. **Verify** button text changes to "Show"
36. Take a screenshot of hidden results state
37. Click the Show button
38. **Verify** results container is visible again
39. **Verify** button text changes back to "Hide"
40. Take a screenshot of shown results state

### Download Button Functionality
41. **Verify** the Download button is present and clickable
42. Take a final screenshot showing the complete interface

## Success Criteria
- First query executes successfully and displays results
- Second query executes successfully without cloneNode error
- Third query executes successfully to confirm robustness
- Hide/Show toggle button works correctly after multiple queries
- Download button remains functional after multiple queries
- No JavaScript console errors during execution
- 10 screenshots are taken
