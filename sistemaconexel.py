import json
import sys
from pathlib import Path

# --- NUEVA LIBRERÍA DE ANÁLISIS Y EXPORTACIÓN DE DATOS ---
import pandas as pd

# --- LIBRERÍA GRÁFICA PARA ESTADÍSTICAS ---
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ARCHIVO_ESTUDIANTES = Path(__file__).with_name("estudiantes_registrados.json")


def cargar_estudiantes():
    if not ARCHIVO_ESTUDIANTES.exists():
        return []
    try:
        with open(ARCHIVO_ESTUDIANTES, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if isinstance(datos, list):
                return datos
    except (json.JSONDecodeError, OSError):
        pass
    return []


def guardar_estudiantes(estudiantes):
    with open(ARCHIVO_ESTUDIANTES, "w", encoding="utf-8") as archivo:
        json.dump(estudiantes, archivo, ensure_ascii=False, indent=2)


class VentanaEstadisticas(QDialog):
    """Ventana emergente integrada con Matplotlib para visualizar reportes gráficos."""
    def __init__(self, ventas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Estadísticas y Gráficos de Ventas")
        self.resize(950, 600)
        self.setStyleSheet("""
            QDialog { background: #0f1b2b; color: #edf4ff; }
            QLabel { color: #35c19f; font-size: 20px; font-weight: bold; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Panel de Análisis de Ventas")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        if not ventas:
            msg = QLabel("No hay ventas registradas para generar gráficos.")
            msg.setStyleSheet("color: #edf4ff; font-size: 15px; margin: 40px;")
            msg.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg)
            return

        fig = Figure(figsize=(9, 5), facecolor='#0f1b2b')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        totales_por_producto = {}
        conteo_estados = {"Pagada": 0, "Pendiente": 0, "Cancelada": 0}

        for v in ventas:
            prod = v.get("producto", "Desconocido")
            try:
                tot = float(v.get("total", 0))
            except ValueError:
                tot = 0.0
            totales_por_producto[prod] = totales_por_producto.get(prod, 0.0) + tot

            est = v.get("estado", "Pagada")
            if est in conteo_estados:
                conteo_estados[est] += 1
            else:
                conteo_estados[est] = 1

        # 1. Gráfico de Barras (Matplotlib)
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor('#152332')
        productos = list(totales_por_producto.keys())
        totales = list(totales_por_producto.values())

        ax1.bar(productos, totales, color='#35c19f', edgecolor='#8df0dd')
        ax1.set_title("Total Ingresado ($) por Producto", color='#edf4ff', fontsize=12, pad=10)
        ax1.tick_params(colors='#edf4ff', labelsize=9)
        for spine in ax1.spines.values():
            spine.set_color('#48607d')

        # 2. Gráfico Circular (Matplotlib)
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor('#152332')
        labels = [k for k, v in conteo_estados.items() if v > 0]
        sizes = [v for k, v in conteo_estados.items() if v > 0]
        colores_pie = ['#35c19f', '#ffbd2e', '#ff5f56']

        if sizes:
            ax2.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                colors=colores_pie[:len(labels)], startangle=140,
                textprops=dict(color="#edf4ff", fontsize=10)
            )
        ax2.set_title("Distribución por Estado de Venta", color='#edf4ff', fontsize=12, pad=10)

        fig.tight_layout()
        canvas.draw()


class RegistroVentasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ventas = cargar_estudiantes()
        self.setWindowTitle("Registro de Ventas")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(
            """
            QMainWindow { background: #0f1b2b; }
            QWidget { background: #0f1b2b; color: #edf4ff; }
            QLabel { color: #eaf4ff; font-size: 15px; font-weight: 500; }
            QLineEdit, QComboBox, QTextEdit {
                background: #1b2d3f; color: #f3f8ff; border: 1px solid #48607d; border-radius: 10px; padding: 10px 12px; font-size: 16px; selection-background-color: #35c19f;
            }
            QLineEdit::placeholder { color: #a9bad0; }
            QComboBox QAbstractItemView {
                background: #172b3b; color: white;
            }
            QRadioButton {
                color: #edf4ff; font-size: 17px; spacing: 12px;
            }
            QRadioButton::indicator {
                width: 18px; height: 18px; border: 2px solid #9cb4d1; border-radius: 9px; background: transparent;
            }
            QRadioButton::indicator:checked {
                background: #35c19f; border: 2px solid #35c19f;
            }
            QPushButton {
                background: #2ec4a6; color: #FFFFFF; border: 2px solid #35c19f; border-radius: 10px; padding: 10px 18px; font-size: 14px; font-weight: 700; min-height: 42px;
            }
            QPushButton:hover { background: #25b596; }
            QPushButton#btnGuardar { background: #35c19f; }
            QFrame { border: none; }
            """
        )

        self.central = QWidget()
        self.setCentralWidget(self.central)

        contenedor_principal = QVBoxLayout(self.central)
        contenedor_principal.setContentsMargins(30, 20, 30, 16)
        contenedor_principal.setSpacing(14)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        contenido_scroll = QWidget()
        contenido_scroll_layout = QVBoxLayout(contenido_scroll)
        contenido_scroll_layout.setContentsMargins(0, 0, 0, 40)
        contenido_scroll_layout.setSpacing(14)

        self.titulo = QLabel("Registro de Ventas")
        self.titulo.setStyleSheet("font-size: 36px; font-weight: bold; color: #35c19f; margin-bottom: 6px;")
        self.titulo.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.titulo)

        self.subtitulo = QLabel("Complete el formulario y registre la venta realizada.")
        self.subtitulo.setStyleSheet("font-size: 18px; color: #dfeaf5; margin-bottom: 8px;")
        self.subtitulo.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.subtitulo)

        self.panel_form = QWidget()
        self.panel_form.setStyleSheet("background: #152332; border: 1px solid #2b3f53; border-radius: 16px;")
        panel_layout = QVBoxLayout(self.panel_form)
        panel_layout.setContentsMargins(20, 18, 20, 18)
        panel_layout.setSpacing(18)

        encabezado = QLabel("Datos de la venta")
        encabezado.setStyleSheet("color: #dfeaf5; font-size: 17px; font-weight: 600; border-bottom: 1px solid #4f6783; padding-bottom: 6px;")
        panel_layout.addWidget(encabezado)

        form = QWidget()
        grid = QVBoxLayout(form)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)

        # Fila 1
        fila1 = QWidget()
        fila1_layout = QHBoxLayout(fila1)
        fila1_layout.setContentsMargins(0, 0, 0, 0)
        self.producto_input = QLineEdit()
        self.producto_input.setPlaceholderText("Nombre del producto")
        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Ej. 5")
        self.cantidad_input.textChanged.connect(self.calcular_total_automatico)
        fila1_layout.addWidget(QLabel("Producto:"))
        fila1_layout.addWidget(self.producto_input, 2)
        fila1_layout.addWidget(QLabel("Cantidad:"))
        fila1_layout.addWidget(self.cantidad_input, 1)
        grid.addWidget(fila1)

        # Fila 2
        fila2 = QWidget()
        fila2_layout = QHBoxLayout(fila2)
        fila2_layout.setContentsMargins(0, 0, 0, 0)
        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Ej. 250.00")
        self.precio_input.textChanged.connect(self.calcular_total_automatico)
        self.total_input = QLineEdit()
        self.total_input.setPlaceholderText("Calculado automáticamente")
        fila2_layout.addWidget(QLabel("Precio unitario:"))
        fila2_layout.addWidget(self.precio_input, 2)
        fila2_layout.addWidget(QLabel("Total:"))
        fila2_layout.addWidget(self.total_input, 1)
        grid.addWidget(fila2)

        # Fila 3
        fila3 = QWidget()
        fila3_layout = QHBoxLayout(fila3)
        fila3_layout.setContentsMargins(0, 0, 0, 0)
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("Nombre del cliente")
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setPlaceholderText("Nombre del vendedor")
        fila3_layout.addWidget(QLabel("Cliente:"))
        fila3_layout.addWidget(self.cliente_input, 2)
        fila3_layout.addWidget(QLabel("Vendedor:"))
        fila3_layout.addWidget(self.vendedor_input, 1)
        grid.addWidget(fila3)

        # Fila 4
        fila4 = QWidget()
        fila4_layout = QHBoxLayout(fila4)
        fila4_layout.setContentsMargins(0, 0, 0, 0)
        self.pago_combo = QComboBox()
        self.pago_combo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Crédito"])
        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("Ej. 14/09/2026")
        fila4_layout.addWidget(QLabel("Método de pago:"))
        fila4_layout.addWidget(self.pago_combo, 2)
        fila4_layout.addWidget(QLabel("Fecha:"))
        fila4_layout.addWidget(self.fecha_input, 1)
        grid.addWidget(fila4)

        # Estado u Observaciones
        self.estado_grupo = QWidget()
        estado_layout = QHBoxLayout(self.estado_grupo)
        estado_layout.setContentsMargins(0, 0, 0, 0)
        self.estado_pagada = QRadioButton("Pagada")
        self.estado_pagada.setChecked(True)
        self.estado_pendiente = QRadioButton("Pendiente")
        self.estado_cancelada = QRadioButton("Cancelada")
        estado_layout.addWidget(self.estado_pagada)
        estado_layout.addWidget(self.estado_pendiente)
        estado_layout.addWidget(self.estado_cancelada)

        self.comentarios = QTextEdit()
        self.comentarios.setPlaceholderText("Ingrese detalles de la venta...")
        self.comentarios.setStyleSheet("background: #1b2d3f; color: #f3f8ff; border: 1px solid #48607d; border-radius: 10px; min-height: 100px;")

        grid.addWidget(QLabel("Estado de la venta:"))
        grid.addWidget(self.estado_grupo)
        grid.addWidget(QLabel("Observación:"))
        grid.addWidget(self.comentarios)

        panel_layout.addWidget(form)
        contenido_scroll_layout.addWidget(self.panel_form)

        # BARRA DE BOTONES DE ACCIÓN
        self.barra_final = QWidget()
        boton_layout = QHBoxLayout(self.barra_final)
        boton_layout.setContentsMargins(10, 10, 10, 10)
        boton_layout.setSpacing(12)
        boton_layout.addStretch()

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setObjectName("btnGuardar")
        self.btn_guardar.clicked.connect(self.guardar_registro)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.btn_graficos = QPushButton("Ver Gráficos")
        self.btn_graficos.clicked.connect(self.mostrar_graficos)

        # BOTÓN PANDAS: EXPORTAR A EXCEL
        self.btn_exportar = QPushButton("Exportar Excel")
        self.btn_exportar.clicked.connect(self.exportar_excel_pandas)

        self.btn_ayuda = QPushButton("Ayuda")
        self.btn_ayuda.clicked.connect(self.ayuda_monitor)

        boton_layout.addWidget(self.btn_guardar)
        boton_layout.addWidget(self.btn_limpiar)
        boton_layout.addWidget(self.btn_graficos)
        boton_layout.addWidget(self.btn_exportar)
        boton_layout.addWidget(self.btn_ayuda)
        contenido_scroll_layout.addWidget(self.barra_final)

        self.footer = QLabel("INGENIERO INFORMATICO EN DESARRALLO DE SISTEMAS FABRICIO 2026")
        self.footer.setStyleSheet("font-size: 18px; font-weight: bold; color: #dfeaf5; text-align: center;")
        self.footer.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.footer)

        self.scroll_area.setWidget(contenido_scroll)
        contenedor_principal.addWidget(self.scroll_area)

    def calcular_total_automatico(self):
        try:
            cant_str = self.cantidad_input.text().strip()
            precio_str = self.precio_input.text().strip()
            if cant_str and precio_str:
                cant = float(cant_str)
                precio = float(precio_str)
                self.total_input.setText(f"{cant * precio:.2f}")
        except ValueError:
            pass

    def obtener_estado(self):
        if self.estado_pagada.isChecked():
            return "Pagada"
        if self.estado_pendiente.isChecked():
            return "Pendiente"
        return "Cancelada"

    def guardar_registro(self):
        producto = self.producto_input.text().strip()
        cliente = self.cliente_input.text().strip()
        vendedor = self.vendedor_input.text().strip()

        if not producto or not cliente or not vendedor:
            QMessageBox.warning(self, "Datos incompletos", "Complete los campos obligatorios (Producto, Cliente y Vendedor).")
            return

        venta = {
            "producto": producto,
            "cantidad": self.cantidad_input.text().strip(),
            "precio": self.precio_input.text().strip(),
            "total": self.total_input.text().strip(),
            "cliente": cliente,
            "vendedor": vendedor,
            "metodo_pago": self.pago_combo.currentText(),
            "fecha": self.fecha_input.text().strip(),
            "estado": self.obtener_estado(),
            "observacion": self.comentarios.toPlainText().strip(),
        }

        self.ventas.append(venta)
        guardar_estudiantes(self.ventas)
        QMessageBox.information(self, "Éxito", f"Venta de {producto} registrada correctamente.")
        self.limpiar_formulario()

    def limpiar_formulario(self):
        self.producto_input.clear()
        self.cantidad_input.clear()
        self.precio_input.clear()
        self.total_input.clear()
        self.cliente_input.clear()
        self.vendedor_input.clear()
        self.pago_combo.setCurrentIndex(0)
        self.fecha_input.clear()
        self.estado_pagada.setChecked(True)
        self.comentarios.clear()
        self.producto_input.setFocus()

    def mostrar_graficos(self):
        dialogo = VentanaEstadisticas(self.ventas, self)
        dialogo.exec_()

    # --- FUNCIÓN CON PANDAS PARA EXPORTAR A EXCEL / CSV ---
    def exportar_excel_pandas(self):
        if not self.ventas:
            QMessageBox.warning(self, "Sin datos", "No hay ventas registradas para exportar.")
            return

        try:
            # Creación del DataFrame de Pandas a partir de la lista de diccionarios
            df = pd.DataFrame(self.ventas)

            # Renombrar columnas para formato de presentación profesional
            columnas_formato = {
                "producto": "Producto",
                "cantidad": "Cantidad",
                "precio": "Precio Unitario ($)",
                "total": "Total ($)",
                "cliente": "Cliente",
                "vendedor": "Vendedor",
                "metodo_pago": "Método de Pago",
                "fecha": "Fecha de Venta",
                "estado": "Estado",
                "observacion": "Observaciones"
            }
            df = df.rename(columns=columnas_formato)

            # Cuadro de diálogo para elegir la ruta de guardado
            archivo_guardar, filtro = QFileDialog.getSaveFileName(
                self,
                "Exportar Reporte de Ventas",
                "Reporte_Ventas.xlsx",
                "Archivo de Excel (*.xlsx);;Archivo CSV (*.csv)"
            )

            if archivo_guardar:
                if archivo_guardar.endswith('.csv'):
                    df.to_csv(archivo_guardar, index=False, encoding='utf-8-sig')
                else:
                    if not archivo_guardar.endswith('.xlsx'):
                        archivo_guardar += '.xlsx'
                    df.to_excel(archivo_guardar, index=False, engine='openpyxl')

                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"El reporte de ventas ha sido generado correctamente con Pandas en:\n{archivo_guardar}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", f"No se pudo generar el archivo:\n{str(e)}")

    def ayuda_monitor(self):
        mensaje = (
            "Funciones avanzadas del sistema:\n\n"
            "- PyQt5: Manejo de la interfaz visual moderna.\n"
            "- Matplotlib: Generación de gráficos e histogramas ('Ver Gráficos').\n"
            "- Pandas: Exportación de datos a hojas de cálculo Excel/CSV ('Exportar Excel').\n"
            "- Cálculo automático de Total al escribir cantidad y precio."
        )
        QMessageBox.information(self, "Monitor / Ayuda", mensaje)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = RegistroVentasApp()
    ventana.show()
    sys.exit(app.exec_())