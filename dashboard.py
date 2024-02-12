import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import warnings
import calendar
import plotly.figure_factory as ff
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore Dashboard",page_icon="bar_chart", layout="wide")

# to give it a title with the bar chart emoji
st.title("Superstore Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}<style/>',unsafe_allow_html=True)

# To read excel file
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel("Superstore.xls")
    return df
       
df = get_data_from_excel()



# To add Date filters
col1,col2=st.columns((2))
df["Order Date"]=pd.to_datetime(df["Order Date"])

# Getting the min and max date
startdate=pd.to_datetime(df["Order Date"]).min()
enddate=pd.to_datetime(df["Order Date"]).max()

with col1:
    date1=pd.to_datetime(st.date_input("Start Date", startdate))

with col2:
    date2=pd.to_datetime(st.date_input("End Date", enddate))

df=df[(df["Order Date"]>=date1) &(df["Order Date"]<= date2)].copy()

# To create the filters sidebar
# Create for Region
st.sidebar.header("Choose your filter")
region=st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2=df.copy()
else:
    df2=df[df["Region"].isin(region)]

# Create for State
state=st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2["State"].isin(state)]

# Create for city
city=st.sidebar.multiselect("Pick your City",df3["City"].unique())
if not city:
    df4=df3.copy()
else:
    df4=df3[df3["City"].isin(city)]

# Filter the data based on Region, State and City
    
if not region and not state and not city:
    filtered_df=df
elif not state and not city:
    filtered_df=df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df=df[df["State"].isin(state)]
elif state and city:
    filtered_df=df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df=df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df=df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df= df3[df3["City"].isin(city)]
else:
    filtered_df=df3[df3["Region"].isin(region)& df3["State"].isin(state)& df3["City"].isin(city)]

category_df=filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

# To add KPIs
total_sales = int(filtered_df["Sales"].sum())
total_profit = int(filtered_df["Profit"].sum())
total_quantity = int(filtered_df["Quantity"].sum())


top_left_column,top_middle_column, top_right_column = st.columns(3)
with top_left_column:
    st.subheader("Total Sales")
    st.subheader(f"${total_sales:,}")
with top_middle_column:
    st.subheader("Total Order Quantity")
    st.subheader(f"{total_quantity:,}")
with top_right_column:
    st.subheader("Total Profit")
    st.subheader(f"${total_profit:,}")

st.markdown("""---""")

# To create the charts
col1, col2 = st.columns((2))
with col1:
    st.subheader("Sales by Category")
    fig=px.bar(category_df,x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
               template="seaborn")
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=8)
    #fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(
    xaxis=dict(title=None),
    yaxis=dict(title=None, showticklabels=False),
    showlegend=False)
    st.plotly_chart(fig,use_container_width=True, height=200)

with col2:
    st.subheader("Sales by Region")
    fig=px.pie(filtered_df,values="Sales", names="Region", hole=0.7) 
    fig.update_traces(text= filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


coll1, coll2 = st.columns((2))       
# Top 10 customers by sales
with coll1:
        top_customers = filtered_df.groupby("Customer Name").sum().nlargest(10, "Sales").reset_index()
        top_customers = top_customers.sort_values(by="Sales", ascending=True) 
        st.subheader("Top 10 Customers by Sales")
        fig = px.bar(top_customers, x="Sales", y="Customer Name", text=['${:,.2f}'.format(x) for x in top_customers["Sales"]],
                    orientation="h", template="seaborn")
        fig.update_traces(textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

# Top 10 subcategories by sales
with coll2:
        top_subcategories = filtered_df.groupby("Sub-Category").sum().nlargest(10, "Sales").reset_index()
        top_subcategories = top_subcategories.sort_values(by="Sales", ascending=True) 
        st.subheader("Top 10 Subcategories by Sales")
        fig = px.bar(top_subcategories, x="Sales", y="Sub-Category", text=['${:,.2f}'.format(x) for x in top_subcategories["Sales"]],
                    orientation="h", template="seaborn")
        fig.update_traces(textposition='inside')
        fig.update_layout(yaxis=dict(title='Sub-Category'))
        st.plotly_chart(fig, use_container_width=True)
        
 # To Create Time Series Chart
filtered_df["month_year"] =filtered_df["Order Date"].dt.to_period("M")

st.subheader("Time Series Analysis") 

linechart=pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2=px.line(linechart, x="month_year", y="Sales", labels={"Sales: Amount"}, height=500, width=1000,template="gridon")
st.plotly_chart(fig2, use_container_width=True)


# To create a segment for the charts
segment_df=filtered_df.groupby(by=["Segment"], as_index=False)["Sales"].sum()
shipmode_df=filtered_df.groupby(by=["Ship Mode"], as_index=False)["Sales"].sum()

chart1,chart2=st.columns((2))
with chart1:
    st.subheader("Sales by Segment")
    fig=px.bar(segment_df,y="Sales", x="Segment",text=['${:,.2f}'.format(x) for x in segment_df["Sales"]], template="seaborn")
    #fig.update_traces(text=filtered_df["Segment"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    

with chart2:
    st.subheader("Sales by Ship Mode")
    fig=px.bar(shipmode_df,y="Sales", x="Ship Mode",text=['${:,.2f}'.format(x) for x in shipmode_df["Sales"]], template="seaborn")
   # fig.update_traces(text=filtered_df["Category"], textposition="outside")
    
    st.plotly_chart(fig, use_container_width=True)


# The month by sales HeatMap

st.subheader("HeatMap showing Monthly Sales by Subcategory ")
filtered_df["month"] = filtered_df["Order Date"].dt.month
filtered_df["month"] = filtered_df["month"].apply(lambda x: calendar.month_name[x])


# Define the order of months
month_order = [calendar.month_name[i] for i in range(1, 13)]

sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns='month')
sub_category_Year = sub_category_Year.reindex(columns=month_order)  # Reindex columns to ensure chronological order
#f_sub_category_Year = sub_category_Year.applymap(lambda x: '${:,.2f}'.format(x))
st.write(sub_category_Year.style.background_gradient(cmap="Blues"))


# To create scatter plot
st.subheader("Relationship between Sales and Profit")
data1=px.scatter(filtered_df, x="Sales",y="Profit", size="Quantity", color="Category")
data1['layout'].update(xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)