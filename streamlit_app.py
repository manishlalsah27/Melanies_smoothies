import streamlit as st
import requests
from snowflake.snowpark.functions import col

response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

if response.status_code == 200:
    st.json(response.json())
else:
    st.error(f"Error: {response.status_code}")

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Input
Name_on_order = st.text_input("Name of the smoothie:")
st.write("The name of the smoothie will be:", Name_on_order)

try:
    # ✅ Cloud connection
    conn = st.connection("snowflake")
    session = conn.session()

    # ✅ Load data (convert to pandas)
    my_dataframe = session.sql(
        "SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
    ).to_pandas()

    fruit_list = my_dataframe["FRUIT_NAME"].tolist()

    # ✅ Multiselect
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_list,
        max_selections=5
    )

    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)

        if st.button('Submit order'):
            if Name_on_order:
                insert_sql = f"""
                    INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                    VALUES ('{ingredients_string}', '{Name_on_order}')
                """

                session.sql(insert_sql).collect()
                st.success(f'Your Smoothie is ordered, {Name_on_order}! ✅')
            else:
                st.warning("Please enter name")

except Exception as e:
    st.error(f"Error: {e}")
