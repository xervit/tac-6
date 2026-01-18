"""
Tests for the export endpoints (table export and query results export)
"""

import pytest
import sqlite3
import tempfile
import os
import csv
import io
from fastapi.testclient import TestClient
from unittest.mock import patch

# We need to set up the database path before importing the app
@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a test database before each test"""
    # Ensure db directory exists
    os.makedirs("db", exist_ok=True)

    # Create test database
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS test_users")
    cursor.execute("DROP TABLE IF EXISTS empty_table")

    # Create test tables
    cursor.execute('''
        CREATE TABLE test_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    # Create an empty table for testing empty exports
    cursor.execute('''
        CREATE TABLE empty_table (
            id INTEGER PRIMARY KEY,
            value TEXT
        )
    ''')

    # Insert test data with special characters
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob, Jr.', 'bob@example.com', 25))  # Name with comma
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie "Chuck"', 'charlie@example.com', 35))  # Name with quotes

    conn.commit()
    conn.close()

    yield

    # Cleanup
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_users")
    cursor.execute("DROP TABLE IF EXISTS empty_table")
    conn.commit()
    conn.close()


from server import app

client = TestClient(app)


class TestTableExportEndpoint:
    """Test the GET /api/table/{table_name}/export endpoint"""

    def test_export_valid_table(self):
        """Test exporting a valid table returns CSV data"""
        response = client.get("/api/table/test_users/export")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="test_users.csv"' in response.headers["content-disposition"]

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check header
        assert rows[0] == ['id', 'name', 'email', 'age']

        # Check data rows (3 rows of data)
        assert len(rows) == 4  # 1 header + 3 data rows

    def test_export_table_csv_escaping(self):
        """Test that special characters are properly escaped in CSV"""
        response = client.get("/api/table/test_users/export")

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check that comma in name is properly handled
        names = [row[1] for row in rows[1:]]  # Skip header
        assert 'Bob, Jr.' in names
        assert 'Charlie "Chuck"' in names

    def test_export_missing_table(self):
        """Test exporting a non-existent table returns 404"""
        response = client.get("/api/table/nonexistent_table/export")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_invalid_table_name(self):
        """Test exporting with invalid table name returns 400"""
        response = client.get("/api/table/users';DROP TABLE users;--/export")

        assert response.status_code == 400

    def test_export_empty_table(self):
        """Test exporting an empty table returns CSV with only headers"""
        response = client.get("/api/table/empty_table/export")

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check only header row exists
        assert len(rows) == 1
        assert rows[0] == ['id', 'value']


class TestExportResultsEndpoint:
    """Test the POST /api/export-results endpoint"""

    def test_export_valid_results(self):
        """Test exporting valid query results returns CSV data"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="query_results.csv"' in response.headers["content-disposition"]

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check header
        assert rows[0] == ['id', 'name', 'email']

        # Check data rows
        assert len(rows) == 3  # 1 header + 2 data rows
        assert rows[1] == ['1', 'Alice', 'alice@example.com']
        assert rows[2] == ['2', 'Bob', 'bob@example.com']

    def test_export_results_with_custom_filename(self):
        """Test exporting with custom filename"""
        request_data = {
            "columns": ["id", "name"],
            "results": [{"id": 1, "name": "Test"}],
            "filename": "my_export.csv"
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200
        assert 'attachment; filename="my_export.csv"' in response.headers["content-disposition"]

    def test_export_results_filename_without_extension(self):
        """Test that .csv extension is added if missing"""
        request_data = {
            "columns": ["id"],
            "results": [{"id": 1}],
            "filename": "my_export"
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200
        assert 'attachment; filename="my_export.csv"' in response.headers["content-disposition"]

    def test_export_empty_results(self):
        """Test exporting empty results returns CSV with only headers"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": []
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check only header row exists
        assert len(rows) == 1
        assert rows[0] == ['id', 'name', 'email']

    def test_export_results_with_null_values(self):
        """Test exporting results with null values"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": None},
                {"id": 2, "name": None, "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Null values should be converted to empty strings or "None"
        assert len(rows) == 3

    def test_export_results_with_nested_objects(self):
        """Test exporting results with nested objects (should be stringified)"""
        request_data = {
            "columns": ["id", "data"],
            "results": [
                {"id": 1, "data": {"nested": "value"}},
                {"id": 2, "data": ["list", "values"]}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Nested objects should be stringified
        assert len(rows) == 3
        assert "nested" in rows[1][1]  # Dict should be converted to string
        assert "list" in rows[2][1]  # List should be converted to string

    def test_export_results_csv_escaping(self):
        """Test that special characters are properly escaped in CSV"""
        request_data = {
            "columns": ["id", "description"],
            "results": [
                {"id": 1, "description": "Contains, comma"},
                {"id": 2, "description": 'Contains "quotes"'},
                {"id": 3, "description": "Contains\nnewline"}
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content - csv module handles proper parsing
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Check that special characters are properly parsed back
        assert rows[1][1] == "Contains, comma"
        assert rows[2][1] == 'Contains "quotes"'
        assert rows[3][1] == "Contains\nnewline"

    def test_export_results_missing_column_in_row(self):
        """Test exporting results where a row is missing a column value"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice"},  # Missing email
                {"id": 2, "email": "bob@example.com"}  # Missing name
            ]
        }

        response = client.post("/api/export-results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content
        content = response.text
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Missing values should be empty strings
        assert len(rows) == 3
        assert rows[1][2] == ""  # Missing email should be empty
        assert rows[2][1] == ""  # Missing name should be empty
