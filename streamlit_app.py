# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write("""  Choose the fruits you want in your custom Smoothie!  """)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
 #   st.dataframe(data= my_dataframe,use_container_width= True)
  #  st.stop()

    pd_df= my_dataframe.to_panda()
    st.dataframe(pd_df)
    st.stop()

    

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

    # Process ingredients selection
    if ingredients_list:
        ingredients_string = ''
        for fruit_chosen in ingredients_list:
            ingredients_string +=fruit_chosen+''
            search_on = pd_df.loc[pd_df['FRUIT_NAME']==fruit_chosen, 'SEARCH_ON'].iloc[0]
          #  st.write('The Search value for ' , fruit_chosen, 'is', search_on, '.')          
            st.subheader(fruit_chosen+= fruit_chosen +'Nutrition Information')
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            # smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
            smoothiefroot_response.raise_for_status()
                if smoothiefroot_response.status_code == 200:
                    st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                else:
                    st.warning(f"Failed to fetch details for {fruit_chosen}")


        # ✅ IMAGE WALA CODE YAHI ADD KIYA HAI (exact same)
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
       # st.text(smoothiefroot_response.json())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

        # SQL statement
        my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                            VALUES ('{}', '{}')""".format(ingredients_string, name_on_order)

        # Button to submit order
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")
