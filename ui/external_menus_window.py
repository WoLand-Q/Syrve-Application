# ui/external_menus_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtWidgets import (
    QPushButton, QHeaderView
)
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,  # Установите уровень логирования
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("syrve_cloud1.log"),
                        logging.StreamHandler()
                    ])
from PyQt5.QtCore import Qt
import json

class ExternalMenusWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Внешние меню')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Список внешних меню')
        layout.addWidget(self.label)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        try:
            data = self.cloud_api.get_external_menus()
            external_menus = data.get('externalMenus', [])
            self.display_external_menus(external_menus)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить данные: {e}')
            logging.error(f'Не удалось получить данные внешних меню: {e}')

    def display_external_menus(self, external_menus):
        self.table.clear()
        headers = ['ID', 'Название', 'Описание']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(external_menus))
        for row_idx, menu in enumerate(external_menus):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(menu.get('id', ''))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(menu.get('name', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(menu.get('description', '')))
        self.table.resizeColumnsToContents()
        logging.debug("Внешние меню успешно отображены в таблице.")

class PaymentTypesWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Типы платежей')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Типы платежей')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Кнопка обновления
        self.refresh_button = QPushButton('Обновить типы платежей')
        self.refresh_button.clicked.connect(self.fetch_payment_types)
        layout.addWidget(self.refresh_button)

        # Таблица для отображения типов платежей
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Код", "Название", "Комментарий",
            "Тип обработки", "Тип платежа"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Автоматическая загрузка при инициализации
        self.fetch_payment_types()

    def fetch_payment_types(self):
        try:
            organizations = self.cloud_api.get_organizations()
            organization_ids = [org['id'] for org in organizations]
            logging.debug(f'Organizations fetched: {organization_ids}')
            if not organization_ids:
                QMessageBox.warning(self, 'Предупреждение', 'Нет доступных организаций.')
                return

            payment_types_data = self.cloud_api.get_payment_types(organization_ids)
            payment_types = payment_types_data.get('paymentTypes', [])

            self.populate_table(payment_types)

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить типы платежей: {e}')
            logging.error(f"Не удалось получить типы платежей: {e}")

    def populate_table(self, payment_types):
        self.table.setRowCount(0)  # Очистить таблицу

        for payment in payment_types:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(payment.get('id', '')))
            self.table.setItem(row_position, 1, QTableWidgetItem(payment.get('code', '')))
            self.table.setItem(row_position, 2, QTableWidgetItem(payment.get('name', '')))
            self.table.setItem(row_position, 3, QTableWidgetItem(payment.get('comment', '')))
            self.table.setItem(row_position, 4, QTableWidgetItem(payment.get('paymentProcessingType', '')))
            self.table.setItem(row_position, 5, QTableWidgetItem(payment.get('paymentTypeKind', '')))

        self.table.resizeRowsToContents()
        logging.debug("Типы платежей успешно отображены в таблице.")
