import requests
import streamlit as st
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Hybrid RAG Assistant",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Spotify Architecture Assistant")
st.caption(
    "Ask questions about the Spotify-like web application architecture. "
    "Answers are retrieved from a PDF knowledge base and knowledge graph."
)

question = st.text_area(
    "Enter your question",
    placeholder="Example: Which service handles recommendations?",
    max_chars=1000,
)

if st.button("Ask Question", type="primary"):
    if not question or len(question.strip()) < 3:
        st.warning("Please enter a meaningful question.")
    else:
        with st.spinner("Retrieving evidence and generating an answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/retrieve",
                    json={"question": question.strip()},
                    timeout=90,
                )

                if response.status_code == 200:
                    result = response.json()

                    if result["status"] == "answered":
                        st.subheader("Answer")
                        st.write(result["answer"])
                    elif result["status"] == "needs_clarification":
                        st.warning(result["answer"])
                    else:
                        st.info(result.get("message", "No answer returned."))

                    with st.expander("View evaluation details"):
                        st.json(result.get("evaluation", {}))

                else:
                    st.error(
                        f"API returned HTTP {response.status_code}: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI. Start the backend "
                    "in another terminal and try again."
                )
            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")
            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")