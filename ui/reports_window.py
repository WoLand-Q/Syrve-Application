# ui/reports_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from api.syrve_cloud import SyrveCloudAPI

class ReportsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Отчёты')
        layout.addWidget(self.label)

        self.fetch_data_button = QPushButton('Получить данные организаций')
        self.fetch_data_button.clicked.connect(self.fetch_data)
        layout.addWidget(self.fetch_data_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def fetch_data(self):
        try:
            # Получение списка организаций
            organizations = self.cloud_api.get_organizations()
            if organizations:
                self.display_organizations(organizations)
            else:
                QMessageBox.information(self, 'Информация', 'Нет данных для отображения.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить данные: {e}')

    def display_organizations(self, organizations):
        self.table.clear()
        headers = ['ID', 'Название', 'Адрес']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(organizations))
        for row_idx, org in enumerate(organizations):
            self.table.setItem(row_idx, 0, QTableWidgetItem(org.get('id', '')))
            self.table.setItem(row_idx, 1, QTableWidgetItem(org.get('name', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(org.get('address', '')))
