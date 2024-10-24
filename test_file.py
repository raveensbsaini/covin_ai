from fastapi import testclient
from fastapi.testclient import TestClient
from main import app
import random

def test_file():
    with TestClient(app) as client:
        response = client.get("/")
        assert  response.status_code == 405
        print(response.text)
        response  = client.post("/",headers={"name":"ravindra","password":f'{random.randint}'+"saini"},json={"email":"ravindrasaini@gmail.com","phone":"9234"})
        print(response.text)
        print(response.status_code)
        assert response.status_code == 200
        response  = client.post("/",headers={"name":"ravindra","password":f'{random.randint}'+"saini"},json={"email":"ravindrasaini@gmail.com","phone":"9234"})
        print(response.text)
        print(response.status_code)
        assert response.status_code == 400
        response.post(/user_details)
