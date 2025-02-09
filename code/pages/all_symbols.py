import streamlit as st

import pandas as pd
import numpy as np

import handlers.data_handler as dh
import handlers.analysis_handler as ah

def load_ohlc_data():
    st.session_state.ohlc_data = dh.get_data(st.session_state.selected_symbol, st.session_state.selected_timeframe)
    
    if "movement_stats" in st.session_state:
        del st.session_state.movement_stats
    if "movement_stats_melted" in st.session_state:
        del st.session_state.movement_stats_melted

def analyze_ohlc_data():
    history_len = st.session_state.history_len
    return_len = st.session_state.return_len
    st.session_state.movement_stats = ah.get_stats_from_previous_movement(st.session_state.ohlc_data, history_len, return_len)
    st.session_state.movement_stats["symbol"] = st.session_state.selected_symbol

    if "movement_stats_accumulated" in st.session_state:
        st.session_state.movement_stats_accumulated = pd.concat([st.session_state.movement_stats_accumulated, st.session_state.movement_stats])
    else:
        st.session_state.movement_stats_accumulated = st.session_state.movement_stats


def aggregate_movement_stats():
    return_cols = [col for col in st.session_state.movement_stats_accumulated.columns if "return" in col]
    st.session_state.movement_stats_aggregated = st.session_state.movement_stats_accumulated.groupby(["pattern"]).agg({"count": "sum", **{col: "sum" for col in return_cols}}).reset_index()

def all_symbols_page():
    st.title("Analyze all Symbols")

    with st.container(border=True):
        st.selectbox("Timeframe", st.session_state.available_timeframes, key="selected_timeframe", index=len(st.session_state.available_timeframes) - 1, on_change=load_ohlc_data)
        st.slider("History Length", min_value=1, max_value=10, value=3, key="history_len")
        st.slider("Return Length", min_value=1, max_value=10, value=3, key="return_len")
        
        if st.button("Start Analysis"):
            st.session_state.total_klines_loaded = 0
            analysis_progress = st.progress(0 / len(st.session_state.available_symbols))
                
            for i, symbol in enumerate(st.session_state.available_symbols):
                analysis_progress.progress((i + 1) / len(st.session_state.available_symbols), f"Analyzing {symbol}")
                st.session_state.selected_symbol = symbol
                load_ohlc_data()
                if st.session_state.ohlc_data is None:
                    pass
                    # st.toast(f"Could not load {st.session_state.selected_symbol}, skipping...", icon="⚠️")
                else:
                    analyze_ohlc_data()
            
            analysis_progress.progress(0.999, "Aggregating Movement Data")
            aggregate_movement_stats()
            analysis_progress.progress(1.0, "Analysis completed")
        
        if "movement_stats_accumulated" in st.session_state:
            st.divider()

            st.dataframe(
                st.session_state.movement_stats_aggregated,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "pattern": st.column_config.AreaChartColumn(y_min=-1, y_max=1, width=50),
                    "count": st.column_config.ProgressColumn(min_value=0, max_value=st.session_state.ohlc_data.shape[0], format="%.0f", width=50),
                }
            )
            with st.expander("View Raw Data", expanded=False):
                st.dataframe(
                    st.session_state.movement_stats_accumulated,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "pattern": st.column_config.AreaChartColumn(y_min=-1, y_max=1, width=50),
                        "count": st.column_config.ProgressColumn(min_value=0, max_value=st.session_state.ohlc_data.shape[0], format="%.0f", width=50),
                    }
                )

            with st.spinner("Plotting Data"):
                st.scatter_chart(
                    data=st.session_state.movement_stats_aggregated,
                    y="value",
                    x="return_type",
                    size="count",
                )
              
            