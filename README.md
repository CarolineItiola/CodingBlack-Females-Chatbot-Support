# CBF Support Chatbot

A support chatbot for Coding Black Females, built live in a workshop
during CBF Global Tech Conference Fest 2026. 

Live app - https://codingblack-females-chatbot-support-hywo4jhqdvzyjdm8bbtgeq.streamlit.app/

The session went from an empty file to a
deployed URL.

This repository holds the finished code, the reasoning behind each
stage, and what to change to point it at your own organisation.

The chatbot answers questions on membership, the bootcamps and events,
and says so plainly when it does not know rather than filling the gap.

Built with the Claude API and Streamlit.

---

## The problem this solves

Ask a language model about an organisation it has never read about
and it will answer confidently anyway.

On the first run of this build I asked how to join Coding Black
Females. It said:

> "They often have Slack channels or other community platforms for
> members."

CBF announce their events on Meetup and Eventbrite, which is written
plainly on their website. The model had not read it. It filled a gap
with something that sounded reasonable.

This is the failure I designed against, and you do not fix it by
asking the model to be more accurate. I fixed it by giving it a fixed
set of facts, telling it explicitly what it does not know, and making
it say so.

---

## What it does

- Answers only from a defined set of facts about CBF
- Returns structured JSON rather than prose, so the reply is a value
  the code can act on rather than a message a person has to read
- Validates its own output and retries up to three times when the
  format is wrong
- Escalates to a human, with an email address, when the question
  falls outside what it knows
- Caches the unchanging part of the prompt to reduce cost

---

## Running it

This is the finished version of what was built in the session. Work
through it at your own pace alongside the slides and recording.

```
git clone <this repo>
cd cbf-support-chatbot
pip install anthropic python-dotenv streamlit
```

Create a `.env` file containing one line:

```
ANTHROPIC_API_KEY=sk-ant-your-key
```

Then:

```
python chatbot.py      # runs one question in the terminal
streamlit run app.py   # opens the chat interface
```

An Anthropic API key is free to create at console.anthropic.com, but
the account needs credits before the key will work.

---

## How it was built

Seven stages, each ending in something that runs.

**A. First call.** One message to the API. It answers, but in prose
the code cannot read, with content that cannot be traced.

**B. Facts and shape.** A system prompt carrying real CBF information,
a required JSON schema, and an explicit list of what the bot does not
know so that it escalates instead of guessing.

**C. Few-shot examples.** Three worked answers, including one that
admits a gap. This is not fixing correctness, which stage B handled.
It pins down tone and length, and shows the model what escalating
looks like rather than only describing it.

**D. Validation and retry.** The first time the code tries to read the
reply rather than print it, `json.loads` fails. The JSON is fine, it
is just not at the start of the string, because the model reasons in
`<thinking>` tags first. The fix slices from the first brace to the
last and retries up to three times, returning `None` honestly rather
than crashing.

**E. Prompt caching.** The facts and examples are identical on every
call, so they are marked for caching and paid for once.

**F. The interface.** About thirty lines of Streamlit. It is short
precisely because the output is structured: it reads fields off a
dictionary rather than parsing text.

**G. Deployment.** The key has to work in two places, since there is
no `.env` on Streamlit Cloud. The code tries `st.secrets` first and
falls back to `.env` locally, so the same file runs in both.

---

## Make it your own

Two things change. Everything else stays as it is.

**`ORG_FACTS`** holds everything the bot is allowed to say. Replace it
with your own organisation's information, and keep the
`YOU DO NOT KNOW` section, because that is what turns guessing into
escalating.

**`EXAMPLES`** holds three worked answers. Replace them with replies
in your own voice, and keep one that escalates.

Both sit inside a clearly marked block at the top of `chatbot.py`.

The schema, the retry loop, the caching, the escalation and the
interface do not need touching.

---

## Two things worth knowing

**Prompt caching has a minimum length, and fails silently below it.**
Anthropic will not cache a prompt shorter than 1,024 tokens for Claude
Sonnet. This system prompt is around eight hundred, so `cache_control`
is accepted and quietly ignored, with no error and no warning. The
only way to tell is to check `cache_read_input_tokens` in the response.

**The model does not return exactly what you asked for.** It was told
to reply with JSON and nothing else. It replied with reasoning, then a
markdown fence, then the JSON. Anything reading that output has to
handle it, which is what the retry loop exists for.

---

## Built in one hour and thirty minutes

This was a live build delivered in one hour and thirty minutes. That sets the scope.
What follows is what the hour did not allow, rather than what was
overlooked.

**No memory between sessions.** Streamlit holds the conversation in
session state, so a refresh clears it. Persisting it needs a database,
which is a workshop of its own.

**Mentorship questions always escalate.** This one is not about time.
CBF do not publish the details, so the bot has no reliable source and
says so. That is the escalation path working exactly as designed.

---

## What I would do next

**A test suite** covering the edge cases: very short messages, several
questions at once, off topic requests, and anything the facts block
does not cover. The escalation path is the one that most needs proving.

Delivered by Caroline Itiola for Coding Black Females, September 2026.

The two findings above came out of building this in front of a room,
where failures happen in public and get explained rather than quietly
fixed. That is the honest case for live builds over polished demos.
