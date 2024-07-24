import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
import math
import numpy as np
from config import state_abbr_map
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='USA Hockey Registration dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.




@st.cache_data
def get_registration_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/registration_by_state.csv'
    df = pd.read_csv(DATA_FILENAME, thousands=',')

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP

    # Convert years from string to integers
    df['Year'] = pd.to_numeric(df['Year']).replace(',', '')
    print(df['Year'])
    df['Total'] = pd.to_numeric(df['Total'])

    return df

df = get_registration_data()
df['id']=df['State'].map(state_abbr_map)

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: USA Hockey Player Registration

Browse Historical Player Registration data from the [USA Hockey](https://www.usahockey.com/membershipstats) website.
As you'll notice, the data only goes back to 2007 right now, but data back to 1996 is soon to come!
'''

# Add some spacing
''
''

min_value = df['Year'].min()
max_value = df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

states = df['State'].unique()

if not len(states):
    st.warning("Select at least one state")

selected_states = st.multiselect(
    'Which states would you like to view?',
    states,
    ['MA', 'MN', 'NY', 'NJ', 'OH', 'IL'])

''
''
''

# Filter the data
filtered_df = df[
    (df['State'].isin(selected_states))
    & (df['Year'] <= to_year)
    & (from_year <= df['Year'])
]

st.header('Registration count over time', divider='gray')

''

st.line_chart(
    filtered_df,
    x='Year',
    y='Total',
    color='State',
)

''
''


first_year = df[df['Year'] == from_year]
#print(first_year)
last_year = df[df['Year'] == to_year]

st.header(f'Total in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, state in enumerate(selected_states):
    col = cols[i % len(cols)]

    with col:
        first_reg = first_year[df['State'] == state]['Total'].iat[0]
        last_reg = last_year[df['State'] == state]['Total'].iat[0]

        if math.isnan(first_reg):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_reg / first_reg:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{state} Player Count',
            value=f'{last_reg}',
            delta=growth,
            delta_color=delta_color
        )


# Add some spacing
''
''
''
''
''
''

''

# Add map


df['state_id'] = df['state_id'].astype(str)

url_geojson = 'https://raw.githubusercontent.com/robbygrathwohl/USTemps/main/data/us_states.json'
data_geojson_remote = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))


states_map = alt.Chart(data_geojson_remote).mark_geoshape(
    stroke='white',
    strokeWidth=1
).encode(
    color=alt.Color('Total:Q').scale(scheme='viridis')
).properties(
    title='US State Registration',
    projection={'type': 'albersUsa'},
).transform_lookup(
     lookup='properties.STATE',
     from_=alt.LookupData(df, 'id', ['Total'])
)




st.altair_chart(states_map, use_container_width=True)
