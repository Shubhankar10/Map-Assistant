# Map Assistant
## Project Overview

The Map Assistant is an intelligent map planner that integrates two relational databases — one for **user & trip data** and another for **POI, routes, and API results** — along with an **LLM layer** for natural language interpretation, summarization, and explanation.

The system provides personalized trip suggestions, builds structured itineraries, aggregates and summarizes reviews, finds balanced meeting points for groups, optimizes multi-spot routes, compares flights/hotels/trains, and supports journaling of travel experiences.

The design separates **deterministic data operations** (SQL, spatial queries, API calls) from **LLM-driven tasks** (parameter extraction, summarization, narration, trade-off explanation).

---

# Key Features

### 1. Personalized Itinerary Planner

### 2. Smart Trip Suggestions

### 3. Review Aggregator & Summarizer

### 4. Meeting Point Recommender

### 5. Multi-spot Route Optimization & Comparison

### 6. User Trip Journal

---

# Data Architecture

### A. User & Trip Management DB (Relational DB 1)

Stores **user profiles, preferences, itineraries and journals**.

### B. POI / API & Spatial DB (Relational DB 2)

Stores **POIs, reviews, cached routes, transport & hotel offers** with spatial queries via PostGIS.

### C. LLM Layer (Query Breakdown & Web Data Gathering)

Handles **natural language → structured queries**, **summaries**, **narratives**, and **explanations of trade-offs**.

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/Map-Assistant.git
   cd Map-Assistant
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:

   ```
   LLM_API_KEY=your_nvidia_build_api_key_here
   MAPS_API_KEY=your_google_api_key_here

---

## How to Run the Program

### **Option 1 — Run the Web App (Browser Interface)**

To launch the interactive Streamlit interface:

```bash
streamlit run app.py
```

This will open the app in your default web browser (e.g., [http://localhost:8501](http://localhost:8501)).
You can input travel queries, explore itineraries, and view summarized recommendations.

---

### **Option 2 — Run the Core Logic from Console**

To test the backend flow directly from terminal:

1. Open `main.py`.
2. Locate the **demo query section**, e.g.:

   ```python
   demo_query = "Plan a 3-day budget heritage trip to Jaipur"
   ```
3. Modify the query as desired.
4. Run the script:

   ```bash
   python main.py
   ```

This will print the **structured context**, **retrieved POIs**, and **LLM-generated itinerary** directly to the console.

---
