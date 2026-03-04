# modules/config.py

# Ustawienia wyglądu
THEME_MODE = "Dark"
COLOR_THEME = "blue"

# Ustawienia domyślne analizy
DEFAULT_CONFIG = {
    'initial_sigma': 10.0,
    'default_model': 'Gaussian',
    'savgol_polyorder': 3,
    'savgol_window': 11
}

# Kolory do wykresów (poszerzona paleta)
PEAK_COLORS = ['#FF00FF', '#228B22', '#DC143C', '#FFA500', '#0000CD', '#8B008B', '#FF1493', '#008080', '#FF4500', '#1E90FF']

# --- STRUKTURY DRUGORZĘDOWE (AMID I / I') ---
# Format: (min, max, nazwa_struktury)
# Kolejność na liście definiuje priorytet! Wąskie zakresy wyżej.

STRUCTURE_RANGES_H2O = [
    (1680, 1695, "Beta-Sheet (Anti)"),
    (1695, 1720, "Aggregates (Anti)"),
    (1665, 1680, "Turns"),
    (1658, 1665, "3_10 Helix"),
    (1650, 1658, "Alpha-Helix"),
    (1640, 1650, "Random Coil"),
    (1624, 1640, "Beta-Sheet"),
    (1615, 1624, "Aggregates"),
    (1580, 1615, "Side Chains")
]

STRUCTURE_RANGES_D2O = [
    (1675, 1690, "Beta-Sheet (Anti)"),
    (1690, 1720, "Aggregates (Anti)"),
    (1655, 1675, "Turns"),
    (1650, 1655, "3_10 Helix"),
    (1640, 1650, "Alpha-Helix"),
    (1636, 1645, "Random Coil"),
    (1620, 1638, "Beta-Sheet"),
    (1605, 1620, "Aggregates"),
    (1580, 1605, "Side Chains")
]

# Lista opcji dla ComboBoxa w interfejsie (żeby użytkownik mógł ręcznie zmienić)
STRUCTURE_OPTIONS = [
    "Alpha-Helix",
    "Beta-Sheet",
    "Beta-Sheet (Anti)",
    "Random Coil",
    "Turns",
    "3_10 Helix",
    "Aggregates",
    "Aggregates (Anti)",
    "Side Chains",
    "Other"
]