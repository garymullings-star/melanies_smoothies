# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your 
  custom Smoothie
  """
)

#import streamlit as st

title = st.text_input('Name of person on this order')
st.write('The name on your Smoothie will be', title)


# option = st.selectbox(
#     'What is your favourite fruit?',
#     ('Banana', 'Strawberries', 'Jack Fruit')
# )

# st.write('You selected:', option)

connection_parameters = st.secrets["snowflake"]

# connection_parameters = {
# account == "ODEUAMO-YKB64805",
# user == "sgnillumg",
# password == "SnowSwagg42!!!",
# role == "SYSADMIN",
# warehouse == "COMPUTE_WH",
# database == "SMOOTHIES",
# schema == "PUBLIC",
# client_session_keep_alive == true
# }

session = Session.builder.configs(connection_parameters).create()

# ✅ Health check query
try:
    result = session.sql("SELECT CURRENT_DATE").collect()
    st.success(f"Snowflake connection OK. Current date: {result[0][0]}")
except Exception as e:
    st.error(f"Snowflake connection failed: {e}")
  
#my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME'))
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()


ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
    , max_selections=5
    )

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    ingredients_string = ''
   #name_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
       # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order
    )
                    values ('""" + ingredients_string + """','""" + title + """')"""

     

    st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:

    # if ingredients_string:
        session.sql(my_insert_stmt,).collect()
        st.success('Your Smoothie is ordered ' +  title + '!',icon="✅")
      
#new section to display smoothiefront nutrition info


# Call the API
#smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")  
#st.text(smoothiefroot_response.json())
#df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)



