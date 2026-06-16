# AI-Based Classroom Behavior Monitoring with Optimized Video Storage

## Overview

This project is an AI-powered classroom surveillance system designed to automatically detect abnormal student behavior and reduce unnecessary video storage. The system uses YOLOv8 Pose Estimation, ByteTrack tracking, and custom behavior analysis algorithms to identify classroom anomalies such as:

* Fighting / Aggressive Behavior
* Standing on Benches

Instead of recording video continuously, the system stores only anomaly-related clips, significantly reducing storage requirements while preserving important events.

---

## Features

### Real-Time Human Detection

* Detects students using YOLOv8s-Pose.
* Extracts 17 human body keypoints.

### Pose-Based Standing Detection

* Learns normal seated posture during baseline calibration.
* Detects students standing on benches using:

  * Shoulder elevation analysis
  * Leg extension analysis
  * Ankle elevation analysis

### Fight Detection

* Uses wrist velocity estimation.
* Uses proximity analysis through Intersection over Union (IoU).
* Generates alerts only when aggressive movement and close interaction occur simultaneously.

### Multi-Object Tracking

* Tracks individuals using ByteTrack.
* Maintains unique IDs for each student.

### Optimized Video Storage

* Records only anomaly events.
* Supports:

  * Pre-event buffering
  * Event recording
  * Post-event recording
* Reduces storage consumption compared to continuous CCTV recording.

---

## Technologies Used

### Deep Learning

* YOLOv8s-Pose

### Computer Vision

* Human Detection
* Pose Estimation
* Motion Analysis
* Bounding Box Analysis
* Object Tracking

### Libraries

* Python
* OpenCV
* NumPy
* Ultralytics YOLO

---

## System Architecture

```text
CCTV Camera
      │
      ▼
Video Stream
      │
      ▼
YOLOv8 Pose Estimation
      │
      ▼
Human Keypoint Extraction
      │
 ┌────┴─────┐
 ▼          ▼
Standing    Fighting
Detection   Detection
 ▼          ▼
Anomaly Classification
      │
      ▼
Alert Generation
      │
      ▼
Optimized Video Storage
      │
      ▼
Saved Anomaly Clips
```

---

## Detection Methodology

### Standing on Bench Detection

The system first performs baseline calibration to learn normal seated posture.

An anomaly is triggered when:

* Shoulder position is significantly higher than baseline.
* Hip-to-ankle distance increases.
* Ankles are elevated above the normal floor position.
* Conditions persist for multiple consecutive frames.

### Fighting Detection

The system calculates:

* Wrist movement velocity
* Bounding box overlap (IoU)

A fight alert is generated only when:

* Wrist velocity exceeds a predefined threshold.
* Students are in close proximity.
* Conditions persist across multiple frames.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/AI-Classroom-Monitoring.git
cd AI-Classroom-Monitoring
```

### Install Dependencies

```bash
pip install ultralytics opencv-python numpy
```

---

## Download YOLO Model

The project uses:

```text
yolov8s-pose.pt
```

Download automatically through Ultralytics or place the model file in the project directory.

---

## Run the Project

Update:

```python
VIDEO_SOURCE = "new.mp4"
```

Then execute:

```bash
python main.py
```

Press:

```text
q
```

to exit.

---

## Project Structure

```text
AI-Classroom-Monitoring/
│
├── main.py
├── anomaly_recordings/
├── yolov8s-pose.pt
├── README.md
└── sample_videos/
```

---

## Results

The system successfully:

* Detects fighting behavior.
* Detects standing on benches.
* Maintains student identities using ByteTrack.
* Generates real-time alerts.
* Stores only anomaly clips.

---

## Future Enhancements

* Sleeping Detection
* Mobile Notification System
* Multi-Camera Monitoring
* Cloud Storage Integration
* Student Attendance Integration
* Transformer-Based Action Recognition
* Edge AI Deployment using Jetson Devices

---

## Applications

* Smart Classrooms
* Educational Institutions
* School Safety Monitoring
* Classroom Discipline Monitoring
* Automated Surveillance Systems

---

## Authors

* Abhinav Singh
* Abdul Hafeez
* Kaushal Jain

### Guide

Dr. Vinay TR

Department of Artificial Intelligence and Data Science

---

## License

This project is developed for academic and educational purposes.
# AI-Based Classroom Behavior Monitoring with Optimized Video Storage

## Overview

This project is an AI-powered classroom surveillance system designed to automatically detect abnormal student behavior and reduce unnecessary video storage. The system uses YOLOv8 Pose Estimation, ByteTrack tracking, and custom behavior analysis algorithms to identify classroom anomalies such as:

* Fighting / Aggressive Behavior
* Standing on Benches

Instead of recording video continuously, the system stores only anomaly-related clips, significantly reducing storage requirements while preserving important events.

---

## Features

### Real-Time Human Detection

* Detects students using YOLOv8s-Pose.
* Extracts 17 human body keypoints.

### Pose-Based Standing Detection

* Learns normal seated posture during baseline calibration.
* Detects students standing on benches using:

  * Shoulder elevation analysis
  * Leg extension analysis
  * Ankle elevation analysis

### Fight Detection

* Uses wrist velocity estimation.
* Uses proximity analysis through Intersection over Union (IoU).
* Generates alerts only when aggressive movement and close interaction occur simultaneously.

### Multi-Object Tracking

* Tracks individuals using ByteTrack.
* Maintains unique IDs for each student.

### Optimized Video Storage

* Records only anomaly events.
* Supports:

  * Pre-event buffering
  * Event recording
  * Post-event recording
* Reduces storage consumption compared to continuous CCTV recording.

---

## Technologies Used

### Deep Learning

* YOLOv8s-Pose

### Computer Vision

* Human Detection
* Pose Estimation
* Motion Analysis
* Bounding Box Analysis
* Object Tracking

### Libraries

* Python
* OpenCV
* NumPy
* Ultralytics YOLO

---

## System Architecture

```text
CCTV Camera
      │
      ▼
Video Stream
      │
      ▼
YOLOv8 Pose Estimation
      │
      ▼
Human Keypoint Extraction
      │
 ┌────┴─────┐
 ▼          ▼
Standing    Fighting
Detection   Detection
 ▼          ▼
Anomaly Classification
      │
      ▼
Alert Generation
      │
      ▼
Optimized Video Storage
      │
      ▼
Saved Anomaly Clips
```

---

## Detection Methodology

### Standing on Bench Detection

The system first performs baseline calibration to learn normal seated posture.

An anomaly is triggered when:

* Shoulder position is significantly higher than baseline.
* Hip-to-ankle distance increases.
* Ankles are elevated above the normal floor position.
* Conditions persist for multiple consecutive frames.

### Fighting Detection

The system calculates:

* Wrist movement velocity
* Bounding box overlap (IoU)

A fight alert is generated only when:

* Wrist velocity exceeds a predefined threshold.
* Students are in close proximity.
* Conditions persist across multiple frames.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/AI-Classroom-Monitoring.git
cd AI-Classroom-Monitoring
```

### Install Dependencies

```bash
pip install ultralytics opencv-python numpy
```

---

## Download YOLO Model

The project uses:

```text
yolov8s-pose.pt
```

Download automatically through Ultralytics or place the model file in the project directory.

---

## Run the Project

Update:

```python
VIDEO_SOURCE = "new.mp4"
```

Then execute:

```bash
python main.py
```

Press:

```text
q
```

to exit.

---

## Project Structure

```text
AI-Classroom-Monitoring/
│
├── main.py
├── anomaly_recordings/
├── yolov8s-pose.pt
├── README.md
└── sample_videos/
```

---

## Results

The system successfully:

* Detects fighting behavior.
* Detects standing on benches.
* Maintains student identities using ByteTrack.
* Generates real-time alerts.
* Stores only anomaly clips.

---

## Future Enhancements

* Sleeping Detection
* Mobile Notification System
* Multi-Camera Monitoring
* Cloud Storage Integration
* Student Attendance Integration
* Transformer-Based Action Recognition
* Edge AI Deployment using Jetson Devices

---

## Applications

* Smart Classrooms
* Educational Institutions
* School Safety Monitoring
* Classroom Discipline Monitoring
* Automated Surveillance Systems

---

## Authors

* Abhinav Singh
* Abdul Hafeez
* Kaushal Jain

### Guide

Dr. Vinay TR

Department of Artificial Intelligence and Data Science

---

## License

This project is developed for academic and educational purposes.
