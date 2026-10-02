import ast
import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CalculadoraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expression = ""
        self.setWindowTitle("Calculadora")
        self.resize(420, 640)
        self.setMinimumSize(360, 520)
        self.setStyleSheet(
            """
            QMainWindow { background: #0f1b2b; }
            QWidget { background: #0f1b2b; color: #edf4ff; }
            QLineEdit {
                background: #16283a; color: #f3f8ff; border: 1px solid #48607d;
                border-radius: 12px; padding: 18px 16px; font-size: 32px; font-weight: 600;
                qproperty-alignment: AlignRight;
            }
            QPushButton {
                background: #1b2d3f; color: #edf4ff; border: 1px solid #3b536d;
                border-radius: 12px; font-size: 22px; font-weight: 600; min-height: 60px;
            }
            QPushButton:hover { background: #25425f; }
            QPushButton:pressed { background: #1a3c57; }
            QPushButton#btnOperator { background: #0f3d4d; color: #8ef0d4; border: 1px solid #2ec4a6; }
            QPushButton#btnOperator:hover { background: #125b68; }
            QPushButton#btnEqual { background: #2ec4a6; color: #06241d; border: 1px solid #35c19f; }
            QPushButton#btnEqual:hover { background: #25b596; }
            QPushButton#btnAction { background: #243a4d; color: #dff8ff; border: 1px solid #4b6f8d; }
            QPushButton#btnAction:hover { background: #2d4c66; }
            """
        )

        self.central = QWidget()
        self.setCentralWidget(self.central)

        principal = QVBoxLayout(self.central)
        principal.setContentsMargins(20, 20, 20, 20)
        principal.setSpacing(18)

        self.titulo = QWidget()
        titulo_layout = QHBoxLayout(self.titulo)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        self.titulo_label = QPushButton("Calculadora")
        self.titulo_label.setEnabled(False)
        self.titulo_label.setStyleSheet(
            "background: transparent; border: none; color: #35c19f; font-size: 30px; font-weight: bold;"
        )
        titulo_layout.addWidget(self.titulo_label)
        principal.addWidget(self.titulo)

        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        principal.addWidget(self.display)

        self.panel = QWidget()
        self.panel.setStyleSheet("background: #152332; border: 1px solid #2b3f53; border-radius: 16px;")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(12)

        botones = [
            ("C", "btnAction"),
            ("⌫", "btnAction"),
            ("%", "btnOperator"),
            ("÷", "btnOperator"),
            ("7", None),
            ("8", None),
            ("9", None),
            ("×", "btnOperator"),
            ("4", None),
            ("5", None),
            ("6", None),
            ("-", "btnOperator"),
            ("1", None),
            ("2", None),
            ("3", None),
            ("+", "btnOperator"),
            ("±", "btnAction"),
            ("0", None),
            (".", None),
            ("=", "btnEqual"),
        ]

        for i, (texto, nombre) in enumerate(botones):
            boton = QPushButton(texto)
            if nombre:
                boton.setObjectName(nombre)
            boton.clicked.connect(lambda checked=False, valor=texto: self.agregar_valor(valor))
            fila = i // 4
            columna = i % 4
            grid.addWidget(boton, fila, columna)

        panel_layout.addLayout(grid)
        principal.addWidget(self.panel)

    def agregar_valor(self, valor):
        if valor == "C":
            self.expression = ""
            self.display.setText("0")
            return

        if valor == "⌫":
            self.expression = self.expression[:-1]
            self.display.setText(self.expression if self.expression else "0")
            return

        if valor == "±":
            if not self.expression:
                return
            try:
                numero = float(self.expression)
                self.expression = str(-numero)
            except ValueError:
                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression
            self.display.setText(self.expression)
            return

        if valor == "%":
            if not self.expression:
                return
            try:
                self.expression = str(float(self.expression) / 100)
            except ValueError:
                self.expression = self.expression + "%"
            self.display.setText(self.expression)
            return

        if valor in {"+", "-", "×", "÷"}:
            simbolo = {"+": "+", "-": "-", "×": "*", "÷": "/"}[valor]
            if not self.expression:
                if simbolo == "-":
                    self.expression = "-"
            else:
                ultimo = self.expression[-1]
                if ultimo in "+-*/":
                    self.expression = self.expression[:-1] + simbolo
                else:
                    self.expression += simbolo
            self.display.setText(self.expression)
            return

        if valor == "=":
            self.calcular()
            return

        if valor == ".":
            if not self.expression:
                self.expression = "0."
            elif self.expression[-1] == ".":
                return
            else:
                ultimo_operador = max(
                    self.expression.rfind("+"),
                    self.expression.rfind("-"),
                    self.expression.rfind("*"),
                    self.expression.rfind("/"),
                )
                sub = self.expression[ultimo_operador + 1 :]
                if "." in sub:
                    return
                self.expression += "."
            self.display.setText(self.expression)
            return

        if self.expression == "0":
            self.expression = valor
        else:
            self.expression += valor
        self.display.setText(self.expression)

    def calcular(self):
        texto = self.expression.strip()
        if not texto:
            return

        try:
            texto = texto.replace("×", "*").replace("÷", "/")
            nodo = ast.parse(texto, mode="eval")
            for subn in ast.walk(nodo):
                if isinstance(subn, ast.Call):
                    raise ValueError("Operación no válida")
                if isinstance(subn, (ast.Name, ast.Attribute, ast.Subscript)):
                    raise ValueError("Operación no válida")

            resultado = eval(compile(nodo, "<calculadora>", "eval"), {"__builtins__": {}}, {})
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            self.expression = str(resultado)
            self.display.setText(self.expression)
        except Exception:
            QMessageBox.warning(self, "Error", "Expresión inválida")
            self.expression = ""
            self.display.setText("0")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = CalculadoraApp()
    ventana.show()
    sys.exit(app.exec_())
