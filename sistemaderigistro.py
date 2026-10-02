import json
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
            QRadioButton, QCheckBox {
                color: #edf4ff; font-size: 17px; spacing: 12px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 18px; height: 18px;
            }
            QRadioButton::indicator {
                border: 2px solid #9cb4d1; border-radius: 9px; background: transparent;
            }
            QRadioButton::indicator:checked {
                background: #35c19f; border: 2px solid #35c19f;
            }
            QCheckBox::indicator {
                border: 2px solid #9cb4d1; border-radius: 4px; background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #35c19f; border: 2px solid #35c19f;
            }
            QPushButton {
                background: #d9f8f3; color: #07252d; border: 2px solid #35c19f; border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: 700; min-height: 42px; max-height: 52px; min-width: 120px;
            }
            QPushButton:hover { background: #c3f4e8; color: #041a1f; }
            QPushButton:pressed { background: #9fe9d9; color: #041a1f; }
            QPushButton:focus { outline: none; border: 2px solid #8df0dd; }
            QPushButton#btnGuardar { background: #2ec4a6; color: #FFFFFF; border: 2px solid #35c19f; }
            QPushButton#btnGuardar:hover { background: #25b596; }
            QPushButton#btnLimpiar, QPushButton#btnAyuda { background: #2ec4a6; color:#FFFFFF; border: 2px solid #35c19f; }
            QFrame { border: none; }
            """
        )

        self.central = QWidget()
        self.central.setStyleSheet("background: #0f1b2b;")
        self.setCentralWidget(self.central)

        contenedor_principal = QVBoxLayout(self.central)
        contenedor_principal.setContentsMargins(30, 20, 30, 16)
        contenedor_principal.setSpacing(14)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setContentsMargins(0, 0, 0, 12)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        contenido_scroll = QWidget()
        contenido_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        contenido_scroll_layout = QVBoxLayout(contenido_scroll)
        contenido_scroll_layout.setContentsMargins(0, 0, 0, 40)
        contenido_scroll_layout.setSpacing(14)

        self.titulo = QLabel("Registro de Ventas")
        self.titulo.setStyleSheet("font-size: 36px; font-weight: bold; color: #35c19f; margin-bottom: 6px; letter-spacing: 0.5px;")
        self.titulo.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.titulo)

        self.subtitulo = QLabel("Complete el formulario y registre la venta realizada.")
        self.subtitulo.setStyleSheet("font-size: 18px; color: #dfeaf5; margin-bottom: 8px; font-weight: 500;")
        self.subtitulo.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.subtitulo)

        self.panel_form = QWidget()
        self.panel_form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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

        fila1 = QWidget()
        fila1_layout = QHBoxLayout(fila1)
        fila1_layout.setContentsMargins(0, 0, 0, 0)
        fila1_layout.setSpacing(18)

        self.producto_label = QLabel("Producto:")
        self.producto_input = QLineEdit()
        self.producto_input.setPlaceholderText("Nombre del producto")

        self.cantidad_label = QLabel("Cantidad:")
        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Ej. 5")

        fila1_layout.addWidget(self.producto_label)
        fila1_layout.addWidget(self.producto_input, 2)
        fila1_layout.addWidget(self.cantidad_label)
        fila1_layout.addWidget(self.cantidad_input, 1)
        grid.addWidget(fila1)

        fila2 = QWidget()
        fila2_layout = QHBoxLayout(fila2)
        fila2_layout.setContentsMargins(0, 0, 0, 0)
        fila2_layout.setSpacing(18)

        self.precio_label = QLabel("Precio unitario:")
        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Ej. 250.00")

        self.total_label = QLabel("Total:")
        self.total_input = QLineEdit()
        self.total_input.setPlaceholderText("Ej. 1250.00")

        fila2_layout.addWidget(self.precio_label)
        fila2_layout.addWidget(self.precio_input, 2)
        fila2_layout.addWidget(self.total_label)
        fila2_layout.addWidget(self.total_input, 1)
        grid.addWidget(fila2)

        fila3 = QWidget()
        fila3_layout = QHBoxLayout(fila3)
        fila3_layout.setContentsMargins(0, 0, 0, 0)
        fila3_layout.setSpacing(18)

        self.cliente_label = QLabel("Cliente:")
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("Nombre del cliente")

        self.vendedor_label = QLabel("Vendedor:")
        self.vendedor_input = QLineEdit()
        self.vendedor_input.setPlaceholderText("Nombre del vendedor")

        fila3_layout.addWidget(self.cliente_label)
        fila3_layout.addWidget(self.cliente_input, 2)
        fila3_layout.addWidget(self.vendedor_label)
        fila3_layout.addWidget(self.vendedor_input, 1)
        grid.addWidget(fila3)

        fila4 = QWidget()
        fila4_layout = QHBoxLayout(fila4)
        fila4_layout.setContentsMargins(0, 0, 0, 0)
        fila4_layout.setSpacing(18)

        self.pago_label = QLabel("Método de pago:")
        self.pago_combo = QComboBox()
        self.pago_combo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Crédito"])

        self.fecha_label = QLabel("Fecha:")
        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("Ej. 14/09/2026")

        fila4_layout.addWidget(self.pago_label)
        fila4_layout.addWidget(self.pago_combo, 2)
        fila4_layout.addWidget(self.fecha_label)
        fila4_layout.addWidget(self.fecha_input, 1)
        grid.addWidget(fila4)

        self.estado_label = QLabel("Estado de la venta:")
        self.estado_grupo = QWidget()
        estado_layout = QHBoxLayout(self.estado_grupo)
        estado_layout.setContentsMargins(0, 0, 0, 0)
        estado_layout.setSpacing(18)

        self.estado_pagada = QRadioButton("Pagada")
        self.estado_pagada.setChecked(True)
        self.estado_pendiente = QRadioButton("Pendiente")
        self.estado_cancelada = QRadioButton("Cancelada")
        estado_layout.addWidget(self.estado_pagada)
        estado_layout.addWidget(self.estado_pendiente)
        estado_layout.addWidget(self.estado_cancelada)

        self.comentario_label = QLabel("Observación:")
        self.comentarios = QTextEdit()
        self.comentarios.setPlaceholderText("Ingrese detalles de la venta...")
        self.comentarios.setStyleSheet("background: #1b2d3f; color: #f3f8ff; border: 1px solid #48607d; border-radius: 10px; min-height: 120px; padding: 8px; font-size: 16px;")

        grid.addWidget(self.estado_label)
        grid.addWidget(self.estado_grupo)
        grid.addWidget(self.comentario_label)
        grid.addWidget(self.comentarios)

        panel_layout.addWidget(form)
        contenido_scroll_layout.addWidget(self.panel_form)
        contenido_scroll_layout.addStretch(1)

        self.barra_final = QWidget()
        self.barra_final.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.barra_final.setMinimumHeight(82)
        self.barra_final.setStyleSheet("border-top: 2px solid #35c19f; margin-top: 6px; margin-bottom: 12px;")
        boton_layout = QHBoxLayout(self.barra_final)
        boton_layout.setContentsMargins(10, 10, 10, 10)
        boton_layout.setSpacing(18)
        boton_layout.addStretch()

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setObjectName("btnGuardar")
        self.btn_guardar.setMinimumHeight(42)
        self.btn_guardar.clicked.connect(self.guardar_registro)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("btnLimpiar")
        self.btn_limpiar.setMinimumHeight(42)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.btn_ayuda = QPushButton("Ayuda / Monitor")
        self.btn_ayuda.setObjectName("btnAyuda")
        self.btn_ayuda.setMinimumHeight(42)
        self.btn_ayuda.clicked.connect(self.ayuda_monitor)

        boton_layout.addWidget(self.btn_guardar)
        boton_layout.addWidget(self.btn_limpiar)
        boton_layout.addWidget(self.btn_ayuda)
        contenido_scroll_layout.addWidget(self.barra_final)

        self.footer = QLabel("INGENIERO INFORMATICO EN DESARRALLO DE SISTEMAS FABRICIO 2026")
        self.footer.setStyleSheet("font-size: 18px; font-weight: bold; color: #dfeaf5; text-align: center; margin-top: 8px; margin-bottom: 12px;")
        self.footer.setAlignment(Qt.AlignCenter)
        contenido_scroll_layout.addWidget(self.footer)

        self.scroll_area.setWidget(contenido_scroll)
        contenedor_principal.addWidget(self.scroll_area)

    def obtener_estado(self):
        if self.estado_pagada.isChecked():
            return "Pagada"
        if self.estado_pendiente.isChecked():
            return "Pendiente"
        return "Cancelada"

    def guardar_registro(self):
        producto = self.producto_input.text().strip()
        cantidad = self.cantidad_input.text().strip()
        precio = self.precio_input.text().strip()
        total = self.total_input.text().strip()
        cliente = self.cliente_input.text().strip()
        vendedor = self.vendedor_input.text().strip()
        metodo_pago = self.pago_combo.currentText()
        fecha = self.fecha_input.text().strip()
        estado = self.obtener_estado()
        observacion = self.comentarios.toPlainText().strip()

        if not producto:
            QMessageBox.warning(self, "Datos incompletos", "Debe ingresar el nombre del producto.")
            return

        if not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Debe ingresar el nombre del cliente.")
            return

        if not vendedor:
            QMessageBox.warning(self, "Datos incompletos", "Debe ingresar el nombre del vendedor.")
            return

        venta = {
            "producto": producto,
            "cantidad": cantidad,
            "precio": precio,
            "total": total,
            "cliente": cliente,
            "vendedor": vendedor,
            "metodo_pago": metodo_pago,
            "fecha": fecha,
            "estado": estado,
            "observacion": observacion,
        }

        self.ventas.append(venta)
        guardar_estudiantes(self.ventas)
        QMessageBox.information(
            self,
            "Venta registrada",
            f"La venta de {producto} fue registrada correctamente.",
        )
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

    def ayuda_monitor(self):
        mensaje = (
            "Ayuda de ventas:\n"
            "- Complete los datos principales de la venta.\n"
            "- El estado puede ser pagada, pendiente o cancelada.\n"
            "- Los datos se guardan automáticamente en un archivo JSON.\n"
            "- El botón Limpiar reinicia el formulario."
        )
        QMessageBox.information(self, "Monitor / Ayuda", mensaje)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = RegistroVentasApp()
    ventana.show()
    sys.exit(app.exec_())
