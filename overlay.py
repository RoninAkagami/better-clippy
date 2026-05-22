
"""
Transparent Clippy Overlay Module
note: this file was 50% ai generated(claude)
Ronin Akagami @ 2026
"""
# PyQt imports
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPlainTextEdit

# Standard imports
import sys
import time
import os

class ClippyOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.dragging = False
        self.drag_position = QPoint()

        self.input_bubble = None
        self.user_input = None

        self.input_container = None
        self.input_text_edit = None

        self.on_user_input = None

        self.init_ui()
        self.setup_window_properties()

    
    def init_ui(self):
        """load clippy + speech bubble and then display"""

        image_path = os.path.join(os.path.dirname(__file__), "images/clippy.png")

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"[ERROR] Failed to load image: {image_path}")
            sys.exit(1)

        # Since the image is kinda too big, dividing by 7 to make it smaller
        scaled_pixmap = pixmap.scaled(
            pixmap.width() // 7,
            pixmap.height() // 7,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Creating image label
        self.image_label = QLabel(self)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.resize(
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # creating speech bubble label (initially hidden)
        self.bubble_label = QLabel(self)
        self.bubble_label.setText("Im Clppy!")
        self.bubble_label.setWordWrap(True) 
        self.bubble_label.setMaximumWidth(200)  
        self.bubble_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 225, 235);
                border: 1px solid #888;
                border-radius: 10px;
                padding: 6px;
                color: black;
                font-size: 10pt;
            }
        """)

        self.bubble_label.adjustSize()
        self.bubble_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        
        self.position_bubble(corner="left") # position bubble 

        # Window size needs to account for bubble on the left
        total_width = self.bubble_label.width() + self.image_label.width() + 10
        total_height = max(self.bubble_label.height(), self.image_label.height())
        self.resize(total_width, total_height)

    def setup_window_properties(self):
        """Make window transparent and always-on-top"""

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground, True)

    # Bubble positioning logic
    def position_bubble(self, corner="top_right"):
        self.bubble_label.adjustSize()

        if corner == "top_right":
            x = self.image_label.width() - self.bubble_label.width()
            y = 0
        elif corner == "top_left":
            x = 0
            y = 0
        elif corner == "bottom_right":
            x = self.image_label.width() - self.bubble_label.width()
            y = self.image_label.height() - self.bubble_label.height()
        elif corner == "bottom_left":
            x = 0
            y = self.image_label.height() - self.bubble_label.height()
        elif corner == "left": # Left isnt really a corner but its okay ig
            x = 0
            y = 0
            self.bubble_label.move(x, y)
            clippy_x = self.bubble_label.width() + 10
            self.image_label.move(clippy_x, 0)

        # Account for input container if visible
            image_right = self.image_label.x() + self.image_label.width()
            total_width = max(image_right, self.bubble_label.width())
        
            if self.input_container is not None:
                total_width = max(total_width, self.input_container.width())
                total_height = self.image_label.height() + self.input_container.height() + 5
            else:
                total_height = max(self.bubble_label.height(), self.image_label.height())
        
            self.resize(total_width, total_height)

            self.bubble_label.raise_()
        else:
            x = 0
            y = 0

        self.bubble_label.move(x, y)
        self.bubble_label.raise_()


    # Public API to change message
    def set_message(self, text):
        if not self.bubble_label.isVisible():
            self.bubble_label.show()
        self.bubble_label.setText("...") # So it looks like its thinking
        delay = 3000 if len(text) > 20 else 1500  # milliseconds
        QTimer.singleShot(delay, lambda: self._update_message_text(text))
        self.position_bubble(corner="left")
    
        
        wait = 5 if len(text) < 40 else 10 # Schedule hide, longer messages stay longer
        QTimer.singleShot((delay + wait * 1000), self.hide_clippy_speech) # Use QTimer, since time.sleep freezes the GUI for some reason.

    def _update_message_text(self, text):
        """Helper to update message and resize bubble"""
        self.bubble_label.setText(text)
        self.position_bubble(corner="left")  # Resize after text changes

    def hide_clippy_speech(self):
        if self.bubble_label.isVisible():
            self.bubble_label.hide()

    # Dragging support (since it cant be a scarecrow)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    # ESC to quit
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        elif event.key()==Qt.Key_F9:
            self.toggle_input_bubble()
        else:
            pass

# create/destroy the input bubble 
    def toggle_input_bubble(self):
        if self.input_container is not None:
            self.input_container.deleteLater()
            self.input_container = None
            self.input_text_edit = None

            # Calculate proper width accounting for actual image position
            image_right = self.image_label.x() + self.image_label.width()
            bubble_width = self.bubble_label.width() if self.bubble_label.isVisible() else 0
            total_width = max(image_right, bubble_width)
            total_height = max(self.bubble_label.height() if self.bubble_label.isVisible() else 0, 
                              self.image_label.height())
            self.resize(total_width, total_height)
            return

    # Create container (child of main window, so it moves with Clippy)
        self.input_container = QWidget(self)
        self.input_container.setObjectName("InputContainer")
    # Opaque style
        self.input_container.setStyleSheet("""
        #InputContainer {
            background-color: #f5f5f5;
            border: 1px solid #888;
            border-radius: 8px;
        }
        QPlainTextEdit {
            font-size: 14px;
            border: 1px solid #aaa;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        QPushButton {
            font-size: 14px;
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)

        layout = QVBoxLayout(self.input_container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

    # Text edit
        self.input_text_edit = QPlainTextEdit()
        self.input_text_edit.setPlaceholderText("Type your message...")
        self.input_text_edit.setFixedWidth(200)
        self.input_text_edit.setFixedHeight(50)
        self.input_text_edit.textChanged.connect(self.resize_input_bubble)
        layout.addWidget(self.input_text_edit)

        send_btn = QPushButton("Send")
        send_btn.setFixedHeight(20)
        send_btn.clicked.connect(self.on_send_clicked)
        layout.addWidget(send_btn)

        self.input_container.adjustSize()
        x = 0
        y = self.image_label.height() + 5
        self.input_container.setGeometry(x, y,
                                     self.input_container.width(),
                                     self.input_container.height())
        self.input_container.show()

    # Resize main window accounting for image's actual position
        image_right = self.image_label.x() + self.image_label.width()
        total_width = max(image_right, self.input_container.width())
        total_height = self.image_label.height() + self.input_container.height() + 5
        self.resize(total_width, total_height)

        self.input_text_edit.setFocus()


    # Auto-resize bubble as user types (this was a pain in the ass to make)
    def resize_input_bubble(self):
        if self.input_container is None:
            return
        doc = self.input_text_edit.document()
        doc_height = doc.size().height() + 20
        new_height = max(100, min(doc_height, 300))
        self.input_text_edit.setFixedHeight(int(new_height))

        self.input_container.adjustSize()
        y = self.image_label.height() + 5
        self.input_container.setGeometry(0, y,
                                         self.input_container.width(),
                                         self.input_container.height())

        # resize main window again
        total_width = max(self.image_label.width(), self.input_container.width())
        total_height = self.image_label.height() + self.input_container.height() + 5
        self.resize(total_width, total_height)

    # Change user input variable, and then delete the input bubble
    def on_send_clicked(self):
        if self.input_container is None:
            return
        self.user_input = self.input_text_edit.toPlainText().strip()

        if self.on_user_input:
            self.on_user_input(self.user_input)
            
        self.input_container.deleteLater()
        self.input_container = None
        self.input_text_edit = None
        self.resize(self.image_label.width(), self.image_label.height())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Clippy Overlay")

    window = ClippyOverlay()

    # position on screen (top-right-ish)
    screen_geometry = app.primaryScreen().geometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    x = int(screen_width * 0.75)
    y = int(screen_height * 0.25)

    window.move(x, y)

    window.show()

    print("Clippy overlay running")
    print("Drag to move")
    print("ESC to close")

    # optional message  
    # window.set_message("I watch you sleep...(nah kidding, just watching your screen)")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()