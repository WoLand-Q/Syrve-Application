# ui/terminal_groups_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

# ui/terminal_groups_window.py

class TerminalGroupsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Группы терминалов')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Список групп терминалов')
        layout.addWidget(self.label)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        try:
            organizations = self.cloud_api.get_organizations()
            organization_ids = [org['id'] for org in organizations]
            terminal_groups_response = self.cloud_api.get_terminal_groups(organization_ids)
            terminal_groups_list = []

            for org_terminal_groups in terminal_groups_response.get('terminalGroups', []):
                org_id = org_terminal_groups['organizationId']
                items = org_terminal_groups.get('items', [])
                for group in items:
                    group['organizationId'] = org_id
                    terminal_groups_list.append(group)

            self.display_terminal_groups(terminal_groups_list)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить данные: {e}')

    def display_terminal_groups(self, terminal_groups):
        self.table.clear()
        headers = ['ID', 'Название', 'Адрес', 'Часовой пояс', 'ID организации']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(terminal_groups))
        for row_idx, group in enumerate(terminal_groups):
            self.table.setItem(row_idx, 0, QTableWidgetItem(group.get('id', '')))
            self.table.setItem(row_idx, 1, QTableWidgetItem(group.get('name', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(group.get('address', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(group.get('timeZone', '')))
            self.table.setItem(row_idx, 4, QTableWidgetItem(group.get('organizationId', '')))
