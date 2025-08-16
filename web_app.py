import streamlit as st
import pandas as pd
import io
from keywordGen import  read_keyword_input_file


st.title("📊 Amazon Campaign Excel Converter")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    st.info("📂 File uploaded successfully. Starting conversion...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Fake progress for UI
    for percent in range(0, 101, 25):
        progress_bar.progress(percent)
        status_text.text(f"Processing... {percent}%")
        import time; time.sleep(0.3)

    # Process file in memory
    final_df = read_keyword_input_file(uploaded_file)

    # Convert to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        final_df.to_excel(writer, index=False)
    output.seek(0)

    st.success("✅ Conversion complete! Download your file below 👇")

    st.download_button(
        label="📥 Download Converted File",
        data=output,
        file_name="converted_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
