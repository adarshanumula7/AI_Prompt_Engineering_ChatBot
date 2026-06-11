import panel as pn
from dotenv import load_dotenv
from groq import Groq
import os
import io, json

pn.extension()
load_dotenv(override=True)


API_KEY = os.getenv("GROQ_API_KEY")

# region helper methods
def get_response_from_messages(chat_history, model="llama-3.3-70b-versatile", temperature=0):
    messages = [
        {"role": "system", "content": system_prompt},
        *chat_history
    ]
    # print("Before Groq call")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    # print("After Groq call")
    return response.choices[0].message.content

def chat_callback(message, user, instance):
    try: 
        chat_history.append({"role": "user", "content": message})
        # print("Entered Chat Callback")
        # prompt = f"{system_prompt}\n\n" + "\n".join(chat_history)
        response = get_response_from_messages(chat_history, model=model_select.value, temperature=temperature.value)
        # print("Got response from get_response_from_messages")
        chat_history.append({"role": "assistant", "content": response})
        # print(chat_history)
        return response
    except Exception as e:
        print("ERROR: ", repr(e))
        raise

def generate_chat_json():
    json_str = json.dumps(chat_history, indent=2)
    return io.StringIO(json_str)

def generate_txt():
    text = ""

    for msg in chat_history:
        text += f"{msg['role'].capitalize()}:\n"
        text += f"{msg['content']}\n\n"

    return io.StringIO(text)

# endregion 

# region UI details
temperature = pn.widgets.FloatSlider(
    name="Temperature",
    start=0,
    end=2,
    step=0.1,
    value=0.7
)

model_select = pn.widgets.Select(
    name="Model",
    options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    value="llama-3.3-70b-versatile"
)

download_button = pn.widgets.FileDownload(
    filename="chat_history.txt",
    button_type="primary",
    label="Download Chat History",
    sizing_mode="stretch_width",
    callback=generate_txt
)
# endregion

# Initialize the GenAI client
client = Groq(api_key=API_KEY)

# region model definitions
system_prompt = """
You are an AI Prompt Engineering Assistant.

Your primary goal is to help users create clear, effective, and well-structured prompts for AI systems.

Core Principles:

1. Clarity and Specificity

* Encourage users to clearly describe their objective.
* Ask follow-up questions when requirements are ambiguous.
* Help users provide relevant context, constraints, examples, and desired output formats.

2. Give the Model Time to Think

* Break complex tasks into smaller steps.
* Encourage reasoning before conclusions.
* For analytical tasks, first identify the problem, then develop a solution, and finally produce the answer.

3. Structured Prompt Creation
   When a user's request lacks information, guide them to provide:

* Goal or objective
* Background/context
* Constraints
* Input data
* Expected output format
* Examples (if available)

4. Prompt Optimization
   Transform weak prompts into stronger prompts by:

* Removing ambiguity
* Adding context
* Defining output requirements
* Specifying evaluation criteria
* Breaking large tasks into subtasks

5. Response Style

* Be concise and professional.
* Explain why a prompt can be improved.
* Provide an improved prompt whenever possible.
* When information is missing, ask targeted questions instead of guessing.

6. Reasoning Framework
   For complex requests:
   Step 1: Understand the objective.
   Step 2: Identify missing information.
   Step 3: Propose a structured prompt.
   Step 4: Explain improvements.
   Step 5: Present the final optimized prompt.

Output Format:

### Analysis

Briefly explain weaknesses or missing information.

### Improved Prompt

Provide an optimized prompt ready for use.

### Additional Suggestions

Optional recommendations for achieving better AI results.

Never fabricate requirements that the user did not provide. If critical information is missing, ask clarifying questions first.
"""
# endregion

# Display chat interface
chat_ui = pn.chat.ChatInterface(
    callback=chat_callback,
    sizing_mode="stretch_width",
    height=600,
    message_params={
        "styles": {
            "background": "#2b2b2b",
            "color": "white"
        }
    }
)

chat_history = []  # This will store the conversation history

pn.extension(
    raw_css=[
        """
        button[aria-label="Toggle the Sidebar"]::after {
            display: none !important;
        }
        .message {
            color: black !important;
        }

        .message-content {
            color: black !important;
        }

        .message-content p,
        .message-content li,
        .message-content span {
            color: black !important;
        }
        """
    ]
)

header = pn.pane.Markdown("""
### AI Prompt Engineering Assistant

Create better AI prompts and get higher-quality responses.

This assistant helps you:
- Clarify goals and requirements
- Add missing context and constraints
- Define the desired output format
- Break complex tasks into smaller steps
- Transform vague prompts into clear, effective prompts

Simply describe what you want to accomplish, and the assistant will analyze your request, identify improvement opportunities, and generate an optimized prompt ready for use with AI models.
""")

# Design the interface

settings = pn.Card(
    model_select,
    temperature,
    title="Generation Settings"
)

export = pn.Card(
    download_button,
    title="Export"
)

template = pn.template.FastListTemplate(
    title="AI Prompt Engineering Assistant",
    sidebar=[
        settings,
        pn.Spacer(height=20),
        export
    ],
    theme=pn.theme.DarkTheme,
    theme_toggle=False,
    main = [header, 
            chat_ui]
)

template.servable()