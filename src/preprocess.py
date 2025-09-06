# src/preprocess.py

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box

# --------------------------
# 1. LOAD CSV DATA DYNAMICALLY
# --------------------------
def load_data(filepath):
    """
    Load CSV dynamically.
    Detects latitude, longitude, and date columns automatically.
    """
    df = pd.read_csv(filepath)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Detect latitude & longitude columns
    lat_col = next((c for c in df.columns if "lat" in c.lower()), None)
    lon_col = next((c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()), None)
    if not lat_col or not lon_col:
        raise ValueError("No latitude/longitude column found in CSV")
    
    df = df.dropna(subset=[lat_col, lon_col])
    df = df.rename(columns={lat_col: "Latitude", lon_col: "Longitude"})

    # Detect date column, else use today
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    if date_col:
        df["Date"] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        df["Date"] = pd.to_datetime("today")

    # Optional: fill missing CrimeType
    if "CrimeType" not in df.columns:
        df["CrimeType"] = "Unknown"
    else:
        df["CrimeType"] = df["CrimeType"].fillna("Unknown")

    return df

# --------------------------
# 2. CREATE GEO DATAFRAME
# --------------------------
def create_geodf(df):
    """
    Convert DataFrame to GeoDataFrame
    """
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326"
    )
    return gdf

# --------------------------
# 3. CREATE GRID FOR HEATMAP
# --------------------------
def create_grid(gdf, cell_size_m=2000):
    """
    Create square grid covering the area of gdf.
    cell_size_m: cell size in meters
    """
    # Convert to metric CRS (meters)
    gdf_m = gdf.to_crs(epsg=3857)
    minx, miny, maxx, maxy = gdf_m.total_bounds

    # Compute number of cells in x and y directions
    x_cells = int((maxx - minx) // cell_size_m + 1)
    y_cells = int((maxy - miny) // cell_size_m + 1)

    # Generate grid polygons
    polygons = []
    for i in range(x_cells):
        for j in range(y_cells):
            x0 = minx + i * cell_size_m
            y0 = miny + j * cell_size_m
            polygons.append(box(x0, y0, x0 + cell_size_m, y0 + cell_size_m))

    grid = gpd.GeoDataFrame({'grid_id': range(len(polygons)), 'geometry': polygons}, crs=gdf_m.crs)
    return grid.to_crs(gdf.crs)

# --------------------------
# 4. ASSIGN POINTS TO GRID (WITHOUT RTREE)
# --------------------------
def assign_points_to_grid(gdf, grid):
    """
    Assign each point to a grid cell WITHOUT using sjoin.
    Works without rtree or pygeos.
    """
    grid_ids = []
    grid_list = list(grid.itertuples(index=False))
    for point in gdf.geometry:
        assigned = None
        for row in grid_list:
            if row.geometry.contains(point):
                assigned = row.grid_id
                break
        grid_ids.append(assigned)
    gdf["grid_id"] = grid_ids
    return gdf

# --------------------------
# 5. AGGREGATE DAILY COUNTS FOR PROPHET
# --------------------------
def aggregate_daily_counts(joined_gdf):
    """
    Aggregate crime counts by day
    Returns DataFrame with columns ds (date) and y (count)
    """
    if "Date" not in joined_gdf.columns:
        joined_gdf["Date"] = pd.to_datetime("today")
    joined_gdf["Date"] = pd.to_datetime(joined_gdf["Date"], errors="coerce")
    
    counts = joined_gdf.groupby("Date").size().reset_index(name="y")
    counts = counts.rename(columns={"Date": "ds"})
    counts = counts.sort_values("ds").reset_index(drop=True)
    return counts
