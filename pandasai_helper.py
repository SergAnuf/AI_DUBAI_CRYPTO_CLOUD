from pandasai.llm import OpenAI
from pandasai import SmartDataframe

class PandasAIAssistant:
    def __init__(self, api_key, df):
        """
        Initialize the PandasAI assistant with OpenAI and dataframe
        """
        self.llm = OpenAI(api_key=api_key)
        self.sdf = SmartDataframe(df, config={"llm": self.llm})
    
    def chat(self, query):
        """
        Process a natural language query against the dataframe
        """
        try:
            response = self.sdf.chat(query)
            return response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"