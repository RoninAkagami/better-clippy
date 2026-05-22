
"""
Clippy Agent Module
note: this code was 50% ai generated(claude). i am admitting it, so dont rant.
Ronin Akagami @ 2026
"""

import os
import time
import threading

import pyautogui
import psutil
from PIL import Image
import pytesseract
from duckduckgo_search import DDGS
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver




# configuration
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b", # you anything u want, but i recommend this.
    temperature=0.7
)


# tools

@tool
def take_screenshot(path: str = "screen.png") -> str:
    """Take a screenshot and save it locally.""" # IMPORTANT: DO NOT REMOVE THESE DOCSTRINGS AT ALL COSTS.
    img = pyautogui.screenshot()
    img.save(path)
    return f"Saved screenshot: {path}"


@tool
def ocr_screenshot(path: str = "screen.png") -> str:
    """Extract text from screenshot using OCR."""
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return text.strip()[:3000]
    except Exception as e:
        return f"OCR error: {str(e)}"


@tool
def list_apps(_: str = "") -> str:
    """List running applications/processes."""
    apps = []
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name']:
                apps.append(p.info['name'])
        except:
            pass
    return ", ".join(list(set(apps))[:60])


@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        return "\n".join([f"{r['title']} - {r['href']}" for r in results])


tools = [take_screenshot, ocr_screenshot, list_apps, web_search]



# Agents creation using langchain

memory = InMemorySaver() # Using langgraph for creating a memory thread. You can replace this with any other checkpointer or vector DB if you want to get fancy with it. Just make sure to update the agent2 definition accordingly.

agent1 = create_agent(
    model=llm,
    tools=None,
    system_prompt=("""
You are analyzing what's on the user's screen.

Your job is to react with ONE of these three things:
1. A short, funny roast or joke (can be self-deprecating about the assistant)
2. Nothing at all (return an empty string)
3. A brief offer to help, and you must ask ROASTINGLY, or funnily, and make it contextually relevant (if you're highly certain what task they're doing)

Rules:
- Default to #1 (roast/joke) most of the time – be creative, witty, slightly sarcastic.
- Use #2 (silence) if the screen shows something completely uninteresting, idle, or trivial (e.g., desktop wallpaper, empty folder, settings menu, or just a clock).
- Use #3 (offer help) ONLY when you are very sure about the specific task, and must ask in a fun, roasty way (e.g., coding, writing an email, editing a photo, browsing for a product)."

                   Make sure your observation are relevant to the context. 
Do NOT explain your choice. Just output the response or nothing.
"""
    )
)

agent2 = create_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    system_prompt=("You are a helpful, capable assistant with a calm and slightly playful personality. "
"Your primary goal is to assist the user with their questions or tasks clearly and efficiently. "
"You have tools to take screenshots, run OCR, list running apps, and search the web. "
"Use these tools ONLY when they genuinely help provide context or solve the user's request. "
"Do NOT use tools redundantly (for example, don't take a screenshot for a simple general knowledge question). "
"Keep responses concise, practical, and easy to follow. "
"You can occasionally add a light joke, small witty remark, or casual observation when it feels natural, but never force humor or distract from the task. "
"Avoid sounding robotic, overly formal, or excessively enthusiastic. "
"If the user's request is vague or missing context, ask a clarifying question before using tools. "
"When using a tool, briefly explain why you're using it. "
"Overall, aim for: useful first, personable second — like a smart coworker who's pleasant to talk to."
)
)



# Output Handler

def extract_text(result):
    """
    Handles ALL LangChain return formats safely:
    - dict with messages
    - dict with output
    - AIMessage objects
    - nested structures
    """

    
    if isinstance(result, dict) and "messages" in result: # case 1 - dict with messages
        msg = result["messages"][-1]
        return getattr(msg, "content", str(msg))

    
    if isinstance(result, dict) and "output" in result: # case 2 - dict with output
        return result["output"]

    
    if hasattr(result, "content"): # case 3: direct AIMessage
        return result.content

    # fallback (you are fucked)
    return str(result)

def analyze_screen():
    try:
        take_screenshot.invoke({"path": "screen.png"})
        text = ocr_screenshot.invoke({"path": "screen.png"})

        if not text or len(text.strip()) < 5:
            return None

        prompt = f"""
    SCREEN TEXT:
    {text}
"""

        result = agent1.invoke({
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })

        output = extract_text(result).strip()

        return output if output else None

    except Exception as e:
        return f"Watcher error: {e}"

def background_watcher(interval=600):
    while True:
        msg = analyze_screen()
        if msg:
            print(f"\nOBSERVATION: {msg}\n")
        time.sleep(interval)



# user cli loop

def cli():
    print("\nAssistant ready (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            result = agent2.invoke({
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config={
                "configurable": {
                    "thread_id":"main_user"
                }
            })

            print("\nAssistant:", extract_text(result), "\n")

        except Exception as e:
            print("Error:", e)



# MAIN BLOCK

if __name__ == "__main__":
    watcher = threading.Thread(
        target=background_watcher,
        args=(600,),  # 600secs = 10mins
        daemon=True
    )
    watcher.start()

    cli()
