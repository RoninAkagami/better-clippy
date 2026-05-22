# better-clippy
> I know no one is going to read this README, nor this repo, but for my satisfaction...

# Clippy - that annoying MS Office Assistant revived
> but this time - not so annoying but funny

## What it is is

This is a project made as an attempt to revive that annoying-ass MS Office assistant - Clippy, with a few important caveats:
- It does not open when you open a specific app, but is always there, as a translucent, always-on-top icon
- Every 10 mins or so, it takes a screenshot, and sends to an llm via groq, to either roast you, say something funny, or ask for help, which is then displayed as clippy's speech.
- And when you press F9, an input bar appears, to ask the llm. The llm has some tools, with which it can search the web, see what processes are running, etc..., with/without
which it can answer. The answer is displayed as clippy's speech.
- It maintains a memory of the current conversation, so isnt a goldfish.

## How it works

There are two main modules:

### Agent
This module handles everything related to the AI behind clippy.
We are using GROQ api for the llms, and langchain for turning the llm into a 'agent' 
There are further two agents, with their own task:

#### Background Watcher
Every 10 mins, or any duration we set, the following activites happen:
- A screenshot is taken using pyautogui and saved as screen.png
- pytesseract (the ocr library) is used to extract the text from the screenshot
- The text is fed to the watcher agent, which has a system prompt to make either
    * a funny joke, roasting you, or self decapration based on the observations
    * Stay silent, if nothing interesting is happening
    * Ask for help, in a funny way, if certainty is high about the task the user is doing.
- Then we use the extract text function, which does this
    * If Agent's response is a dict with messages(case 1), we do getattr(result["messages"][-1]msg, "content", str(result["messages"][-1]))
    * If agent's response is a dict with output:
    result["output"]
    * If agent's response is a direct AIMessage:
    result.content

    * I know this function might be absolutely useless, but i got some errors regarding formatting of the agent, so i just asked AI
- Note: This agent is named agent1, and has no memory, and no tools

#### Main/User Agent
This agent is the one you interact with, it has the following capabilities:
* A conversational memory using langgraph's InMemory
* The following tools:
    - take_screenshot
    - ocr_screenshot
    - list_apps
    - websearch
* A system prompt explaining it's personality and purpose
* This agent is called agent2

> agent.py just runs a cli loop with agent2, and runs the background_watcher on a seperate thread using agent1.


### Overlay
- This module spawns an image of clippy, with its window being transparent.
- The clippy image was too big, so i divided the pixmap by 7
- I used PyQt5 to create a widget and made it transparent using PyQt's window's api:
    * Qt.FramelessWindowHint
    * Qt.WindowsStayOnTopHint
    * Qt.Tool
    * setAttribute(Qt.WA_TranslucentBackground, True)
- The whole widget can be dragged, using PyQt's built-in dragging=True, and setting drag_position to wherever we drag it
- Whether we are dragging or not is determined by mouseMoveEvent and mouseReleaseEvent
- The whole widget is destroyed upon clicking Esc button

#### Speech Bubble
- To simulate clippy speaking, a speech bubble label is created, which is initially hidden. We create a QLabel for it, and make it opaque. 
- We use a function called position_bubble to position it properly in the widget, and also accounting for the input container.
- The size of the speech bubble changes, according to the length of text.

#### Public Api
- to programatically change, or update the text, we use the set_message function of the class. 
- This function does the following flow:
    * Shows the bubble_label if it is hidden
    * Displays "..." for a few seconds(time dependant on the length of text) to simulate thinking
    * We use QTimer.singleShot to delay, and then use update_message_text, which is a function that actually displays the text, and positions bubble to the left. 
    * After that, we show the text only for a few seconds(dependent on length of text), and then hide the speech bubble

#### Input bubble
- Since i want clippy to take input, an input container is spawned(when pressed F9) 
- This container, calculates proper width accounting for the width of actual image. 
- The container is a child of main window, since it needs to move along with clippy  
- We use QPlainTextEdit to make a mini-text editor

- A send button is Created(QPushButton), upon which clicked, changes the value of the variable user_input
- Whenever the send button is clicked, a function, that is to be defined externally runs(that func is part of the class)


### Integration 
We ofcourse need to integrate both these modules. 
It is done like this:
* We create a QApplication, then initialize ClippyOverlay class.
* Create a QThread called Qwatch to run the background agent
* Use pyqtSignal to see whether the message is ready.
* Run the watcher thread, and connect the message ready signal with the thread. 
* Open the GUI
* Initialize the on_user_input function of the overlay class with a function 'user' which simply runs the agent2.



## NOTE
* If you are using this, you are requested, to contribute.
* Star it if you want, dont if you dont want to. 

## LICENSE
DONT BE A DICK

> Made by Ronin Akagami @ 2026















