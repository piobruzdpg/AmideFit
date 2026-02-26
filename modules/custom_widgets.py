# modules/custom_widgets.py
import customtkinter as ctk
import tkinter as tk



class DraggableEntry(ctk.CTkEntry):
    def __init__(self, master, step=0.1, sensitivity=0.5, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.step = step
        self.sensitivity = sensitivity
        self.command = command  # Funkcja wywoływana po zmianie (przyjmuje nową wartość jako arg)

        self.start_y = 0
        self.start_value = 0.0
        self.is_dragging = False

        self._entry.bind("<ButtonPress-1>", self.on_press)
        self._entry.bind("<B1-Motion>", self.on_drag)
        self._entry.bind("<ButtonRelease-1>", self.on_release)
        self._entry.configure(cursor="sb_v_double_arrow")

    def on_press(self, event):
        self.start_y = event.y_root
        try:
            val_str = self.get().replace(',', '.')
            self.start_value = float(val_str)
            self.is_dragging = False
        except ValueError:
            self.start_value = 0.0

    def on_drag(self, event):
        delta_y = self.start_y - event.y_root
        if abs(delta_y) < 3 and not self.is_dragging: return
        self.is_dragging = True

        # [NOWE] Wciśnięcie klawisza SHIFT (maska bitowa 1) spowalnia przesuwanie 10-krotnie
        speed_modifier = 0.1 if (event.state & 0x0001) else 1.0

        # Obliczamy nową wartość uwzględniając modyfikator prędkości
        change = delta_y * self.sensitivity * self.step * speed_modifier
        new_value = self.start_value + change

        # Zabezpieczenie przed wartościami ujemnymi (większość parametrów > 0)
        if new_value < 0: new_value = 0

        # Formatowanie: jeśli trzymamy Shift lub krok jest mały, pokazujemy więcej miejsc po przecinku
        effective_step = self.step * speed_modifier
        if effective_step < 0.1:
            fmt = "{:.4f}"
        elif effective_step < 1:
            fmt = "{:.2f}"
        else:
            fmt = "{:.1f}"

        self.delete(0, "end")
        self.insert(0, fmt.format(new_value))

        # LIVE UPDATE
        if self.command: self.command(new_value)

    def on_release(self, event):
        if self.is_dragging and self.command:
            try:
                val = float(self.get().replace(',', '.'))
                self.command(val)  # Wywołujemy funkcję z gui.py przekazując nową wartość
            except:
                pass
        self.is_dragging = False





class ToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.id = None
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def show(self):
        if not self.widget.winfo_exists():
            return
        # Przesunięcie lekko w prawo i w dół od kursora/widgetu
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")

        # Styl tooltipa (ciemny motyw pasujący do CustomTkinter)
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#2b2b2b", foreground="#ffffff",
                         relief='solid', borderwidth=1, font=("Arial", 10))
        label.pack(ipadx=8, ipady=4)

    def hide(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()