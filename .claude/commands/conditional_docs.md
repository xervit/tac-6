# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions
- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on anything under app/server
    - When operating on anything under app/client
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the server or client

- app/client/src/style.css
  - Conditions:
    - When you need to make changes to the client's style

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `adws/adw_*.py` files

- adws/README.md
  - Conditions:
    - When you're operating in the `adws/` directory

- app_docs/bug-d3aa734f-consecutive-query-clonenode-fix.md
  - Conditions:
    - When working with the displayResults() function in app/client/src/main.ts
    - When debugging consecutive query execution issues
    - When implementing features that manipulate the results section DOM
    - When troubleshooting "Cannot read properties of null" errors related to cloneNode
    - When working with the toggle button or results actions container
- app_docs/feature-f80ea819-one-click-table-exports.md
  - Conditions:
    - When implementing CSV export functionality
    - When working with table or query result data exports
    - When adding download buttons to the UI
    - When troubleshooting export endpoint issues
    - When modifying the ADW pipeline test configuration
- app_docs/feature-71f548c7-csv-query-headers.md
  - Conditions:
    - When working with CSV export metadata or headers
    - When implementing query context preservation in exports
    - When modifying the ExportResultsRequest data model
    - When troubleshooting CSV export formatting issues
    - When adding metadata to exported files
