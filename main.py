from agent import agent1, agent2
from agent import analyze_screen, extract_text
from overlay import ClippyOverlay

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal

app = QApplication(sys.argv)
app.setApplicationName("Clippy Overlay")

window = ClippyOverlay()

class Qwatch(QThread):
    message_ready = pyqtSignal(str)

    def run(self):
        interval = 600
        while True:
            msg = analyze_screen()
            if msg:
                self.message_ready.emit(msg)
            time.sleep(interval)

watch_agent_thread = Qwatch()
watch_agent_thread.message_ready.connect(window.set_message)
watch_agent_thread.start()

screen_geometry = app.primaryScreen().geometry()
screen_width = screen_geometry.width()
screen_height = screen_geometry.height()

x = int(screen_width * 0.75)
y = int(screen_height * 0.25)

window.move(x, y)
window.show()

def user(user_input):
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

        window.set_message(extract_text(result))
    
    except Exception as e:
        window.set_message(f"Error: {e}")

window.on_user_input = user

sys.exit(app.exec_())