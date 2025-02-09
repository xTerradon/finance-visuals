import streamlit as st

import handlers.data_handler as dh

from pages.single_symbol import single_symbol_page
from pages.all_symbols import all_symbols_page

single_symbol_page_st = st.Page(single_symbol_page, title="Single Symbol", icon="📊")
all_symbols_page_st = st.Page(all_symbols_page, title="All Symbols", icon="📈")

def main():
    st.title("OHLC Data Analysis")

    if "available_symbols" not in st.session_state:
        with st.spinner("Loading available symbols..."):
            st.session_state.available_symbols = dh.get_available_symbols()

    if "available_timeframes" not in st.session_state:
        with st.spinner("Loading available timeframes..."):
            st.session_state.available_timeframes = dh.get_available_timeframes()


    with st.container(border=True):
        leftcol, rightcol = st.columns(2)
        with leftcol:
            st.metric("Number of Symbols", len(st.session_state.available_symbols))
        with rightcol:
            st.metric("Number of Timeframes", len(st.session_state.available_timeframes))

    all_symbols_page()

    st.header("Actions")
    if st.button("Analyze Single Symbol", use_container_width=True):
        st.switch_page(single_symbol_page_st)
    if st.button("Analyze All Symbols", use_container_width=True):
        st.switch_page(all_symbols_page_st)

home_page_st = st.Page(main, icon="🏠")


pg = st.navigation(
    [
        home_page_st,
        single_symbol_page_st,
        all_symbols_page_st,
    ], 
    position="hidden"
)
pg.run()