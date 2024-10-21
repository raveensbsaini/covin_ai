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

1. Clone the repository:
   ```bash
   git clone >

