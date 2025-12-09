# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session

from snowflake.snowpark.functions import col

import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_of_order = st.text_input('Name on Smoothie: ')
st.write("The name of your Smoothie will be: ", name_of_order)

#session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe  
    , max_selections=5
)

if ingredients_list:
   ingredients_string = ''

   for fruit_chosen in ingredients_list:
       ingredients_string += fruit_chosen + ' '

   # The original my_insert_stmt was missing the column names for both values
   # Corrected statement now specifies both columns: (ingredients, name_on_order)
   my_insert_stmt = f"""
       INSERT INTO smoothies.public.orders(ingredients, name_on_order)
       VALUES ('{ingredients_string.strip()}', '{name_of_order}')
   """
   
   time_to_insert = st.button('Submit Order')
   if time_to_insert:
    # Use session.sql() and st.success() within the button logic
    session.sql(my_insert_stmt).collect()
    st.success(f'Your Smoothie is ordered, {name_of_order}!', icon="✅")

if ingredients_list:
  ingredients_string = ''

  for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '
    st.subheader(fruit_chosen + ' Nutrition Information')
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon" + fruit_chosen)
    #st.text(smoothiefroot_response.json())
    sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
