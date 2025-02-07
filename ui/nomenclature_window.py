# ui/nomenclature_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
import json

class NomenclatureWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Номенклатура')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        organizations = self.cloud_api.get_organizations()
        self.organizations = organizations
        for org in organizations:
            self.organization_combo.addItem(org['name'], org['id'])
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.load_button = QPushButton('Загрузить номенклатуру')
        self.load_button.clicked.connect(self.load_nomenclature)
        layout.addWidget(self.load_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Кнопка сохранения
        self.save_button = QPushButton('Сохранить в файл')
        self.save_button.clicked.connect(self.save_to_file)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        padding: 10px;
                        font-size: 14px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                    QTableWidget {
                        background-color: #ecf0f1;
                        font-size: 14px;
                    }
                    QHeaderView::section {
                        background-color: #34495e;
                        color: white;
                        padding: 4px;
                        border: none;
                    }
                """)
    def load_nomenclature(self):
        organization_id = self.organization_combo.currentData()
        try:
            nomenclature = self.cloud_api.get_nomenclature(organization_id)
            if nomenclature:
                self.nomenclature_data = nomenclature
                self.display_nomenclature(nomenclature)
            else:
                QMessageBox.information(self, 'Информация', 'Нет данных для отображения.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить данные: {e}')

    def display_nomenclature(self, nomenclature):
        self.table.clear()
        products = nomenclature.get('products', [])
        headers = ['ID', 'Название', 'Цена', 'Группа']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            self.table.setItem(row_idx, 0, QTableWidgetItem(product.get('id', '')))
            self.table.setItem(row_idx, 1, QTableWidgetItem(product.get('name', '')))
            price = product.get('price', 0)
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(price)))
            parent_group = product.get('parentGroup', '')
            self.table.setItem(row_idx, 3, QTableWidgetItem(parent_group))

    def save_to_file(self):
        if hasattr(self, 'nomenclature_data'):
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить в JSON", "", "JSON Files (*.json);;All Files (*)", options=options)
            if fileName:
                try:
                    with open(fileName, mode='w', encoding='utf-8') as file:
                        json.dump(self.nomenclature_data, file, ensure_ascii=False, indent=4)
                    QMessageBox.information(self, 'Успех', f'Данные сохранены в файл {fileName}')
                except Exception as e:
                    QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить файл: {e}')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Нет данных для сохранения.')
