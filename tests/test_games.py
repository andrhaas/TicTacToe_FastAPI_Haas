from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, Game
import pytest

client = TestClient(app)
def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    
def test_read_main_message():
    response = client.get('/')
    assert response.json()['status'] == 'ok'
    
def test_no_auth_create_game():
    response = client.post('/games/')
    assert response.status_code == 401
    
def test_no_auth_list_games():
    response = client.get('/games/')
    assert response.status_code == 401
    
def test_no_auth_get_game():
    response = client.get('/games/1')
    assert response.status_code == 401
    
def test_no_auth_make_move():
    response = client.put('/games/1/move/1?symbol=X')
    assert response.status_code == 401
    
def test_no_auth_delete_game():
    response = client.delete('/games/1')
    assert response.status_code == 401
    
def test_invalid_game_id():
    response = client.get('/games/9999')
    assert response.status_code == 401
    
def test_auth_route_exists():
    response = client.post('/auth/login', data={'username':'fail', 'password':'fail'})
    assert response.status_code == 401
    
def test_register_route_exists():
    response = client.post('/auth/register', data={'username':'', 'password':''})
    assert response.status_code == 422



def test_auth_create_game():
    client.post('/auth/register', data={'username':'testuser1', 'password':'pw1'})
    token_response = client.post('/auth/login', data={'username':'testuser1', 'password':'pw1'})
    token = token_response.json()['access_token']
    
    response = client.post('/games/?player_symbol=X', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert 'id' in response.json()

def test_auth_list_games():
    client.post('/auth/register', data={'username':'testuser2', 'password':'pw2'})
    token_response = client.post('/auth/login', data={'username':'testuser2', 'password':'pw2'})
    token = token_response.json()['access_token']
    
    response = client.get('/games/', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_auth_make_move():
    client.post('/auth/register', data={'username':'testuser3', 'password':'pw3'})
    token_response = client.post('/auth/login', data={'username':'testuser3', 'password':'pw3'})
    token = token_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    game_response = client.post('/games/?player_symbol=X', headers=headers)
    game_id = game_response.json()['id']
    
    response = client.put(f'/games/{game_id}/move/1?symbol=X', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['board'][0] == 'X'
    
    
    
    
    
    
    

def test_user_in_db():
    username = "db_test_user"
    
    client.post('/auth/register', data={'username': username, 'password': 'pw'})
    
    
    db = SessionLocal()
    user_in_db = db.query(User).filter(User.username == username).first()
    db.close()
 
    assert user_in_db is not None
    assert user_in_db.username == username

def test_game_in_db():
    username = "db_test_user2"
    client.post('/auth/register', data={'username': username, 'password': 'pw'})
    token = client.post('/auth/login', data={'username': username, 'password': 'pw'}).json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    

    game_response = client.post('/games/?player_symbol=O', headers=headers)
    game_id = game_response.json()['id']
    

    db = SessionLocal()
    game_in_db = db.query(Game).filter(Game.id == game_id).first()
    db.close()
    

    assert game_in_db is not None
    assert game_in_db.id == game_id


