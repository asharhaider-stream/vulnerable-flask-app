import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200

def test_search_returns_200(client):
    response = client.get("/search?cnic=test")
    assert response.status_code == 200

def test_sql_injection_returns_results(client):
    response = client.get("/search?cnic=' OR '1'='1")
    assert response.status_code == 200

def test_report_page_loads(client):
    response = client.get("/report?name=TestOfficer")
    assert response.status_code == 200

def test_xss_reflects_input(client):
    response = client.get("/report?name=<script>alert(1)</script>")
    assert response.status_code == 200

def test_download_valid_file(client):
    response = client.get("/download?file=case001.txt")
    assert response.status_code == 200

def test_download_missing_file(client):
    response = client.get("/download?file=nonexistent.txt")
    assert response.status_code == 200
    assert b"File not found" in response.data