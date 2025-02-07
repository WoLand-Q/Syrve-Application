# ui/organizations_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

class OrganizationsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Организации')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Список организаций')
        layout.addWidget(self.label)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        try:
            organizations = self.cloud_api.get_organizations()
            if organizations:
                self.display_organizations(organizations)
            else:
                QMessageBox.information(self, 'Информация', 'Нет данных для отображения.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить данные: {e}')

    def display_organizations(self, organizations):
        self.table.clear()
        headers = ['ID', 'Название', 'Адрес', 'Телефон']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(organizations))
        for row_idx, org in enumerate(organizations):
            self.table.setItem(row_idx, 0, QTableWidgetItem(org.get('id', '')))
            self.table.setItem(row_idx, 1, QTableWidgetItem(org.get('name', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(org.get('address', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(org.get('phone', '')))
