from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.datastructures import QueryParams
from fastapi.responses import StreamingResponse
from typing import Dict, Literal, Annotated
import json
import time
import io
import csv
from databases import Database
from pydantic import BaseModel, EmailStr, Json
import sqlite3
from contextlib import asynccontextmanager
import functions
from typing import Any
import os

if os.environ.get("TESTING_DB") == "1":
    database = Database("sqlite+aiosqlite:///test.db")
else:
    database = Database("sqlite+aiosqlite:///database.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await database.execute(
        query="""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT UNIQUE,
                amount INTEGER DEFAULT(0)
            );
        """
    )
    await database.execute(
        query="""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                time REAL NOT NULL,
                user_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                split_data TEXT DEFAULT(NULL),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """
    )
    await database.execute(
        query="""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_id INTEGER NOT NULL,
                borrower_id INTEGER NOT NULL,
                lender_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                FOREIGN KEY(expense_id) REFERENCES expenses(id),
                FOREIGN KEY(borrower_id) REFERENCES users(id),
                FOREIGN KEY(lender_id) REFERENCES users(id)
            );
        """
    )
    yield
    await database.disconnect()


class CreateNewUser(BaseModel):
    email: EmailStr
    phone: str


class AddExpense(BaseModel):
    method: Literal["exact"] | Literal["percentage"] | Literal["equal"]
    amount: int
    split_data: Dict[str, int] | None = None


class RetrieveIndividualUserExpense(BaseModel):
    name: str
    password: str


class OverallExpense(BaseModel):
    name: str
    password: str


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def create_new_user(
    body: CreateNewUser,
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):  # This route is used to create new user
    query = """INSERT INTO 'users'('name','phone','email','password')VALUES(:name,:phone,:email,:password)"""
    values = {
        "name": name,
        "phone": body.phone,
        "email": body.email,
        "password": password,
    }
    try:       
        await database.execute(query=query, values=values)
        return "you are now successfully registered"
    except sqlite3.IntegrityError as e:
         raise HTTPException(
            400,
            f"either password or name is not suitable. Please try with different password or name,{str(e)}.",
        )
    except Exception as e:
        raise  HTTPException(500,str(e))
                    

@app.get("/user_details")  # This api send back users detail if valid user present
async def get_user_details(
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):
    query = "SELECT * FROM users WHERE name = :name and password = :password;"
    values = {"name": name, "password": password}
    a = await database.fetch_one(query=query, values=values)
    if not a:
        raise HTTPException(401,"Invalid username or password")
    a = dict(a)
    return a


@app.post("/add_expense")  # This route is used to add expense
async def add_expense(
    body: AddExpense,
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):
    if body.amount == 0:
        raise HTTPException(400, "amount cannot be 0")
    current_time = time.time()
    async with database.transaction():
        user_id = await database.fetch_one(
            query="SELECT id FROM users WHERE name=:name and password = :password",
            values={"name": name, "password": password},
        )
        if user_id:
            user_id = dict(user_id)["id"]
        else:
            raise HTTPException(401, "Invalid username or password")
        all_users = await database.fetch_all("select id from users;")
        all_users = {dict(i)["id"] for i in all_users}
        if (
            await functions.data_validation(body.amount, body.method, body.split_data, all_users)
            == False
        ):
            raise HTTPException(
                400,
                """split_data must be of type {'user_id':integer} 
                  ,All users_id must be a valid user_id
                  ,If method is percentage then total sum must be 100 eg: split_data = {"2":30,"4":"30","3""40"} 
                  ,If method = exact then total sum must be equal to amount
                  ,If method is exact There must  no split_data in body of requemust .
                  Check the following something is mismatched.
                  ."""
            )

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
        if body.method == "percentage":
            assert split_data is  not None
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
                await database.execute(
                    query="UPDATE users SET amount = :borrower_amount  WHERE id = :borrower_id;",
                    values={
                        "borrower_amount": borrower_amount,
                        "borrower_id": borrower_user_id,
                    },
                )

        if body.method == "equal":
            async with database.transaction():
                users_list = await database.fetch_all(query="SELECT id FROM users")
                users_list = [dict(i)["id"] for i in users_list]
                new_amount = body.amount / len(users_list)
                for i in users_list:
                    await database.execute(
                        query="INSERT INTO loans(expense_id,borrower_id,lender_id,amount) VALUES(:expense_id,:borrower_id,:lender_id,:amount);",
                        values={
                            "expense_id": expense_id,
                            "borrower_id": i,
                            "lender_id": user_id,
                            "amount": new_amount,
                        },
                    )
                    previous_amount = await database.fetch_one(
                        query="SELECT amount FROM users WHERE id=:id", values={"id": i}
                    )
                    previous_amount = dict(previous_amount)["amount"] + new_amount
                    await database.execute(
                        query="UPDATE users SET amount = :amount  WHERE id = :id;",
                        values={"amount": previous_amount, "id": i},
                    )

        if body.method == "exact":
            assert body.split_data is not None
            split_data = dict(body.split_data)
            for key in split_data:
                new_amount = split_data[key]
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
                await database.execute(
                    query="UPDATE users SET amount = :borrower_amount  WHERE id = :borrower_id;",
                    values={
                        "borrower_amount": borrower_amount,
                        "borrower_id": borrower_user_id,
                    },
                )

    raise HTTPException(200, "successfully added expense")


@app.get("/retrieve_individual_user_expense")
async def retreive_expense(
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):
    async with database.transaction():
        amount = await database.fetch_one(
            query="SELECT amount FROM users WHERE name=:name AND password=:password;",
            values={"name": name, "password": password},
        )
        if not amount:
            raise HTTPException(401, "Invalid username or password")
        else:
            amount = dict(amount)["amount"]
        return amount


@app.get("/overall_expense")
async def overall_expense(
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):
    async with database.transaction():
        user_id = await database.fetch_one(
            query="SELECT id FROM users WHERE name=:name AND password=:password;",
            values={"name": name, "password": password},
        )
        if not user_id:
            raise HTTPException(401, "Invalid username or password")
        else:
            user_id = dict(user_id)["id"]
        amount = await database.fetch_one(
            query="SELECT SUM(amount) AS total_amount FROM expenses as answer;"
        )
        if not amount:
            raise HTTPException(401, "Invalid username or password")
        else:
            amount = dict(amount)["total_amount"]
        return amount


@app.get("/balance_sheet")
async def download_balance_sheet(
    name: Annotated[str | None, Header()] = None,
    password: Annotated[str | None, Header()] = None,
):
    async with database.transaction():
        user_id = await database.fetch_one(
            query="SELECT id FROM users WHERE name=:name AND password=:password;",
            values={"name": name, "password": password},
        )
        if not user_id:
            raise HTTPException(401,"Invalid username or password")
        all_users_data = await database.fetch_all(query="select * from users;")
        all_users_data = [dict(i) for i in all_users_data]
    output = io.StringIO()
    writer = csv.writer(output)
    overall_expenses = 0

    writer.writerow(["user_name", "user_gmail", "amount", "overall_expenses"])
    for data in all_users_data:
        user_name = data["name"]
        user_gmail = data["email"]
        amount = await retreive_expense(user_name, data["password"])
        overall_expenses = await overall_expense(user_name, data["password"])
        writer.writerow(
            [f"{user_name}", f"{user_gmail}", f"{amount}", f"{overall_expenses}"]
        )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=balanceSheet.csv"},
    )
