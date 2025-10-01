from flask import Flask, request, jsonify

import threading
import queue
import uuid
import io

from PIL import Image, ImageTk, ImageSequence

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import webbrowser

import configparser

#### CFG parsing

config = configparser.ConfigParser()
config.read("settings.cfg")

host_ip =  config["API"]["host"]
host_port =  config["API"]["port"]

background = config["general"]["background"]

################

app = Flask(__name__)

request_queue = queue.Queue()
responses = {}
lock = threading.Lock()

current_version = "v2.0"

class AnimatedGIF(tk.Label):
    def __init__(self, master, gif_path):
        self.master = master
        self.gif = Image.open(gif_path)
        self.frames = [frame.copy() for frame in ImageSequence.Iterator(self.gif)]
        self.photo_frames = []
        self.current = 0

        # takes the gif dimension and set the correct window lenght for it
        self.original_width, self.original_height = self.frames[0].size
        self.master.geometry(f"{self.original_width}x{self.original_height}")
        self.master.configure(bg="black")

        super().__init__(master, bg="black")
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_background()
        self.after(100, self.update_frame)

    def update_background(self):
        # get the current windows lenght
        win_w = self.master.winfo_width()
        win_h = self.master.winfo_height()
        frame = self.frames[self.current]

        # manages all the window / background aspect ratio and dimension
        frame_ratio = frame.width / frame.height
        win_ratio = win_w / win_h

        if win_ratio > frame_ratio:
            new_height = win_h
            new_width = int(frame_ratio * new_height)
        else:
            new_width = win_w
            new_height = int(new_width / frame_ratio)

        resized = frame.resize((new_width, new_height), Image.LANCZOS)
        img = Image.new("RGB", (win_w, win_h), "black")
        img.paste(resized, ((win_w - new_width) // 2, (win_h - new_height) // 2))
        self.photo = ImageTk.PhotoImage(img)
        self.configure(image=self.photo)

    def update_frame(self):
        self.current = (self.current + 1) % len(self.frames)
        self.update_background()
        self.after(100, self.update_frame)

class SolverGUI:
    def __init__(self):
        self.current_id = None
        # --- intin window ---
        
        self.root = tk.Tk()
        self.root.title(f"Image Solver {current_version} - Elxss's creation - In Queue : 0 - Currently :")
        self.root.iconbitmap('Icons/msagent.ico')
        self.current_request = None

        # --- Background
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- load gif ---
        self.gif = Image.open(background)
        self.frames = [frame.copy() for frame in ImageSequence.Iterator(self.gif)]
        self.frame_count = len(self.frames)
        self.current = 0
        self.photo = None

        self.menu_bar = tk.Menu(self.root)
        
        # Menu "Options"
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)

        # self.advanced_menu = tk.Menu(self.options_menu, tearoff=0)
        # self.advanced_menu.add_command(label="Mode Sombre", command=self.show_credits)
        # self.advanced_menu.add_command(label="Exporter les données", command=self.show_credits)
        

        # self.options_menu.add_cascade(label="Configure Server Type", menu=self.advanced_menu)
        
        # --------------------------------

        self.options_menu.add_command(label="Clear Queue", command=self.clear_queue)
        self.options_menu.add_separator()
        # --------------------------------

        self.options_menu.add_command(label="Quit", command=self.quit_app)
        self.options_menu.add_command(label="Credits", command=self.show_credits)
        self.options_menu.add_command(label="Github Repo", command=self.show_credits)
        
        
        self.menu_bar.add_cascade(label="More", menu=self.options_menu)
        self.root.config(menu=self.menu_bar)

        # --- Ajust window size to the gif
        orig_w, orig_h = self.frames[0].size
        self.root.geometry(f"{orig_w}x{orig_h}")
        self.root.minsize(orig_w, orig_h)

        # --- Styles ttk--
        style = ttk.Style(self.root)
        style.theme_use("default")
        style.configure("TLabel", background="black", foreground="white")
        style.configure("TEntry", fieldbackground="gray20", foreground="white")
        style.configure("TButton", background="gray30", foreground="white")
        style.configure("TFrame", background="black")

        self.container = ttk.Frame(self.canvas, style="TFrame")
        self.container_id = self.canvas.create_window(0, 0, window=self.container, anchor=tk.CENTER)

        #magic settls
        self.setup_gui()
        self.root.bind("<Configure>", self.on_resize)
        self.play()
        self.root.after(100, self.process_queue)

    def setup_gui(self):
        # --- load icons
        self.icon_queue = tk.PhotoImage(file="Icons/queue.png")
        self.icon_current = tk.PhotoImage(file="Icons/current.png")
        self.icon_send = tk.PhotoImage(file="Icons/send.png").subsample(2, 2)
        self.icon_skip = tk.PhotoImage(file="Icons/skip.png").subsample(2, 2)

        # queue
        queue_frame = ttk.Frame(self.container, style="TFrame")
        queue_frame.pack(pady=10)

        self.queue_label = ttk.Label(queue_frame, text="In Queue: 0", image=self.icon_queue, compound="left")
        self.queue_label.pack(side=tk.LEFT, padx=10)

        self.current_label = ttk.Label(queue_frame, text="Currently: None", image=self.icon_current, compound="left")
        self.current_label.pack(side=tk.LEFT)

        # show img
        self.image_label = tk.Label(self.container, bg="black")
        self.image_label.pack(pady=10)

        # controls
        control_frame = ttk.Frame(self.container, style="TFrame")
        control_frame.pack(pady=10)

        self.entry = ttk.Entry(control_frame, width=30)
        self.entry.pack(side=tk.LEFT, padx=5)

        send_button = ttk.Button(control_frame, text="Send", image=self.icon_send, compound="right", command=self.submit)
        send_button.pack(side=tk.LEFT, padx=2)

        skip_button = ttk.Button(control_frame, text="Skip", image=self.icon_skip, compound="right", command=self.skip)
        skip_button.pack(side=tk.LEFT)

        self.entry.bind("<Return>", lambda e: self.submit())

    def resize_frame(self, frame, cw, ch):
        """everything is in the name of the function !"""
        fr = frame.width / frame.height
        if cw / ch > fr:
            new_h = ch
            new_w = int(fr * new_h)
        else:
            new_w = cw
            new_h = int(new_w / fr)
        resized = frame.resize((new_w, new_h), Image.LANCZOS)
        black = Image.new("RGB", (cw, ch), "black")
        black.paste(resized, ((cw - new_w) // 2, (ch - new_h) // 2))
        return black

    def play(self):
        # animate
        self.update_frame()
        self.root.after(100, self.play)

    def update_frame(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        frame = self.frames[self.current]
        bg_img = self.resize_frame(frame, w, h)
        self.photo = ImageTk.PhotoImage(bg_img)

        self.canvas.delete("bg")
        self.canvas.create_image(w//2, h//2, image=self.photo, anchor=tk.CENTER, tags="bg")
        # recenter
        self.canvas.coords(self.container_id, w//2, h//2)

        self.current = (self.current + 1) % self.frame_count

    def on_resize(self, event):
        """ draws the background once the window gets resized"""
        self.update_frame()

    def process_queue(self):
        with lock:
            queue_size = request_queue.qsize()
            self.queue_label.config(text=f"In Queue: {queue_size}")
            self.root.title(f"Image Solver {current_version} - Elxss's creation - In Queue : {queue_size} - Currently : {self.current_id}")
            
            if not self.current_request and not request_queue.empty():
                self.current_request = request_queue.get()
                self.display_image(*self.current_request)
                
        self.root.after(100, self.process_queue)

    def display_image(self, req_id, img_data):
        """Displays the image on the gui"""
        try:
            image = Image.open(io.BytesIO(img_data))
            image.thumbnail((500, 500))
            
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.current_label.config(text=f"Currently: {req_id[:8]}")

            self.current_id = req_id[:8]
        except Exception as e:
            print(f"Error: {e}")

    def submit(self):
        if self.current_request and self.entry.get():
            req_id, _ = self.current_request
            with lock:
                responses[req_id] = self.entry.get()
            self.clear_interface()

    def skip(self):
        """skips a captcha"""
        if self.current_request:
            req_id, _ = self.current_request
            with lock:
                responses[req_id] = 'SKIPPED'
            self.clear_interface()

    def clear_interface(self):
        """everything is in the name of the function !"""
        self.current_request = None
        self.image_label.config(image='')
        self.entry.delete(0, tk.END)
        self.current_label.config(text="Currently: None")

    def clear_queue(self):
        """everything is in the name of the function !"""
        while not request_queue.empty():
            request_queue.get()
        self.skip()

    def quit_app(self):
        """close the app"""
        self.root.destroy()

    def show_credits(self):
        """dialog box"""
        messagebox.showinfo(f"Image Solver {current_version} - Credits", f" Made with love by Elxss (myself)\n Never stop to learn !\n Please, Consider Staring this Project on Github :)\n Current Version : {current_version}")

    def open_github_repo():
        url = "https://github.com/Elxss/Image-Captcha-Solver"
        webbrowser.open(url)


#### API
@app.route('/api/submit', methods=['POST'])
def handle_submission():
    if 'image' not in request.files:
        return jsonify(error="No Image Sent"), 400
    
    file = request.files['image']
    img_data = file.read()
    req_id = str(uuid.uuid4())
    
    with lock:
        request_queue.put((req_id, img_data))
    
    return jsonify(
        request_id=req_id,
        queue_position=request_queue.qsize()
    )

@app.route('/api/check/<req_id>', methods=['GET'])
def check_response(req_id):
    with lock:
        status = responses.get(req_id, 'PENDING')
        queue_pos = sum(1 for _ in request_queue.queue if _[0] == req_id)
        
    return jsonify(
        status=status,
        queue_position=queue_pos
    )

def run_server():
    gui = SolverGUI()
    threading.Thread(target=app.run, kwargs={
        'host': host_ip,
        'port': host_port,
        'use_reloader':False,
        'threaded':True
    }, daemon=True).start()
    gui.root.mainloop()

if __name__ == '__main__':
    run_server()