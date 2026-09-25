import json
import os
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=api_key)

cache_stats = {"hits": 0, "misses": 0, "tokens_saved": 0}


# ===== SWAP THIS BLOCK FOR YOUR ORGANISATION =====
ORG_FACTS = """
MEMBERSHIP: free to join at codingblackfemales.com/join-us
Members get courses, programmes, events, partner opportunities
and the job board.

BOOTCAMPS at codingblackfemales.com/academy
- AWS re/Start: become a Cloud Engineer
- Entry To Tech: become a Software Engineer
- Advanced Full Stack: become a Senior Software Engineer,
  for career returners or experienced professionals

EVENTS: around two events a month, announced on Meetup and
Eventbrite, both linked from codingblackfemales.com/events

CONTACT: codingblackfemales.com/contact

YOU DO NOT KNOW: the mentorship programme, deadlines,
bootcamp dates, or specific event dates. Say so and escalate.
"""
EXAMPLES = """
Three examples of the tone and length expected.

Member: How do I join?
{
  "intent": "membership",
  "response_text": "You can join free at codingblackfemales.com/join-us. That gives you courses, events, partner opportunities and the job board.",
  "suggested_actions": ["Sign up at codingblackfemales.com/join-us"],
  "confidence": 0.95,
  "needs_human": false
}

Member: I have never coded before. Which bootcamp?
{
  "intent": "bootcamps",
  "response_text": "Entry To Tech is built for complete beginners and trains you as a Software Engineer.",
  "suggested_actions": ["Read about Entry To Tech at codingblackfemales.com/academy"],
  "confidence": 0.9,
  "needs_human": false
}

Member: When does the next bootcamp start?
{
  "intent": "bootcamps",
  "response_text": "I do not have the start dates. Please email itiolacaroline@yahoo.com and someone will come back to you.",
  "suggested_actions": ["Email itiolacaroline@yahoo.com"],
  "confidence": 0.9,
  "needs_human": true
}
"""

# ===== END OF SWAPPABLE BLOCK =====

SYSTEM_PROMPT = """You are the support assistant for Coding
Black Females. Answer only from the facts below. If the answer
is not there, say so and set needs_human to true. Never guess.
""" + ORG_FACTS + EXAMPLES + """
Reply with this JSON and nothing else:
Keep response_text to two sentences. Give one or two actions.

{
  "intent": "membership|events|bootcamps|mentorship|general",
  "response_text": "your reply to the member",
  "suggested_actions": ["action one", "action two"],
  "confidence": 0.9,
  "needs_human": false
}

When needs_human is true, include this in response_text:
"Please email itiolacaroline@yahoo.com and someone will come back to you."

Reason inside <thinking> tags first. Be warm.
"""

def get_response(question, max_retries=3):
    for attempt in range(max_retries):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=[
                {
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
                }
            ],


            messages=[{"role": "user", "content": question}],
        )
        read = getattr(response.usage,"cache_read_input_tokens", 0)
        if read:
            cache_stats["hits"] += 1
            cache_stats["tokens_saved"] += read
        else:
            cache_stats["misses"] += 1
        
        raw = response.content[0].text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            print("Attempt", attempt + 1, "gave invalid JSON. Retrying.")
    return None


if __name__ == "__main__":
    result = get_response("How do I get matched with a mentor?")
    if result:
        print(result["response_text"])
        print("needs_human:", result["needs_human"])
    else:
        print("No valid response after 3 attempts.")
    print("cache:", cache_stats)



