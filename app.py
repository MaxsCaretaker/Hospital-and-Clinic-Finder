import tkinter as tk
from tkinter import ttk, messagebox
import requests
import folium
import os
import webbrowser

# ── Theme ───────────────────────────────────────────
BG = "#1e1e2e"
CARD = "#2a2a3e"
ACCENT = "#e05c5c"
TEXT = "#ffffff"
SUBTEXT = "#aaaacc"
GREEN = "#4caf50"
RED = "#ef5350"

HEADERS = {"User-Agent": "hospital-finder-app"}

# ── Root ─────────────────────────────────────────────
root = tk.Tk()
root.title("🏥 Hospital & Clinic Finder")
root.geometry("700x650")
root.configure(bg=BG)
root.resizable(False, False)

# ── Functions ─────────────────────────────────────────
def search():
    city = city_var.get().strip()
    if not city:
        messagebox.showwarning("Missing Input", "Please enter a city or zip code.")
        return

    status_var.set("Searching...")
    root.update()
    clear_results()

    # Step 1: Geocode the city
    try:
        geo_response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10
        )
        geo_data = geo_response.json()
    except Exception:
        messagebox.showerror("Error", "Could not connect. Check your internet connection.")
        status_var.set("")
        return

    if not geo_data:
        messagebox.showwarning("Not Found", f"Could not find location: {city}")
        status_var.set("")
        return

    lat = float(geo_data[0]["lat"])
    lon = float(geo_data[0]["lon"])

    # Step 2: Search hospitals
    facility_type = type_var.get()
    query = "hospital" if facility_type == "Hospitals" else \
            "clinic" if facility_type == "Clinics" else "hospital clinic"

    try:
        search_response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 20,
                "viewbox": f"{lon-0.3},{lat+0.3},{lon+0.3},{lat-0.3}",
                "bounded": 1,
                "addressdetails": 1
            },
            headers=HEADERS,
            timeout=10
        )
        results = search_response.json()
    except Exception:
        messagebox.showerror("Error", "Search failed. Please try again.")
        status_var.set("")
        return

    if not results:
        status_var.set("No results found.")
        return

    # Store results for map
    root.search_results = results
    root.search_lat = lat
    root.search_lon = lon

    # Display in list
    for i, place in enumerate(results, 1):
        name = place.get("display_name", "Unknown")
        short_name = name.split(",")[0]
        address = ", ".join(name.split(",")[1:4]).strip()

        frame = tk.Frame(results_frame, bg=CARD, pady=8, padx=12)
        frame.pack(fill="x", pady=3)

        tk.Label(frame, text=f"{i}. {short_name}",
                 font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT,
                 anchor="w").pack(fill="x")
        tk.Label(frame, text=address,
                 font=("Segoe UI", 9), bg=CARD, fg=SUBTEXT,
                 anchor="w").pack(fill="x")

    status_var.set(f"Found {len(results)} facilities near {city}")
    map_btn.config(state="normal")

def clear_results():
    for widget in results_frame.winfo_children():
        widget.destroy()
    map_btn.config(state="disabled")
    root.search_results = []

def open_map():
    results = getattr(root, "search_results", [])
    lat = getattr(root, "search_lat", 34.05)
    lon = getattr(root, "search_lon", -118.24)

    if not results:
        return

    # Build folium map
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Center marker
    folium.Marker(
        [lat, lon],
        popup="Search Location",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

    # Hospital markers
    for place in results:
        p_lat = float(place.get("lat", 0))
        p_lon = float(place.get("lon", 0))
        name = place.get("display_name", "Unknown").split(",")[0]

        folium.Marker(
            [p_lat, p_lon],
            popup=name,
            icon=folium.Icon(color="red", icon="plus-sign")
        ).add_to(m)

    # Save and open in browser
    map_file = os.path.abspath("map.html")
    m.save(map_file)
    webbrowser.open(f"file:///{map_file}")

# ── Header ───────────────────────────────────────────
header = tk.Frame(root, bg=ACCENT, pady=15)
header.pack(fill="x")
tk.Label(header, text="🏥  Hospital & Clinic Finder",
         font=("Segoe UI", 22, "bold"), bg=ACCENT, fg=TEXT).pack()
tk.Label(header, text="Find nearby healthcare facilities",
         font=("Segoe UI", 10), bg=ACCENT, fg="#ddd").pack()

# ── Search Card ──────────────────────────────────────
search_card = tk.Frame(root, bg=CARD, padx=20, pady=15)
search_card.pack(fill="x", padx=20, pady=15)

tk.Label(search_card, text="Search", font=("Segoe UI", 13, "bold"),
         bg=CARD, fg=ACCENT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

# City input
tk.Label(search_card, text="City or Zip Code", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 10))
city_var = tk.StringVar()
tk.Entry(search_card, textvariable=city_var, width=28,
         bg="#3a3a55", fg=TEXT, insertbackground=TEXT,
         relief="flat", font=("Segoe UI", 11)).grid(row=2, column=0, ipady=6, padx=(0, 10))

# Facility type
tk.Label(search_card, text="Facility Type", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w", padx=(0, 10))
type_var = tk.StringVar(value="Both")
ttk.Combobox(search_card, textvariable=type_var, width=12,
             values=["Both", "Hospitals", "Clinics"]).grid(row=2, column=1, padx=(0, 10))

# Search button
def make_btn(parent, text, cmd, color, state="normal"):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg=TEXT, font=("Segoe UI", 10, "bold"),
                     relief="flat", padx=12, pady=6, cursor="hand2", state=state)

make_btn(search_card, "🔍 Search", search, ACCENT).grid(row=2, column=2, padx=5)

# ── Status ───────────────────────────────────────────
status_var = tk.StringVar()
tk.Label(root, textvariable=status_var, font=("Segoe UI", 9),
         bg=BG, fg=SUBTEXT).pack(anchor="w", padx=22)

# ── Results ───────────────────────────────────────────
tk.Label(root, text="Results", font=("Segoe UI", 13, "bold"),
         bg=BG, fg=ACCENT).pack(anchor="w", padx=20, pady=(5, 3))

results_container = tk.Frame(root, bg=BG)
results_container.pack(fill="both", expand=True, padx=20)

scrollbar = tk.Scrollbar(results_container)
scrollbar.pack(side="right", fill="y")

canvas = tk.Canvas(results_container, bg=BG, highlightthickness=0,
                   yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=canvas.yview)

results_frame = tk.Frame(canvas, bg=BG)
canvas_window = canvas.create_window((0, 0), window=results_frame, anchor="nw")

def on_configure(e):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas_window, width=canvas.winfo_width())

results_frame.bind("<Configure>", on_configure)

# ── Map Button ────────────────────────────────────────
map_btn = make_btn(root, "🗺️  View on Map", open_map, "#4caf50", state="disabled")
map_btn.pack(pady=10)

root.search_results = []
root.mainloop()