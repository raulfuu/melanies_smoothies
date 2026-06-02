# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
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
# session = get_active_session() 
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Show the multiselect box
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', my_dataframe, max_selections=5
)   

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Build the insert statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # Create the Submit button
    time_to_insert = st.button('Submit Order')
    
    # Only run the SQL when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


import requests  
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")  
st.text(smoothiefroot_response.json())
