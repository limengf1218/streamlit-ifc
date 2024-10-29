import ifcopenshell
import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="IFC Stream",
    page_icon="✍️",
)

def callback_upload():
    session = st.session_state
    try:
        session["file_name"] = session["uploaded_file"].name
        session["array_buffer"] = session["uploaded_file"].getvalue()
        session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8", errors='ignore'))
        session["is_file_loaded"] = True

        # Reset previous data
        session["isHealthDataLoaded"] = False
        session["HealthData"] = {}
        session["Graphs"] = {}
        session["SequenceData"] = {}
        session["CostScheduleData"] = {}
        session["DataFrame"] = None
        session["Classes"] = []
        session["IsDataFrameLoaded"] = False
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {e}")

def get_project_name():
    session = st.session_state
    if "ifc_file" in session:
        return session["ifc_file"].by_type("IfcProject")[0].Name
    else:
        return "Unknown Project"

def main():
    session = st.session_state
    st.title("Streamlit IFC")
    st.markdown(
        """ 
        ### 📁 Click on Browse File in the Side Bar to start
        """
    )

    # Add File uploader to Side Bar Navigation
    st.sidebar.header('Model Loader')
    st.sidebar.file_uploader("Choose a file", type=['ifc'], key="uploaded_file", on_change=callback_upload)

    # Add File Name and Success Message
    if session.get("is_file_loaded"):
        st.sidebar.success('Project successfully loaded')
        st.sidebar.write("🔃 You can reload a new file")

        st.subheader(f'Start Exploring "{get_project_name()}"')

if __name__ == "__main__":
    main()
