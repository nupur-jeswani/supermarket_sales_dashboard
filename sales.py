import io
from matplotlib.axis import XAxis
from numpy import average
import streamlit as st
import plotly.express as px
import pandas as pd


# setting title of our dashboard
st.set_page_config(
    page_title="Supermarket Sales Dashboard", 
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)


# importing the dataset and caching it to enhance the performance of our web app
@st.cache
def get_data() :
    df = pd.read_excel(
        io = "datasets//supermarket_sales.xlsx",
        engine = "openpyxl",
        sheet_name = "Sales",
        skiprows = 3,
        usecols = "B:R",
    )

    # with the help of EDA we discovered that the time column is of type object when it should be of date time data type
    # converting the time column to the appropriate data type and adding a new column required for our dashboard
    df["Hour"] = pd.to_datetime(df["Time"], format = "%H:%M:%S").dt.hour

    return df


df = get_data()


# Creating the sidebar (adding filters)
st.sidebar.header("Filtering Area -")

city_selection = st.sidebar.multiselect(
    label = "Select City/Cities - ",
    options = df["City"].unique(),
    default = df["City"].unique(),
)

customer_type_selection = st.sidebar.multiselect(
    label = "Select Customer Type(s) - ",
    options = df["Customer_type"].unique(),
    default = df["Customer_type"].unique()
)

gender_selection = st.sidebar.multiselect(
    label = "Select Gender(s) - ",
    options = df["Gender"].unique(),
    default = df["Gender"].unique()
)

# Creating a query
df_selection = df.query(
    "City == @city_selection & Customer_type == @customer_type_selection & Gender == @gender_selection"
)

# main section
st.header(":chart_with_upwards_trend: Supermarket Sales Dashboard")

# KPIs
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 2)
average_stars = ":star:" * int(round(average_rating, 0))
average_sales = round(df_selection["Total"].mean(), 2)

# layout for our KPIs
left, middle, right = st.columns(3)

with left:
    st.markdown("<h4>Total Sales</h4>", True)
    # using f - string to perform string interpolation
    st.markdown(f"<h5>US $ {total_sales :,}</h5>", True)

with middle:
    st.markdown(f"<h4>Average Rating: {average_rating}</h4>", True)
    st.markdown(f"{average_stars}")

with right:
    st.markdown("<h4>Average Sales per Transaction:", True)
    st.markdown(f"<h5>US $ {average_sales}</h5>", True)

st.markdown("---")

# Dashboard Charts

# chart 1

# grouping the products together, summing the grouped values, we want only the "Total" column from our dataset 
# and then sorting the data selected by taking "Total" column as reference
product_line_sales = (df_selection.groupby(by = ["Product line"]).sum()[["Total"]].sort_values(by = "Total"))

product_sales_chart = px.bar(
    product_line_sales,
    x = "Total",
    y = product_line_sales.index,
    orientation = "h", # horizontal bar chart
    title = "<b><i>Sales by Product Line</i></b>",
    template = "plotly_white"
)

# updating layout of our plot
product_sales_chart.update_layout(
    plot_bgcolor = "rgba(0, 0, 0, 0)", # for white background
    xaxis = (dict(showgrid = False)) # removing gridlines
)


# chart 2
hourly_sales = df_selection.groupby(by = ["Hour"]).sum()[["Total"]]

hourly_sales_chart = px.bar(
    hourly_sales,
    x = hourly_sales.index,
    y = "Total",
    title = "<b><i>Sales by Hour</i></b>",
    template = "plotly_white"
)

hourly_sales_chart.update_layout(
    xaxis = dict(tickmode = "linear"), # this will ensure all the tick labels on the xaxis are displayed
    plot_bgcolor = "rgba(0, 0, 0, 0)",
    yaxis = dict(showgrid = False)
)

# displaying charts
left_column, right_column = st.columns(2)

with left_column:
    left_column.plotly_chart(product_sales_chart, use_container_width = True)

with right_column:
    right_column.plotly_chart(hourly_sales_chart, use_container_width = True)



# hiding some default items given by streamlit
hide_styles = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""

st.markdown(hide_styles, unsafe_allow_html = True)