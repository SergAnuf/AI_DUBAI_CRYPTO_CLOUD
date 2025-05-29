#!/bin/bash

echo "Stopping any running Streamlit processes..."
pkill -f streamlit

echo "Clearing Streamlit cache..."
streamlit cache clear --yes

echo "Clearing Streamlit's temporary folder..."
rm -rf ~/.streamlit/cache
rm -rf ~/.streamlit/config.toml
rm -rf ~/.streamlit/credentials.toml

echo "Done. Ready to launch Streamlit!"
