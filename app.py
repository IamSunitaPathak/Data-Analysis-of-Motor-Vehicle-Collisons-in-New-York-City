import streamlit as st 
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"/Users/iamsu/OneDrive/Python Projects/Build a Data Science Web App with Streamlit and Python/Motor_Vehicle_Collisions_-_Crashes.csv" #add / and then file path then / and the filename with the extension
)


st.title("Motor Vehicle Collisons in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to"
" analyze Motor Vehicle Collisions in NYC 🗽 💥 🚗")

@st.cache(persist=True) #decorating the function to make it performant
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']]) # parse_dates converte strings to datetime in Python and put your rows of interest
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True) #trick in working with strealit and map data is that you cannot have any missing values in columns corresponding to the latitude and longitude as it will jsut break the application
    # also another thing to note: LATITUDE and LONGITUDE have to be specified as columns for streamlit to pull up the data
    lowercase = lambda x: str(x).lower() #using string method to convert all the columns name to a string and then lower case it
    data.rename(lowercase, axis='columns', inplace=True) #renaming the columns as lowercase data 
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000) #loading 100000 rows from the dataframe named as 'data'
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of people injured in vehicle collision", 0, 19) #slider can have the range from 0 to max number of injuries
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how="any"))
#passing the latitude and longitude columns to plot and dropping na, how? from any one of them
#if we change the number of people injured in the map, it updates it really fast. It is becasue of st.cache thta was used before. If not used, have been very slower.


st.header("How many collisons occur during a given time of day?")
hour = st.selectbox("Hour to look at", range(0,24), 1) #hour should range from 0, 24 and the option should be of difference 1
data = data[data['date/time'].dt.hour == hour] # so with the change in tme the data in the table gets updated


st.markdown("Vehicle Collisions betweem %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50, #pitched at 50 degrees
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True, #makes 3D map
        pickable=True,
        elevation_scale=4,
        elevation_range = [0, 1000],        
        ),
    ],
))
#zoomed out the map to specified latitude and longitude


st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 Dangerous Streets By Affected Type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])    
    
    

if st.checkbox("Show Raw Data", False): # Creating the checkbox and 'False' means it is unchecked at first
    st.subheader('Raw Data')
    st.write(data)
    

