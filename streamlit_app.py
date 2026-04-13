import streamlit as st
import requests
from snowflake.snowpark.functions import col



st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

try:
    # ✅ Correct connection
    conn = st.connection("snowflake")
    session = conn.session()

    # ✅ Correct query + pandas conversion
    my_dataframe = session.sql(
        "SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
    ).to_pandas()

    fruit_list = my_dataframe["FRUIT_NAME"].tolist()

    # ✅ Multiselect fix
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_list,
        max_selections=5
    )

    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)

        for fruit_chosen in ingredients_list:
            try:
                response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
                response.raise_for_status()

                data = response.json()
                st.write(f"### {fruit_chosen} details")
                st.json(data)

            except Exception as e:
                st.error(f"API error for {fruit_chosen}: {e}")

        # ✅ Insert query
        if st.button('Submit Order'):
            if name_on_order:
                insert_sql = f"""
                    INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                    VALUES ('{ingredients_string}', '{name_on_order}')
                """

                session.sql(insert_sql).collect()
                st.success(f'Your Smoothie is ordered, {name_on_order}! ✅')
            else:
                st.warning("Please enter a name before ordering")

except Exception as ex:
    st.error(f"Error: {str(ex)}")
