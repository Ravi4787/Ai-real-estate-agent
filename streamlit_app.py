import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS
import os
import re
import pandas as pd
from datetime import datetime

from properties import properties

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Real Estate Agent",
    page_icon="🏠",
    layout="wide"
)

# ---------------- LOAD ENV ----------------
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------- FUNCTIONS ----------------
def search_web(query):
    results_text = []

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

        for result in results:
            results_text.append(result["body"])

    return "\n".join(results_text)


def calculate_emi(principal, rate, years):
    monthly_rate = rate / 12 / 100
    months = years * 12

    emi = (
        principal * monthly_rate * (1 + monthly_rate) ** months
    ) / (
        (1 + monthly_rate) ** months - 1
    )

    return round(emi, 2)


# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🏠 AI Real Estate Assistant")
st.sidebar.success("Smart Property Advisor AI")

st.sidebar.markdown("""
### Features
- 🏘 Property Search  
- 📊 Market Analysis  
- 💰 EMI Calculator  
- 📍 Location Insights  
- 🤖 AI Chat Assistant  
""")

# ---------------- LEAD FORM ----------------
st.sidebar.markdown("### 📞 Book a Site Visit")

lead_name = st.sidebar.text_input("Your Name")
lead_phone = st.sidebar.text_input("Phone Number")

lead_budget = st.sidebar.selectbox(
    "Budget",
    ["Below 50L", "50L - 1Cr", "1Cr - 5Cr", "5Cr+"]
)

if st.sidebar.button("Submit Lead"):

    lead_data = {
        "Name": lead_name,
        "Phone": lead_phone,
        "Budget": lead_budget,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.DataFrame([lead_data])

    df.to_csv(
        "leads.csv",
        mode="a",
        header=not os.path.exists("leads.csv"),
        index=False
    )

    st.sidebar.success("Lead saved successfully!")

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.quick_question = ""
    st.rerun()


# ---------------- HEADER ----------------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.title("🏠 AI Real Estate Agent")

    st.markdown("""
    ## Find Smart Real Estate Investments with AI

    ✅ Property Suggestions  
    ✅ Investment Insights  
    ✅ EMI Calculations  
    ✅ Market Trends  
    ✅ AI Guidance  
    """)

with col2:
    st.image(
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa",
        use_container_width=True
    )


# ---------------- PROPERTIES ----------------
st.subheader("🔥 Featured Properties")

cols = st.columns(2)

for i, prop in enumerate(properties):

    with cols[i % 2]:

        st.image(
            prop["image"],
            use_container_width=True
        )

        st.markdown(f"""
        ### 🏡 {prop['name']}
        📍 {prop['location']}  
        🏠 {prop['type']}  
        💰 {prop['price']}  
        📐 {prop['sqft']} sqft  
        """)

        brochure_file = prop["brochure"]

        with open(brochure_file, "rb") as file:

            st.download_button(
                label=f"📄 View {prop['name']} Brochure",
                data=file,
                file_name=brochure_file,
                mime="application/pdf",
                key=f"brochure_{prop['name']}"
            )


# ---------------- INVESTMENT SCORE ----------------
st.subheader("📈 Investment Score")

col1, col2, col3 = st.columns(3)

col1.metric("Hitech City", "9.2/10", "High Growth")
col2.metric("Gachibowli", "8.8/10", "Good ROI")
col3.metric("Kondapur", "8.5/10", "Rental Demand")


# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""


# ---------------- QUICK ACTIONS ----------------
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 2BHK under 50L"):
        st.session_state.quick_question = "Show me 2BHK apartments under 50 lakhs"

with col2:
    if st.button("📍 Hitech City investment"):
        st.session_state.quick_question = "Is Hitech City good for real estate investment?"

with col3:
    if st.button("💰 EMI calculation"):
        st.session_state.quick_question = "I need loan EMI calculation"


# ---------------- DISPLAY CHAT HISTORY ----------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- CHAT HEADING ----------------
st.markdown("## 🤖 Ask the AI Property Advisor")

st.write(
    "Ask about investment, EMI, properties, locations, or market trends."
)


# ---------------- CHAT INPUT ----------------
typed_question = st.chat_input("Ask anything about real estate...")

if typed_question:
    user_input = typed_question

elif st.session_state.quick_question:
    user_input = st.session_state.quick_question
    st.session_state.quick_question = ""

else:
    user_input = None


# ---------------- AI RESPONSE ----------------
if user_input:

    st.chat_message("user").write(user_input)

    # EMI FEATURE
    if "emi" in user_input.lower() or "loan" in user_input.lower():

        numbers = re.findall(r'\d+\.?\d*', user_input)

        if len(numbers) >= 3:

            principal = float(numbers[0])
            rate = float(numbers[1])
            years = int(float(numbers[2]))

            if "crore" in user_input.lower():
                principal *= 10000000

            elif "lakh" in user_input.lower() or "lakhs" in user_input.lower():
                principal *= 100000

            emi = calculate_emi(
                principal,
                rate,
                years
            )

            ai_reply = f"""
🏦 Loan EMI Details

💰 Loan Amount: ₹{principal:,.0f}  
📈 Interest Rate: {rate}%  
📅 Tenure: {years} years  

✅ Monthly EMI: ₹{emi:,.2f}
"""

        else:

            ai_reply = """
Please provide the following details for EMI calculation:

1. Loan amount  
2. Interest rate  
3. Loan tenure in years  

Example:  
EMI for 40 lakhs at 8.5% for 20 years
"""

    else:

        web_data = search_web(user_input)

        system_prompt = """
        You are an AI Real Estate Assistant.

        Give realistic answers only.
        Do NOT invent fake property data.

        Use web data if needed.
        Keep answers short and useful.
        """

        messages = [{"role": "system", "content": system_prompt}]

        messages += st.session_state.messages

        messages.append({
            "role": "user",
            "content": f"""
User Question:
{user_input}

Web Data:
{web_data}
"""
        })

        with st.spinner("AI is thinking... 🤖"):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )

            ai_reply = response.choices[0].message.content

    st.chat_message("assistant").markdown(
        f"### 🤖 AI Assistant\n\n{ai_reply}"
    )

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": ai_reply}
    )


# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🚀 AI Real Estate Agent | Built with Python + Streamlit + Groq")