import importlib

# List of packages you want to check
packages = [
    "streamlit",
    "pandas",
    "numpy",
    "tqdm",
    "python_dotenv",
    "openai",
    "pandasai",
    "pandasai_openai",
    "langchain",
    "langchain_community",
    "langchain_core",
    "langsmith",
    "geopy",
    "requests",
    "pyyaml",
    "dataclasses_json"
]

for pkg in packages:
    try:
        module = importlib.import_module(pkg.replace("-", "_"))
        version = getattr(module, "__version__", "No __version__ attribute")
        print(f"{pkg}=={version}")
    except ModuleNotFoundError:
        print(f"{pkg} not installed")
    except Exception as e:
        print(f"{pkg} error: {e}")
