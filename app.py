import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
import os, datetime

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1X3qV0HIWKIFupqZ6N5dLb9_7giwXp5EjyGJXYEYS_bg"
SHEET_NAME = "Test-IIITB-Meals"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
SECRET_FILE = os.path.join(os.getcwd(), "gcp_secret.json")

@st.experimental_singleton()
def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_file(
        SECRET_FILE,
        scopes=[SCOPE],
    )

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(
            credentials, http=httplib2.Http()
        )
        return HttpRequest(new_http, *args, **kwargs)

    authorized_http = google_auth_httplib2.AuthorizedHttp(
        credentials, http=httplib2.Http()
    )
    service = build(
        "sheets",
        "v4",
        requestBuilder=build_request,
        http=authorized_http,
    )
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


st.set_page_config(page_title="IIITB Mess Menu", page_icon="🥘", layout="centered")
st.title("🥘 IIITB Mess Menu")

gsheet_connector = connect_to_gsheet()

@st.experimental_memo()
def get_data(sheet_name, sheet_range) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!{sheet_range}",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df

main = get_data("Main", "A:B")
breakfast = get_data("Breakfast", "A:H")
lunch = get_data("Lunch", "A:H")
snacks = get_data("Snacks", "A:H")
dinner = get_data("Dinner", "A:H")

if st.sidebar.button("Hot refresh"):
    get_data.clear()
    main = get_data("Main", "A:B")
    breakfast = get_data("Breakfast", "A:H")
    lunch = get_data("Lunch", "A:H")
    snacks = get_data("Snacks", "A:H")
    dinner = get_data("Dinner", "A:H")

start_date = main["start_date"][1]
end_date = main["end_date"][1]
last_updated_at = datetime.datetime.now()
_start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
_end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y')

st.sidebar.write("Current menu is for the date range")
st.sidebar.write(f"{_start_date.strftime('%d-%b-%Y')} to {_end_date.strftime('%d-%b-%Y')}")
st.sidebar.write(f"Last updated at : {last_updated_at}")
st.sidebar.write(f"Open original [Menu Sheet]({GSHEET_URL})")

cols = st.columns((1, 1))
day = cols[0].date_input("Which day menu?", min_value = datetime.date(_start_date.year, _start_date.month, _start_date.day), max_value = datetime.date(_end_date.year, _end_date.month, _end_date.day)).strftime("%A")
category = cols[1].selectbox(
    "Category:", ["Breakfast", "Lunch", "Snacks", "Dinner"], index=0
)
    
if(day and category):
    df = pd.DataFrame()
    if category == "Breakfast":
        df['Type'] = breakfast['Type']
        df[day] = breakfast[day]
    elif category == "Lunch":
        df['Type'] = lunch['Type']
        df[day] = lunch[day]
    elif category == "Snacks":
        df['Type'] = snacks['Type']
        df[day] = snacks[day]
    else:
        df['Type'] = dinner['Type']
        df[day] = dinner[day]
    st.dataframe(df)

expander_breakfast = st.expander("See whole breakfast menu")
with expander_breakfast:
    st.dataframe(breakfast)

expander_lunch = st.expander("See whole lunch menu")
with expander_lunch:
    st.dataframe(lunch)

expander_snacks = st.expander("See whole snacks menu")
with expander_snacks:
    st.dataframe(snacks)

expander_dinner = st.expander("See whole dinner menu")
with expander_dinner:
    st.dataframe(dinner)