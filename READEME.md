# Expense Sharing Application

This FastAPI-based application is designed to manage user details, add and split expenses using different methods, and generate a downloadable balance sheet in CSV format.

## Features

- **User Registration**: Users can register by providing their name, phone, email, and password.
- **Add Expense**: Users can add expenses and split them using one of three methods:
  - **Equal Split**: The expense is divided equally among all users.
  - **Exact Split**: The expense is split according to exact amounts specified by the user.
  - **Percentage Split**: The expense is split based on percentages for each user.
- **Retrieve Expenses**: Users can view their individual expenses.
- **Generate Balance Sheet**: A balance sheet of all users' expenses can be downloaded as a CSV file.

## Table of Contents

- [Installation](#installation)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
  - [Create New User](#create-new-user)
  - [Add Expense](#add-expense)
  - [Retrieve User Expenses](#retrieve-user-expenses)
  - [Download Balance Sheet](#download-balance-sheet)
- [Error Handling](#error-handling)
- [License](#license)

## Installation

To set up the Expense Sharing Application locally, follow these steps:

### Prerequisites

Ensure you have the following installed on your machine:

- Python 3.7 or higher
- pip (Python package installer)
- SQLite (comes pre-installed with Python)

### Step-by-Step Installation

1. **Clone the Repository**

   Open your terminal and clone the repository using the following command:

   ```bash
   git clone https://github.com/raveensbsaini/covin_ai.git
   ```
2.  **go to directory**
  direct to covin_ai folder
    ``` bash
    cd covin_ai
3. **setup git and virtual environment**

4. **install dependencies**
    ```
      pip3 install -r requirements.txt
    ```
5.  ** check database.db in your current directory**
    - if not exits
    ```
      touch database.db
    ```
5.  **Run bash script **
    It will run fastapi server on your behalf.
    ```
      start.sh
    ```
6.  ** or simple just run**
    if you don't you bash
    ```
      fastapi run main.py
    ```

  
# Database Schema

The Expense Sharing Application uses a SQLite database to manage user data, expenses, and loans. The following tables are created to facilitate the functionalities of the application:

## Tables

### 1. Users Table

- **Table Name**: `users`
- **Description**: This table stores information about the registered users of the application.

| Column Name | Data Type | Constraints                  | Description                   |
|-------------|-----------|------------------------------|-------------------------------|
| id          | INTEGER   | PRIMARY KEY AUTOINCREMENT    | Unique identifier for users   |
| name        | TEXT      | NOT NULL                     | User's name                   |
| phone       | TEXT      | UNIQUE                       | User's phone number           |
| email       | TEXT      | UNIQUE                       | User's email address          |
| password    | TEXT      | UNIQUE                       | User's password               |
| amount      | INTEGER   | DEFAULT(0)                   | Total amount owed by the user |

### 2. Expenses Table

- **Table Name**: `expenses`
- **Description**: This table keeps track of expenses added by users.

| Column Name | Data Type | Constraints                  | Description                   |
|-------------|-----------|------------------------------|-------------------------------|
| id          | INTEGER   | PRIMARY KEY AUTOINCREMENT    | Unique identifier for expenses |
| amount      | INTEGER   | NOT NULL                     | Amount of the expense         |
| time        | REAL      | NOT NULL                     | Timestamp of the expense      |
| user_id     | INTEGER   | NOT NULL, FOREIGN KEY        | ID of the user who added the expense |
| method      | TEXT      | NOT NULL                     | Method used to split the expense (e.g., equal, exact, percentage) |
| split_data  | TEXT      | DEFAULT(NULL)                | JSON string of split data (e.g., user IDs and corresponding amounts) |

### 3. Loans Table

- **Table Name**: `loans`
- **Description**: This table tracks the loans between users based on shared expenses.

| Column Name   | Data Type | Constraints                      | Description                   |
|---------------|-----------|----------------------------------|-------------------------------|
| id            | INTEGER   | PRIMARY KEY AUTOINCREMENT        | Unique identifier for loans    |
| expense_id    | INTEGER   | NOT NULL, FOREIGN KEY            | ID of the related expense      |
| borrower_id   | INTEGER   | NOT NULL, FOREIGN KEY            | ID of the user borrowing the amount |
| lender_id     | INTEGER   | NOT NULL, FOREIGN KEY            | ID of the user lending the amount |
| amount        | INTEGER   | NOT NULL                         | Amount borrowed or lent        |

## Relationships

- **Users to Expenses**: One user can have multiple expenses, but each expense is linked to one user (`user_id`).
- **Expenses to Loans**: Each expense can result in multiple loans, representing the borrowing and lending relationships among users (`expense_id`).

## Initialization

The database tables are automatically created if they do not exist when the FastAPI application starts up.
## API Endpoints

The Expense Sharing Application provides the following API endpoints for managing users, expenses, and generating reports.

### 1. Create New User

- **Method**: `POST`
- **URL**: `/`
- **Headers**:
  - `name`: User's name (string)
  - `password`: User's password (string)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "phone": "1234567890"
  }
- **Responses**:
  - **200 OK**: `"you are now successfully registered"`
  - **400 Bad Request**: `"either password or name is not suitable"`

### 2. Add Expense

- **Method**: `POST`
- **URL**: `/add_expense`
- **Headers**:
  - `name`: User's name (string)
  - `password`: User's password (string)
- **Request Body**:
  ```json
  {
    "method": "equal",  // Options: "exact", "percentage", "equal"
    "amount": 200,
    "split_data": {
      "user_id_1": 50,
      "user_id_2": 50
    }
  }
### 3. Retrieve Individual User Expenses

- **Method**: `GET`
- **URL**: `/retrieve_individual_user_expense`
- **Headers**:
  - `name`: User's name (string)
  - `password`: User's password (string)
- **Responses**:
  - **200 OK**: Returns the user's total amount
  - **401 Unauthorized**: `"No such users found. Please check credentials"`

---

### 4. Overall Expense

- **Method**: `GET`
- **URL**: `/overall_expense`
- **Headers**:
  - `name`: User's name (string)
  - `password`: User's password (string)
- **Responses**:
  - **200 OK**: Returns the total amount of expenses
  - **401 Unauthorized**: `"No such users found. Please check credentials"`


### 5. Download Balance Sheet

- **Method**: `GET`
- **URL**: `/balance_sheet`
- **Headers**:
  - `name`: User's name (string)
  - `password`: User's password (string)
- **Responses**:
  - **200 OK**: Downloads the balance sheet as a CSV file
  - **401 Unauthorized**: `"No such users found. Please check credentials"`
- ## To download use balanche sheet use `wget`
## Error Handling

The Expense Sharing Application implements error handling for various scenarios. Below are common error responses and their meanings:

- **400 Bad Request**
  - **Description**: This error occurs when the request sent by the client is invalid or cannot be processed.
  - **Example**: 
    - `"amount cannot be 0"`: When the amount provided in the request body is zero.
    - `"either password or name is not suitable"`: When the user registration fails due to invalid credentials.

- **401 Unauthorized**
  - **Description**: This error occurs when the provided credentials are incorrect or when a user tries to access a resource without being authenticated.
  - **Example**: 
    - `"No such users found. Please check credentials"`: When the user credentials provided do not match any existing users in the database.

- **422 Unprocessable Entity**
  - **Description**: This error occurs when the server understands the content type of the request entity but was unable to process the contained instructions.
  - **Example**: 
    - `"JSON decode error"`: When there is an issue with the format of the JSON data sent in the request body.

Ensure that the client handles these error responses gracefully to improve user experience and provide feedback on what went wrong.
## License

This project is not licensed . 

### Summary of the License:
- You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.
- You must include the original copyright notice and permission notice in all copies or substantial portions of the software.
- The software is provided "as is", without warranty of any kind, express or implied. The authors are not liable for any claims, damages, or other liabilities.

For more details, contact me on raveensbsaini@gmail.com.
