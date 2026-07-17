import streamlit as st


def show_loader(message="🤖 Processing invoice... Please wait..."):
    placeholder = st.empty()

    placeholder.markdown(
        f"""
    <style>
    .loader-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(255,255,255,0.75);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 999999;
    }}

    .spinner {{
        border: 8px solid #f3f3f3;
        border-top: 8px solid #4CAF50;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        animation: spin 1s linear infinite;
        margin: auto;
    }}

    .loader-text {{
        margin-top: 20px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }}

    @keyframes spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    </style>

    <div class="loader-overlay">
        <div>
            <div class="spinner"></div>
            <div class="loader-text">{message}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    return placeholder
