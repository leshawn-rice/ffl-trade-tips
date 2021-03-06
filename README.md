# *[Fantasy Football Trade Tips v1](https://www.ffl-trade-tips.herokuapp.com)*
## (ffl-trade-tips.herokuapp.com)
### This project uses the **ESPN Fantasy Sports API v3**

### FFL Trade Tips V1 allows the user to create an account, add their ESPN Fantasy Football Public leagues to their account, generate trade suggestions, and simulate trades

### I chose these features because simulating and generating trades is not something ESPN offers, but would be very useful. The scope of this projects is purposefully small-scale in v1 as its primary purpose it to showcase what I've learned thus far in Springboard's Software Engineering Bootcamp.

### User Flows:

### Sign Up
#### Index -> Login/Sign Up -> Sign Up
![Signing Up Demo](app/static/img/signup.gif)
### Add a League
#### Sign Up -> Add A League -> Index
![Add a League Demo](app/static/img/addleague.gif)
### General Flow
#### Index -> (if not signed in) Login -> Leagues -> League X -> Team Y -> Player Z
![General Demo](app/static/img/generalflow.gif)
### View Saved Trades
#### Index -> Profile 
![View Saved Trades Demo](app/static/img/viewsavedtrades.gif)
# This project was built with:
- Python: Flask, Flask-SQLAlchemy, Flask-WTForms, Flask-BCrypt, Flask-Mail
- PostgreSQL
- Bootstrap
- JQuery
- FontAwesome