import requests
import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="LedgerLens", page_icon="📄", layout="wide")

st.title("📄 LedgerLens")
st.subheader("AI Invoice Extraction")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Upload Invoice", "Documents", "Manual Review", "Dashboard"]
)

#############################################
# Upload Tab
#############################################

with tab1:

    uploaded_file = st.file_uploader("Choose Invoice", type=["jpg", "jpeg", "png"])

    if uploaded_file:

        left, right = st.columns([1, 2])

        with left:
            st.subheader("Invoice Preview")

            st.image(uploaded_file, width=220)

        with right:

            if st.button("Upload Invoice"):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                progress = st.progress(0)

                with st.spinner("🤖 Processing invoice..."):

                    progress.progress(30)

                    response = requests.post(f"{API_URL}/ingest", files=files)

                    progress.progress(100)

                progress.empty()

                if response.status_code == 200:

                    data = response.json()

                    st.success(data["message"])

                    st.session_state["document_id"] = data["document"]["id"]

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

                else:

                    st.error(response.text)


#############################################
# Documents Tab
#############################################

with tab2:

    st.header("Documents")

    col1, col2 = st.columns(2)

    with col1:
        vendor = st.text_input("Vendor")

    with col2:
        filename = st.text_input("Filename")

    col3, col4 = st.columns(2)

    with col3:
        status = st.selectbox("Status", ["", "uploaded", "processed", "approved"])

    with col4:
        page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)

    col5, col6 = st.columns(2)

    with col5:
        sort_by = st.selectbox(
            "Sort By", ["id", "vendor", "filename", "invoice_date", "total"]
        )

    with col6:
        order = st.selectbox("Order", ["desc", "asc"])

    page = st.number_input("Page", min_value=1, value=1, step=1)

    params = {
        "vendor": vendor,
        "filename": filename,
        "status": status,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "order": order,
    }

    response = requests.get(f"{API_URL}/documents", params=params)

    if response.status_code == 200:

        result = response.json()

        st.write(f"Total Records: {result['total']}")
        st.write(f"Page: {result['page']} of {result['total_pages']}")

        documents = result["data"]

        if documents:

            df = pd.DataFrame(documents)

            display_columns = [
                "id",
                "filename",
                "vendor",
                "invoice_number",
                "invoice_date",
                "currency",
                "total",
                "overall_confidence",
                "status",
            ]

            display_columns = [c for c in display_columns if c in df.columns]

            st.dataframe(df[display_columns], use_container_width=True, hide_index=True)

        else:
            st.warning("No Documents Found")

#############################################
# Manual Review
#############################################

with tab3:

    st.header("Manual Review")

    document_id = st.number_input("Document ID", min_value=1, step=1)

    if st.button("Load Document"):

        response = requests.get(f"{API_URL}/document/{document_id}")

        if response.status_code == 200:

            st.session_state["review_doc"] = response.json()

        else:

            st.error("Document Not Found")

    if "review_doc" in st.session_state:

        doc = st.session_state["review_doc"]

        vendor = st.text_input("Vendor", value=doc.get("vendor") or "")

        invoice_number = st.text_input(
            "Invoice Number", value=doc.get("invoice_number") or ""
        )

        invoice_date = st.text_input(
            "Invoice Date", value=doc.get("invoice_date") or ""
        )

        currency = st.text_input("Currency", value=doc.get("currency") or "")

        subtotal = st.number_input("Subtotal", value=float(doc.get("subtotal") or 0))

        tax = st.number_input("Tax", value=float(doc.get("tax") or 0))

        total = st.number_input("Total", value=float(doc.get("total") or 0))

        confidence = st.slider(
            "Confidence", 0.0, 1.0, float(doc.get("overall_confidence") or 0)
        )

        status = st.selectbox(
            "Status",
            ["uploaded", "processed", "reviewed", "approved"],
            index=(
                0
                if doc.get("status") is None
                else ["uploaded", "processed", "reviewed", "approved"].index(
                    doc.get("status")
                )
            ),
        )

        st.subheader("Processed Invoice")

        image_url = f"{API_URL}/processed/{document_id}"

        st.image(image_url, caption="Watermarked Invoice", use_container_width=True)

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
                "status": status,
            }

            response = requests.put(f"{API_URL}/document/{document_id}", json=payload)

            if response.status_code == 200:

                st.success("Document Updated Successfully")

                st.session_state.pop("review_doc")

            else:

                st.error(response.text)

#############################################
# Dashboard
#############################################

with tab4:

    st.header("📊 LedgerLens Dashboard")

    if st.button("🔄 Refresh Dashboard"):

        st.rerun()

    ####################################################
    # Dashboard Summary
    ####################################################

    response = requests.get(f"{API_URL}/dashboard")

    if response.status_code != 200:

        st.error("Unable to load dashboard")

    else:

        dashboard = response.json()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📄 Documents", dashboard["total_documents"])

        with col2:
            st.metric("📤 Uploaded", dashboard["uploaded"])

        with col3:
            st.metric("✅ Processed", dashboard["processed"])

        with col4:
            st.metric("✔ Approved", dashboard["approved"])

        st.divider()

        col5, col6, col7 = st.columns(3)

        with col5:
            st.metric("Today's Uploads", dashboard["today_uploads"])

        with col6:
            st.metric("Average Confidence", f"{dashboard['average_confidence']:.2f}")

        with col7:
            st.metric("Invoice Amount", f"₹ {dashboard['total_invoice_amount']:.2f}")

    ####################################################
    # Charts
    ####################################################

    left, right = st.columns(2)

    ########################################
    # Pie Chart
    ########################################

    with left:

        response = requests.get(f"{API_URL}/dashboard/status")

        if response.status_code == 200:

            status = response.json()

            if status:

                labels = [x["status"] for x in status]

                values = [x["count"] for x in status]

                fig, ax = plt.subplots(figsize=(3, 3))

                ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)

                ax.set_title("Document Status", fontsize=12)

                st.pyplot(fig, use_container_width=False)

            else:

                st.info("No status data available.")

    ########################################
    # Bar Chart
    ########################################

    with right:

        response = requests.get(f"{API_URL}/dashboard/daily")

        if response.status_code == 200:

            daily = response.json()

            if daily:

                dates = [x["date"] for x in daily]

                counts = [x["count"] for x in daily]

                fig, ax = plt.subplots(figsize=(5, 3))

                ax.bar(dates, counts)

                ax.set_title("Daily Uploads", fontsize=12)

                ax.set_xlabel("Date")

                ax.set_ylabel("Documents")

                plt.xticks(rotation=45)

                st.pyplot(fig, use_container_width=False)

            else:

                st.info("No upload history available.")
