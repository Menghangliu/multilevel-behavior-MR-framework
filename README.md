# Multilevel Behavior Recognition and MR Interaction Framework

This repository contains the core implementation used in the paper:

**“A Multilevel Computing Framework for Behavior Recognition and Interaction in Mixed Reality Workspaces.”**

It includes the essential components for reproducing the behavioral state computation pipeline and the mapping of multilevel behavioral cues to MR spatial adaptations.

---

## 📌 Repository Overview

This project integrates three main modules:

1. **Behavior data extraction**  
   - Using the ZED depth camera for skeletal tracking  
   - Using Google Vision API for facial emotion detection  

2. **Behavior state computation**  
   - Implemented in Rhino/Grasshopper scripts  
   - Computes lower-body posture, upper-limb posture, social orientation, and emotional cues  
   - Normalizes all state values to the 0–1 range  

3. **MR interaction mapping**  
   - Unity + Meta XR SDK  
   - Receives behavioral state values and updates virtual spatial attributes (openness, partitioning, regularity, ceiling height, saturation, etc.)  

The repository provides the key logic required to replicate the main methodology presented in the manuscript.

---

## 📁 Folder Structure

root/
│
├── body_tracking_and_emotion_recognition.py
│ Python script for:
│ - ZED skeletal tracking (joint extraction)
│ - Google Vision API emotion recognition
│
├── Rhino&Grasshopper/
│ Grasshopper definitions and scripts for:
│ - Multilevel behavior state computation
│ - Lower-body state (hip & knee angles)
│ - Upper-limb state (shoulder & elbow angles)
│ - Social state (head vector–based)
│ - Attentional state (head vector–based)
│ - Spatial openness adjustment
│ - Spatial regularity adjustment
│ - Partitioning height control
│ - Ceiling height control
│ - Hue and saturation control
│ - Mapping normalized states to MR parameters
│
├── Humanizing_MR(Unity)/
│ Unity scripts for:
│ - Integration with Meta Quest 3 environment
│
├── LICENSE
│
└── README.md

##  Usage Instructions

### 1. Behavior Data Extraction (Python)

Run:

python body_tracking_and_emotion_recognition.py
Functions performed:

Extract 34 skeletal keypoints using ZED SDK

Detect emotion likelihoods using Google Vision API

Output send via UDP to Grasshopper

### 2. Behavior State Computation (Grasshopper)
Open the Grasshopper definitions inside Rhino&Grasshopper/.

The scripts perform:

Compute joint angles (hip, knee, shoulder, elbow)

Angle normalization (min–max scaling)

Lower-body physical state computation---Spatial Openness

Upper-limb physical state computation---Spatial Regularity

Head-vector–based social state---Spatial Partitioning 

Attentional state---Ceiling Height

Emotional state---Color Saturation

Outputs are streamed to Unity using OSC/UDP.

### 3. MR Interaction Mapping (Unity)
Place the C# scripts in Humanizing_MR(Unity)/ into your Unity project.

These scripts update MR spatial parameters such as:

Use Meta XR SDK to deploy to the Meta Quest 3.



## Requirements
### Python
Python 3.10+

numpy

opencv-python

google-cloud-vision

pyzed (ZED SDK Python API)

Install using:
pip install -r requirements.txt

### Unity

Unity 2022+

Meta XR SDK

TextMeshPro

Standard C# environment

🔍 Reproducibility Notes
This repository provides all essential components required to reproduce:

Multilevel behavioral state recognition

Normalized state computation

Mapping from behavioral states to MR environment transformations

Additional details and full methodology are described in Section 3–4 of the revised manuscript.

📄 License
This project is released under the MIT License.

✉ Contact

For academic questions regarding this implementation, please contact:

Menghang Liu
Email: lmh564465@outlook.com




