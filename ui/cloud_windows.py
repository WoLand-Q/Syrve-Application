# ui/cloud_windows.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QTextEdit, QComboBox, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QHBoxLayout, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QDateTime
import json
import pandas as pd
import logging

class LoyaltyManagementWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Управление Лояльностью')
        self.setFixedSize(800, 800)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Управление Лояльностью Клиентов')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Организации
        org_layout = QVBoxLayout()
        self.organization_label = QLabel('Выберите Организацию:')
        self.organization_combo = QComboBox()
        org_layout.addWidget(self.organization_label)
        org_layout.addWidget(self.organization_combo)
        layout.addLayout(org_layout)

        # Ввод телефона
        self.phone_label = QLabel('Телефон клиента:')
        self.phone_input = QLineEdit()
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)

        # Кнопка получения информации о клиенте
        self.fetch_customer_button = QPushButton('Получить Информацию о Клиенте')
        self.fetch_customer_button.clicked.connect(self.fetch_customer_info)
        layout.addWidget(self.fetch_customer_button)

        # Поле для отображения информации о клиенте
        self.customer_info = QTextEdit()
        self.customer_info.setReadOnly(True)
        layout.addWidget(self.customer_info)

        # Кнопка проверки нового клиента
        self.check_new_customer_button = QPushButton('Проверить, является ли клиент новым')
        self.check_new_customer_button.clicked.connect(self.check_new_customer)
        layout.addWidget(self.check_new_customer_button)

        # Кнопка генерации промокода
        self.generate_coupon_button = QPushButton('Сгенерировать Промокод')
        self.generate_coupon_button.clicked.connect(self.generate_coupon)
        layout.addWidget(self.generate_coupon_button)

        self.setLayout(layout)

        # Загрузка списка организаций при инициализации
        self.load_organizations()

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
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

    def fetch_customer_info(self):
        organization_id = self.organization_combo.currentData()
        phone = self.phone_input.text().strip()

        if not all([organization_id, phone]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите организацию и введите телефон.')
            return

        try:
            logging.debug("Обновление organization_id в API клиенте")
            self.cloud_api.organization_id = organization_id

            logging.debug(f"Получение информации о клиенте с телефоном: {phone}")
            customer_info = self.cloud_api.get_customer_info(phone)
            if customer_info:
                logging.debug("Информация о клиенте получена, отображение информации")
                self.display_customer_info(customer_info)
                logging.debug("Извлечение бренда клиента")
                comment = customer_info.get("comment", "")
                if comment is None:
                    comment = ""
                self.current_customer_brand = self.extract_brand(comment)
                self.current_customer_id = customer_info.get("id")
                logging.debug(f"Текущий бренд клиента: {self.current_customer_brand}")
            else:
                QMessageBox.information(self, 'Информация', 'Клиент не найден.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить информацию о клиенте: {e}')
            logging.error(f"Не удалось получить информацию о клиенте: {e}")

    def display_customer_info(self, customer_info):
        """
        Отображение информации о клиенте в текстовом поле.
        """
        info_text = (
            f"ID: {customer_info.get('id', 'N/A')}\n"
            f"Имя: {customer_info.get('name', 'N/A')}\n"
            f"Фамилия: {customer_info.get('surname', 'N/A')}\n"
            f"Отчество: {customer_info.get('middleName', 'N/A')}\n"
            f"Телефон: {customer_info.get('phone', 'N/A')}\n"
            f"Email: {customer_info.get('email', 'N/A')}\n"
            f"Комментарий: {customer_info.get('comment', 'N/A')}\n"
            f"Дата регистрации: {customer_info.get('whenRegistered', 'N/A')}\n"
            f"Дата согласия на обработку данных: {customer_info.get('personalDataConsentFrom', 'N/A')} до {customer_info.get('personalDataConsentTo', 'N/A')}\n"
        )
        self.customer_info.setText(info_text)
        logging.debug("Информация о клиенте отображена в интерфейсе.")

    def extract_brand(self, comment):
        """
        Извлечение бренда из комментария клиента.
        """
        if "SH" in comment:
            return "SH"
        elif "BL" in comment:
            return "BL"
        elif "BS" in comment:
            return "BS"
        else:
            return "Unknown"

    def check_new_customer(self):
        if not hasattr(self, 'current_customer_id') or not self.current_customer_id:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, сначала получите информацию о клиенте.')
            return

        try:
            transactions = self.cloud_api.get_transactions_by_revision(
                self.current_customer_id,
                revision=0,
                last_transaction_id=None
            )
            is_new = self.cloud_api.is_new_customer(transactions, brand_id=self.current_customer_brand)
            if is_new:
                QMessageBox.information(self, 'Информация', 'Клиент является новым.')
            else:
                QMessageBox.information(self, 'Информация', 'Клиент не является новым.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось проверить статус клиента: {e}')
            logging.error(f"Не удалось проверить статус клиента: {e}")

    def generate_coupon(self):
        if not hasattr(self, 'current_customer_id') or not self.current_customer_id:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, сначала получите информацию о клиенте.')
            return

        if self.current_customer_brand == "Unknown":
            QMessageBox.warning(self, 'Ошибка', 'Не удалось определить бренд клиента.')
            return

        try:
            # Загрузка существующих купонов
            existing_coupons = self.cloud_api.load_existing_coupons('existing_coupons.txt')

            # Генерация нового промокода
            promo_code = self.cloud_api.create_new_coupon(prefix='N', brand=self.current_customer_brand, existing_coupons=existing_coupons)
            QMessageBox.information(self, 'Успех', f'Сгенерирован промокод: {promo_code}')

            # Сохранение промокода
            success = self.cloud_api.save_new_coupon('existing_coupons.txt', promo_code)
            if success:
                logging.debug(f"Промокод {promo_code} успешно сохранён.")
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить промокод.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сгенерировать промокод: {e}')
            logging.error(f"Не удалось сгенерировать промокод: {e}")

class DeliveryHistoryWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('История Доставок')
        self.setFixedSize(800, 800)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Получение Истории Доставок')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Организации
        org_layout = QHBoxLayout()
        self.organization_label = QLabel('Выберите Организацию:')
        self.organization_combo = QComboBox()
        org_layout.addWidget(self.organization_label)
        org_layout.addWidget(self.organization_combo)
        layout.addLayout(org_layout)

        # Телефон
        self.phone_label = QLabel('Телефон:')
        self.phone_input = QLineEdit()
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)

        # Кнопка получения истории доставок
        self.fetch_history_button = QPushButton('Получить Историю Доставок')
        self.fetch_history_button.clicked.connect(self.fetch_delivery_history)
        layout.addWidget(self.fetch_history_button)

        # Таблица для отображения истории доставок
        self.history_table = QTableWidget()
        layout.addWidget(self.history_table)

        # Кнопка сохранения отчета
        self.save_button = QPushButton('Сохранить в CSV')
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Загрузка списка организаций при инициализации
        self.load_organizations()

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            if organizations:
                self.organization_combo.clear()
                for org in organizations:
                    org_id = org.get("id", "")
                    org_name = org.get("name", "Без названия")
                    self.organization_combo.addItem(f"{org_name} ({org_id})", org_id)
                logging.debug("Список организаций успешно загружен и отображен в выпадающем списке.")
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Список организаций пуст.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить список организаций: {e}')
            logging.error(f"Не удалось загрузить список организаций: {e}")

    def fetch_delivery_history(self):
        phone = self.phone_input.text().strip()
        organization_id = self.organization_combo.currentData()
        logging.debug(f"Введённый телефон: {phone}")
        logging.debug(f"Выбранная организация ID: {organization_id}")

        if not phone:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите телефон.')
            return

        if not organization_id:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите организацию.')
            return

        try:
            logging.debug("Обновление organization_id в API клиенте")
            self.cloud_api.organization_id = organization_id

            # Получаем информацию о клиенте по телефону
            logging.debug(f"Получение информации о клиенте с телефоном: {phone}")
            customer_info = self.cloud_api.get_customer_info(phone)
            if not customer_info:
                QMessageBox.information(self, 'Информация', 'Клиент не найден.')
                return

            customer_id = customer_info.get('id')
            if not customer_id:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось получить ID клиента.')
                return

            logging.debug(f"Получение истории доставок для клиента ID: {customer_id}")
            transactions = self.cloud_api.get_delivery_history(customer_id)
            if transactions:
                self.display_history(transactions)
            else:
                QMessageBox.information(self, 'Информация', 'История доставок не найдена.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить историю доставок: {e}')
            logging.error(f"Не удалось получить историю доставок: {e}")

    def display_history(self, transactions):
        self.history_table.clear()
        try:
            if not transactions:
                QMessageBox.information(self, 'Информация', 'История транзакций пуста.')
                return

            # Определяем все возможные ключи из транзакций
            all_keys = set()
            for transaction in transactions:
                all_keys.update(transaction.keys())

            headers = sorted(list(all_keys))
            self.history_table.setColumnCount(len(headers))
            self.history_table.setHorizontalHeaderLabels(headers)
            self.history_table.setRowCount(len(transactions))

            for row, transaction in enumerate(transactions):
                for col, key in enumerate(headers):
                    value = transaction.get(key, "")
                    if isinstance(value, dict):
                        value = json.dumps(value, ensure_ascii=False)
                    self.history_table.setItem(row, col, QTableWidgetItem(str(value)))

            self.history_table.resizeColumnsToContents()
            logging.debug("История транзакций успешно отображена в таблице.")
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при отображении истории: {e}')
            logging.error(f"Ошибка при отображении истории: {e}")

    def save_report(self):
        if self.history_table.rowCount() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Нет данных для сохранения.')
            return

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет в CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            try:
                headers = [self.history_table.horizontalHeaderItem(i).text() for i in range(self.history_table.columnCount())]
                data = []
                for row in range(self.history_table.rowCount()):
                    row_data = []
                    for col in range(self.history_table.columnCount()):
                        item = self.history_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                df = pd.DataFrame(data, columns=headers)
                df.to_csv(fileName, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Успех', f'Отчет успешно сохранен в {fileName}')
                logging.debug(f"Отчет по доставкам сохранен в {fileName}")
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить отчет: {e}')
                logging.error(f"Не удалось сохранить отчет: {e}")
