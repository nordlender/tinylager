# tinylager
A tiny web app for small scale gear rentals. Made for my climbing club. Vibe coded like hell and probably a stinking pile of doohickey but I'm not spending my precious time doing web.

It is a work in progress.

## Features
- A small "shop" where users can add items to their shopping cart
- A checkout where the shopping cart can be changed, with a field for name and phone number
- A return interface where an order can be returned or partially returned
- An overview of rentals
- A simple database with redundant tables in case this sucks
- An inventory page where fields can be edited

## Dependencies
Flask.
```uv add requirements.txt```
or
```pip install requirements.txt```

## Installation/setup
### Dependencies
Make sure SQLite 3 is installed on your system, for example
```bash
sudo apt install sqlite3
```

You can then install dependencies
```uv add requirements.txt```
or
```pip install requirements.txt```

Then, the database has to be added
```bash
touch orders.db && sqlite3 orders.db '.read schema.sql'
```

You should now have a database `orders.db` with the schema from `schema.sql`. You can verify this by doing
```bash
sqlite3 orders.db .schema
```

## Usage
The app is spun up by running `main.py`. You can do this 

## To do
### Order overview
- Add visual feedback/warning if rental is beyond 2 weeks
- Add "extend rental" button

### General
- Add header with buttons on all non-user pages
- Add "add to inventory" interface for non-technical users (might be tricky) to add new products
- Add authentication page that uses external API with OAuth to make sure that only members can access the app
- Get name, email and phone number from external API

### Rentals
- Wait list
- Max rentable (not max stock)
