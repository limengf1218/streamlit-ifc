# chatbot_page.py

import openai
from openai import OpenAI
import streamlit as st
import ifcopenshell
import pandas as pd
import traceback
import os

# Set your OpenAI API key
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"],
    base_url="https://litellm.govtext.gov.sg/",
    default_headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"},

)


def main():
    st.set_page_config(
        page_title="IFC Chatbot",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🤖 IFC Model Chatbot")
    st.markdown("Ask any question about your IFC model.")

    session = st.session_state

    # Check if the IFC file is loaded
    if "ifc_file" not in session:
        st.warning("Please load an IFC file from the Home page.")
        return

    # Initialize chat history in session state
    if "chat_history" not in session:
        session["chat_history"] = []

    # Chatbot interface
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send"):
        if user_input.strip() == "":
            st.error("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = process_query(user_input, session["ifc_file"])
                    # Display the conversation
                    session["chat_history"].append(("You", user_input))
                    session["chat_history"].append(("Chatbot", response))
                    for speaker, text in session["chat_history"]:
                        if speaker == "You":
                            st.markdown(f"**You:** {text}")
                        else:
                            st.markdown(f"**Chatbot:** {text}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    traceback.print_exc()

def process_query(user_query, ifc_file):
    # Construct the prompt for the OpenAI API
    prompt = f"""
You are an expert in IFC files and ifcopenshell library.
Write Python code using ifcopenshell to answer the following question:
"{user_query}"
Only use the 'ifc_file' object provided; do not import any modules.
Only provide the code snippet without any explanations.
Do not include any markdown formatting, code fences, comments, or import statements.
The code should assign the answer to a variable named 'result'.
"""



    # Call the OpenAI API to get the code
    response = client.chat.completions.create(
        model="gpt-4o-prd-gcc2-lb",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    code = response.choices[0].message.content
    code = sanitize_code(code)

    # Debugging: Print the generated code
    print("Generated code:")
    print(code)

    # Execute the code
    result = execute_code(code, ifc_file)

    return result

def sanitize_code(code):
    # Remove markdown code fences, comments, and import statements
    lines = code.split('\n')
    sanitized_lines = []
    for line in lines:
        stripped_line = line.strip()
        if (
            not stripped_line.startswith('```') and
            not stripped_line.startswith('#') and
            not stripped_line.startswith('import') and
            'import ' not in stripped_line
        ):
            sanitized_lines.append(line)
    sanitized_code = '\n'.join(sanitized_lines)
    return sanitized_code

def execute_code(code, ifc_file):
    # Define a restricted global and local namespace
    allowed_builtins = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'float', 'int', 'len',
        'list', 'max', 'min', 'range', 'set', 'str', 'sum', 'tuple', 'zip'
    }
    restricted_globals = {
        "__builtins__": {k: __builtins__[k] for k in allowed_builtins},
        "ifcopenshell": ifcopenshell,
        "pd": pd,
    }
    local_vars = {
        "ifc_file": ifc_file,
        "result": None,
    }

    # Check for disallowed statements before execution
    if 'import ' in code:
        raise RuntimeError("Import statements are not allowed.")

    # Execute the code
    try:
        exec(code, restricted_globals, local_vars)
    except Exception as e:
        raise RuntimeError(f"Error executing code: {e}")

    # Get the result
    if "result" in local_vars:
        return local_vars["result"]
    else:
        raise ValueError("The generated code did not produce a 'result' variable.")
    
if __name__ == "__main__":
    main()