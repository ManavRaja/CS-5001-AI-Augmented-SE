import pytest
from flask import Flask
from src.flask import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Welcome to the minimal Flask project!"

def test_echo_route(client):
    test_data = {"key": "value"}
    response = client.post('/echo', json=test_data)
    assert response.status_code == 200
    assert response.json == test_data

def test_echo_route_empty_payload(client):
    response = client.post('/echo', json={})
    assert response.status_code == 200
    assert response.json == {}

def test_echo_route_invalid_json(client):
    response = client.post('/echo', data='invalid json')
    assert response.status_code == 415

def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_echo_route_non_json_payload(client):
    response = client.post('/echo', data='plain text')
    assert response.status_code == 415

def test_echo_route_missing_json_header(client):
    response = client.post('/echo')
    assert response.status_code == 415
