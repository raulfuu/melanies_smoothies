# Import python packages
import streamlit as st
import requests  
import pandas as pd # <-- Added pandas
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: ")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input('Name of Smoothie')
st.write('The name of your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Pull BOTH columns from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

# Show the multiselect box (using just the FRUIT_NAME column for the UI)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', pd_df['FRUIT_NAME'], max_selections=5
)   

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Look up the exact SEARCH_ON value for the fruit the user chose
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Swap out 'fruit_chosen' for 'search_on' in the API URL
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)  
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Build the insert statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # Create the Submit button
    time_to_insert = st.button('Submit Order')
    
    # Only run the SQL when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
