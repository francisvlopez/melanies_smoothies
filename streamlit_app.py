# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ——————————————————————————
# USER INPUT
# ——————————————————————————
name_of_order = st.text_input('Name on Smoothie:')
st.write("The name of your Smoothie will be:", name_of_order)

# ——————————————————————————
# SNOWFLAKE CONNECTION
# ——————————————————————————
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

pd_df = my_dataframe.to_pandas()

# ——————————————————————————
# FIXED: multiselect must use a list (not a Snowpark dataframe)
# ——————————————————————————
ingredient_options = pd_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    ingredient_options,
    max_selections=5
)

# ——————————————————————————
# SUBMIT ORDER
# ——————————————————————————
if ingredients_list:

    # Build string of ingredients
    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_of_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_of_order}!", icon="✅")

# ——————————————————————————
# SHOW NUTRITION INFO
# ——————————————————————————
if ingredients_list:
    for fruit_chosen in ingredients_list:

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )
