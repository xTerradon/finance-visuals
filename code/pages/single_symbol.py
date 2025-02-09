import streamlit as st

import pandas as pd
import numpy as np

import handlers.data_handler as dh
import handlers.analysis_handler as ah

def load_ohlc_data():
    with st.spinner("Loading data..."):
        st.session_state.ohlc_data = dh.get_data(st.session_state.selected_symbol, st.session_state.selected_timeframe)
    
    if "movement_stats" in st.session_state:
        del st.session_state.movement_stats
    if "movement_stats_melted" in st.session_state:
        del st.session_state.movement_stats_melted

def analyze_ohlc_data():
    history_len = st.session_state.history_len
    return_len = st.session_state.return_len
    st.session_state.movement_stats = ah.get_stats_from_previous_movement(st.session_state.ohlc_data, history_len, return_len)

def melt_movement_stats():
    return_cols = [col for col in st.session_state.movement_stats.columns if "return" in col]
    st.session_state.movement_stats_melted = st.session_state.movement_stats.melt(
        id_vars=["pattern", "count"], 
        value_vars=return_cols,
        var_name="return_type", 
        value_name="value")

def single_symbol_page():
    st.title("Analyze Single Symbol")

    with st.container(border=True):
        leftcol, rightcol = st.columns(2)
        with leftcol:
            st.selectbox("Symbol", st.session_state.available_symbols, key="selected_symbol", on_change=load_ohlc_data)
        with rightcol:
            st.selectbox("Timeframe", st.session_state.available_timeframes, key="selected_timeframe", index=len(st.session_state.available_timeframes) - 1, on_change=load_ohlc_data)

        if "oclh_data" not in st.session_state:
            load_ohlc_data()

        if st.session_state.ohlc_data is None:
            st.error("Could not load data")
        else:
            st.line_chart(
                data=st.session_state.ohlc_data, 
                x="time", 
                y=["open", "high", "low", "close"],
                x_label="Time",
                y_label="Price",
            )

    if st.session_state.ohlc_data is not None:
        with st.container(border=True):
            st.slider("History Length", min_value=1, max_value=10, value=5, key="history_len")
            st.slider("Return Length", min_value=1, max_value=10, value=3, key="return_len")

            if st.button(f"Analyze {st.session_state.ohlc_data.shape[0]} klines", disabled="movement_stats" in st.session_state):
                analyze_ohlc_data()
            
            if "movement_stats" in st.session_state:
                st.divider()
                st.dataframe(
                    st.session_state.movement_stats,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "pattern": st.column_config.AreaChartColumn(y_min=-1, y_max=1, width=50),
                        "count": st.column_config.ProgressColumn(min_value=0, max_value=st.session_state.ohlc_data.shape[0], format="%.0f", width=50),
                    }
                )

                melt_movement_stats()

                st.scatter_chart(
                    data=st.session_state.movement_stats_melted,
                    y="value",
                    x="return_type",
                    size="count",
                )
            