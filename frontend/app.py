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

tab1, tab2, tab3 = st.tabs([
    "Upload Invoice",
    "Documents",
    "Manual Review"
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
            
#############################################
# Manual Review
#############################################

with tab3:

    st.header("Manual Review")

    document_id = st.number_input(
        "Document ID",
        min_value=1,
        step=1
    )

    if st.button("Load Document"):

        response = requests.get(
            f"{API_URL}/document/{document_id}"
        )

        if response.status_code == 200:

            st.session_state["review_doc"] = response.json()

        else:

            st.error("Document Not Found")

    if "review_doc" in st.session_state:

        doc = st.session_state["review_doc"]

        vendor = st.text_input(
            "Vendor",
            value=doc.get("vendor") or ""
        )

        invoice_number = st.text_input(
            "Invoice Number",
            value=doc.get("invoice_number") or ""
        )

        invoice_date = st.text_input(
            "Invoice Date",
            value=doc.get("invoice_date") or ""
        )

        currency = st.text_input(
            "Currency",
            value=doc.get("currency") or ""
        )

        subtotal = st.number_input(
            "Subtotal",
            value=float(doc.get("subtotal") or 0)
        )

        tax = st.number_input(
            "Tax",
            value=float(doc.get("tax") or 0)
        )

        total = st.number_input(
            "Total",
            value=float(doc.get("total") or 0)
        )

        confidence = st.slider(
            "Confidence",
            0.0,
            1.0,
            float(doc.get("overall_confidence") or 0)
        )

        status = st.selectbox(
            "Status",
            [
                "uploaded",
                "processed",
                "reviewed",
                "approved"
            ],
            index=0
            if doc.get("status") is None
            else [
                "uploaded",
                "processed",
                "reviewed",
                "approved"
            ].index(doc.get("status"))
        )

        if st.button("Save Changes"):

            payload = {

                "vendor": vendor,

                "invoice_number": invoice_number,

                "invoice_date": invoice_date,

                "currency": currency,

                "subtotal": subtotal,

                "tax": tax,

                "total": total,

                "overall_confidence": confidence,

                "status": status
            }

            response = requests.put(

                f"{API_URL}/document/{document_id}",

                json=payload

            )

            if response.status_code == 200:

                st.success("Document Updated Successfully")

                st.session_state.pop("review_doc")

            else:

                st.error(response.text)