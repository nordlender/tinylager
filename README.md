# tinylager
A tiny web app for small scale gear rentals. Made for my climbing club. Vibe coded like hell and probably a stinking pile of doohickey but I'm not spending my precious time doing web.

It is a work in progress.

## To do
### Order overview
- Add visual feedback/warning if rental is beyond 2 weeks
- Add "extend rental" button

### General
- Add header with buttons on all non-user pages
- Add inventory page
- Add "add to inventory" interface for non-technical users (might be tricky) to add new products
- Add authentication page that uses external API with OAuth to make sure that only members can access the app
- Get name, email and phone number from external API

## Features
- A small "shop" where users can add items to their shopping cart
- A checkout where the shopping cart can be changed, with a field for name and phone number
- A return interface where an order can be returned or partially returned
- An overview of rentals
- A simple database with redundant tables in case this sucks

## Dependencies
Flask.
```uv add requirements.txt```
or
```pip install requirements.txt```
