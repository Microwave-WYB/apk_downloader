import zipfile
import io
import streamlit as st
from apk_downloader import download_single


if __name__ == "__main__":
    st.set_page_config(page_title="APKPure Downloader")
    st.title(
        "APK Pure Downloader",
        help="The first result in APKPure search will be downloaded.",
    )
    single_tab, multi_tab = st.tabs(["Single", "Multiple"])
    with single_tab:
        single_download_form = st.form("single_download")
        with single_download_form:
            keywords = st.text_input("Enter search keywords")

        if single_download_form.form_submit_button("Submit"):
            with st.spinner("Preparing download..."):
                file = download_single(keywords)
                if file:
                    st.download_button("Download APK", file, f"{keywords}.apk")
    with multi_tab:
        multi_download_form = st.form("multi_download")
        with multi_download_form:
            keywords = st.text_area("Enter search keywords, separated by ';'")
            keywords_list = keywords.split(";")
        if multi_download_form.form_submit_button("Submit"):
            progress_bar = st.progress(0)
            # Create a BytesIO object to store the ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for i, keywords in enumerate(keywords_list):
                    progress_bar.progress(
                        (i) / len(keywords_list),
                        f"Preparing download: {keywords}",
                    )
                    file_pointer = download_single(keywords)
                    if file_pointer:
                        # Generate a file name based on the keywords
                        file_name = f"{keywords}.apk"
                        # Read the content from the file pointer
                        file_content = file_pointer.read()
                        zip_file.writestr(file_name, file_content)
                progress_bar.progress(1.0, "APKs are ready")

            # Seek the buffer to the beginning after writing
            zip_buffer.seek(0)

            # Provide a download button for the ZIP file
            st.download_button(
                label="Download All APKs",
                data=zip_buffer,
                file_name="APKs.zip",
                mime="application/zip",
            )
