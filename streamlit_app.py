import streamlit as st
import requests

st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

try:
    # ✅ Connection
    conn = st.connection("snowflake")
    session = conn.session()

    # ✅ Fetch BOTH columns
    df = session.sql(
        "SELECT FRUIT_NAME, SEARCH_ON FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
    ).to_pandas()

    # mapping dictionary
    fruit_map = dict(zip(df["FRUIT_NAME"], df["SEARCH_ON"]))

    fruit_list = df["FRUIT_NAME"].tolist()

    # ✅ Multiselect
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_list,
        max_selections=5
    )

    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)

        st.subheader("🍎 Nutrition Info")

        for fruit in ingredients_list:
            try:
                clean_fruit = fruit_map.get(fruit)

                response = requests.get(
                    f"https://fruityvice.com/api/fruit/{clean_fruit}"
                )
                response.raise_for_status()

                st.write(f"### {fruit}")
                st.json(response.json())

            except Exception as e:
                st.warning(f"No data for {fruit}")

        # ✅ Insert
        if st.button('Submit Order'):
            if name_on_order:
                insert_sql = f"""
                    INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                    VALUES ('{ingredients_string}', '{name_on_order}')
                """

                session.sql(insert_sql).collect()
                st.success(f'Your Smoothie is ordered, {name_on_order}! ✅')
            else:
                st.warning("Please enter your name")

except Exception as ex:
    st.error(f"Error: {str(ex)}")
