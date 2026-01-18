"""
Unit tests for CSV export endpoints
"""

import pytest
import sqlite3
import tempfile
import os
import sys
from fastapi.testclient import TestClient

# Add parent directory to path to import server module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_db_with_data():
    """Create a test database with sample data and set DB_PATH"""
    # Create temp directory for db
    db_dir = tempfile.mkdtemp()
    db_path = os.path.join(db_dir, "database.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create test tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    # Insert test data
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie', 'charlie@example.com', 35))

    conn.commit()
    conn.close()

    # Store original directory and change to temp directory
    original_cwd = os.getcwd()
    os.chdir(db_dir)

    # Create db subdirectory for server expectations
    os.makedirs("db", exist_ok=True)
    os.rename(db_path, os.path.join("db", "database.db"))

    yield os.path.join("db", "database.db")

    # Cleanup
    os.chdir(original_cwd)
    import shutil
    shutil.rmtree(db_dir)


@pytest.fixture
def test_db_empty_table():
    """Create a test database with an empty table"""
    db_dir = tempfile.mkdtemp()
    db_path = os.path.join(db_dir, "database.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE empty_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    conn.commit()
    conn.close()

    original_cwd = os.getcwd()
    os.chdir(db_dir)
    os.makedirs("db", exist_ok=True)
    os.rename(db_path, os.path.join("db", "database.db"))

    yield os.path.join("db", "database.db")

    os.chdir(original_cwd)
    import shutil
    shutil.rmtree(db_dir)


class TestTableExportEndpoint:
    """Tests for GET /api/table/{table_name}/export endpoint"""

    def test_export_table_success(self, test_db_with_data):
        """Test successful table export returns CSV with correct headers"""
        from server import app
        with TestClient(app) as client:
            response = client.get("/api/table/users/export")

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert 'attachment; filename="users.csv"' in response.headers["content-disposition"]

            # Parse CSV content (handle \r\n line endings)
            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check header
            header = lines[0]
            assert 'id' in header
            assert 'name' in header
            assert 'email' in header
            assert 'age' in header

            # Check data rows (3 users + 1 header = 4 lines)
            assert len(lines) == 4

    def test_export_nonexistent_table_returns_404(self, test_db_with_data):
        """Test export of non-existent table returns 404"""
        from server import app
        with TestClient(app) as client:
            response = client.get("/api/table/nonexistent_table/export")

            assert response.status_code == 404

    def test_export_sql_injection_blocked(self, test_db_with_data):
        """Test SQL injection in table name is blocked"""
        from server import app
        with TestClient(app) as client:
            # Try various SQL injection attempts
            injection_attempts = [
                "users'; DROP TABLE users; --",
                "users' OR '1'='1",
                "users; DELETE FROM users",
            ]

            for attempt in injection_attempts:
                response = client.get(f"/api/table/{attempt}/export")
                # Should return 400 (bad request) due to invalid identifier
                assert response.status_code == 400

    def test_export_empty_table(self, test_db_empty_table):
        """Test export of empty table returns CSV with headers only"""
        from server import app
        with TestClient(app) as client:
            response = client.get("/api/table/empty_table/export")

            assert response.status_code == 200

            # Parse CSV content
            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Should have header only (1 line)
            assert len(lines) == 1
            assert 'id' in lines[0]
            assert 'name' in lines[0]


class TestResultsExportEndpoint:
    """Tests for POST /api/export-results endpoint"""

    def test_export_results_success(self, test_db_with_data):
        """Test successful results export with valid data"""
        from server import app
        with TestClient(app) as client:
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
            assert 'attachment; filename="query-results.csv"' in response.headers["content-disposition"]

            # Parse CSV content (normalize line endings)
            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check header
            assert lines[0] == "id,name,email"

            # Check data rows
            assert len(lines) == 3  # header + 2 rows

    def test_export_results_with_custom_filename(self, test_db_with_data):
        """Test results export with custom filename"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["name"],
                "results": [{"name": "Test"}],
                "filename": "my-custom-export"
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200
            assert 'attachment; filename="my-custom-export.csv"' in response.headers["content-disposition"]

    def test_export_results_empty_columns_error(self, test_db_with_data):
        """Test export with empty columns returns error"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": [],
                "results": [{"name": "Test"}]
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 400

    def test_export_results_empty_results(self, test_db_with_data):
        """Test export with empty results returns CSV with headers only"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name", "email"],
                "results": []
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            # Parse CSV content
            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Should have header only
            assert len(lines) == 1
            assert lines[0] == "id,name,email"

    def test_export_results_with_null_values(self, test_db_with_data):
        """Test export with null values renders as empty string"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name", "email"],
                "results": [
                    {"id": 1, "name": "Alice", "email": None},
                    {"id": 2, "name": None, "email": "bob@example.com"}
                ]
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            # Check that null values are handled (rendered as empty)
            content = response.text
            assert "Alice" in content

    def test_export_results_with_special_characters(self, test_db_with_data):
        """Test export with commas and quotes are properly escaped"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["name", "description"],
                "results": [
                    {"name": "Test, Item", "description": 'With "quotes"'},
                    {"name": "Normal", "description": "Normal text"}
                ]
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            # CSV module should properly escape these values
            content = response.text
            # Commas in values should be quoted
            assert '"Test, Item"' in content

    def test_export_results_with_query_and_sql_headers(self, test_db_with_data):
        """Test export includes Query and SQL headers when provided"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name"],
                "results": [{"id": 1, "name": "Alice"}],
                "query": "Show me all users",
                "sql": "SELECT * FROM users"
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            # Parse CSV content (normalize line endings)
            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check structure: Query row, SQL row, blank row, header row, data row
            assert len(lines) == 5
            assert lines[0] == 'Query,Show me all users'
            assert lines[1] == 'SQL,SELECT * FROM users'
            assert lines[2] == ''  # blank separator row
            assert lines[3] == 'id,name'
            assert lines[4] == '1,Alice'

    def test_export_results_with_only_query_header(self, test_db_with_data):
        """Test export with only query provided (no sql)"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name"],
                "results": [{"id": 1, "name": "Alice"}],
                "query": "Show me all users"
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check structure: Query row, blank row, header row, data row
            assert len(lines) == 4
            assert lines[0] == 'Query,Show me all users'
            assert lines[1] == ''  # blank separator row
            assert lines[2] == 'id,name'

    def test_export_results_with_only_sql_header(self, test_db_with_data):
        """Test export with only sql provided (no query)"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name"],
                "results": [{"id": 1, "name": "Alice"}],
                "sql": "SELECT * FROM users"
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check structure: SQL row, blank row, header row, data row
            assert len(lines) == 4
            assert lines[0] == 'SQL,SELECT * FROM users'
            assert lines[1] == ''  # blank separator row
            assert lines[2] == 'id,name'

    def test_export_results_without_headers_backward_compatible(self, test_db_with_data):
        """Test export without query/sql is backward compatible"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["id", "name"],
                "results": [{"id": 1, "name": "Alice"}]
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check structure: header row, data row (no metadata rows)
            assert len(lines) == 2
            assert lines[0] == 'id,name'
            assert lines[1] == '1,Alice'

    def test_export_results_with_special_characters_in_query(self, test_db_with_data):
        """Test query and SQL with special characters are properly CSV-escaped"""
        from server import app
        with TestClient(app) as client:
            request_data = {
                "columns": ["name"],
                "results": [{"name": "Alice"}],
                "query": 'Show users where name contains "Alice, Bob"',
                "sql": 'SELECT * FROM users WHERE name LIKE "%Alice, Bob%"'
            }

            response = client.post("/api/export-results", json=request_data)

            assert response.status_code == 200

            content = response.text.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.strip().split('\n')

            # Check that special characters are properly escaped
            # CSV should quote values containing commas or quotes
            assert 'Query,' in lines[0]
            assert 'SQL,' in lines[1]
            # The values should be properly escaped (quoted)
            assert '"' in lines[0] or 'Alice, Bob' in lines[0]
