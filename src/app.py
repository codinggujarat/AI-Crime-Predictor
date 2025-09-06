import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from src.preprocess import load_data, create_geodf, create_grid, assign_points_to_grid, aggregate_daily_counts
from src.model import train_model, load_model, forecast_future
from datetime import datetime

# ---------------- Flask app setup ----------------
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates"),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../static")
)

# ---------------- Directories ----------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
MODEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../models")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

CRIME_FILE = os.path.join(UPLOAD_FOLDER, "crime_data.csv")

# ---------------- Routes ----------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file!"}), 400

    # Save uploaded file as crime_data.csv
    file.save(CRIME_FILE)

    try:
        df = load_data(CRIME_FILE)
        gdf = create_geodf(df)
        grid = create_grid(gdf)
        joined = assign_points_to_grid(gdf, grid)
        daily_counts = aggregate_daily_counts(joined)
        daily_counts.to_csv(os.path.join(UPLOAD_FOLDER, "daily_counts.csv"), index=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "✅ File uploaded successfully!", "columns": list(df.columns), "rows": len(df)})

@app.route("/train", methods=["POST"])
def train():
    daily_counts_path = os.path.join(UPLOAD_FOLDER, "daily_counts.csv")
    if not os.path.exists(daily_counts_path):
        return jsonify({"error": "Please upload CSV first!"}), 400

    daily_counts = pd.read_csv(daily_counts_path)
    daily_counts = daily_counts.rename(columns={daily_counts.columns[0]: "ds", daily_counts.columns[1]: "y"})

    try:
        train_model(daily_counts, date_col="ds", target_col="y")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "✅ Model trained successfully!"})

# ---------------- Updated Table Route ----------------
@app.route("/table")
def crime_table():
    if not os.path.exists(CRIME_FILE):
        return render_template("table.html", crime_list=[], summary="No data available. Please upload CSV first!")

    df = pd.read_csv(CRIME_FILE)

    # Convert numeric fields
    if 'severity_score' in df.columns:
        df['severity_score'] = pd.to_numeric(df['severity_score'], errors='coerce')

    crime_list = df.to_dict(orient="records")

    # Optional ML summary: top locations and top crime types
    top_grids = df['location'].value_counts().nlargest(2).index.tolist() if 'location' in df.columns else []
    top_crimes = df['CrimeType'].value_counts().nlargest(2).index.tolist() if 'CrimeType' in df.columns else []
    summary = f"In the next week, {', '.join(top_grids)} have the highest probability of {', '.join(top_crimes)}." if top_grids and top_crimes else "ML summary not available."

    return render_template("table.html", crime_list=crime_list, summary=summary)

@app.route("/forecast", methods=["GET"])
def forecast():
    model = load_model()
    if model is None:
        return jsonify({"error": "Model not trained yet!"}), 400

    forecast_df = forecast_future(model, periods=30)
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    # Forecast Line Chart
    chart_data = {
        "labels": forecast_df["ds"].dt.strftime("%Y-%m-%d").tolist(),
        "data": forecast_df["yhat"].round(2).tolist()
    }

    # Initialize variables
    crime_types = []
    crime_counts = []
    grid_ids = []
    grid_counts = []
    daily_labels = []
    daily_values = []

    # Load crime CSV
    crime_file = os.path.join(UPLOAD_FOLDER, "crime_data.csv")
    if os.path.exists(crime_file):
        df = pd.read_csv(crime_file)

        # Crime type distribution
        if 'CrimeType' in df.columns:
            crime_counts_series = df['CrimeType'].value_counts()
            crime_types = list(crime_counts_series.index)
            crime_counts = [int(x) for x in crime_counts_series.values]

        # Grid counts
        gdf = create_geodf(df)
        grid = create_grid(gdf)
        joined = assign_points_to_grid(gdf, grid)
        grid_counts_series = joined['grid_id'].value_counts().sort_index()
        grid_ids = [str(x) for x in grid_counts_series.index]
        grid_counts = [int(x) for x in grid_counts_series.values]

        # Historical daily counts
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            daily_counts_series = df.groupby('date').size().sort_index()
            daily_labels = [d.strftime("%Y-%m-%d") for d in daily_counts_series.index]
            daily_values = [int(x) for x in daily_counts_series.values]

    # Render template
    return render_template(
        "forecast_chart.html",
        chart_data=chart_data,
        crime_types=crime_types,
        crime_counts=crime_counts,
        grid_ids=grid_ids,
        grid_counts=grid_counts,
        daily_labels=daily_labels,
        daily_values=daily_values
    )

@app.route("/download-model", methods=["GET"])
def download_model():
    model_file = os.path.join(MODEL_FOLDER, "crime_forecast.pkl")
    if not os.path.exists(model_file):
        return jsonify({"error": "Train the model first!"}), 400
    return send_from_directory(MODEL_FOLDER, "crime_forecast.pkl", as_attachment=True)

@app.route("/download-demo", methods=["GET"])
def download_demo_csv():
    demo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "crime_data.csv")
    # Explanation: __file__ = src/app.py
    # os.path.dirname(__file__) = src
    # os.path.dirname(os.path.dirname(__file__)) = project root
    # + "data/crime_data.csv" = correct path

    if not os.path.exists(demo_file):
        return "Demo file not found!", 404

    return send_from_directory(
        directory=os.path.dirname(demo_file),
        path=os.path.basename(demo_file),
        as_attachment=True
    )

@app.route("/get-heatmap-data", methods=["GET"])
def get_heatmap_data():
    if not os.path.exists(CRIME_FILE):
        return jsonify([])

    df = pd.read_csv(CRIME_FILE)
    df.columns = [c.strip().lower() for c in df.columns]
    lat_col = next((c for c in df.columns if "lat" in c), None)
    lon_col = next((c for c in df.columns if "lon" in c or "lng" in c), None)

    if lat_col and lon_col:
        result = [{"latitude": row[lat_col], "longitude": row[lon_col], "intensity": 0.7} for _, row in df.iterrows()]
        return jsonify(result)

    return jsonify([])

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
