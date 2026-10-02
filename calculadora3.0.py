import flet as ft
import math
import re

def main(page: ft.Page):
    page.title = "Calculadora Científica - Flet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 420
    page.window_height = 740
    page.window_resizable = False
    page.bgcolor = "#0F172A"

    current_expression = ""
    angle_mode = ["DEG"]
    history_list = []

    display_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#F8FAFC")
    history_text = ft.Text("", size=13, color="#64748B")

    def update_display():
        display_text.value = current_expression if current_expression else "0"
        page.update()

    def calculate_result(e):
        nonlocal current_expression
        if not current_expression:
            return
        
        expr_str = current_expression
        try:
            parsed = expr_str.replace('×', '*').replace('÷', '/').replace('^', '**')
            parsed = parsed.replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt')
            parsed = re.sub(r'(\d+)!', lambda m: f"math.factorial({m.group(1)})", parsed)

            def deg_sin(x): return math.sin(math.radians(x) if angle_mode[0] == "DEG" else x)
            def deg_cos(x): return math.cos(math.radians(x) if angle_mode[0] == "DEG" else x)
            def deg_tan(x): return math.tan(math.radians(x) if angle_mode[0] == "DEG" else x)

            safe_dict = {
                'math': math, 'sin': deg_sin, 'cos': deg_cos, 'tan': deg_tan,
                'log': math.log10, 'ln': math.log, 'sqrt': math.sqrt, 'abs': abs
            }

            result = eval(parsed, {"__builtins__": None}, safe_dict)

            if isinstance(result, float) and result.is_integer():
                res_str = str(int(result))
            elif isinstance(result, float):
                res_str = f"{result:.8g}"
            else:
                res_str = str(result)

            record = f"{expr_str} = {res_str}"
            history_list.append(record)
            if len(history_list) > 3:
                history_list.pop(0)
            
            history_text.value = "\n".join(history_list)
            current_expression = res_str
            update_display()
        except ZeroDivisionError:
            display_text.value = "Error: div/0"
            current_expression = ""
            page.update()
        except Exception:
            display_text.value = "Error"
            current_expression = ""
            page.update()

    def button_click(e):
        nonlocal current_expression
        char = e.control.text
        
        if char == 'C':
            current_expression = ""
        elif char == 'DEL':
            current_expression = current_expression[:-1]
        elif char == '=':
            calculate_result(None)
            return
        elif char in ('sin', 'cos', 'tan', 'log', 'ln', '√'):
            current_expression += f"{char}("
        elif char == 'x²':
            current_expression += "^2"
        elif char == '1/x':
            current_expression += "^(-1)"
        elif char == 'n!':
            current_expression += "!"
        elif char == 'mod':
            current_expression += " % "
        else:
            current_expression += char
        
        update_display()

    def toggle_mode(e):
        angle_mode[0] = "RAD" if angle_mode[0] == "DEG" else "DEG"
        mode_btn.text = angle_mode[0]
        page.update()

    def clear_history(e):
        history_list.clear()
        history_text.value = ""
        page.update()

    # Controles superiores
    mode_btn = ft.ElevatedButton(text="DEG", width=65, height=32, on_click=toggle_mode, bgcolor="#1E293B", color="#F8FAFC")
    clear_hist_btn = ft.ElevatedButton(text="🗑", width=45, height=32, on_click=clear_history, bgcolor="#1E293B", color="#F8FAFC")
    
    header = ft.Row([
        ft.Text("CIENTÍFICA", size=14, weight=ft.FontWeight.BOLD, color="#94A3B8"),
        ft.Row([clear_hist_btn, mode_btn], spacing=5)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    display_container = ft.Container(
        content=ft.Column([
            history_text,
            display_text
        ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END),
        bgcolor="#0F172A",
        padding=15,
        border_radius=10,
        height=110
    )

    buttons = [
        ['C', 'DEL', '(', ')', 'mod'],
        ['sin', 'cos', 'tan', 'π', 'e'],
        ['log', 'ln', '√', 'x²', '^'],
        ['7', '8', '9', '÷', '1/x'],
        ['4', '5', '6', '×', 'n!'],
        ['1', '2', '3', '-', '='],
        ['0', '.', '+']
    ]

    grid_controls = []
    for row in buttons:
        row_buttons = []
        for btn_text in row:
            w = 142 if btn_text == '0' else 67
            h = 45
            if btn_text in ['C', 'DEL']:
                bg = "#991B1B"
            elif btn_text == '=':
                bg = "#2563EB"
            elif not btn_text.isnumeric() and btn_text != '.':
                bg = "#334155"
            else:
                bg = "#1E293B"
                
            btn = ft.ElevatedButton(text=btn_text, width=w, height=h, on_click=button_click, color="#F8FAFC", bgcolor=bg)
            row_buttons.append(btn)
        grid_controls.append(ft.Row(row_buttons, spacing=5, alignment=ft.MainAxisAlignment.CENTER))

    page.add(
        ft.Container(
            content=ft.Column([
                header,
                display_container,
                ft.Column(grid_controls, spacing=5),
                ft.Container(
                    content=ft.Text("Desarrollado por Dario Marquez", size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=5)
                )
            ], spacing=10),
            width=390,
            padding=10
        )
    )

if __name__ == "__main__":
    ft.app(target=main)