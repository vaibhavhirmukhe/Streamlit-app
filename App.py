import streamlit as st
import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable,DatasetDriftMetric, DatasetSummaryMetric, ColumnSummaryMetric,ColumnValueListMetric, ColumnDriftMetric, ColumnDistributionMetric, DatasetMissingValuesMetric
from evidently import ColumnMapping
import streamlit.components.v1 as components
import os


st.set_page_config(layout="wide", page_title="Reports")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


def read_html_report(report_filename):
    with open(report_filename, "r", encoding="utf-8") as f:
        return f.read()

@st.cache_data
def load_data(filename): 
    df = pd.read_csv(filename, low_memory=False)
    return df


def impute_nan(df):
    
    default_datetime = pd.to_datetime("01/01/1900 00:00:00.000", format="%d/%m/%Y %H:%M:%S.%f")
    
    for col in df.columns:
        
        if df[col].dtype == "object":
            df[col] = df[col].fillna("missing")
            
        elif (df[col].dtype == "int64") or (df[col].dtype == "float64"):
            df[col] = df[col].fillna(-9999.01)
            
        elif df[col].dtype == "datetime64[ns]":
            df[col] = df[col].fillna(default_datetime)
            
    return df



def get_report(selected_metric, df):

    if selected_metric == "Dataset Summary Metric":
        report = Report(
            metrics=[DatasetSummaryMetric()]
        )
    
    elif selected_metric == "Dataset Missing Values Metric":
        report = Report(
            metrics=[DatasetMissingValuesMetric()]
        )
        
    elif selected_metric == "Column Summary Metric":

        column = st.sidebar.selectbox('Select Column', df.columns)
        
        report = Report(
            metrics=[ColumnSummaryMetric(column_name=column)]
        )

    elif selected_metric == "Column Drift Metric":

        column = st.sidebar.selectbox('Select Column', df.columns)

        report = Report(
            metrics=[ColumnDriftMetric(column_name=column)]
        )

    elif selected_metric == "Column Distribution Metric":

        column = st.sidebar.selectbox('Select Column', df.columns)

        report = Report(
            metrics=[ColumnDistributionMetric(column_name=column)]
        )

    elif selected_metric == "Data Drift Table":

        report = Report(
            metrics=[DataDriftTable(cat_stattest='psi')]
        )
    
    
    return report


df = load_data('Data_for_DB_update.csv')

metric_list = ["Dataset Summary Metric","Dataset Missing Values Metric","Data Drift Table", "Column Summary Metric", "Column Drift Metric", "Column Distribution Metric"]

selected_metric = st.sidebar.selectbox(
        label="📈 Select Report", options=metric_list
)

st.header(f"Report : {selected_metric}")

if selected_metric == "Data Drift Table" :

    df2 = impute_nan(df).copy()

    reference_data = df2[:2000]
    current_data = df2[2000:]

else:
    reference_data = df[:2000]
    current_data = df[2000:]


report = get_report(selected_metric, df)

with st.spinner("Generating Report..."):
    report.run(reference_data=reference_data, current_data=current_data)
    

metric_file_name = f'{selected_metric}.html'
report_path = os.path.join("Metrics", metric_file_name)
report.save_html(report_path)

current_directory = os.getcwd()

report_filename = os.path.join(current_directory, report_path)

report_html = read_html_report(report_filename)

# Display the HTML report using components
components.html(report_html, width=1000, height=1200, scrolling=True)


