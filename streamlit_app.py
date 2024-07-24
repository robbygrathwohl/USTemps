import streamlit as st
import pandas as pd
import math
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
    df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 2007
    MAX_YEAR = 2024

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
    df = df.melt(
        ['State'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR)],
        'Year',
        'Total',
    )

    # Convert years from string to integers
    df['Year'] = pd.to_numeric(df['Year'])

    return df

df = get_registration_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
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
filtered_gdp_df = df[
    (df['State'].isin(selected_states))
    & (df['Year'] <= to_year)
    & (from_year <= df['Year'])
]

st.header('Registratoin count over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='Total',
    color='State',
)

''
''


first_year = df[df['Year'] == from_year]
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
