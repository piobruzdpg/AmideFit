# modules/gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import RectangleSelector
import numpy as np
import os
import json
import pandas as pd
from modules.config import THEME_MODE, COLOR_THEME, STRUCTURE_OPTIONS
from modules.logic import AmideLogic
from modules.custom_widgets import DraggableEntry, ToolTip

ctk.set_appearance_mode(THEME_MODE)
ctk.set_default_color_theme(COLOR_THEME)


class AmideFitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.logic = AmideLogic()

        self.title("AmideFit-Py v1.1 (Multi-Shape)")
        self.geometry("1400x900")

        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crop_mode = False;
        self.crop_points = [];
        self.crop_lines = []
        self.baseline_mode = False;
        self.baseline_points = [];
        self.baseline_lines = []
        self.add_peak_mode = False
        self.offset_mode = False
        self.show_deriv = False

        self._init_left_panel()
        self._init_center_panel()
        self._init_right_panel()
        self._init_menu()

        # INICJALIZACJA ZOOM SELECTORA (Domyślnie nieaktywny)
        # drawtype='box' rysuje prostokąt
        # button=[1] oznacza, że reaguje tylko na lewy przycisk myszy
        self.zoom_selector = RectangleSelector(self.ax_main, self.on_zoom_select,
                                               useblit=True,
                                               button=[1],
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=False)  # Interactive=False chowa go po puszczeniu
        self.zoom_selector.set_active(False)

        # Flaga trybu zoom
        self.zoom_mode = False

    def _init_left_panel(self):
        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # --- SEKCJA 1: PLIK ---
        ctk.CTkLabel(self.left_frame, text="AmideFit", font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20,
                                                                                        pady=(20, 5))
        ctk.CTkLabel(self.left_frame, text="v1.4", font=("Arial", 12), text_color="gray").grid(row=1, column=0, padx=20,
                                                                                               pady=(0, 15))

        self.btn_load = self._add_btn("Wczytaj Widmo", self.load_file, 2,
                                      tooltip="Wczytuje widmo z pliku (.csv, .txt, .dpt).")

        # Wybór rozpuszczalnika
        self.solvent_var = tk.StringVar(value="H2O")
        frame_solv = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame_solv.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        lbl_solv = ctk.CTkLabel(frame_solv, text="Rozpuszczalnik:", font=("Arial", 11))
        lbl_solv.pack(side="left", padx=(0, 5))
        ToolTip(lbl_solv, "Wybór rozpuszczalnika koryguje automatyczne zgadywanie struktur.")

        rb_h2o = ctk.CTkRadioButton(frame_solv, text="H₂O", variable=self.solvent_var, value="H2O",
                                    command=self.on_solvent_change, width=50)
        rb_h2o.pack(side="left", padx=2)
        rb_d2o = ctk.CTkRadioButton(frame_solv, text="D₂O", variable=self.solvent_var, value="D2O",
                                    command=self.on_solvent_change, width=50)
        rb_d2o.pack(side="left", padx=2)

        # --- SEKCJA 2: OBRÓBKA ---
        ctk.CTkLabel(self.left_frame, text="OBRÓBKA", anchor="w", font=("Arial", 12, "bold"), text_color="gray").grid(
            row=4, column=0, padx=20, pady=(20, 5), sticky="w")

        self.btn_zoom = ctk.CTkButton(self.left_frame, text="Zoom / Reset", command=self.toggle_zoom, state="disabled",
                                      fg_color="#6A5ACD")
        self.btn_zoom.grid(row=5, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_zoom, "LPM: Zaznacz prostokąt, aby powiększyć.\nPPM: Kliknij na wykres, aby zresetować widok.")

        self.btn_crop = ctk.CTkButton(self.left_frame, text="Przytnij", command=self.toggle_crop, state="disabled")
        self.btn_crop.grid(row=6, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_crop, "Kliknij dwa punkty na wykresie, aby obciąć widmo.")

        self.btn_offset = ctk.CTkButton(self.left_frame, text="Offset (0)", command=self.toggle_offset,
                                        state="disabled")
        self.btn_offset.grid(row=7, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_offset, "Kliknij na wykresie, aby przesunąć oś Y w dół (wskazany punkt osiągnie wartość 0).")

        self.btn_baseline = ctk.CTkButton(self.left_frame, text="Linia (2 pkt)", command=self.toggle_baseline,
                                          state="disabled")
        self.btn_baseline.grid(row=8, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_baseline, "Wskaż dwa punkty na widmie. Zostanie odjęta prosta łącząca te punkty.")

        self.btn_asls = ctk.CTkButton(self.left_frame, text="Linia (AsLS)", command=self.run_asls_baseline,
                                      state="disabled", fg_color="#551a8b")
        self.btn_asls.grid(row=9, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_asls, "Algorytm AsLS automatycznie 'napina' linię pod widmem, usuwając np. ogon Amidu II.")

        frame_smooth = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame_smooth.grid(row=10, column=0, padx=20, pady=3, sticky="ew")
        frame_smooth.grid_columnconfigure(0, weight=1)
        self.btn_smooth = ctk.CTkButton(frame_smooth, text="Wygładź", command=self.run_smoothing, state="disabled",
                                        width=100)
        self.btn_smooth.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ToolTip(self.btn_smooth, "Wygładza szum filtrem Savitzky-Golay.")
        self.ent_smooth_win = ctk.CTkEntry(frame_smooth, width=40, placeholder_text="11", justify="center")
        self.ent_smooth_win.insert(0, "11")
        self.ent_smooth_win.grid(row=0, column=1)
        ToolTip(self.ent_smooth_win, "Rozmiar okna (musi być nieparzyste).")

        self.btn_interp = ctk.CTkButton(self.left_frame, text="Interpoluj (2x)", command=self.run_interpolation,
                                        state="disabled")
        self.btn_interp.grid(row=11, column=0, padx=20, pady=3, sticky="ew")
        ToolTip(self.btn_interp, "Zagęszcza punkty pomiarowe krzywą sklejaną (Cubic Spline).")

        self.btn_undo = ctk.CTkButton(self.left_frame, text="Cofnij", command=self.undo_action, state="disabled",
                                      fg_color="gray")
        self.btn_undo.grid(row=12, column=0, padx=20, pady=(15, 3), sticky="ew")
        ToolTip(self.btn_undo, "Cofa ostatnią operację modyfikującą dane (np. przycięcie).")

        # --- SEKCJA 3: ANALIZA ---
        ctk.CTkLabel(self.left_frame, text="ANALIZA", anchor="w", font=("Arial", 12, "bold"), text_color="gray").grid(
            row=13, column=0, padx=20, pady=(20, 5), sticky="w")

        frame_deriv = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame_deriv.grid(row=14, column=0, padx=20, pady=3, sticky="ew")
        frame_deriv.grid_columnconfigure(0, weight=1)
        self.btn_deriv = ctk.CTkButton(frame_deriv, text="2. Pochodna", command=self.toggle_derivative,
                                       state="disabled", width=100)
        self.btn_deriv.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ToolTip(self.btn_deriv, "Pokazuje zarys 2. pochodnej. Maksimima wskazują położenie ukrytych pików.")
        self.ent_window = ctk.CTkEntry(frame_deriv, width=40, placeholder_text="11", justify="center")
        self.ent_window.insert(0, "11")
        self.ent_window.grid(row=0, column=1)
        ToolTip(self.ent_window, "Okno wygładzania dla pochodnej (nieparzyste).")

        # --- SEKCJA 4: FITOWANIE ---
        ctk.CTkLabel(self.left_frame, text="FITOWANIE", anchor="w", font=("Arial", 12, "bold"), text_color="gray").grid(
            row=15, column=0, padx=20, pady=(20, 5), sticky="w")

        self.combo_model = ctk.CTkComboBox(self.left_frame, values=["Gaussian", "Lorentzian", "Voigt", "PseudoVoigt"])
        self.combo_model.set("Gaussian")
        self.combo_model.grid(row=16, column=0, padx=20, pady=5, sticky="ew")
        ToolTip(self.combo_model, "Wybierz model matematyczny dodawanego piku.")

        self.btn_add_peak = self._add_btn("+ Dodaj Pik", self.toggle_add_peak, 17, state="disabled", color="green",
                                          tooltip="Zaznacz, a następnie kliknij na wykresie maksimum pasma, aby dodać pik składowy.")

        frame_algo = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame_algo.grid(row=18, column=0, padx=20, pady=5, sticky="ew")
        lbl_alg = ctk.CTkLabel(frame_algo, text="Metoda:", font=("Arial", 10))
        lbl_alg.pack(side="left")
        self.combo_algo = ctk.CTkComboBox(frame_algo, values=["Levenberg-Marquardt", "Nelder-Mead", "Powell"],
                                          width=120, font=("Arial", 11))
        self.combo_algo.set("Levenberg-Marquardt")
        self.combo_algo.pack(side="right")
        ToolTip(self.combo_algo, "Zmień na Nelder-Mead, jeśli domyślny algorytm zwraca błąd.")

        self.btn_run_fit = self._add_btn("URUCHOM FIT", self.run_fit_gui, 19, state="disabled", color="#8B0000",
                                         tooltip="Rozpoczyna iteracyjną optymalizację do minimalnego błędu rezydualnego.")

        # --- SEKCJA 5: EKSPORT ---
        ctk.CTkLabel(self.left_frame, text="EKSPORT", anchor="w", font=("Arial", 12, "bold"), text_color="gray").grid(
            row=20, column=0, padx=20, pady=(20, 5), sticky="w")
        self.btn_export = self._add_btn("Zapisz Wyniki (.xlsx)", self.export_xlsx, 21, state="disabled",
                                        tooltip="Zapisuje wykresy oraz szczegółowe parametry pików (obszar, struktura) do Excela.")

    # Pomocnicza metoda (musi zostać, ale lekko zmodyfikowana o sticky)
    def _add_btn(self, text, cmd, row, state="normal", color=None, tooltip=None):
        btn = ctk.CTkButton(self.left_frame, text=text, command=cmd, state=state)
        if color: btn.configure(fg_color=color)
        btn.grid(row=row, column=0, padx=20, pady=3, sticky="ew")
        if tooltip:
            ToolTip(btn, tooltip)
        return btn

    def _init_center_panel(self):
        self.center_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Pasek statystyk (GoF) na górze wykresu
        self.frame_stats = ctk.CTkFrame(self.center_frame, height=30, fg_color="#222222")
        self.frame_stats.pack(side=tk.TOP, fill=tk.X, padx=0, pady=(0, 5))

        self.lbl_gof = ctk.CTkLabel(self.frame_stats, text="Jakość dopasowania: (brak)", font=("Consolas", 12),
                                    text_color="yellow")
        self.lbl_gof.pack(pady=2)

        # Wykresy (bez zmian)
        self.fig, (self.ax_main, self.ax_res) = plt.subplots(2, 1, sharex=True,
                                                             gridspec_kw={'height_ratios': [3, 1]},
                                                             figsize=(8, 6), dpi=100)
        self._style_plots()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.center_frame)
        self.toolbar.update()

        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
    def _style_plots(self):
        self.fig.patch.set_facecolor('#2b2b2b')
        for ax in [self.ax_main, self.ax_res]:
            ax.set_facecolor('#1f1f1f')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.grid(True, linestyle='--', alpha=0.3)
            for spine in ax.spines.values(): spine.set_color('white')
        self.ax_main.set_ylabel("Absorbancja")
        self.ax_res.set_ylabel("Residua")
        self.ax_res.set_xlabel("Liczba falowa (cm⁻¹)")

    def _init_right_panel(self):
        self.right_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.right_frame.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(self.right_frame, text="Parametry Pików", font=("Arial", 16, "bold")).pack(pady=10)
        self.peaks_scroll = ctk.CTkScrollableFrame(self.right_frame)
        self.peaks_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def _init_menu(self):
        menubar = tk.Menu(self)

        # --- PLIK ---
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz Projekt (Full)", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Importuj Piki (Template)", command=self.import_peaks_only)
        file_menu.add_separator()
        file_menu.add_command(label="Zapisz Projekt", command=self.save_project)
        menubar.add_cascade(label="Plik", menu=file_menu)

        # --- USTAWIENIA (NOWE) ---
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Zmień motyw (Jasny/Ciemny)", command=self.toggle_theme)
        settings_menu.add_separator()
        settings_menu.add_command(label="Parametry domyślne sesji", command=self.open_settings_window)
        menubar.add_cascade(label="Ustawienia", menu=settings_menu)

        # --- POMOC (NOWE) ---
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Teoria: Kształty Pików",
                              command=lambda: self.show_help_file("PIK.md", "Teoria: Kształty Pików"))
        help_menu.add_command(label="Teoria: Metody Fitowania",
                              command=lambda: self.show_help_file("FIT.md", "Teoria: Metody Fitowania"))
        help_menu.add_command(label="Teoria: Pasma Amidu I",
                              command=lambda: self.show_help_file("PASMA.md", "Teoria: Pasma Amidu I"))
        menubar.add_cascade(label="Pomoc", menu=help_menu)

        self.config(menu=menubar)
    # --- ACTION HANDLERS ---

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('Data', '*.csv *.dpt *.txt'), ('All', '*.*')])
        if path:
            try:
                self.logic.load_data(path)
                self.refresh_all(full_reset=True)
                self._enable_buttons()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

    def _enable_buttons(self):
        """Aktywuje przyciski po wczytaniu pliku"""
        buttons = [
            self.btn_zoom,  # Zoom
            self.btn_crop,  # Przytnij
            self.btn_offset,  # Offset
            self.btn_baseline,  # Linia 2pkt
            self.btn_asls,  # Linia AsLS
            self.btn_smooth,  # Wygładź
            self.btn_interp,  # Interpoluj
            self.btn_deriv,  # Pochodna
            self.btn_add_peak,  # Dodaj Pik
            self.btn_run_fit  # Uruchom Fit
        ]

        for btn in buttons:
            btn.configure(state="normal")

    def undo_action(self):
        if self.logic.undo():
            self.plot_spectrum()
            if not self.logic.history: self.btn_undo.configure(state="disabled", fg_color="gray")

    def refresh_all(self, full_reset=False):
        self.plot_spectrum()
        self.update_right_panel()
        if full_reset: self.btn_undo.configure(state="disabled", fg_color="gray")

    def plot_spectrum(self):
        self.ax_main.clear()
        self.ax_res.clear()

        x = self.logic.x_data
        y = self.logic.y_data

        if x is not None:
            # 1. Główny wykres
            self.ax_main.plot(x, y, color='#00ffcc', label='Exp', linewidth=1.5, alpha=0.5, zorder=1)

            curves = self.logic.calculate_model_curves()

            # --- RYSOWANIE PIKÓW I ETYKIET ---
            if curves:
                # Maksimum dla skalowania etykiet
                y_max_plot = max(y)

                for i, comp in enumerate(curves['components']):
                    self.ax_main.plot(x, comp['y'], linestyle='--', color=comp['color'], alpha=0.8)
                    self.ax_main.fill_between(x, comp['y'], alpha=0.1, color=comp['color'])

                    # Rysowanie Etykiety Struktury nad pikiem
                    p_data = self.logic.peaks[i]
                    center_x = p_data['center']
                    # Znajdź Y w maksimum piku (z modelu)
                    idx_center = (np.abs(x - center_x)).argmin()
                    peak_height = comp['y'][idx_center]

                    # Dodaj tekst (np. "Beta-Sheet")
                    struct_short = p_data.get('structure', '')[:4]  # Skrót dla czytelności wykresu
                    self.ax_main.text(center_x, peak_height + (y_max_plot * 0.02), struct_short,
                                      color=comp['color'], fontsize=8, ha='center', rotation=90)

                self.ax_main.plot(x, curves['total'], color='red', label='Fit', linewidth=2, zorder=3)

                # Residua (domyślnie)
                if not self.show_deriv:
                    self.ax_res.plot(x, curves['residuals'], color='yellow', linewidth=1)
                    self.ax_res.set_ylabel("Residua")

            # --- RYSOWANIE 2. POCHODNEJ (JEŚLI AKTYWNA) ---
            if self.show_deriv:
                try:
                    window = self.ent_window.get()
                    dx, dy = self.logic.get_second_derivative(window)
                    # Rysujemy na dolnym panelu zamiast residuów
                    self.ax_res.clear()  # Czyścimy residua
                    self.ax_res.plot(dx, dy, color='cyan', linewidth=1.2, label="2nd Deriv")
                    self.ax_res.set_ylabel("2. Pochodna (-)")
                    self.ax_res.legend(fontsize=6)
                except Exception as e:
                    print(f"Błąd pochodnej: {e}")

            # Ustawienia osi
            self.ax_main.set_xlim(max(x), min(x))
            self.ax_res.set_xlim(max(x), min(x))
            if not self.show_deriv: self.ax_res.axhline(0, color='white', linestyle=':')
            self.ax_main.legend(facecolor='#2b2b2b', labelcolor='white')

        self._style_plots()
        self.canvas.draw()

    # --- PRAWY PANEL ---
    def update_right_panel(self):
        for w in self.peaks_scroll.winfo_children(): w.destroy()

        for i, p in enumerate(self.logic.peaks):
            f = ctk.CTkFrame(self.peaks_scroll)
            f.pack(fill="x", pady=2)
            f.grid_columnconfigure(1, weight=1)

            # Wiersz 0: Nagłówek
            ctk.CTkLabel(f, text="■", text_color=p['color']).grid(row=0, column=0, padx=5)
            lbl_title = ctk.CTkLabel(f, text=f"{p['id']} ({p['type'][:3]})", font=("Arial", 11, "bold"))
            lbl_title.grid(row=0, column=1, sticky="w")
            ToolTip(lbl_title, f"ID Piku: {p['id']}\nTyp: {p['type']}")

            ctk.CTkButton(f, text="✕", width=20, fg_color="#8B0000", command=lambda idx=i: self.delete_peak(idx)).grid(
                row=0, column=3, padx=5)

            # Wiersz 1: Struktura
            lbl_str = ctk.CTkLabel(f, text="Struktura:", font=("Arial", 10))
            lbl_str.grid(row=1, column=0, sticky="e")
            combo_struct = ctk.CTkComboBox(f, values=STRUCTURE_OPTIONS, height=20, width=120, font=("Arial", 10))
            combo_struct.set(p.get('structure', 'Other'))
            combo_struct.grid(row=1, column=1, columnspan=2, sticky="ew", padx=2, pady=2)
            combo_struct.configure(command=lambda choice, idx=i: self.on_structure_change(idx, choice))
            ToolTip(combo_struct, "Struktura drugorzędowa białka.\nTrafia do raportu Excel.")

            # Wiersz 2: Pozycja
            self._add_param_row(f, 2, "Pos:", i, "center", p['center'], "lock_center",
                                "Pozycja (Center). Przeciągaj myszą, aby zmieniać płynnie (Shift spowalnia).")

            # Wiersz 3: FWHM
            fwhm_val = self.logic.convert_sigma_to_fwhm(p['sigma'], p['type'])
            self._add_param_row(f, 3, "FWHM:", i, "sigma", fwhm_val, "lock_sigma",
                                "Szerokość połówkowa piku. Zaznacz pole z prawej, aby zablokować.")

            # Wiersz 4: Area
            self._add_param_row(f, 4, "Area:", i, "area", p['area'], "lock_area", "Pole pod pikiem (Amplitude).")

            # Wiersz 5: Parametry dodatkowe
            if p['type'] == 'Voigt':
                self._add_param_row(f, 5, "Gam:", i, "gamma", p.get('gamma', 1.0), "lock_extra",
                                    "Gamma: udział szerokości Lorentza w splocie Voigta.")
            elif p['type'] == 'PseudoVoigt':
                self._add_param_row(f, 5, "Frac:", i, "fraction", p.get('fraction', 0.5), "lock_extra",
                                    "Frakcja: % udziału Lorentza w funkcji Gaussa (0 do 1).")

    # Nowy handler dla zmiany struktury
    def on_structure_change(self, idx, new_structure):
        self.logic.update_peak_param(idx, 'structure', new_structure)
        self.plot_spectrum()  # Odśwież, żeby zmienić etykietę na wykresie

    def _add_param_row(self, parent, row, lbl, idx, key, val, lock_key, tooltip_text=""):
        lbl_widget = ctk.CTkLabel(parent, text=lbl, font=("Arial", 10))
        lbl_widget.grid(row=row, column=0, sticky="e")
        ToolTip(lbl_widget, tooltip_text)

        step = 0.1
        sens = 0.2
        if key == 'area':
            step = 0.1
            sens = 0.5
        elif key == 'fraction':
            step = 0.01

        def on_drag_finish(new_val):
            if key == 'sigma':
                self.logic.update_peak_fwhm(idx, new_val)
            else:
                self.logic.update_peak_param(idx, key, new_val)
            self.plot_spectrum()

        ent = DraggableEntry(parent, width=70, height=20, font=("Arial", 10),
                             step=step, sensitivity=sens,
                             command=on_drag_finish)

        ent.insert(0, f"{val:.2f}")
        ent.grid(row=row, column=1, sticky="ew")
        ent.bind('<Return>', lambda e, i=idx, k=key, w=ent: self.on_param_change(i, k, w))
        ToolTip(ent, tooltip_text)  # Podpięcie pod samo pole wpisywania

        is_locked = self.logic.peaks[idx].get(lock_key, False)
        chk = ctk.CTkCheckBox(parent, text="", width=16, height=16,
                              command=lambda i=idx, k=lock_key: self.logic.toggle_peak_lock(i, k))
        if is_locked: chk.select()
        chk.grid(row=row, column=2, padx=2)
        ToolTip(chk, "Zablokuj ten parametr podczas fitowania")

    def _trigger_param_update(self, idx, key):
        # Musimy znaleźć widget, który wywołał zdarzenie.
        # W DraggableEntry wywołujemy callback bez argumentów, więc tutaj musimy
        # odczytać wartość z GUI. Ponieważ update_right_panel przerysowuje wszystko,
        # musimy podejść sprytnie.

        # W DraggableEntry on_release wywołuje on_change_callback.
        # Problem: musimy przekazać "siebie" (widget) do funkcji update.
        pass

    def on_param_change(self, idx, key, widget):
        try:
            val = float(widget.get().replace(',', '.'))

            # Specjalna obsługa dla FWHM (bo klucz to 'sigma', ale wpisano FWHM)
            if key == 'sigma':
                self.logic.update_peak_fwhm(idx, val)
            elif key == 'fraction' and not (0 <= val <= 1):
                raise ValueError
            else:
                self.logic.update_peak_param(idx, key, val)

            self.plot_spectrum()
            widget.configure(text_color="white")
        except:
            widget.configure(text_color="red")

    def delete_peak(self, idx):
        self.logic.delete_peak(idx)
        self.refresh_all()

    # --- TOOLS ---
    def toggle_crop(self):
        self._reset_modes()
        self.crop_mode = not self.crop_mode
        if self.crop_mode:
            self.btn_crop.configure(fg_color="orange", text="Wskaż zakres...")
        else:
            self.btn_crop.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Przytnij (Zakres)")

    def toggle_baseline(self):
        self._reset_modes()
        self.baseline_mode = not self.baseline_mode
        if self.baseline_mode:
            self.btn_baseline.configure(fg_color="orange", text="Wskaż 2 pkt...")
        else:
            self.btn_baseline.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Linia Bazowa")

    def toggle_add_peak(self):
        self._reset_modes()
        self.add_peak_mode = not self.add_peak_mode
        if self.add_peak_mode:
            # Pobieramy nazwę modelu z ComboBoxa
            current_model = self.combo_model.get()
            self.btn_add_peak.configure(fg_color="orange", text=f"Kliknij ({current_model})...")
        else:
            self.btn_add_peak.configure(fg_color="green", text="+ Dodaj Pik")

        # Logika przycisku Pochodnej
    def toggle_derivative(self):
        self.show_deriv = not self.show_deriv
        if self.show_deriv:
            self.btn_deriv.configure(fg_color="orange", text="Ukryj Deriv")
        else:
            self.btn_deriv.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="2. Pochodna")
        self.plot_spectrum()

    # --- ZOOM LOGIC ---

    def toggle_zoom(self):
        """Włącza/Wyłącza tryb lupy"""
        self._reset_modes()  # Wyłącz inne tryby

        self.zoom_mode = not self.zoom_mode
        if self.zoom_mode:
            self.btn_zoom.configure(fg_color="orange", text="Reset (PPM)")
            self.zoom_selector.set_active(True)
            self.canvas.get_tk_widget().configure(cursor="crosshair")  # Zmiana kursora na celownik
        else:
            self.btn_zoom.configure(fg_color="#6A5ACD", text="🔍")
            self.zoom_selector.set_active(False)
            self.canvas.get_tk_widget().configure(cursor="arrow")

    def on_zoom_select(self, eclick, erelease):
        """Callback wywoływany po zaznaczeniu prostokąta myszką"""
        # Pobieramy współrzędne zaznaczenia
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        if x1 is None or x2 is None: return

        # USTAWIENIE OSI Z ZACHOWANIEM KIERUNKU FTIR (Malejące X)
        # Niezależnie jak użytkownik zaznaczył (lewo->prawo czy prawo->lewo),
        # zawsze ustawiamy lewą krawędź jako większą wartość, a prawą jako mniejszą.
        new_xmax = max(x1, x2)
        new_xmin = min(x1, x2)

        new_ymax = max(y1, y2)
        new_ymin = min(y1, y2)

        self.ax_main.set_xlim(new_xmax, new_xmin)  # <--- KLUCZOWE DLA IR
        self.ax_main.set_ylim(new_ymin, new_ymax)

        # Aktualizujemy też oś X dla residuów, żeby były zsynchronizowane
        self.ax_res.set_xlim(new_xmax, new_xmin)

        self.canvas.draw()

    def reset_zoom_view(self):
        """Resetuje widok do pełnego zakresu danych"""
        if self.logic.x_data is None: return

        x = self.logic.x_data
        y = self.logic.y_data

        # Reset X (Malejąco!)
        self.ax_main.set_xlim(max(x), min(x))
        self.ax_res.set_xlim(max(x), min(x))

        # Reset Y (z małym marginesem)
        margin = (max(y) - min(y)) * 0.05
        self.ax_main.set_ylim(min(y) - margin, max(y) + margin)

        # Skalowanie residuów (jeśli są)
        self.ax_res.relim()
        self.ax_res.autoscale_view()

        self.canvas.draw()

    def _reset_modes(self):
        # ... (początek bez zmian)
        self.crop_mode = False;
        self.crop_points = []
        self.baseline_mode = False;
        self.baseline_points = []
        self.add_peak_mode = False
        self.offset_mode = False
        self.zoom_mode = False
        self.zoom_selector.set_active(False)
        self.canvas.get_tk_widget().configure(cursor="arrow")

        # Reset kolorów i tekstów
        self.btn_crop.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Przytnij")
        self.btn_offset.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Offset (0)")
        self.btn_baseline.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Linia (2 pkt)")
        self.btn_add_peak.configure(fg_color="green", text="+ Dodaj Pik")

        # [ZMIANA] Reset tekstu przycisku Zoom
        self.btn_zoom.configure(fg_color="#6A5ACD", text="Zoom / Reset")

        [l.remove() for l in self.crop_lines + self.baseline_lines]
        self.crop_lines = [];
        self.baseline_lines = []
        self.canvas.draw()

    def on_canvas_click(self, event):
        if event.inaxes != self.ax_main: return

        # [NOWE] Obsługa Prawego Przycisku Myszy (button 3) dla resetu zoomu
        if event.button == 3:
            # Działa zawsze lub tylko w trybie zoom - jak wolisz.
            # Tutaj: Działa zawsze dla wygody.
            self.reset_zoom_view()
            return

        # Lewy przycisk myszy (button 1)
        if event.button == 1:
            if self.offset_mode:
                # ... (stara logika offsetu)
                shift_val = self.logic.apply_offset(event.xdata)
                self.btn_undo.configure(state="normal")
                self.refresh_all()
                self.toggle_offset()
                return

            if self.add_peak_mode:
                # ... (stara logika dodawania piku)
                model_type = self.combo_model.get()
                self.logic.add_peak(event.xdata, event.ydata, model_type=model_type)
                self.refresh_all()

            elif self.baseline_mode:
                # ... (stara logika baseline)
                self.baseline_points.append((event.xdata, event.ydata))
                pt, = self.ax_main.plot(event.xdata, event.ydata, 'ro');
                self.baseline_lines.append(pt)
                self.canvas.draw()
                if len(self.baseline_points) == 2:
                    (x1, y1), (x2, y2) = self.baseline_points
                    self.logic.apply_linear_baseline(x1, y1, x2, y2)
                    self.btn_undo.configure(state="normal")
                    self.toggle_baseline()
                    self.plot_spectrum()

            elif self.crop_mode:
                # ... (stara logika crop)
                self.crop_points.append(event.xdata)
                line = self.ax_main.axvline(x=event.xdata, color='yellow', linestyle='--');
                self.crop_lines.append(line)
                self.canvas.draw()
                if len(self.crop_points) == 2:
                    if self.logic.apply_crop(self.crop_points[0], self.crop_points[1]):
                        self.btn_undo.configure(state="normal")
                    self.toggle_crop()
                    self.plot_spectrum()

    # --- I/O ---
    # Obsługa wygładzania
    def run_smoothing(self):
        """Obsługa przycisku Wygładzania (SG)"""
        try:
            # Pobieramy szerokość okna z pola tekstowego
            win = self.ent_smooth_win.get()

            # Wywołujemy logikę
            if self.logic.apply_smoothing(win):
                self.refresh_all()
                self.btn_undo.configure(state="normal")
                print(f"Wygładzono SG (okno={win})")
            else:
                messagebox.showwarning("Błąd", "Nie udało się wygładzić danych (sprawdź parametr okna).")
        except Exception as e:
            print(f"Błąd GUI Smooth: {e}")

    def run_interpolation(self):
        """Obsługa przycisku Interpolacji"""
        # Wywołujemy logikę (factor=2 podwaja liczbę punktów)
        success, n_points = self.logic.apply_interpolation(factor=2)

        if success:
            self.refresh_all()
            self.btn_undo.configure(state="normal")
            messagebox.showinfo("Interpolacja", f"Zwiększono rozdzielczość.\nNowa liczba punktów: {n_points}")
        else:
            messagebox.showerror("Błąd", "Interpolacja nie powiodła się.")

    def run_fit_gui(self):
        # Mapowanie nazw z ComboBoxa na kody lmfit
        ALGO_MAP = {
            "Levenberg-Marquardt": "leastsq",
            "Nelder-Mead": "nelder",
            "Powell": "powell"
        }
        method_name = self.combo_algo.get()
        method_code = ALGO_MAP.get(method_name, "leastsq")

        try:
            # Uruchomienie fitowania i pobranie statystyk
            stats = self.logic.run_optimization(method=method_code)

            self.refresh_all()
            self.btn_export.configure(state="normal", fg_color="green")

            # Aktualizacja paska GoF
            gof_text = f"R²: {stats['r2']:.4f}  |  Chi²: {stats['chisqr']:.2e}  |  RMSE: {stats['rmse']:.4f}  |  Iter: {stats['nfev']}"
            self.lbl_gof.configure(text=gof_text, text_color="#00ff00" if stats['r2'] > 0.99 else "orange")

            messagebox.showinfo("Sukces", f"Fitowanie zakończone!\n\n{gof_text}")

        except Exception as e:
            # ROZBUDOWANA OBSŁUGA BŁĘDÓW (Punkt 4)
            error_msg = str(e)
            suggestion = ""

            if "Number of calls to function has reached maxfev" in error_msg:
                suggestion = "Sugestia: Algorytm potrzebował więcej czasu. Spróbuj zwiększyć limity (przyszła wersja) lub użyj metody 'Nelder-Mead'."
            elif "not a number" in error_msg or "NaN" in error_msg:
                suggestion = "Sugestia: Parametry przybrały niepoprawne wartości. Sprawdź czy sigmy nie są ujemne lub zablokuj niektóre parametry."
            elif "flat" in error_msg:
                suggestion = "Sugestia: Wykres lub model wydaje się płaski. Dodaj więcej pików."
            else:
                suggestion = "Sugestia: Spróbuj zmienić metodę fitowania na 'Nelder-Mead' lub zablokuj pozycje pików."

            full_msg = f"Niestety, algorytm napotkał problem:\n\n{error_msg}\n\n{suggestion}"
            messagebox.showerror("Błąd Fitowania", full_msg)

    # Obsługa Offsetu
    def toggle_offset(self):
        self._reset_modes()
        self.offset_mode = not self.offset_mode
        if self.offset_mode:
            self.btn_offset.configure(fg_color="orange", text="Wskaż 0...")
        else:
            self.btn_offset.configure(fg_color=["#3B8ED0", "#1F6AA5"], text="Offset (0)")

    def export_xlsx(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            try:
                df_c, df_p = self.logic.prepare_export_dataframes()
                with pd.ExcelWriter(path, engine='openpyxl') as writer:
                    df_p.to_excel(writer, sheet_name="Parameters", index=False)
                    df_c.to_excel(writer, sheet_name="Spectral_Data", index=False)
                messagebox.showinfo("Info", "Zapisano!")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

    def save_project(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Project", "*.json")])
        if path:
            try:
                state = self.logic.get_project_state()
                with open(path, 'w') as f:
                    json.dump(state, f, indent=4)
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

    def load_project(self):
        path = filedialog.askopenfilename(filetypes=[("Project", "*.json")])
        if path:
            try:
                with open(path, 'r') as f:
                    state = json.load(f)
                self.logic.load_project_state(state)
                self.refresh_all(full_reset=True)
                self._enable_buttons()
                if self.logic.peaks: self.btn_export.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

# [NOWE] Handler dla AsLS Baseline
    def run_asls_baseline(self):
        """Uruchamia automatyczną korekcję tła AsLS"""
        # Możesz tu dodać proste okienko dialogowe z pytaniem o parametr lambda,
        # ale na start użyjemy uniwersalnych wartości dla IR (lam=10^5, p=0.001)
        try:
            if self.logic.apply_asls_baseline(lam=100000, p=0.001):
                self.btn_undo.configure(state="normal")
                self.plot_spectrum()
                messagebox.showinfo("Sukces", "Zastosowano korekcję AsLS (Lambda=10^5).")
            else:
                messagebox.showwarning("Błąd", "Brak danych.")
        except Exception as e:
            messagebox.showerror("Błąd AsLS", str(e))

    # [NOWE] Handler dla Importu Pików
    def import_peaks_only(self):
        """Pozwala wczytać piki z innego projektu na obecne widmo"""
        if self.logic.x_data is None:
             messagebox.showwarning("Uwaga", "Najpierw wczytaj widmo, do którego chcesz zaimportować piki.")
             return

        path = filedialog.askopenfilename(filetypes=[("Project", "*.json")])
        if path:
            try:
                count = self.logic.import_peaks_from_project(path)
                if count > 0:
                    self.refresh_all() # Odświeża panel boczny i wykres
                    self.btn_export.configure(state="normal")
                    messagebox.showinfo("Import", f"Zaimportowano {count} pików.\nMożesz teraz dopasować je do nowych danych.")
                else:
                    messagebox.showwarning("Info", "Plik nie zawierał żadnych pików.")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

    # [NOWE] Handler dla zmiany rozpuszczalnika
    def on_solvent_change(self):
        new_solvent = self.solvent_var.get()
        self.logic.set_solvent(new_solvent)

        # Jeśli na wykresie są już piki, możemy chcieć "przegadnąć" ich struktury na nowo
        if self.logic.peaks:
            for i, p in enumerate(self.logic.peaks):
                # Opcjonalnie: można sprawdzić, czy struktura nie była ustawiona ręcznie
                # Wersja prosta: zgaduje dla wszystkich na nowo
                new_struct = self.logic._guess_structure(p['center'])
                self.logic.update_peak_param(i, 'structure', new_struct)

            self.update_right_panel()  # Odświeża tabelę pików
            self.plot_spectrum()  # Odświeża etykiety na wykresie
            print(f"Zmieniono rozpuszczalnik na {new_solvent}. Przypisania zaktualizowane.")

    # --- USTAWIENIA I POMOC ---

    def toggle_theme(self):
        """Przełącza motyw między jasnym a ciemnym"""
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def open_settings_window(self):
        """Otwiera okno zmiany parametrów domyślnych dla bieżącej sesji"""
        from modules.config import DEFAULT_CONFIG

        win = ctk.CTkToplevel(self)
        win.title("Ustawienia Domyślne Sesji")
        win.geometry("350x250")
        win.attributes('-topmost', True)  # Zawsze na wierzchu

        # Szerokość (Sigma)
        ctk.CTkLabel(win, text="Domyślna Sigma:").grid(row=0, column=0, padx=15, pady=15, sticky="e")
        ent_sigma = ctk.CTkEntry(win, width=120)
        ent_sigma.insert(0, str(DEFAULT_CONFIG['initial_sigma']))
        ent_sigma.grid(row=0, column=1, padx=10, pady=15)

        # Model
        ctk.CTkLabel(win, text="Domyślny Model:").grid(row=1, column=0, padx=15, pady=15, sticky="e")
        cmb_model = ctk.CTkComboBox(win, values=["Gaussian", "Lorentzian", "Voigt", "PseudoVoigt"], width=120)
        cmb_model.set(DEFAULT_CONFIG['default_model'])
        cmb_model.grid(row=1, column=1, padx=10, pady=15)

        # Okno SG
        ctk.CTkLabel(win, text="Rozmiar okna SG:").grid(row=2, column=0, padx=15, pady=15, sticky="e")
        ent_sg = ctk.CTkEntry(win, width=120)
        ent_sg.insert(0, str(DEFAULT_CONFIG['savgol_window']))
        ent_sg.grid(row=2, column=1, padx=10, pady=15)

        def save_settings():
            try:
                # Zapis do słownika w pamięci
                DEFAULT_CONFIG['initial_sigma'] = float(ent_sigma.get())
                DEFAULT_CONFIG['default_model'] = cmb_model.get()
                DEFAULT_CONFIG['savgol_window'] = int(ent_sg.get())

                # Aktualizacja GUI z nowymi wartościami
                self.combo_model.set(DEFAULT_CONFIG['default_model'])
                self.ent_smooth_win.delete(0, 'end')
                self.ent_smooth_win.insert(0, str(DEFAULT_CONFIG['savgol_window']))

                win.destroy()
                print("Zaktualizowano parametry sesji.")
            except ValueError:
                messagebox.showerror("Błąd", "Wprowadź poprawne wartości liczbowe.")

        btn_save = ctk.CTkButton(win, text="Zastosuj", command=save_settings, fg_color="green")
        btn_save.grid(row=3, column=0, columnspan=2, pady=10)

    def show_help_file(self, filename, title):
        """Wczytuje i wyświetla plik Markdown w nowym oknie"""
        import os
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("800x600")

        # Dla wygody czytania pliku tekstowego
        txt = ctk.CTkTextbox(win, wrap="word", font=("Arial", 14))
        txt.pack(fill="both", expand=True, padx=15, pady=15)

        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                txt.insert("0.0", content)
            except Exception as e:
                txt.insert("0.0", f"Błąd odczytu pliku:\n{str(e)}")
        else:
            txt.insert("0.0",
                       f"Brak pliku {filename} w głównym folderze aplikacji!\nUpewnij się, że plik znajduje się obok pliku main.py.")

        txt.configure(state="disabled")  # Blokada przed przypadkowym skasowaniem tekstu przez studenta
