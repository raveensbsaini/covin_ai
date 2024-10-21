from os import pread
from fastapi import FastAPI, HTTPException
from typing import Dict, Literal
import json
import time

from databases import Database
from pydantic import BaseModel, EmailStr, Json
from contextlib import asynccontextmanager
import functions
from typing import Any

database = Database("sqlite+aiosqlite:///database.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await database.execute(
        query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,email TEXT UNIQUE ,
                password TEXT UNIQUE,amount INTEGER DEFAULT(0)
            );
        """
    )
    await database.execute(
        query="CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT,amount INTEGER NOT NULL,time REAL NOT NULL,user_id INTEGER NOT NULL,method TEXT NOT NULL,split_data TEXT DEFAULT(NULL),FOREIGN KEY (user_id) REFERENCES users(id));"
    )
    await database.execute(
        query="CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT,expense_id INTEGER NOT NULL,borrower_id INTEGER NOT NULL,lender_id INTEGER NOT NULL,amount INTEGER NOT NULL,FOREIGN KEY(expense_id) REFERENCES expenses(id),FOREIGN KEY(borrower_id) REFERENCES users(id),FOREIGN KEY(lender_id) REFERENCES users(id));"
    )
    yield
    await database.disconnect()


class CreateNewUser(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class GetUserDetails(BaseModel):
    name: str
    password: str


class AddExpense(BaseModel):
    name: str
    password: str
    method: Literal["exact"] | Literal["percentage"] | Literal["equal"]
    amount: int
    split_data: Dict[str, int] | None = None


class RetrieveIndividualUserExpense(BaseModel):
    name: str
    password: str


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def create_new_user(body: CreateNewUser):  # This route is used to create new user
    query = "INSERT INTO 'users'('name','phone','email','password') VALUES(:name,:phone,:email,:password)"
    values = {
        "name": body.name,
        "phone": body.phone,
        "email": body.email,
        "password": body.password,
    }
    try:
        async with database.transaction():
            await database.execute(query=query, values=values)
        return "you are now successfully registered"
    except:
        return HTTPException(
            400,
            "either password or name is not suitable. Please try with different password or name.",
        )


@app.post("/user_input")  # This api send back users detail if valid user present
async def get_user_input(body: GetUserDetails):
    query = "SELECT * FROM users WHERE name = :name and password = :password;"
    values = {"name": body.name, "password": body.password}
    async with database.transaction():
        a = await database.fetch_one(query=query, values=values)
    a = dict(a)
    return a


@app.post("/add_expense")  # This route is used to add expense
async def add_expense(body: AddExpense):
    if body.amount == 0:
        return HTTPException(400, "amount cannot be 0")
    current_time = time.time()
    async with database.transaction():
        user_id = await database.fetch_one(
            query="SELECT id FROM users WHERE name=:name and password = :password",
            values={"name": body.name, "password": body.password},
        )
        if user_id:
            user_id = dict(user_id)["id"]
        else:
            return HTTPException(401, "No such users found")
        await database.execute(
            query="INSERT INTO expenses(amount,time,user_id,method,split_data) VALUES(:amount,:time,:user_id,:method,:split_data);",
            values={
                "amount": body.amount,
                "time": current_time,
                "user_id": user_id,
                "method": str(body.method),
                "split_data": str(body.split_data),
            },
        )
        expense_id = await database.fetch_one(
            query="SELECT id FROM expenses WHERE time=:time;",
            values={"time": current_time},
        )
        expense_id = dict(expense_id)["id"]
        if body.method == "percentage" and await functions.check(
            body.split_data, database
        ):
            # add data to loan table
            # add total amount to users table
            split_data = dict(body.split_data)
            for key in split_data:
                new_amount = (body.amount * split_data[key]) / 100
                lender_user_id = user_id
                borrower_user_id = int(key)
                await database.execute(
                    query="INSERT INTO loans(expense_id,borrower_id,lender_id,amount) VALUES(:expense_id,:borrower_id,:lender_id,:amount);",
                    values={
                        "expense_id": expense_id,
                        "borrower_id": borrower_user_id,
                        "lender_id": lender_user_id,
                        "amount": new_amount,
                    },
                )
                borrower_amount = await database.fetch_one(
                    query="SELECT amount FROM users WHERE id=:id",
                    values={"id": borrower_user_id},
                )
                borrower_amount = dict(borrower_amount)["amount"] + new_amount
                print(borrower_amount)
                await database.execute(
                    query="UPDATE users SET amount = :borrower_amount  WHERE id = :borrower_id;",
                    values={
                        "borrower_amount": borrower_amount,
                        "borrower_id": borrower_user_id,
                    },
                )
            return "successfully added expense"

        else:
            return HTTPException(
                400,
                "split_data must be of type {'user_id':integer} and total sum of integer must be 100 when method is percentage.",
            )
        if body.method == "equal":
            pass

            #
        if body.method == "exact":
            pass
            #
    return HTTPException(400, "internal server error")


@app.get("/retrieve_individual_user_expense")
async def retreive_expense(body: RetrieveIndividualUserExpense):
    async with database.transaction():
        amount = await database.fetch_one(
            query="SELECT amount FROM users WHERE name=:name AND password=:password;",
            values={"name": body.name, "password": body.password},
        )
        if not amount:
            return HTTPException(401, "No such users found. Please check credentials")
        else:
            amount = dict(amount)["amount"]
        return amount


@app.get("overall_expense")
def overall_expense():
    pass


@app.get("balance_sheet")
def download_balance_sheet():
    pass
