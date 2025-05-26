# AI_DUBAI_CRYPTO_CLOUD

Project structure: 

├── app.py                               "main streamlit app"             
├── data                                 "local data"
│   ├── dubai.geojson
│   └── uae_real_estate_2024.csv
├── exports                              "plot files"
│   └── charts
│       └── temp_chart.png
├── notebooks   
│   ├── agent_with_tools.ipynb           "prototyping"
│   └── EDA.ipynb
├── README.md                            
├── requirements.txt              
└── src                   
    ├── classifiers.py                   "Classification routing models"
    ├── process_data.py                  "Data processing"
    └── tools.py                         "LangChain tools"


TESTS:

pytest tests/test_agent.py
to run specific test: pytest tests/test_agent.py::test_valid_output_query
