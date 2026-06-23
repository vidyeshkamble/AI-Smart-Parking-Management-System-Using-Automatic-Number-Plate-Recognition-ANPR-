import cv2
from ultralytics import YOLO
import cvzone
from paddleocr import PaddleOCR
from datetime import datetime
import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import scrolledtext,messagebox, ttk
import threading
import qrcode

from NewDatabase import Database
from flaskapplication.app import ParkingApp

# ======= QR Functions =======

def get_local_ip():
    import socket
    """Return your local Wi-Fi IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def showFlaskQR(frame):
    """Generate Flask QR code, save it to /QR folder, and show it in Tkinter"""
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    
    # Ensure folder exists
    os.makedirs("QR", exist_ok=True)

    # Save QR code
    qr_path = os.path.join("QR", "flask_qr.png")
    qr = qrcode.make(url)
    qr.save(qr_path)  # Save to disk
    print(f"✅ QR saved at: {qr_path}")

    # Load for display
    img = Image.open(qr_path)
    img = img.resize((150, 150))
    photo = ImageTk.PhotoImage(img)

    # Display inside Tkinter frame
    tk.Label(frame, image=photo, bg="white").pack(pady=5)
    frame.image = photo  # prevent garbage collection

# ======= Login Functions =======

def login():
    login = tk.Tk()
    login.title("Login")
    login.geometry("400x300")
    login.configure(bg='#e8e8e8')
    
    tk.Label(login, text="Login Page", font=("Arial", 18, "bold"), bg='#e8e8e8',fg='#333').pack(pady=20)
    tk.Label(login, text="Username: ",bg="#f2f2f2", font=( "Arial", 12)).pack(pady=(10,0))
    username_enter = tk.Entry(login, width=25, font= ("Arial", 12))
    username_enter.pack(pady=5)
    tk.Label(login, text="Password: ",bg="#f2f2f2", font=("Arial", 12)).pack(pady=(10, 0))
    password_entry = tk.Entry(login, width=25, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)
    
    def validate_login():
        username = username_enter.get().strip()
        password = password_entry.get().strip()
        database = Database()        
        if database.fetchlogin(username, password):
            login.destroy()
            mainsystem()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            
    tk.Button(login, text="Login", command=validate_login, bg="#0078D7", fg="white",
              font=("Arial", 12, "bold"), width=15, height=1).pack(pady=20)
    login.mainloop()

# ======= Main Functions =======

def mainsystem():
    # Load models
    model = YOLO("./Models/best0.1.pt")
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    names = model.names

    # Prepare log file
    log_file = os.path.join(
        r"C:\Users\vidye\OneDrive\Desktop\DYP Project\PlateDetection\OutputNoPlate",
        f"Plates_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )

    # Data tracking variables
    id_to_plate = {}
    EntryFlag = True

    # Capture video
    cap = cv2.VideoCapture("./Videos/mycarplate.mp4")

    root = tk.Tk()
    root.title("Number Plate Detection")
    root.geometry("1920x1080")
    root.configure(bg="#e8e8e8")

    # Configure root grid (2x2 layout)
    root.rowconfigure(0, weight=2, uniform="row")   # Top row: video + tables
    root.rowconfigure(1, weight=1, uniform="row")   # Bottom row: live tab + buttons
    root.columnconfigure(0, weight=1, uniform="col")
    root.columnconfigure(1, weight=1, uniform="col")

    # ====================== Frames ====================== #

    # --- Video Frame ---
    video_frame = tk.Label(root, bg="black")
    video_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

    # --- Table Frame ---
    table_frame = tk.Frame(root, bg="#e8e8e8")
    table_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

    # --- Live Detection Log Frame ---
    liveDetactiontab_frame = tk.Frame(root, bg="#e8e8e8")
    liveDetactiontab_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

    # --- Button Frame ---
    button_frame = tk.Frame(root, bg="#e8e8e8")
    button_frame.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

    # ====================== Widgets ====================== #

    # --- Live Detection Tab ---
    liveDetactiontab = scrolledtext.ScrolledText(
        liveDetactiontab_frame, wrap=tk.WORD, bg="#f7f7f7", fg="black", font=("Arial", 12)
    )
    liveDetactiontab.pack(expand=True, fill="both", padx=10, pady=10)

    # --- Buttons ---
    tk.Button(button_frame, text="Replay Video",command=lambda:replay_video(), width=15, height=2).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(button_frame, text="Entry",command=lambda:setEntryFlag(), width=15, height=2).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(button_frame, text="Exit",command=lambda:setExitFlag(), width=15, height=2).grid(row=0, column=2, padx=10, pady=10)

    # Center buttons horizontally
    for i in range(3):
        button_frame.columnconfigure(i, weight=1)
        
    # Configure grid for table_frame
    for i in range(4):  # 4 rows total: label/table, label/table
        table_frame.rowconfigure(i, weight=1, uniform="row_t")
    for j in range(2):  # 2 columns: left & right
        table_frame.columnconfigure(j, weight=1, uniform="col_t")

    # --- Entry Table ---
    entry_label = tk.Label(table_frame, text="Entry Table", font=("Arial", 14, "bold"), bg="#e8e8e8")
    entry_label.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="n")
    table = ttk.Treeview(table_frame, columns=("No", "Plate"), show='headings')
    table.heading("No", text="No.")
    table.heading("Plate", text="Plate Number")
    table.column("No", width=80, anchor="center")
    table.column("Plate", width=200, anchor="center")
    table.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # --- Exit Table ---
    exit_label = tk.Label(table_frame, text="Exit Table", font=("Arial", 14, "bold"), bg="#e8e8e8")
    exit_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="n")
    exitTable = ttk.Treeview(table_frame, columns=("No", "Plate"), show='headings')
    exitTable.heading("No", text="No.")
    exitTable.heading("Plate", text="Plate Number")
    exitTable.column("No", width=80, anchor="center")
    exitTable.column("Plate", width=200, anchor="center")
    exitTable.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # --- Bill Table ---
    bill_label = tk.Label(table_frame, text="Bill Table", font=("Arial", 14, "bold"), bg="#e8e8e8")
    bill_label.grid(row=0, column=1, padx=10, pady=(0, 5), sticky="n")
    billTable = ttk.Treeview(table_frame, columns=("Car No.", "Duration", "Amount"), show='headings')
    billTable.heading("Car No.", text="Car No.")
    billTable.heading("Duration", text="Duration")
    billTable.heading("Amount", text="Amount")
    billTable.column("Car No.", width=80, anchor="center")
    billTable.column("Duration", width=80, anchor="center")
    billTable.column("Amount", width=80, anchor="center")
    billTable.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")

    # --- QR Table ---
    qr_label = tk.Label(table_frame, text="QR Table", font=("Arial", 14, "bold"), bg="#e8e8e8")
    qr_label.grid(row=2, column=1, padx=10, pady=(10, 5), sticky="n")
    QrTab = ttk.Treeview(table_frame, columns=("QR",), show='headings')
    QrTab.heading("QR", text="QR Details")
    QrTab.column("QR", width=200, anchor="center")
    QrTab.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="nsew")
    showFlaskQR(QrTab)

    # ====================== Sets ====================== #
    enter_no_plate = set()
    exit_no_plate = set()


    database = Database()
    # ---------------- Functions ---------------- #
    def log_message(msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        liveDetactiontab.insert(tk.END, f"{timestamp} | {msg}\n")
        liveDetactiontab.see(tk.END)
        return timestamp

    def display_entry():
        """Display sorted entry plates."""
        table.delete(*table.get_children())
        sorted_entries = sorted(enter_no_plate)
        for i, plate in enumerate(sorted_entries, start=1):
            table.insert("", tk.END, values=(i, plate))

    def display_exit():
        """Display sorted exit plates."""
        exitTable.delete(*exitTable.get_children())
        sorted_exits = sorted(exit_no_plate)
        for i, plate in enumerate(sorted_exits, start=1):
            exitTable.insert("", tk.END, values=(i, plate))

    def setEntryFlag():
        nonlocal EntryFlag
        EntryFlag = True
        log_message("🟩 Entry Mode Active")
        print("🟩 Entry Mode Active")
        replay_video()

    def setExitFlag():
        nonlocal EntryFlag
        EntryFlag = False
        log_message("🟥 Exit Mode Active")
        print("🟥 Exit Mode Active")
        replay_video()

    def replay_video():
        """Restart the video and clear all stored data."""
        nonlocal cap
        cap.release()
        cap = cv2.VideoCapture("./Videos/mycarplate.mp4")
        table.delete(*table.get_children())
        exitTable.delete(*exitTable.get_children())
        liveDetactiontab.delete(1.0, tk.END)
        enter_no_plate.clear()
        exit_no_plate.clear()
        id_to_plate.clear()
        process_video()

    def updateBillTable(plate, duration, bill):
        """Update the bill table with new entry."""
        billTable.insert("", tk.END, values=(plate, str(duration), f"₹{bill}"))

    def process_video():
        """Main loop that processes each video frame."""
        nonlocal cap
        ret, frame = cap.read()
        if not ret:
            print("Video ended.")
            cap.release()
            return

        frame = cv2.resize(frame, (480, 270))
        results = model.track(frame, persist=True)

        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.int().cpu().tolist()

            for track_id, box, class_id in zip(ids, boxes, class_ids):
                x1, y1, x2, y2 = box
                cls_name = names[class_id]

                # Draw detection box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cvzone.putTextRect(frame, cls_name.upper(), (x1, y1 - 10),
                                scale=1, thickness=2, colorT=(255, 255, 255),
                                colorR=(0, 0, 255), offset=5, border=2)

                # Process only number plates
                if cls_name.lower() == "numberplate":
                    cropped_plate = frame[y1:y2, x1:x2]
                    if cropped_plate.size == 0:
                        continue

                    # Run OCR once per new track_id
                    if track_id not in id_to_plate:
                        result = ocr.ocr(cropped_plate, cls=True)
                        plate_text = ""
                        for line in result:
                            if line:
                                plate_text += ''.join([word[1][0] for word in line])
                        plate_text = plate_text.replace(" ", "").strip()

                        if plate_text:
                            id_to_plate[track_id] = plate_text
                            timestamp = log_message(f"ID: {track_id} | Plate: {plate_text}")

                            if EntryFlag:
                                if plate_text not in enter_no_plate:
                                    enter_no_plate.add(plate_text)
                                    print(f"✅ Saved Entry: {plate_text}")
                                    database.insertVehicle(plate_text)
                                    display_entry()
                            else:
                                if plate_text not in exit_no_plate:
                                    exit_no_plate.add(plate_text)
                                    print(f"🚗 Saved Exit: {plate_text}")
                                    database.insertParkingExit(plate_text)
                                    
                                    print(database.fetchBill())
                                    bill, duration = database.fetchBill() # doubt in this line
                                    print(bill,duration,"========================")
                                    updateBillTable(plate_text, duration, bill)
                                    display_exit()

                # Show label with ID and detected text
                label = f"ID: {track_id} | {id_to_plate.get(track_id, 'Detecting...')}"
                cvzone.putTextRect(frame, label, (x1, y2 + 10),
                                scale=1, thickness=2, colorT=(0, 0, 0),
                                colorR=(225, 225, 0), offset=5, border=2)

        # Convert and show video frame in Tkinter
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        video_frame.config(image=imgtk)
        video_frame.image = imgtk
        root.after(10, process_video)

    # Start video processing
    process_video()
    root.mainloop()

# ======= Web Application Functions =======
    
def start_app():
    app = ParkingApp()
    app.run()

# ======= Lounching 2 Thread of Web Application ======= 
    
threading.Thread(target=start_app, daemon=True).start()

# == Main Program Start ==

login()