import streamlit as st

import pandas as pd
import numpy as np

import handlers.data_handler as dh
import handlers.analysis_handler as ah

import os

def load_ohlc_data():
    st.session_state.ohlc_data = dh.get_data(st.session_state.selected_symbol, st.session_state.selected_timeframe)

def del_session_ohlc():
    if "movement_stats_accumulated" in st.session_state:
        del st.session_state.movement_stats_accumulated
    if "movement_stats_aggregated" in st.session_state:
        del st.session_state.movement_stats_aggregated
    if "total_klines_loaded" in st.session_state:
        del st.session_state.total_klines_loaded

def analyze_ohlc_data():
    history_len = st.session_state.history_len
    return_len = st.session_state.return_len
    st.session_state.ohlc_data_annotated = ah.annotate_data(st.session_state.ohlc_data, history_len, return_len)
    st.session_state.movement_stats = ah.get_stats_from_previous_movement(st.session_state.ohlc_data_annotated, history_len, return_len)
    st.session_state.movement_stats["symbol"] = st.session_state.selected_symbol

    if "movement_stats_accumulated" in st.session_state:
        st.session_state.movement_stats_accumulated = pd.concat([st.session_state.movement_stats_accumulated, st.session_state.movement_stats])
    else:
        st.session_state.movement_stats_accumulated = st.session_state.movement_stats



def all_symbols_page():
    st.title("Analyze all Symbols")

    with st.container(border=True):
        st.selectbox("Timeframe", st.session_state.available_timeframes, key="selected_timeframe", index=len(st.session_state.available_timeframes) - 1)
        st.slider("History Length", min_value=1, max_value=10, value=2, key="history_len")
        st.slider("Return Length", min_value=1, max_value=10, value=2, key="return_len")
        
        if st.button("Start Analysis", disabled="total_klines_loaded" in st.session_state):
            if f"updown_h{st.session_state.history_len}_r{st.session_state.return_len}.pkl" in os.listdir("../evaluation_data/"):
                st.session_state.movement_stats_aggregated = pd.read_pickle(f"../evaluation_data/updown_h{st.session_state.history_len}_r{st.session_state.return_len}.pkl")
            else:
                del_session_ohlc()
                st.session_state.total_klines_loaded = 0
                analysis_progress = st.progress(0 / len(st.session_state.available_symbols))
                    
                for i, symbol in enumerate(st.session_state.available_symbols):
                    analysis_progress.progress((i + 1) / len(st.session_state.available_symbols), f"Analyzing {str(i + 1).zfill(len(str(len(st.session_state.available_symbols))))}/{len(st.session_state.available_symbols)}: {symbol} ")
                    st.session_state.selected_symbol = symbol
                    load_ohlc_data()
                    if st.session_state.ohlc_data is None:
                        pass
                        # st.toast(f"Could not load {st.session_state.selected_symbol}, skipping...", icon="⚠️")
                    else:
                        analyze_ohlc_data()
                
                analysis_progress.progress(0.999, "Aggregating Movement Data")
                st.session_state.movement_stats_aggregated = ah.aggregate_movement_stats(st.session_state.movement_stats_accumulated)
                st.session_state.movement_stats_aggregated.to_pickle(f"../evaluation_data/updown_h{st.session_state.history_len}_r{st.session_state.return_len}.pkl")
                analysis_progress.progress(1.0, "Analysis completed")
                del st.session_state.total_klines_loaded
        
    if "movement_stats_aggregated" in st.session_state:
        st.divider()

        if "movement_stats_accumulated" in st.session_state:
            with st.expander("Show Movement Stats", expanded=False):
                st.dataframe(st.session_state.movement_stats_accumulated, use_container_width=True, hide_index=True)

        st.dataframe(
            st.session_state.movement_stats_aggregated,
            use_container_width=True,
            hide_index=True,
            column_config={
                "pattern": st.column_config.AreaChartColumn(y_min=-1, y_max=1, width=50),
                "share": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.2f", width=50),
                "sum_return": st.column_config.BarChartColumn(
                    y_min=min(st.session_state.movement_stats_aggregated[[col for col in st.session_state.movement_stats_aggregated.columns if "return_" in col]].min()),  # Auto-scale min
                    y_max=max(st.session_state.movement_stats_aggregated[[col for col in st.session_state.movement_stats_aggregated.columns if "return_" in col]].max()),  # Auto-scale max
                    width=100
                ),

                "sum_percentage": st.column_config.BarChartColumn(
                    y_min=min(st.session_state.movement_stats_aggregated[[col for col in st.session_state.movement_stats_aggregated.columns if "percentage_" in col]].min()),  # Auto-scale min
                    y_max=max(st.session_state.movement_stats_aggregated[[col for col in st.session_state.movement_stats_aggregated.columns if "percentage_" in col]].max()), # Auto-scale max
                    width=100
                )
            }
        )

        with st.spinner("Plotting Data"):
            st.session_state.movement_stats_aggregated["sum_pattern"] = st.session_state.movement_stats_aggregated.apply(lambda row: sum(list(row["pattern"])), axis=1)
            st.bar_chart(
                data=st.session_state.movement_stats_aggregated,
                x="sum_pattern",
                y="return_1",
                x_label="Sum of Movement Pattern",
                y_label="Return after 1 kline",
                color="share",
            )

    if "ohlc_data_annotated" in st.session_state:
        with st.container(border=True):
            with st.expander("Filter by Pattern", expanded=False):
                st.dataframe(st.session_state.ohlc_data_annotated, use_container_width=True, hide_index=True)
            st.write(st.session_state.movement_stats_aggregated.columns)
            st.selectbox("Pattern", st.session_state.movement_stats_aggregated["pattern"].unique(), key="selected_pattern")

            ohlc_data_filtered = st.session_state.ohlc_data_annotated[st.session_state.ohlc_data_annotated["pattern"] == st.session_state.selected_pattern]
            st.write(ohlc_data_filtered["return_1"].describe())
        
    # TODO: somehow check for recent X days in comparison to all-time
    # TODO: check for current situations that would allow for a prediction
    # TODO: check that symbols history against the overall history
    # TODO: also factor in risk and maximum drawback (maybe the data is skewed by few large samples)
    