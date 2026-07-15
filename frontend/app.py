import requests
import streamlit as st
import pandas as pd
from PIL import Image

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="LedgerLens",
    page_icon="📄",
    layout="wide"
)

st.title("📄 LedgerLens")
st.subheader("AI Invoice Extraction")

tab1, tab2 = st.tabs([
    "Upload Invoice",
    "Documents"
])

#############################################
# Upload Tab
#############################################

with tab1:

    uploaded_file = st.file_uploader(
        "Choose Invoice",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Invoice",
            use_container_width=True
        )

        if st.button("Upload Invoice"):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(
                f"{API_URL}/ingest",
                files=files
            )

            if response.status_code == 200:

                data = response.json()

                st.success(data["message"])

                st.session_state["document_id"] = data["document"]["id"]

            else:

                st.error(response.text)

        if "document_id" in st.session_state:

            if st.button("Extract Invoice"):

                response = requests.post(
                    f"{API_URL}/extract/{st.session_state['document_id']}"
                )

                if response.status_code == 200:

                    result = response.json()["data"]

                    st.success("Extraction Completed")

                    # st.json(result)
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Vendor", result.get("vendor", ""))
                        st.metric("Invoice No", result.get("invoice_number", ""))
                        st.metric("Date", result.get("invoice_date", ""))

                    with col2:
                        st.metric("Subtotal", result.get("subtotal", ""))
                        st.metric("Tax", result.get("tax", ""))
                        st.metric("Total", result.get("total", ""))

                    st.progress(min(max(result.get("confidence", 0), 0), 1))
                    st.write(f"Confidence: {result.get('confidence', 0):.2%}")

                else:

                    st.error(response.text)

#############################################
# Documents Tab
#############################################

with tab2:

    if st.button("Refresh"):

        response = requests.get(
            f"{API_URL}/documents"
        )

        if response.status_code == 200:

            documents = response.json()

            if len(documents) == 0:

                st.warning("No Documents Found")

            else:

               df = pd.DataFrame(documents)

               df = df.drop(
                    columns=[
                        "image_path",
                        "extracted_json",
                        "created_at",
                        "updated_at"
                    ],
                    errors="ignore"
                )

            st.dataframe(
                        df,
                        width='stretch',
                        hide_index=True
                    )