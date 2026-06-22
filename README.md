### Project Name

**AI Smart Parking Management System Using Automatic Number Plate Recognition (ANPR)**

### Project Description

The **AI Smart Parking Management System** is an intelligent parking solution that automates vehicle entry, tracking, payment, and exit using **Artificial Intelligence**, **Computer Vision**, and **QR-based payment integration**.

When a vehicle enters the parking area, a camera captures the vehicle's number plate. Using **Automatic Number Plate Recognition (ANPR)** technology, the system detects and extracts the vehicle registration number and stores it in a database along with the entry time. The system continuously maintains parking records without requiring manual intervention.

When the vehicle is ready to leave, the camera again detects the number plate at the exit gate. The system retrieves the corresponding entry record from the database and calculates the total parking duration and parking fee automatically. A unique QR code is then generated for the customer to make the payment through any supported digital payment application.

After successful payment verification, the Python-based backend updates the parking record, marks the payment as completed, and sends a signal to the automated gate controller. The exit gate then opens automatically, allowing the vehicle to leave the parking area. The system also generates parking reports, transaction records, and vehicle history for efficient parking management.

### Key Features

* AI-based Number Plate Detection and Recognition
* Automatic Vehicle Entry and Exit Tracking
* Real-Time Database Storage
* Parking Duration Calculation
* Automatic Fee Generation
* QR Code-Based Digital Payment
* Payment Verification System
* Automated Gate Control
* Vehicle and Transaction History
* Parking Analytics and Reports

### Technologies Used

* **Python**
* **OpenCV**
* **YOLO (Object Detection)**
* **EasyOCR/Tesseract OCR**
* **MySQL**
* **Flask**
* **QR Code Generation API**
* **ESP32/Arduino (Gate Automation)**
* **HTML, CSS, JavaScript**

<img width="740" height="1600" alt="PhoneInterface" src="https://github.com/user-attachments/assets/23650d5e-781c-477c-9901-8eebba7b1efb" />
