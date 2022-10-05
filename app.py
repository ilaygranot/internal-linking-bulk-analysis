import pandas as pd
import streamlit as st
import csv
import time
import re

def convert_df_cluster(df_cluster):
 return df_cluster.to_csv().encode('utf-8')

 # Handle Download Button State
can_download = False
csv = None
df_cluster = None
uploaded_df_cluster = None
df_xpath = None
uploaded_df_xpath = None
df_cluster_2 = None
kwlistdata = []
bloglistdata = []
outputcsvData = []

tab1, tab2, tab3 = st.tabs(["Manual", "Bulk", "About"])


with tab1:
    st.title("Internal Linking Explorer")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_df_cluster = st.file_uploader("upload your own data here", "csv")
        if uploaded_df_cluster is not None:
            df_cluster = pd.read_csv(uploaded_df_cluster)
    with col2:
        uploaded_df_xpath = st.file_uploader("upload data from screaming frog 🐸", "csv")
        if uploaded_df_xpath is not None:
            df_xpath = pd.read_csv(uploaded_df_xpath)
    # Generate Interactive Form
    with st.form("form"):
        # Ask for user input
        col1, col2 = st.columns(2)
        with col1:
            target_page = st.text_input('Target Page') # Create variable for target page
        with col2:
            target_kw = st.text_input('Target Keywords') # Create variable for target keyword
        # Submit button
        submitted = st.form_submit_button("Apply")
        if submitted:
            if uploaded_df_cluster is None or uploaded_df_xpath is None:
                st.write('Please upload both files first!')
            else:
                # Simple validation
                if target_page == '':
                    st.write('Don\'t forget the target_page!')
                elif target_kw == '':
                    st.write('Don\'t forget the target_kw!')
                else:
                    # rename columns number 3 to "Body" and number 4 to "Text"
                    df_xpath.rename(columns={df_xpath.columns[3]: "Body" },inplace=True)
                    # rename columns number 4 to "Text"
                    df_xpath.rename(columns={df_xpath.columns[4]: "Text" },inplace=True)
                    # merge the two dataframes on address column base on right join and call it df_merge
                    df_merge = pd.merge(df_cluster, df_xpath, on="Address", how="right")
                    # Filter by Target Page & Target Keyword - See all pages that NOT link to target page AND CONTAIN the target keywords
                    lp_filter = ~df_xpath['Body'].str.contains(target_page)
                    kw_filter = df_xpath['Text'].str.contains(target_kw, case=False)
                    # create new df base on the filter and call it new_df
                    new_df = df_merge[lp_filter & kw_filter]
                    # create new column that contain the sentence that contain the target keyword
                    new_df['Context'] = new_df['Text'].apply(lambda x: re.findall(r'[^.]*' + target_kw + '[^.]*', x))
                    # count the amount of times that the target keyword appear in context
                    new_df['KW Count'] = new_df['Context'].apply(lambda x: len(x))
                    # Final Data
                    df_final = new_df.drop(columns=['Body','Status Code', 'Status', 'Text'])
                    # Preview Data
                    st.dataframe(df_final)
                    st.write(len(df_final))
                    # Generate CSV
                    csv = convert_df_cluster(df_final)
                    # Replace all non-ascii characters with the matching ascii character
                    csv = csv.decode('ascii', 'ignore').encode('ascii')
                    can_download = True
    # Show CSV Download Button
    if can_download and csv is not None:
        st.download_button("Press to Download",csv,"file.csv","text/csv",key='download-csv')

with tab2:
    st.title("Internal Linking Explorer")
    #Time script
    start_time = time.time()
    col1, col2 = st.columns(2)
    with col1:
        uploaded_bloglistdf = st.file_uploader("upload urls with body html from screaming frog", "csv")
        if uploaded_bloglistdf is not None:
            bloglistdf = pd.read_csv(uploaded_bloglistdf, encoding="utf8")
            # drop columns "Status Code", "Status" and "Text 1"
            bloglistdf = bloglistdf.drop(columns=["Status Code", "Status"])
            # convert bloglistdf to list 
            bloglistdata = list(bloglistdf.values.tolist())
    with col2:
        uploaded_kwlistdata = st.file_uploader("upload list of urls with target kw", "csv")
        if uploaded_kwlistdata is not None:
            kwlistdata = pd.read_csv(uploaded_kwlistdata, encoding="utf8", header=None ).values.tolist()

    #define output csv content
    
    for j in kwlistdata:
        for i in bloglistdata:
            sourcePage = i[0]
            body1 = i[1]
            targetPage = j[0]
            targetKeyword = j[1]
            body_lower = body1.lower()
            if targetKeyword in body_lower: #keyword
                if targetPage not in body_lower: #url
                    text1 = i[2]
                    # apply lambada on str
                    context = re.findall(r'[^.]*' + targetKeyword + '[^.]*', text1)
                    templist = [targetKeyword, targetPage, sourcePage, context] #keyword,url,source,context
                    outputcsvData.append(templist)

    outputcsvData = pd.DataFrame(outputcsvData, columns=["Target Keyword", "Target Page", "Source Page", "Context" ])
    # Create DataFrame from outputcsvData
    outputcsvData = pd.DataFrame(outputcsvData)
    # Generate CSV and name the headers
    csv = convert_df_cluster(outputcsvData)
    # Replace all non-ascii characters with the matching ascii character
    csv = csv.decode('ascii', 'ignore').encode('ascii')
    can_download = True
    # Show CSV Download Button
    if can_download and csv is not None:
        st.download_button("Press to Download",csv,"file.csv","text/csv",key='download-csv_2')

