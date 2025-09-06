# AI Crime Predictor

## Overview
AI Crime Predictor is a Flask-based web application for predicting and visualizing crime patterns. It allows users to upload crime data, train a forecasting model, view crime statistics in charts, and explore a detailed crime data table.

## Features
- Upload crime CSV data (`crime_data.csv`)
- Train a predictive model for crime forecasting
- Visualize crime data:
  - Predicted crimes for the next 30 days
  - Crime type distribution
  - Crimes per grid cell
  - Historical daily crimes
- View detailed crime table with ML summary
- Download trained model (`crime_forecast.pkl`)
- Display heatmap data of crime locations
- Fully responsive Bootstrap-based UI

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/codinggujarat/AI-Crime-Predictor](https://github.com/codinggujarat/AI-Crime-Predictor)
   cd ai-crime-predictor
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python src/app.py
   ```

## File Structure
```
ai-crime-predictor/
│
├─ data/
│  ├─ crime_data.csv           # Uploaded crime data
│  └─ daily_counts.csv         # Aggregated daily counts
│
├─ models/
│  └─ crime_forecast.pkl       # Trained model
│
├─ src/
│  ├─ app.py                   # Main Flask app
│  ├─ preprocess.py            # Data preprocessing functions
│  └─ model.py                 # ML model training and forecasting
│
├─ templates/
│  ├─ index.html
│  ├─ table.html
│  └─ forecast_chart.html
│
├─ static/
│  └─ css, js, images
│
└─ README.md
```

## Usage
1. Open the app in your browser at `http://127.0.0.1:5000/`
2. Upload a CSV file with crime data
3. Train the model using the upload
4. Explore charts and tables for insights
5. Download the trained model for further use
