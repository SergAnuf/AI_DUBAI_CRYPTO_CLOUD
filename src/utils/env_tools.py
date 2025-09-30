import sys
import streamlit as st
import inspect


def is_running_in_streamlit():
    for frame_info in inspect.stack():
        if "streamlit" in frame_info.filename.lower():
            return True
    return False


"Important decorator to cache resources in Streamlit runtime, otherwise not."


def cache_resource(func):
    if is_running_in_streamlit():
        return st.cache_resource(func)
    else:
        return func  # Don't use caching if not in a Streamlit runtime
