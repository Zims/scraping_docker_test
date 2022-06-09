# save this as app.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)

# Database connection
conn = sqlite3.connect('ss_all_with_class.sqlite3', check_same_thread=False)
c = conn.cursor()

# queries
c.execute("SELECT * FROM ss_all_new ORDER BY id DESC")
# get 20 newest records
c.execute("SELECT * FROM ss_all_new ORDER BY id DESC LIMIT 50")

all_appartments = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]

# Endpoints #



@app.get("/today")
async def today():
    todays_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM ss_all_new WHERE date_added = ? ORDER BY added_to_db DESC", (todays_date,))
    # put them in a list
    todays_ads = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
    todays_ads = jsonify(todays_ads)
    # return todays_ads as json format
    return todays_ads
    
    

# @app.get("/places")
# async def places(request: Request):
#     # return all places in database
#     # only unique values for rajons
#     c.execute("SELECT DISTINCT district FROM ss_all_new")
#     # put them in a list
#     district = [row[0] for row in c.fetchall()]
#     return district


# @app.get("/{district}/{end_date}")
# async def district(request: Request, district: str, end_date: str):
#     district = district.replace('_', ' ')
#     end_date = end_date.replace('_', '-')
#     c.execute("SELECT * FROM ss_all_new WHERE district = ? AND date_added >= ? ORDER BY added_to_db DESC", (district, end_date))
#     # put them in a list
#     district_ads = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#     return district_ads


# @app.get("/{place:str}")
# def get_place(place):
#     if place == "top100":
#         # select only top 100 newest records
#         c.execute("SELECT * FROM ss_all_new ORDER BY added_to_db DESC LIMIT 100")
#         top100 = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#         return top100
#     # elif place == "all":
#     #         # select entire_db newest records
#     #     c.execute("SELECT * FROM ss_all_new ORDER BY date_added DESC")
#     #     entire_db_resp = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#     #     return entire_db_resp
#     else:
#         c.execute("SELECT * FROM ss_all_new WHERE district = ? ORDER BY added_to_db DESC LIMIT 300", (place,))
#         place_appartments = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#         return place_appartments
