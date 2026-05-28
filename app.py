from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS

import os
import re

from properties import properties

# LOAD ENVIRONMENT VARIABLES
load_dotenv()

# GROQ CLIENT
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# EMI FUNCTION
def calculate_emi(principal, rate, years):
    monthly_rate = rate / 12 / 100
    months = years * 12

    emi = (
        principal * monthly_rate * (1 + monthly_rate) ** months
    ) / (
        (1 + monthly_rate) ** months - 1
    )

    return round(emi, 2)

# WEB SEARCH FUNCTION
def search_web(query):
    results_text = []

    with DDGS() as ddgs:
        results = ddgs.text(
            query,
            max_results=5
        )

        for result in results:
            results_text.append(result["body"])

    return "\n".join(results_text)

# SYSTEM PROMPT
system_prompt = f"""
You are an AI Real Estate Assistant.

Use this property data:
{properties}

You help customers:
- find apartments
- answer real estate questions
- explain pricing
- suggest properties

Answer professionally.
"""

# MEMORY
messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

print("AI Real Estate Agent Started!")
print("Type 'exit' to quit.\n")

# MAIN LOOP
while True:

    user_input = input("Customer: ")

    # EXIT
    if user_input.lower() == "exit":
        break

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

            print(f"\nAgent: Monthly EMI is ₹{emi}\n")

        else:

            print("""
Agent: Please provide the following details for EMI calculation:

1. Loan amount
2. Interest rate
3. Loan tenure in years

Example:
EMI for 40 lakhs at 8.5% for 20 years
""")

        continue

    # SEARCH INTERNET
    web_data = search_web(user_input)

    # USER MESSAGE
    messages.append({
        "role": "user",
        "content": f"""
User Question:
{user_input}

Internet Data:
{web_data}
"""
    })

    # AI RESPONSE
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    ai_reply = response.choices[0].message.content

    # PRINT RESPONSE
    print("\nAgent:", ai_reply, "\n")

    # SAVE MEMORY
    messages.append({
        "role": "assistant",
        "content": ai_reply
    })