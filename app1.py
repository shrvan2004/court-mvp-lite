import streamlit as st
import pandas as pd
import os
import re
import json
from io import BytesIO
import google.generativeai as genai


# -----------------------------
# GEMINI CONFIG
# -----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-2.5-flash")


# -----------------------------
# DATA FILE
# -----------------------------
DATA_FILE = "cause_list.json"


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_cases():

    df = pd.read_json(DATA_FILE)

    if "id" in df.columns:
        df["row_number"] = df["id"]
    else:
        df["row_number"] = range(1, len(df)+1)

    df = df.loc[:, ~df.columns.duplicated()]

    return df


# -----------------------------
# TEXT NORMALIZATION
# -----------------------------
def normalize_text(text):

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------
# AI QUERY INTERPRETER
# -----------------------------
def interpret_query(question):

    prompt = f"""
Convert the user legal question into dataframe filters.

Columns available:

case_no
parties
advocate_or_stage
complex
court
scrape_date

Return ONLY JSON.

Example:

{{
"case_no":"",
"parties":"",
"advocate_or_stage":"",
"complex":"",
"court":"",
"scrape_date":""
}}

User question:
{question}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    try:
        filters = json.loads(text)
    except:
        filters = {}

    return filters


# -----------------------------
# EXPORT FUNCTIONS
# -----------------------------
def to_excel(df):

    output = BytesIO()
    df.to_excel(output, index=False)

    return output.getvalue()


def to_csv(df):

    return df.to_csv(index=False)


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Bengaluru Court Cause List", layout="wide")

st.title("Bengaluru Court Cause List Dashboard")


df_original = load_cases()
df = df_original.copy()


# -----------------------------
# DATABASE SUMMARY
# -----------------------------
st.subheader("Database Summary")

col1,col2,col3 = st.columns(3)

with col1:
    st.metric("Total Cases", len(df_original))

with col2:
    st.metric("Total Complexes", df_original["complex"].nunique())

with col3:
    st.metric("Total Courts", df_original["court"].nunique())


# -----------------------------
# DATE FILTER
# -----------------------------
dates = ["All"] + sorted(df_original["scrape_date"].dropna().unique())

date_filter = st.selectbox("Select Date", dates)

if date_filter != "All":
    df = df[df["scrape_date"] == date_filter]


# -----------------------------
# ROBUST SEARCH
# -----------------------------
search = st.text_input("Search case / party / advocate")

if search:

    search_clean = normalize_text(search)

    mask = (
        df["case_no"].astype(str).apply(normalize_text).str.contains(rf"\b{re.escape(search_clean)}\b", regex=True, na=False)
        |
        df["parties"].astype(str).apply(normalize_text).str.contains(rf"\b{re.escape(search_clean)}\b", regex=True, na=False)
        |
        df["advocate_or_stage"].astype(str).apply(normalize_text).str.contains(rf"\b{re.escape(search_clean)}\b", regex=True, na=False)
    )

    df = df[mask]


# -----------------------------
# COURT FILTER
# -----------------------------
courts = ["All"] + sorted(df_original["court"].dropna().unique())

court_filter = st.selectbox("Select Court", courts)

if court_filter != "All":
    df = df[df["court"] == court_filter]


# -----------------------------
# RESULTS TABLE
# -----------------------------
st.subheader("Results")

st.dataframe(df, use_container_width=True)


# -----------------------------
# DOWNLOAD BUTTONS
# -----------------------------
col1,col2 = st.columns(2)

with col1:
    st.download_button("Download CSV", to_csv(df), "cases.csv", "text/csv")

with col2:
    st.download_button(
        "Download Excel",
        to_excel(df),
        "cases.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# -----------------------------
# AI LEGAL ASSISTANT
# -----------------------------
st.subheader("AI Legal Assistant")

question = st.chat_input("Ask about the database")

if question:

    st.chat_message("user").write(question)

    filters = interpret_query(question)

    results = df_original.copy()

    for column,value in filters.items():

        if value:

            search_value = normalize_text(value)

            results = results[
                results[column]
                .astype(str)
                .apply(normalize_text)
                .str.contains(rf"\b{re.escape(search_value)}\b", regex=True, na=False)
            ]

    if "how many" in question.lower():

        answer = f"{len(results)} cases found"

    elif "row" in question.lower():

        answer = f"Row numbers: {results['row_number'].tolist()}"

    else:

        answer = f"{len(results)} matching cases found"

    st.chat_message("assistant").write(answer)

    if not results.empty:
        st.dataframe(results)


# -----------------------------
# AI CASE EXPLANATION
# -----------------------------
st.subheader("AI Case Explanation")

if len(df) > 0:

    case_row = st.number_input(
        "Enter row_number to explain the case",
        min_value=int(df["row_number"].min()),
        max_value=int(df["row_number"].max()),
        step=1
    )

    if st.button("Explain This Case"):

        case_data = df[df["row_number"] == case_row]

        if not case_data.empty:

            case_dict = case_data.iloc[0].to_dict()

            prompt = f"""
Explain this court case in simple language.

Case Data:
{case_dict}

Explain:
1. What the case is about
2. Who the parties are
3. What the next hearing date means
4. Possible legal context
"""

            response = model.generate_content(prompt)

            st.write(response.text)

        else:
            st.warning("Case not found.")
