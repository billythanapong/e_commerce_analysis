import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
# Machine learning extend
import mlxtend
# Import apriori for MBA
from PIL import Image

from mlxtend.frequent_patterns import association_rules, apriori, fpgrowth

def extra_shop_list(rules,item_name,lift_threshold):

    '''Function that obtain the dataframe of specific item name to give out the set of matching item'''

    rec_result = rules[(rules['antecedents'] == {item_name}) & (rules['lift'] > lift_threshold)]
    # Convert frozenset to tuple if each row is 'frozenset
    table_trans = pd.DataFrame(rec_result.applymap(lambda x: tuple(x) if isinstance(x, frozenset) else x ))
    temp1 = table_trans['consequents'].values
    temp2 = []
    # for set in each row of dataframe
    for i in temp1:
        for j in i:
            if j not in temp2:
                temp2.append(j)
            else:
                continue
    return temp2

def get_selected_checkboxes():
    '''return the name of suggested item by search the dynamic checkbox key in session state
    and get the key of check box with True value'''

    return [i.replace('dynamic_checkbox_','') for i in st.session_state.keys()
     if i.startswith('dynamic_checkbox_') and st.session_state[i]]



# Import data
transaction = pd.read_csv('./data/transaction.csv')
bill_data = pd.read_csv('./data/bill_cleaned.csv')
image = Image.open('./shop.jpg')

# Dummy
item_trans = transaction['item'].str.get_dummies('|')

# Change astype to 'bool'
item_trans_bool = item_trans.astype(bool)

with st.sidebar:
    metric = st.radio('Metric for assc rules',['lift','support','confidence'])
    amt_metric = number = st.number_input('Insert a number in range (0,1]')
    lift_threshold = st.select_slider('Lift threshold',options =[0,1,2,3,4,5])


# frequent_itemsets = apriori(basket, min_support = 0.05, use_colnames = True)

# 5 % of items shown will be selected
frequent_itemsets = fpgrowth(item_trans_bool, min_support = 0.000655, use_colnames = True)


# Sorted
frequent_itemsets.sort_values('support', ascending=False)

# สร้าง association rules
# metrices = ['support', 'confidence', 'lift', 'leverage', and 'conviction']
# rules = association_rules(frequent_itemsets, metric = "support", min_threshold = .2)
# rules = association_rules(frequent_itemsets, metric = "confidence", min_threshold = .5)
rules = association_rules(frequent_itemsets, metric = metric, min_threshold =amt_metric )

rules.sort_values(by = 'lift', ascending = False, inplace = True)

# add support number
rules['support_n'] = rules['support']*len(item_trans_bool)


if "page" not in st.session_state:
    st.session_state.page = 0

placeholder = st.empty()

shopping_cart = []
if st.session_state.page == 0:
    # Show in every pages.
    st.title('Market Basket Analysis')
    st.image(image)

    
    shopping_cart = st.multiselect(
    'Which items would you like to add to your cart?',
    bill_data['item_brand'].unique())

    df = pd.DataFrame(shopping_cart,columns=['Items'])
    shop_list = st.table(df)


    # show the last item in options
    if len(shopping_cart) != 0 :
        last_item = shopping_cart[-1]
        # at lift_threshold = 1, this is the list of suggested items
        suggest_item = list(extra_shop_list(rules,last_item,lift_threshold))
        if len(suggest_item) != 0:
  
            # Show the check box of suggested items
            st.write("Other items you may interested :")
            for i in suggest_item:
                st.checkbox(i, key='dynamic_checkbox_' + i)


            add_cart = []
            cols = st.columns(5)

            if cols[0].button("Add to Cart"):
                for i in get_selected_checkboxes():
                    add_cart.append(i)
                df2 = pd.DataFrame(add_cart)

                shop_list.add_rows(df2)

            if cols[1].button('Pay'):
                st.session_state.page = 1

elif(st.session_state.page == 1):
    placeholder.title('Thank you for purchasing')


  