import tkinter as tk
from tkinter import messagebox, filedialog
import math
import re

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica Virtual")
        self.root.geometry("420x700")
        self.root.configure(bg="#0F172A")
        self.root.minsize(400, 660)

        # Variables de estado
        self.current_expression = ""
        self.angle_mode = "DEG"
        self.calculation_history = []

        self.setup_ui()
        self.root.bind('<Key>', self.key_press_event)

    def setup_ui(self):
        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg="#0F172A")
        header_frame.pack(fill="x", padx=15, pady=10)

        title_label = tk.Label(header_frame, text="CIENTÍFICA", bg="#0F172A", fg="#94A3B8", font=("Arial", 12, "bold"))
        title_label.pack(side="left")

        self.mode_btn = tk.Button(header_frame, text="DEG", command=self.toggle_angle_mode, **self.header_btn_style())
        self.mode_btn.pack(side="right", padx=2)

        self.clear_hist_btn = tk.Button(header_frame, text="🗑 Historial", command=self.clear_history, **self.header_btn_style())
        self.clear_hist_btn.pack(side="right", padx=2)

        self.save_hist_btn = tk.Button(header_frame, text="💾 Guardar", command=self.save_history, **self.header_btn_style())
        self.save_hist_btn.pack(side="right", padx=2)

        # --- PANTALLA ---
        display_frame = tk.Frame(self.root, bg="#0F172A")
        display_frame.pack(fill="x", padx=15, pady=5)

        self.history_listbox = tk.Listbox(display_frame, height=4, bg="#0F172A", fg="#64748B", 
                                          bd=0, font=("Arial", 12), highlightthickness=0)
        self.history_listbox.pack(fill="x", pady=(0, 10))
        self.history_listbox.bind('<<ListboxSelect>>', self.load_from_history)

        self.display_var = tk.StringVar(value="0")
        self.display_entry = tk.Entry(display_frame, textvariable=self.display_var, justify="right", 
                                      bg="#0F172A", fg="#F8FAFC", bd=0, font=("Arial", 28, "bold"), readonlybackground="#0F172A")
        self.display_entry.config(state="readonly")
        self.display_entry.pack(fill="x")

        # --- TECLADO ---
        keypad_frame = tk.Frame(self.root, bg="#0F172A")
        keypad_frame.pack(fill="both", expand=True, padx=15, pady=10)

        for i in range(7):
            keypad_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            keypad_frame.grid_columnconfigure(i, weight=1)

        buttons = [
            ('C', 0, 0, 1, 1), ('DEL', 0, 1, 1, 1), ('(', 0, 2, 1, 1), (')', 0, 3, 1, 1), ('mod', 0, 4, 1, 1),
            ('sin', 1, 0, 1, 1), ('cos', 1, 1, 1, 1), ('tan', 1, 2, 1, 1), ('π', 1, 3, 1, 1), ('e', 1, 4, 1, 1),
            ('log', 2, 0, 1, 1), ('ln', 2, 1, 1, 1), ('√', 2, 2, 1, 1), ('x²', 2, 3, 1, 1), ('^', 2, 4, 1, 1),
            ('7', 3, 0, 1, 1), ('8', 3, 1, 1, 1), ('9', 3, 2, 1, 1), ('÷', 3, 3, 1, 1), ('1/x', 3, 4, 1, 1),
            ('4', 4, 0, 1, 1), ('5', 4, 1, 1, 1), ('6', 4, 2, 1, 1), ('×', 4, 3, 1, 1), ('n!', 4, 4, 1, 1),
            ('1', 5, 0, 1, 1), ('2', 5, 1, 1, 1), ('3', 5, 2, 1, 1), ('-', 5, 3, 1, 1), ('=', 5, 4, 2, 1),
            ('0', 6, 0, 1, 2), ('.', 6, 2, 1, 1), ('+', 6, 3, 1, 1)
        ]

        for text, row, col, rowspan, colspan in buttons:
            btn = tk.Button(keypad_frame, text=text, command=lambda t=text: self.on_button_click(t),
                            **self.grid_btn_style(text))
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=4, pady=4)

        # --- FOOTER ---
        footer_label = tk.Label(self.root, text="Desarrollado por Dario Marquez", bg="#0F172A", fg="#64748B", font=("Arial", 9))
        footer_label.pack(side="bottom", pady=10)

    def header_btn_style(self):
        return {"bg": "#1E293B", "fg": "#F8FAFC", "activebackground": "#334155", "activeforeground": "#F8FAFC",
                "bd": 0, "font": ("Arial", 10), "padx": 8, "pady": 4, "relief": "flat"}

    def grid_btn_style(self, text):
        bg_color = "#1E293B"
        if text in ['C', 'DEL']:
            bg_color = "#991B1B" # Rojo
        elif text == '=':
            bg_color = "#2563EB" # Azul
        elif not text.isnumeric() and text != '.':
            bg_color = "#334155" # Gris operaciones

        return {"bg": bg_color, "fg": "#F8FAFC", "activebackground": "#475569", "activeforeground": "#F8FAFC",
                "bd": 0, "font": ("Arial", 14, "bold"), "relief": "flat"}

    def toggle_angle_mode(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.mode_btn.config(text=self.angle_mode)

    def on_button_click(self, char):
        if char == 'C': self.clear_all()
        elif char == 'DEL': self.backspace()
        elif char == '=': self.calculate_result()
        elif char in ('sin', 'cos', 'tan', 'log', 'ln', '√'): self.current_expression += f"{char}("
        elif char == 'x²': self.current_expression += "^2"
        elif char == '1/x': self.current_expression += "^(-1)"
        elif char == 'n!': self.current_expression += "!"
        elif char == 'mod': self.current_expression += " % "
        else: self.current_expression += char
        self.update_display()

    def clear_all(self):
        self.current_expression = ""
        self.update_display()

    def clear_history(self):
        self.calculation_history.clear()
        self.history_listbox.delete(0, tk.END)

    def backspace(self):
        self.current_expression = self.current_expression[:-1]
        self.update_display()

    def update_display(self):
        text = self.current_expression if self.current_expression else "0"
        self.display_var.set(text)

    def load_from_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            text = self.history_listbox.get(selection[0])
            if "=" in text:
                _, res = text.split("=")
                self.current_expression = res.strip()
                self.update_display()

    def calculate_result(self):
        if not self.current_expression: return
        expression_str = self.current_expression
        
        try:
            parsed_expr = expression_str.replace('×', '*').replace('÷', '/').replace('^', '**')
            parsed_expr = parsed_expr.replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt')
            parsed_expr = re.sub(r'(\d+)!', lambda m: f"math.factorial({m.group(1)})", parsed_expr)

            def deg_sin(x): return math.sin(math.radians(x) if self.angle_mode == "DEG" else x)
            def deg_cos(x): return math.cos(math.radians(x) if self.angle_mode == "DEG" else x)
            def deg_tan(x): return math.tan(math.radians(x) if self.angle_mode == "DEG" else x)

            safe_dict = {
                'math': math, 'sin': deg_sin, 'cos': deg_cos, 'tan': deg_tan,
                'log': math.log10, 'ln': math.log, 'sqrt': math.sqrt, 'abs': abs
            }

            result = eval(parsed_expr, {"__builtins__": None}, safe_dict)

            if isinstance(result, float) and result.is_integer():
                result_str = str(int(result))
            elif isinstance(result, float):
                result_str = f"{result:.8g}"
            else:
                result_str = str(result)

            record = f"{expression_str} = {result_str}"
            self.calculation_history.append(record)
            if len(self.calculation_history) > 5:
                self.calculation_history.pop(0)

            self.history_listbox.delete(0, tk.END)
            for item in self.calculation_history:
                self.history_listbox.insert(tk.END, item)
            self.history_listbox.yview(tk.END)

            self.current_expression = result_str
            self.update_display()

        except ZeroDivisionError:
            self.display_var.set("Error: div/0")
            self.current_expression = ""
        except Exception:
            self.display_var.set("Error")
            self.current_expression = ""

    def save_history(self):
        if not self.calculation_history:
            messagebox.showwarning("Aviso", "El historial está vacío.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="historial_calculadora.txt",
            title="Guardar Historial", filetypes=[("Archivos de texto", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=== Historial de Calculadora ===\n")
                    f.write("-" * 32 + "\n")
                    for i, record in enumerate(self.calculation_history, 1):
                        f.write(f"Operación {i}: {record}\n")
                messagebox.showinfo("Éxito", "Historial guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def key_press_event(self, event):
        if event.keysym in ('Return', 'KP_Enter'):
            self.calculate_result()
        elif event.keysym == 'Escape':
            self.clear_all()
        elif event.keysym == 'BackSpace':
            self.backspace()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()