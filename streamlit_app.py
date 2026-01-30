import runpy
import os

# Wrapper to execute the Streamlit app located at frontend/streamlit_app.py
APP_PATH = os.path.join(os.path.dirname(__file__), 'frontend', 'streamlit_app.py')

if __name__ == '__main__':
    runpy.run_path(APP_PATH, run_name='__main__')
