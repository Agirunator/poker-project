
# Project Title

A brief description of what this project does and who it's for


## Contents

Generate this at the end


## Demo

Insert gif or link to demo


## Run Locally

Clone the project

```bash
  git clone https://github.com/Agirunator/poker-project
```

Go to the project directory

```bash
  cd poker-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the app

```bash
  python app.py
```


## Features

- Light/dark mode toggle
- Live previews
- Fullscreen mode
- Cross platform

## Database Structure

This section outlines the SQL tables and their relationships.

### 1. **Table: `users`**
   - **Description**: Stores information about the users.
   - **Primary Key**: 
     - `ID` (INTEGER): Unique identifier for each user, automatically incremented.
   - **Columns**:
     - `ID` (INTEGER): Primary key, auto-incremented.
     - `username` (TEXT): A unique identifier for the user. It must be alphanumeric, enforced by the `CHECK` constraint.
     - `password` (TEXT): The user's password (stored securely).
     - `first_name` (TEXT): The user's first name.
     - `last_name` (TEXT): The user's last name.
     - `created_at` (TIMESTAMP): The timestamp when the user was created. Defaults to the current time.
   - **Constraints**: 
     - `username` must be unique.
     - `username` must only contain alphanumeric characters, enforced by the `CHECK` constraint (`username GLOB '[A-Za-z0-9]*'`).

### 2. **Table: `balance`**
   - **Description**: Stores the balance for each user.
   - **Primary Key**: 
     - `USER_ID` (INTEGER): This is also the foreign key referencing the `ID` in the `users` table.
   - **Columns**:
     - `USER_ID` (INTEGER): Foreign key that references `users(ID)`. This creates a one-to-one relationship between the `users` and `balance` tables.
     - `balance` (REAL): The user's balance, defaulting to `0.0`.
   - **Foreign Key**:
     - `USER_ID` references the `ID` column in the `users` table.

### 3. **Table: `transactions`**
   - **Description**: Stores transaction details for each user.
   - **Primary Key**: 
     - `ID` (INTEGER): Unique identifier for each transaction.
   - **Columns**:
     - `ID` (INTEGER): Primary key, auto-incremented.
     - `USER_ID` (INTEGER): Foreign key that references the `users(ID)` table, linking each transaction to a user.
     - `amount` (REAL): The amount of the transaction (could be positive or negative depending on the transaction type).
     - `transaction_time` (TIMESTAMP): Timestamp for when the transaction occurred. Defaults to the current time.
   - **Foreign Key**: 
     - `USER_ID` references the `ID` column in the `users` table.


## Usage/Examples

```javascript
import Component from 'my-project'

function App() {
  return <Component />
}
```


## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Appendix

Any additional information goes here


## Acknowledgements

- [Card Designs](https://opengameart.org/content/playing-cards-0)

