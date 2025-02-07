# ui/server_windows.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QTextEdit, QDateEdit, QDateTimeEdit, QListWidgetItem,
    QListWidget
)
from PyQt5.QtCore import Qt, QDate, QDateTime
import json
import pandas as pd
import logging
from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtCore import QDateTime

class OlapReportWindow(QWidget):
    def __init__(self, server_api):
        super().__init__()
        self.server_api = server_api
        self.setWindowTitle('OLAP Отчет')
        self.setFixedSize(800, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Создание OLAP Отчета')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Выбор организации
        self.organization_label = QLabel('Выберите Организацию:')
        self.organization_combo = QComboBox()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)
        self.load_organizations()

        # Поля для выбора дат
        self.date_from_label = QLabel('Дата начала:')
        self.date_from_input = QDateEdit()
        self.date_from_input.setCalendarPopup(True)
        self.date_from_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_from_label)
        layout.addWidget(self.date_from_input)

        self.date_to_label = QLabel('Дата окончания:')
        self.date_to_input = QDateEdit()
        self.date_to_input.setCalendarPopup(True)
        self.date_to_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_to_label)
        layout.addWidget(self.date_to_input)

        # Поля для выбора группировки и агрегатных полей
        self.group_by_row_label = QLabel('Группировка по строкам:')
        self.group_by_row_list = QListWidget()
        self.group_by_row_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.group_by_row_label)
        layout.addWidget(self.group_by_row_list)

        self.aggregate_fields_label = QLabel('Агрегатные поля:')
        self.aggregate_fields_list = QListWidget()
        self.aggregate_fields_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.aggregate_fields_label)
        layout.addWidget(self.aggregate_fields_list)

        # Кнопка получения отчета
        self.fetch_report_button = QPushButton('Получить Отчет')
        self.fetch_report_button.clicked.connect(self.fetch_report)
        layout.addWidget(self.fetch_report_button)

        # Таблица для отображения отчета
        self.report_table = QTableWidget()
        layout.addWidget(self.report_table)

        # Кнопка сохранения отчета
        self.save_button = QPushButton('Сохранить в CSV')
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        # Обновление списка доступных полей при загрузке
        self.update_available_fields()
        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.server_api.get_organizations()
            if organizations:
                self.organization_combo.clear()
                for org in organizations:
                    org_id = org.get("id")
                    org_name = org.get("name", "Без названия")
                    if org_id:
                        self.organization_combo.addItem(f"{org_name}", org_id)
                        logging.debug(f"Добавлена организация: {org_name} с ID: {org_id}")
                    else:
                        logging.warning(f"Организация {org_name} не имеет ID и будет пропущена.")
                logging.debug("Список организаций успешно загружен и отображен в выпадающем списке.")
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Список организаций пуст.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить список организаций: {e}')
            logging.error(f"Не удалось загрузить список организаций: {e}")

    def update_available_fields(self):
        report_type = 'SALES'  # Используем только тип отчета SALES
        try:
            self.columns = self.server_api.get_olap_columns(report_type=report_type)
            if self.columns:
                # Очистка списков
                self.group_by_row_list.clear()
                self.aggregate_fields_list.clear()

                for field_name, details in self.columns.items():
                    display_text = f"{details.get('name', field_name)} ({field_name})"

                    # Добавляем только поля, которые можно группировать
                    if details.get('groupingAllowed', False):
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.UserRole, field_name)
                        self.group_by_row_list.addItem(item)

                    # Добавляем только поля, которые можно агрегировать
                    if details.get('aggregationAllowed', False):
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.UserRole, field_name)
                        self.aggregate_fields_list.addItem(item)
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить доступные поля отчета.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить доступные поля отчета: {e}')
            logging.error(f"Не удалось загрузить доступные поля отчета: {e}")

    def fetch_report(self):
        organization_id = self.organization_combo.currentData()
        if not organization_id:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите организацию.')
            return

        date_from = self.date_from_input.date().toString("yyyy-MM-dd")
        date_to = self.date_to_input.date().toString("yyyy-MM-dd")

        report_type = 'SALES'
        build_summary = True  # Можно сделать опциональным

        group_by_row_fields = [item.data(Qt.UserRole) for item in self.group_by_row_list.selectedItems()]
        aggregate_fields = [item.data(Qt.UserRole) for item in self.aggregate_fields_list.selectedItems()]

        if not group_by_row_fields or not aggregate_fields:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите поля группировки и агрегатные поля.')
            return

        # Создаем фильтры автоматически
        filters = {
            "OpenDate.Typed": {
                "filterType": "DateRange",
                "periodType": "CUSTOM",
                "from": date_from,
                "to": date_to,
                "includeLow": True,
                "includeHigh": False
            },
            "OrderDeleted": {
                "filterType": "IncludeValues",
                "values": ["NOT_DELETED"]
            },
            "DeletedWithWriteoff": {
                "filterType": "IncludeValues",
                "values": ["NOT_DELETED"]
            },
            "Department": {
                "filterType": "IncludeValues",
                "values": [organization_id]
            }
        }

        try:
            report = self.server_api.get_olap_report(
                report_type=report_type,
                build_summary=build_summary,
                group_by_row_fields=group_by_row_fields,
                group_by_col_fields=[],
                aggregate_fields=aggregate_fields,
                filters=filters
            )
            if report:
                data = report.get('data', [])
                summary = report.get('summary', [])

                if data:
                    df = pd.DataFrame(data)
                    self.display_report(df)
                else:
                    QMessageBox.information(self, 'Информация', 'Данные отчета отсутствуют.')

                # Можно добавить отображение итогов отчета (summary)
                if summary:
                    summary_df = pd.DataFrame([summary])
                    # Добавьте код для отображения summary_df, если необходимо
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Отчет не был получен.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить отчет: {e}')
            logging.error(f"Не удалось получить отчет: {e}")

    def fetch_report(self):
        organization_id = self.organization_combo.currentData()
        if not organization_id:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите организацию.')
            return

        date_from = self.date_from_input.date().toString("yyyy-MM-dd")
        date_to = self.date_to_input.date().toString("yyyy-MM-dd")

        report_type = self.report_type_combo.currentText()
        build_summary = True  # Можно сделать опциональным
        group_by_row_fields = [item.data(Qt.UserRole) for item in self.group_by_row_list.selectedItems()]
        group_by_col_fields = [item.data(Qt.UserRole) for item in self.group_by_col_list.selectedItems()]
        aggregate_fields = [item.data(Qt.UserRole) for item in self.aggregate_fields_list.selectedItems()]
        filters_str = self.filters_input.toPlainText().strip()

        # Валидация фильтров
        try:
            filters = json.loads(filters_str) if filters_str else {}
        except json.JSONDecodeError:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный JSON в фильтрах.')
            return

        # Добавляем фильтр по дате и организации
        filters["OpenDate.Typed"] = {
            "filterType": "DateRange",
            "periodType": "CUSTOM",
            "from": date_from,
            "to": date_to,
            "includeLow": True,
            "includeHigh": False
        }
        filters["OrderDeleted"] = {
            "filterType": "IncludeValues",
            "values": ["NOT_DELETED"]
        }
        filters["DeletedWithWriteoff"] = {
            "filterType": "IncludeValues",
            "values": ["NOT_DELETED"]
        }
        filters["Department"] = {
            "filterType": "IncludeValues",
            "values": [organization_id]
        }

        try:
            report = self.server_api.get_olap_report(
                report_type=report_type,
                build_summary=build_summary,
                group_by_row_fields=group_by_row_fields,
                group_by_col_fields=group_by_col_fields,
                aggregate_fields=aggregate_fields,
                filters=filters
            )
            if report:
                data = report.get('data', [])
                summary = report.get('summary', [])

                if data:
                    df = pd.DataFrame(data)
                    self.display_report(df)
                else:
                    QMessageBox.information(self, 'Информация', 'Данные отчета отсутствуют.')

                if summary:
                    summary_df = pd.DataFrame([summary])
                    # Можно добавить отображение в интерфейсе
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Отчет не был получен.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить отчет: {e}')
            logging.error(f"Не удалось получить отчет: {e}")

    def display_report(self, df):
        self.report_table.clear()
        self.report_table.setColumnCount(len(df.columns))
        self.report_table.setRowCount(len(df))
        self.report_table.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.report_table.setItem(row, col, item)

        self.report_table.resizeColumnsToContents()
        logging.debug("OLAP отчет успешно отображен в таблице.")

    def save_report(self):
        if self.report_table.rowCount() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Нет данных для сохранения.')
            return

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет в CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            try:
                # Извлечение данных из таблицы
                headers = [self.report_table.horizontalHeaderItem(i).text() for i in range(self.report_table.columnCount())]
                data = []
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                # Создание DataFrame и сохранение
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(fileName, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Успех', f'Отчет успешно сохранен в {fileName}')
                logging.debug(f"OLAP отчет сохранен в {fileName}")
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить отчет: {e}')
                logging.error(f"Не удалось сохранить отчет: {e}")

class BalanceReportWindow(QWidget):
    def __init__(self, server_api):
        super().__init__()
        self.server_api = server_api
        self.setWindowTitle('Отчет по Остаткам')
        self.setFixedSize(800, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Создание Отчета по Остаткам')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Выбор организации
        self.organization_label = QLabel('Выберите Организацию:')
        self.organization_combo = QComboBox()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)
        self.load_organizations()

        # Выбор даты и времени
        self.timestamp_label = QLabel('Дата и время:')
        self.timestamp_input = QDateTimeEdit()
        self.timestamp_input.setCalendarPopup(True)
        self.timestamp_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.timestamp_label)
        layout.addWidget(self.timestamp_input)

        # Кнопка получения отчета
        self.fetch_report_button = QPushButton('Получить Отчет')
        self.fetch_report_button.clicked.connect(self.fetch_report)
        layout.addWidget(self.fetch_report_button)

        # Таблица для отображения отчета
        self.report_table = QTableWidget()
        layout.addWidget(self.report_table)

        # Кнопка сохранения отчета
        self.save_button = QPushButton('Сохранить в CSV')
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.server_api.get_organizations()
            if organizations:
                self.organization_combo.clear()
                for org in organizations:
                    org_id = org.get("id")
                    org_name = org.get("name", "Без названия")
                    if org_id:
                        self.organization_combo.addItem(f"{org_name} ({org_id})", org_id)
                        logging.debug(f"Добавлена организация: {org_name} с ID: {org_id}")
                    else:
                        logging.warning(f"Организация {org_name} не имеет ID и будет пропущена.")
                logging.debug("Список организаций успешно загружен и отображен в выпадающем списке.")
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Список организаций пуст.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить список организаций: {e}')
            logging.error(f"Не удалось загрузить список организаций: {e}")

    def fetch_report(self):
        organization_id = self.organization_combo.currentData()
        timestamp = self.timestamp_input.dateTime().toString("yyyy-MM-ddTHH:mm:ss")

        if not all([organization_id, timestamp]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите организацию и дату.')
            return

        try:
            store_ids = [organization_id]
            report = self.server_api.get_balance_report(store_ids, timestamp)
            if report and isinstance(report, list):
                df = pd.DataFrame(report)
                self.display_report(df)
            else:
                QMessageBox.information(self, 'Информация', 'Данные отчета отсутствуют или некорректны.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить отчет: {e}')
            logging.error(f"Не удалось получить отчет: {e}")

    def display_report(self, df):
        self.report_table.clear()
        self.report_table.setColumnCount(len(df.columns))
        self.report_table.setRowCount(len(df))
        self.report_table.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.report_table.setItem(row, col, item)

        self.report_table.resizeColumnsToContents()

    def save_report(self):
        if self.report_table.rowCount() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Нет данных для сохранения.')
            return

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет в CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            try:
                # Извлечение данных из таблицы
                headers = [self.report_table.horizontalHeaderItem(i).text() for i in range(self.report_table.columnCount())]
                data = []
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                # Создание DataFrame и сохранение
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(fileName, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Успех', f'Отчет успешно сохранен в {fileName}')
                logging.debug(f"Отчет по остаткам сохранен в {fileName}")
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить отчет: {e}')
                logging.error(f"Не удалось сохранить отчет: {e}")
