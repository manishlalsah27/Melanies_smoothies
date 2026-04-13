# Import python packages.
import streamlit as st 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Name input
Name_on_order = st.text_input("Name of the smoothie:")
st.write("The name of the smoothie will be:", Name_on_order)

# ✅ Correct session (Snowflake Streamlit)
session = get_active_session()

# Load table
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME')).to_pandas()

# Multiselect (fix: pandas use karo)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # ✅ Safe SQL (better way)
    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{Name_on_order}')
    """

    # Button
    if st.button('Submit order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {Name_on_order}!', icon="✅")
