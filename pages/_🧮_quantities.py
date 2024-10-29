import streamlit as st
from tools import ifchelper
from tools import pandashelper
from tools import graph_maker

def initialize_session_state():
    session = st.session_state
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

def load_data():
    session = st.session_state
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session["Classes"] = session["DataFrame"]["Class"].value_counts().keys().tolist()
        session["IsDataFrameLoaded"] = True

def get_ifc_pandas():
    session = st.session_state
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session["ifc_file"], 
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame

def download_csv():
    session = st.session_state
    pandashelper.download_csv(session["file_name"], session["DataFrame"])

def download_excel():
    session = st.session_state
    pandashelper.download_excel(session["file_name"], session["DataFrame"])

def execute():  
    st.set_page_config(
        page_title="Quantities",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header("🧮 Model Quantities")
    session = st.session_state

    if "IsDataFrameLoaded" not in session:
        initialize_session_state()
    if not session["IsDataFrameLoaded"]:
        load_data()
    if session["IsDataFrameLoaded"]:    
        tab1, tab2 = st.tabs(["Dataframe Utilities", "Quantities Review"])
        with tab1:
            # Dataframe Review            
            st.header("DataFrame Review")  
            st.write(session["DataFrame"])
            st.button("Download CSV", key="download_csv", on_click=download_csv)
            st.button("Download Excel", key="download_excel", on_click=download_excel)
        with tab2:
            row2col1, row2col2 = st.columns(2)
            with row2col1:
                class_selector = st.selectbox("Select Class", session["Classes"], key="class_selector")
                session["filtered_frame"] = pandashelper.filter_dataframe_per_class(
                    session["DataFrame"], session["class_selector"]
                )
                session["qtos"] = pandashelper.get_qsets_columns(session["filtered_frame"])

                if session["qtos"]:
                    qto_selector = st.selectbox("Select Quantity Set", session["qtos"], key='qto_selector')
                    quantities = pandashelper.get_quantities(session["filtered_frame"], session["qto_selector"])
                    quantities.insert(0, "Count")  # Add "Count" as an option
                    st.selectbox("Select Quantity", quantities, key="quantity_selector")
                    st.radio('Split per', ['Level', 'Type'], key="split_options")
                else:
                    st.warning("No Quantities to Look at!")
                    st.selectbox("Select Quantity", ["Count"], key="quantity_selector")
                    st.radio('Split per', ['Level', 'Type'], key="split_options")

            # Draw Frame
            with row2col2: 
                if session.get("quantity_selector") == "Count":
                    total = pandashelper.get_total(session["filtered_frame"])
                    st.write(f"The total number of {session['class_selector']} is {total}")
                else:
                    st.subheader(f"{session['class_selector']} - {session['quantity_selector']}")
                    graph = graph_maker.load_graph(
                        session["filtered_frame"],
                        session["qto_selector"],
                        session["quantity_selector"],
                        session["split_options"],                                
                    )
                    st.plotly_chart(graph)
    else: 
        st.header("Step 1: Load a file from the Home Page")
        
if __name__ == "__main__":
    execute()
