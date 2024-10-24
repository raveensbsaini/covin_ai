from fastapi import testclient
from fastapi.testclient import TestClient
from main import app
# method test
# data validation test
def test_create_user(): # check create_user api
    with TestClient(app) as client:
        response = client.get("/")
        assert  response.status_code == 405
        response  = client.post("/",headers={"name":"1","password":"2"},json={"email":"3@gmail.com","phone":"4"})
        assert response.status_code == 200
        response  = client.post("/",headers={"name":"1","password":"2"},json={"email":"3@gmail.com","phone":"4"})      
        assert response.status_code == 400
def test_get_user_details(): # check get_user_details api
    with TestClient(app) as client:

        response = client.post("/user_details")
        assert response.status_code == 405

        response  = client.post("/",headers={"name":"5","password":"6"},json={"email":"7@gmail.com","phone":"8"})
        response  = client.get("/user_details",headers={"name":"5","password":"6"})      
        assert response.status_code == 200

        response  = client.get("/user_details",headers={"name":"not_exists","password":"not_exits"})      
        assert response.status_code == 401
def test_add_expense():
    with TestClient(app) as client:
        #1.
        response  = client.get("/add_expense")
        assert response.status_code == 405
        #2.
        response  = client.post("/",headers={"name":"9","password":"10"},json={"email":"11@gmail.com","phone":"12"})
        response  = client.post("/add_expense",headers={"name":"9","password":"10"},json={"method":"equal","amount":100 })      
        assert response.status_code == 200
        #3.
        response  = client.post("/add_expense",headers={"name":"not_exists","password":"not_exists"},json={"method":"exact","amount":100 })      
        assert response.status_code == 401
        #4.
        response  = client.post("/add_expense",headers={"name":"9","password":"10"},json={"method":"not_exists","amount":100 })      
        assert response.status_code == 422
        #5.
        response  = client.post("/add_expense",headers={"name":"9","password":"10"},json={"method":"percentage","amount": 100 })      
        assert response.status_code == 400
        #6.
        response  = client.post("/add_expense",headers={"name":"9","password":"10"},json={"method":"percentage","amount":100,"split_data":{"9":20} })      
        assert response.status_code == 400
