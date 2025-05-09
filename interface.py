import tkinter as tk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from PIL import Image, ImageTk

# ΣΥΝΔΕΣΗ ΜΕΤΑΞΥ .ino ΚΑΙ interface.py
from sensor_reader import SensorReader
sensor_reader = SensorReader(port='/dev/ttyACM0')  # Για Ubuntu/Linux


# Χρώματα
BG_COLOR = "#053B9A"
BTN_COLOR = "#7BFFEB"
HOVER_COLOR = "#5AE3D3"
TEXT_COLOR = "#FFFFFF"
LABEL_COLOR = "#7BFFEB"

root = tk.Tk()
root.title("Interface")
root.geometry("1000x500+80+80")
root.config(bg=BG_COLOR)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


bg_image_path = "circuit.jpeg"
bg_image_raw = Image.open(bg_image_path)
bg_image_scaled = ImageTk.PhotoImage(bg_image_raw)
bg_image = bg_image_scaled

main_frame = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
main_frame.grid(row=0, column=0, sticky="nsew")
bg_id = main_frame.create_image(0, 0, image=bg_image, anchor="nw", tags="bg")
main_frame.bind("<Configure>", lambda e: (
    [main_frame.itemconfig(bg_id, anchor="nw"),
     main_frame.coords(bg_id, 0, 0),
     main_frame.coords(label_window, e.width // 2, 50)] +
    [main_frame.coords(btn, e.width // 2, 100 + i * 62)
     for i, btn in enumerate(button_widgets)]
))
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure(0, weight=1)

# Υποστήριξη για στρογγυλό κουμπί
def _create_round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1
    ]
    return self.create_polygon(points, **kwargs, smooth=True)

tk.Canvas.create_round_rectangle = _create_round_rectangle

# Συνάρτηση για οβάλ κουμπί με hover
def create_rounded_button(parent, text, command, y, custom_width=None, center=True):
    padding = 40
    text_width = custom_width if custom_width else len(text) * 10 + padding
    canvas = tk.Canvas(parent, width=text_width, height=50, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(pady=5)

    rect = canvas.create_round_rectangle(2, 2, text_width - 2, 48, radius=20, fill=BTN_COLOR, outline="")
    label = canvas.create_text(text_width // 2, 25, text=text, fill="#000000", font=("Arial", 12, "bold"))

    def on_click(event): command()
    def on_enter(event): canvas.itemconfig(rect, fill=HOVER_COLOR)
    def on_leave(event): canvas.itemconfig(rect, fill=BTN_COLOR)

    canvas.tag_bind(rect, "<Button-1>", on_click)
    canvas.tag_bind(label, "<Button-1>", on_click)
    canvas.tag_bind(rect, "<Enter>", on_enter)
    canvas.tag_bind(label, "<Enter>", on_enter)
    canvas.tag_bind(rect, "<Leave>", on_leave)
    canvas.tag_bind(label, "<Leave>", on_leave)

    return canvas

open_windows = {}
last_time_window_value = 5.0

def close_window():
    sensor_reader.stop()  # Τερματίζει τη σύνδεση με Arduino
    root.destroy()

def create_logger_window(title, generate_data, with_plot=False, plot_multiple=False):
    if title in open_windows:
        try:
            open_windows[title].destroy()
        except:
            pass

    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("1000x400")
    win.config(bg=BG_COLOR)
    open_windows[title] = win

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(fill="both", expand=True)

    left = tk.Frame(frame, bg=BG_COLOR)
    left.pack(side="left", fill="y")

    text_widget = tk.Text(
        left, bg=BG_COLOR, fg=TEXT_COLOR, font=("Courier", 13, "bold"),
        state="disabled", wrap="none", height=25, width=40
    )
    text_widget.pack(fill="both", expand=False, padx=5, pady=5)

    scrollbar = tk.Scrollbar(left, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

    realtime_flag = tk.BooleanVar(value=True)

    def enable_realtime():
        realtime_flag.set(True)
        text_widget.see("end")

    def create_realtime_button():
        return create_rounded_button(left, "Real-Time Measurements", enable_realtime, y=0, custom_width=240, center=True)

    # Το κουμπί κάτω από το text widget, μέσα στο ίδιο container
    realtime_button = create_realtime_button()
    realtime_button.pack(side="bottom", pady=10)

    def on_scroll(event):
        realtime_flag.set(False)
        return "break"

    text_widget.bind("<MouseWheel>", on_scroll, add='+')
    text_widget.bind("<Button-4>", on_scroll, add='+')
    text_widget.bind("<Button-5>", on_scroll, add='+')

    if with_plot:
        right = tk.Frame(frame, bg=BG_COLOR)

        # Περιοχή για slider ελέγχου εύρους χρόνου
        slider_frame = tk.Frame(right, bg=BG_COLOR)
        slider_frame.pack(fill="x")
        tk.Label(slider_frame, text="Εύρος Χρόνου (s):", bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)
        global last_time_window_value
        time_window = tk.DoubleVar(value=last_time_window_value)
        slider = tk.Scale(slider_frame, from_=1, to=20, resolution=0.5, orient="horizontal", variable=time_window, bg=BG_COLOR, fg=TEXT_COLOR, troughcolor=BTN_COLOR, highlightthickness=0)
        slider.pack(fill="x", padx=5, expand=True)
        right.pack(side="right", fill="both", expand=True)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.set_facecolor("white")
        fig.patch.set_facecolor("white")
        ax.tick_params(colors="black", labelsize=8)
        ax.spines[:].set_color("black")
        ax.set_title(f"{title} - Τιμή vs Χρόνος", color="black", fontsize=10)
        ax.set_xlabel("Χρόνος (s)", color="black")
        ax.set_ylabel("Τιμή", color="black")
        ax.grid(True)

        canvas_plot = FigureCanvasTkAgg(fig, master=right)
        canvas_plot.get_tk_widget().pack(fill="both", expand=True)

        xdata = deque()  # κρατάμε όλα τα δεδομένα, όχι μόνο τα τελευταία 20
        ydata1 = deque()
        ydata2 = deque()
        line1, = ax.plot([], [], color="blue", linewidth=2, label="Θερμοκρασία" if title == "Θερμοκρασία και Υγρασία" else "")
        line2 = None
        if plot_multiple and title == "Θερμοκρασία και Υγρασία":
            line2, = ax.plot([], [], color="orange", linewidth=2, label="Υγρασία")
            ax.legend(loc="upper left")

    def update(counter=[0]):
        parts = generate_data()
        full_line = "  ".join([f"{label}: {value}" for label, value in parts])
        text_widget.configure(state="normal")
        text_widget.insert("end", full_line + "\n")
        text_widget.tag_config("label", foreground=LABEL_COLOR)
        text_widget.tag_config("value", foreground=TEXT_COLOR)
        if realtime_flag.get():
            text_widget.see("end")
        text_widget.configure(state="disabled")

        if with_plot:
            try:
                counter[0] += 1
                xdata.append(counter[0] * 0.1)
                val1 = float(parts[0][1].split()[0])
                ydata1.append(val1)
                line1.set_data(xdata, ydata1)

                if plot_multiple and line2 and len(parts) > 1:
                    val2 = float(parts[1][1].split()[0])
                    ydata2.append(val2)
                    line2.set_data(xdata, ydata2)

                ax.set_xlim(max(0, xdata[-1] - time_window.get()), xdata[-1])
                all_y = list(ydata1) + list(ydata2) if plot_multiple and line2 else list(ydata1)
                ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
                canvas_plot.draw()
                last_time_window_value = time_window.get()
            except:
                pass

        if title in open_windows:
            win.after(100, update)

    update()
    
def show_temp_humidity_window():
    def generator():
        temp, hum = sensor_reader.get_data()
        return [("Θερμοκρασία", f"{temp:.1f} °C"), ("Υγρασία", f"{hum:.1f} %")]


    title = "Θερμοκρασία και Υγρασία"
    if title in open_windows:
        try:
            open_windows[title].destroy()
        except:
            pass

    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("1000x400")
    win.config(bg=BG_COLOR)
    open_windows[title] = win

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(fill="both", expand=True)

    left = tk.Frame(frame, bg=BG_COLOR)
    left.pack(side="left", fill="y")

    text_widget = tk.Text(
        left, bg=BG_COLOR, fg=TEXT_COLOR, font=("Courier", 13, "bold"),
        state="disabled", wrap="none", height=25, width=40
    )
    text_widget.pack(fill="both", expand=False, padx=5, pady=5)

    scrollbar = tk.Scrollbar(left, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

    realtime_flag = tk.BooleanVar(value=True)
    def enable_realtime():
        realtime_flag.set(True)
        text_widget.see("end")

    realtime_button = create_rounded_button(left, "Real-Time Measurements", enable_realtime, y=0, custom_width=240, center=True)
    realtime_button.pack(side="bottom", pady=10)

    def on_scroll(event):
        realtime_flag.set(False)
        return "break"

    text_widget.bind("<MouseWheel>", on_scroll, add='+')
    text_widget.bind("<Button-4>", on_scroll, add='+')
    text_widget.bind("<Button-5>", on_scroll, add='+')

    right = tk.Frame(frame, bg=BG_COLOR)
    right.pack(side="right", fill="both", expand=True)

    # Θερμοκρασία plot
    frame_top = tk.Frame(right, bg=BG_COLOR)
    frame_top.pack(fill="both", expand=True)
    label_top = tk.Label(frame_top, text="Θερμοκρασία", bg=BG_COLOR, fg=TEXT_COLOR)
    label_top.pack()

    slider_top = tk.Scale(frame_top, from_=1, to=20, resolution=0.5, orient="horizontal", bg=BG_COLOR, fg=TEXT_COLOR, troughcolor=BTN_COLOR, highlightthickness=0)
    slider_top.set(5.0)
    slider_top.pack(fill="x")

    fig_top, ax_top = plt.subplots(figsize=(5, 2))
    ax_top.set_facecolor("white")
    fig_top.patch.set_facecolor("white")
    ax_top.grid(True)
    ax_top.set_title("Θερμοκρασία vs Χρόνος", fontsize=10)
    ax_top.set_xlabel("Χρόνος (s)")
    ax_top.set_ylabel("Θερμοκρασία (°C)")
    line_temp, = ax_top.plot([], [], color="blue", linewidth=2)
    canvas_top = FigureCanvasTkAgg(fig_top, master=frame_top)
    canvas_top.get_tk_widget().pack(fill="both", expand=True)

    # Υγρασία plot
    frame_bottom = tk.Frame(right, bg=BG_COLOR)
    frame_bottom.pack(fill="both", expand=True)
    label_bottom = tk.Label(frame_bottom, text="Υγρασία", bg=BG_COLOR, fg=TEXT_COLOR)
    label_bottom.pack()

    slider_bottom = tk.Scale(frame_bottom, from_=1, to=20, resolution=0.5, orient="horizontal", bg=BG_COLOR, fg=TEXT_COLOR, troughcolor=BTN_COLOR, highlightthickness=0)
    slider_bottom.set(5.0)
    slider_bottom.pack(fill="x")

    fig_bottom, ax_bottom = plt.subplots(figsize=(5, 2))
    ax_bottom.set_facecolor("white")
    fig_bottom.patch.set_facecolor("white")
    ax_bottom.grid(True)
    ax_bottom.set_title("Υγρασία vs Χρόνος", fontsize=10)
    ax_bottom.set_xlabel("Χρόνος (s)")
    ax_bottom.set_ylabel("Υγρασία (%)")
    line_hum, = ax_bottom.plot([], [], color="orange", linewidth=2)
    canvas_bottom = FigureCanvasTkAgg(fig_bottom, master=frame_bottom)
    canvas_bottom.get_tk_widget().pack(fill="both", expand=True)

    xdata, y_temp, y_hum = deque(), deque(), deque()

    def update(counter=[0]):
        parts = generator()
        full_line = "  ".join([f"{label}: {value}" for label, value in parts])
        text_widget.configure(state="normal")
        text_widget.insert("end", full_line + "\n")
        if realtime_flag.get():
            text_widget.see("end")
        text_widget.configure(state="disabled")

        counter[0] += 1
        x = counter[0] * 1.0 # << Η ΚΑΤΑΓΡΑΦΗ ΚΑΙ Η ΑΝΑΝΕΩΣΗ ΤΟΥ ΧΡΟΝΟΥ (αν ήταν κάθε 0.1" η μέτρηση, θα έβαζα * 0.1
        xdata.append(x)
        y_temp.append(float(parts[0][1].split()[0]))
        y_hum.append(float(parts[1][1].split()[0]))

        line_temp.set_data(xdata, y_temp)
        ax_top.set_xlim(max(0, x - slider_top.get()), x)
        ax_top.set_ylim(min(y_temp) - 1, max(y_temp) + 1)
        canvas_top.draw()

        line_hum.set_data(xdata, y_hum)
        ax_bottom.set_xlim(max(0, x - slider_bottom.get()), x)
        ax_bottom.set_ylim(min(y_hum) - 1, max(y_hum) + 1)
        canvas_bottom.draw()

        if title in open_windows:
            win.after(1000, update)

    update()

def show_current_window():
    def generator():
        current = round(random.uniform(0.5, 2.0), 2)
        return [("Ρεύμα", f"{current} A")]
    create_logger_window("Ρεύμα κινητήρα", generator, with_plot=True)

def show_motor_params_window():
    def generator():
        rpm = random.randint(1000, 3000)
        return [("RPM", f"{rpm}")]
    create_logger_window("Εκτίμηση παραμέτρων κινητήρα", generator, with_plot=True)

def show_stats_window():
    
    # Δηλώνουμε το realtime_flag και το περνάμε στη logger_window
    realtime_flag = tk.BooleanVar(value=True)

    stats_data = {
        "correct": 0,
        "total": 0,
        "real_counts": {"Μπλε": 0, "Κόκκινο": 0, "Πράσινο": 0},
        "pred_counts": {"Μπλε": 0, "Κόκκινο": 0, "Πράσινο": 0},
        "canvas": None,
        "bars_real": None,
        "bars_pred": None,
        "ax": None,
        "text_widget": None,
        "realtime_flag": realtime_flag,
        "start_update": False
    }

    colors_order = ["Μπλε", "Κόκκινο", "Πράσινο"]
    color_map = {
        "Μπλε": "#00BFFF",
        "Κόκκινο": "#FF0000",
        "Πράσινο": "#00FF00"
    }

    def update_histogram():
        if not stats_data["bars_real"] or not stats_data["bars_pred"]:
            return
        for bar, color in zip(stats_data["bars_real"], colors_order):
            bar.set_height(stats_data["real_counts"][color])
        for bar, color in zip(stats_data["bars_pred"], colors_order):
            bar.set_height(stats_data["pred_counts"][color])
        max_val = max(
            max(stats_data["real_counts"].values()),
            max(stats_data["pred_counts"].values())
        )
        stats_data["ax"].set_ylim(0, max(1, max_val + 1))
        stats_data["canvas"].draw()
    
    def generator():
        if not stats_data["start_update"]:
            return []

        actual = random.choice(colors_order)
        predicted = random.choice(colors_order)
        correct = actual == predicted

        stats_data["total"] += 1
        if correct:
            stats_data["correct"] += 1
        stats_data["real_counts"][actual] += 1
        if correct:
            stats_data["pred_counts"][predicted] += 1

        accuracy = round(100 * stats_data["correct"] / stats_data["total"], 2)

        t = stats_data["text_widget"]
        t.configure(state="normal")

        t.insert("end", f"Ακρίβεια: {accuracy:.2f}%\n", "white")

        def insert_colored_line(label, value):
            t.insert("end", label + " ", "white")
            t.insert("end", value + "\n", value if value in color_map else "white")

        insert_colored_line("Πραγματικό:", actual)
        insert_colored_line("Πρόβλεψη:", predicted)
        t.insert("end", "\n", "white")

        t.configure(state="disabled")

        if stats_data["realtime_flag"].get():
            t.see("end")

        update_histogram()
        return []

    # Δημιουργούμε logger_window και κρατάμε το text_widget
    create_logger_window("Στατιστική ανάλυση ταξινόμησης", generator, with_plot=True)

    parent = open_windows["Στατιστική ανάλυση ταξινόμησης"]
    parent.update_idletasks()

    container = parent.winfo_children()[0]
    children = container.winfo_children()
    if len(children) < 2:
        return

    left_frame, right_frame = children[0], children[1]

    # Απόκτηση του text widget
    for child in left_frame.winfo_children():
        if isinstance(child, tk.Text):
            stats_data["text_widget"] = child
            break

    # Ορισμός χρωματικών tags
    t = stats_data["text_widget"]
    t.config(fg="white", bg=BG_COLOR)
    t.tag_config("white", foreground="white")
    for color, hexcode in color_map.items():
        t.tag_config(color, foreground=hexcode)

    # Καθαρισμός δεξιού frame
    for child in right_frame.winfo_children():
        child.destroy()

    # Δημιουργία του ιστόγραμματος με grid
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    x = range(len(colors_order))

    bars_real = ax.bar(x, [0, 0, 0], width=0.4,
                       label="Πραγματικά", align="center",
                       color=["#77bfff", "#ff9999", "#99ff99"])
    bars_pred = ax.bar([i + 0.4 for i in x], [0, 0, 0], width=0.4,
                       label="Προβλέψεις", align="center",
                       color=["#004eff", "#ff0000", "#00cc00"])

    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(colors_order)
    ax.set_ylabel("Πλήθος")
    ax.set_title("Σύγκριση Πραγματικών vs Προβλέψεων")
    ax.legend()
    ax.grid(True)  # <-- ενεργοποιούμε το grid

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

    stats_data["canvas"] = canvas
    stats_data["bars_real"] = bars_real
    stats_data["bars_pred"] = bars_pred
    stats_data["ax"] = ax
    stats_data["start_update"] = True

def show_noise_window():
    def generator():
        noise = round(random.uniform(0.0, 2.5), 2)
        return [("Θόρυβος", f"{noise} dB")]
    create_logger_window("Επίδραση θορύβου", generator, with_plot=True)

def resize_bg(e):
    global bg_image_scaled
    w, h = e.width, e.height
    if w > 1230 or h > 795:
        resized = bg_image_raw.resize((w, h), Image.LANCZOS)
        bg_image_scaled = ImageTk.PhotoImage(resized)
    else:
        bg_image_scaled = ImageTk.PhotoImage(bg_image_raw)
    main_frame.itemconfig(bg_id, image=bg_image_scaled)
    main_frame.coords(bg_id, 0, 0)
    main_frame.coords(label_window, w // 2, 50)
    for i, btn in enumerate(button_widgets):
        main_frame.coords(btn, w // 2, 100 + i * 62)

label = tk.Label(main_frame, text="Μενού επιλογών", bg=BG_COLOR, fg="#FFFFFF", font=("Arial", 14, "bold"))
label_window = main_frame.create_window(0, 50, window=label, anchor="n")
label.pack(pady=20)

button_widgets = []
for i, (text, func) in enumerate([
    ("Μετρήσεις Θερμοκρασίας/υγρασίας", show_temp_humidity_window),
    ("Μετρήσεις ρεύματος", show_current_window),
    ("Εκτιμήσεις παραμέτρων κινητήρα", show_motor_params_window),
    ("Στατιστική ανάλυση ταξινόμησης", show_stats_window),
    ("Επίδραση θορύβου στην μέτρηση ρεύματος κινητήρα", show_noise_window),
    ("End programm", close_window)
]):
    btn = create_rounded_button(main_frame, text, func, y=0)
    button_widgets.append(btn)

# Ανανεώνουμε τις θέσεις των κουμπιών κατά το resize
main_frame.bind("<Configure>", lambda e: resize_bg(e))

root.mainloop()
