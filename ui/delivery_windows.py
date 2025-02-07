# ui/delivery_windows.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QComboBox, QDateTimeEdit
from PyQt5.QtCore import Qt, QDateTime
import json

class AddItemsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Добавить позиции в заказ')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для ввода данных
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.items_label = QLabel('Позиции заказа (JSON):')
        self.items_input = QTextEdit()
        layout.addWidget(self.items_label)
        layout.addWidget(self.items_input)

        self.combos_label = QLabel('Комбо (JSON, опционально):')
        self.combos_input = QTextEdit()
        layout.addWidget(self.combos_label)
        layout.addWidget(self.combos_input)

        self.add_button = QPushButton('Добавить позиции')
        self.add_button.clicked.connect(self.add_items)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def add_items(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        items_str = self.items_input.toPlainText().strip()
        combos_str = self.combos_input.toPlainText().strip()

        if not all([organization_id, order_id, items_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            items = json.loads(items_str)
            combos = json.loads(combos_str) if combos_str else None
            result = self.cloud_api.add_items_to_order(organization_id, order_id, items, combos)
            QMessageBox.information(self, 'Успех', 'Позиции успешно добавлены в заказ.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить позиции: {e}')

class CloseOrderWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Закрыть заказ')
        self.setFixedSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.delivery_date_label = QLabel('Дата доставки (опционально):')
        self.delivery_date_input = QDateTimeEdit()
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.delivery_date_label)
        layout.addWidget(self.delivery_date_input)

        self.close_button = QPushButton('Закрыть заказ')
        self.close_button.clicked.connect(self.close_order)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def close_order(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        delivery_date = self.delivery_date_input.dateTime().toString('yyyy-MM-dd HH:mm:ss') if self.delivery_date_input.dateTime() else None

        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            result = self.cloud_api.close_order(organization_id, order_id, delivery_date)
            QMessageBox.information(self, 'Успех', 'Заказ успешно закрыт.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось закрыть заказ: {e}')

class CancelOrderWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Отменить заказ')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.cancel_cause_id_label = QLabel('Причина отмены (ID):')
        self.cancel_cause_id_input = QLineEdit()
        layout.addWidget(self.cancel_cause_id_label)
        layout.addWidget(self.cancel_cause_id_input)

        self.removal_type_id_label = QLabel('Тип удаления (ID):')
        self.removal_type_id_input = QLineEdit()
        layout.addWidget(self.removal_type_id_label)
        layout.addWidget(self.removal_type_id_input)

        self.user_id_for_writeoff_label = QLabel('ID пользователя для списания:')
        self.user_id_for_writeoff_input = QLineEdit()
        layout.addWidget(self.user_id_for_writeoff_label)
        layout.addWidget(self.user_id_for_writeoff_input)

        self.cancel_button = QPushButton('Отменить заказ')
        self.cancel_button.clicked.connect(self.cancel_order)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def cancel_order(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        cancel_cause_id = self.cancel_cause_id_input.text().strip() or None
        removal_type_id = self.removal_type_id_input.text().strip() or None
        user_id_for_writeoff = self.user_id_for_writeoff_input.text().strip() or None

        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните обязательные поля.')
            return

        try:
            result = self.cloud_api.cancel_order(
                organization_id,
                order_id,
                cancel_cause_id=cancel_cause_id,
                removal_type_id=removal_type_id,
                user_id_for_writeoff=user_id_for_writeoff
            )
            QMessageBox.information(self, 'Успех', 'Заказ успешно отменен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось отменить заказ: {e}')

class ChangeOrderCompleteBeforeWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить время доставки')
        self.setFixedSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.new_complete_before_label = QLabel('Новое время доставки:')
        self.new_complete_before_input = QDateTimeEdit()
        self.new_complete_before_input.setCalendarPopup(True)
        self.new_complete_before_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.new_complete_before_label)
        layout.addWidget(self.new_complete_before_input)

        self.change_button = QPushButton('Изменить время доставки')
        self.change_button.clicked.connect(self.change_complete_before)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_complete_before(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        new_complete_before = self.new_complete_before_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')

        if not all([organization_id, order_id, new_complete_before]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.change_order_complete_before(organization_id, order_id, new_complete_before)
            QMessageBox.information(self, 'Успех', 'Время доставки успешно изменено.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить время доставки: {e}')

class ChangeOrderDeliveryPointWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить адрес доставки')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.address_label = QLabel('Новый адрес доставки (JSON):')
        self.address_input = QTextEdit()
        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)

        self.change_button = QPushButton('Изменить адрес доставки')
        self.change_button.clicked.connect(self.change_delivery_point)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_delivery_point(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        address_str = self.address_input.toPlainText().strip()

        if not all([organization_id, order_id, address_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            new_delivery_point = json.loads(address_str)
            result = self.cloud_api.change_order_delivery_point(organization_id, order_id, new_delivery_point)
            QMessageBox.information(self, 'Успех', 'Адрес доставки успешно изменен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить адрес доставки: {e}')

class ChangeOrderServiceTypeWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить тип доставки')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.new_service_type_label = QLabel('Новый тип доставки:')
        self.new_service_type_combo = QComboBox()
        self.new_service_type_combo.addItems(['DeliveryByCourier', 'DeliveryByClient', 'DeliveryToCar', 'SelfService'])
        layout.addWidget(self.new_service_type_label)
        layout.addWidget(self.new_service_type_combo)

        self.delivery_point_label = QLabel('Адрес доставки (JSON):')
        self.delivery_point_input = QTextEdit()
        layout.addWidget(self.delivery_point_label)
        layout.addWidget(self.delivery_point_input)

        self.change_button = QPushButton('Изменить тип доставки')
        self.change_button.clicked.connect(self.change_service_type)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_service_type(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        new_service_type = self.new_service_type_combo.currentText()
        delivery_point_str = self.delivery_point_input.toPlainText().strip()

        if not all([organization_id, order_id, new_service_type, delivery_point_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            delivery_point = json.loads(delivery_point_str)
            result = self.cloud_api.change_order_service_type(organization_id, order_id, new_service_type, delivery_point)
            QMessageBox.information(self, 'Успех', 'Тип доставки успешно изменен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить тип доставки: {e}')

class ChangeOrderPaymentsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить платежи заказа')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.payments_label = QLabel('Платежи (JSON):')
        self.payments_input = QTextEdit()
        layout.addWidget(self.payments_label)
        layout.addWidget(self.payments_input)

        self.tips_label = QLabel('Чаевые (JSON, опционально):')
        self.tips_input = QTextEdit()
        layout.addWidget(self.tips_label)
        layout.addWidget(self.tips_input)

        self.change_button = QPushButton('Изменить платежи')
        self.change_button.clicked.connect(self.change_payments)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_payments(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        payments_str = self.payments_input.toPlainText().strip()
        tips_str = self.tips_input.toPlainText().strip()

        if not all([organization_id, order_id, payments_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните обязательные поля.')
            return

        try:
            payments = json.loads(payments_str)
            tips = json.loads(tips_str) if tips_str else None
            result = self.cloud_api.change_order_payments(organization_id, order_id, payments, tips)
            QMessageBox.information(self, 'Успех', 'Платежи успешно изменены.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить платежи: {e}')

class ChangeOrderCommentWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить комментарий к заказу')
        self.setFixedSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.comment_label = QLabel('Новый комментарий:')
        self.comment_input = QTextEdit()
        layout.addWidget(self.comment_label)
        layout.addWidget(self.comment_input)

        self.change_button = QPushButton('Изменить комментарий')
        self.change_button.clicked.connect(self.change_comment)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_comment(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        comment = self.comment_input.toPlainText().strip()

        if not all([organization_id, order_id, comment]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.change_order_comment(organization_id, order_id, comment)
            QMessageBox.information(self, 'Успех', 'Комментарий успешно изменен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить комментарий: {e}')

class PrintDeliveryBillWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Распечатать счет доставки')
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.print_button = QPushButton('Распечатать счет')
        self.print_button.clicked.connect(self.print_bill)
        layout.addWidget(self.print_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def print_bill(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()

        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.print_delivery_bill(organization_id, order_id)
            QMessageBox.information(self, 'Успех', 'Счет успешно отправлен на печать.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось распечатать счет: {e}')

class ConfirmDeliveryWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Подтвердить доставку')
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.confirm_button = QPushButton('Подтвердить доставку')
        self.confirm_button.clicked.connect(self.confirm_delivery)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def confirm_delivery(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()

        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.confirm_delivery(organization_id, order_id)
            QMessageBox.information(self, 'Успех', 'Доставка успешно подтверждена.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось подтвердить доставку: {e}')

class CancelDeliveryConfirmationWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Отменить подтверждение доставки')
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.cancel_button = QPushButton('Отменить подтверждение')
        self.cancel_button.clicked.connect(self.cancel_confirmation)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def cancel_confirmation(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()

        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.cancel_delivery_confirmation(organization_id, order_id)
            QMessageBox.information(self, 'Успех', 'Подтверждение доставки успешно отменено.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось отменить подтверждение: {e}')

class ChangeOrderOperatorWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить оператора заказа')
        self.setFixedSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.operator_id_label = QLabel('ID оператора:')
        self.operator_id_input = QLineEdit()
        layout.addWidget(self.operator_id_label)
        layout.addWidget(self.operator_id_input)

        self.change_button = QPushButton('Изменить оператора')
        self.change_button.clicked.connect(self.change_operator)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_operator(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        operator_id = self.operator_id_input.text().strip()

        if not all([organization_id, order_id, operator_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return

        try:
            result = self.cloud_api.change_order_operator(organization_id, order_id, operator_id)
            QMessageBox.information(self, 'Успех', 'Оператор заказа успешно изменен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить оператора: {e}')

class AddOrderPaymentsWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Добавить оплату к заказу')
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)
        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)
        self.payments_label = QLabel('Платежи (JSON):')
        self.payments_input = QTextEdit()
        layout.addWidget(self.payments_label)
        layout.addWidget(self.payments_input)
        self.tips_label = QLabel('Чаевые (JSON, опционально):')
        self.tips_input = QTextEdit()
        layout.addWidget(self.tips_label)
        layout.addWidget(self.tips_input)
        self.add_button = QPushButton('Добавить оплату')
        self.add_button.clicked.connect(self.add_payments)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def add_payments(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        payments_str = self.payments_input.toPlainText().strip()
        tips_str = self.tips_input.toPlainText().strip()
        if not all([organization_id, order_id, payments_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните обязательные поля.')
            return
        try:
            payments = json.loads(payments_str)
            tips = json.loads(tips_str) if tips_str else None
            result = self.cloud_api.add_order_payments(organization_id, order_id, payments, tips)
            QMessageBox.information(self, 'Успех', 'Оплата успешно добавлена.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить оплату: {e}')

class ChangeDriverInfoWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Изменить информацию о водителе')
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)
        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)
        self.driver_id_label = QLabel('ID водителя (опционально):')
        self.driver_id_input = QLineEdit()
        layout.addWidget(self.driver_id_label)
        layout.addWidget(self.driver_id_input)
        self.estimated_time_label = QLabel('Расчетное время доставки (опционально):')
        self.estimated_time_input = QDateTimeEdit()
        self.estimated_time_input.setCalendarPopup(True)
        self.estimated_time_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.estimated_time_label)
        layout.addWidget(self.estimated_time_input)
        self.change_button = QPushButton('Изменить информацию')
        self.change_button.clicked.connect(self.change_driver_info)
        layout.addWidget(self.change_button)
        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def change_driver_info(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        driver_id = self.driver_id_input.text().strip() or None
        estimated_time = self.estimated_time_input.dateTime().toString('yyyy-MM-dd HH:mm:ss') if self.estimated_time_input.dateTime() else None
        if not all([organization_id, order_id]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните обязательные поля.')
            return
        try:
            result = self.cloud_api.change_driver_info(organization_id, order_id, driver_id, estimated_time)
            QMessageBox.information(self, 'Успех', 'Информация о водителе успешно изменена.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить информацию: {e}')


class CreateDeliveryWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Создать доставку')
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для ввода данных
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.delivery_details_label = QLabel('Детали доставки (JSON):')
        self.delivery_details_input = QTextEdit()
        layout.addWidget(self.delivery_details_label)
        layout.addWidget(self.delivery_details_input)

        self.create_button = QPushButton('Создать доставку')
        self.create_button.clicked.connect(self.create_delivery)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def create_delivery(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        delivery_details_str = self.delivery_details_input.toPlainText().strip()

        if not all([organization_id, order_id, delivery_details_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            delivery_details = json.loads(delivery_details_str)
            result = self.cloud_api.create_delivery(organization_id, order_id, delivery_details)
            QMessageBox.information(self, 'Успех', 'Доставка успешно создана.')
            self.close()
        except json.JSONDecodeError:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный JSON в деталях доставки.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось создать доставку: {e}')


class UpdateOrderExternalDataWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Обновить внешние данные заказа')
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для ввода данных
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.external_data_label = QLabel('Внешние данные (JSON):')
        self.external_data_input = QTextEdit()
        layout.addWidget(self.external_data_label)
        layout.addWidget(self.external_data_input)

        self.update_button = QPushButton('Обновить данные')
        self.update_button.clicked.connect(self.update_external_data)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def update_external_data(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        external_data_str = self.external_data_input.toPlainText().strip()

        if not all([organization_id, order_id, external_data_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            external_data = json.loads(external_data_str)
            result = self.cloud_api.update_order_external_data(organization_id, order_id, external_data)
            QMessageBox.information(self, 'Успех', 'Внешние данные заказа успешно обновлены.')
            self.close()
        except json.JSONDecodeError:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный JSON во внешних данных.')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось обновить внешние данные: {e}')

class UpdateDeliveryStatusWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Обновить статус доставки')
        self.setFixedSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для ввода данных
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.status_label = QLabel('Новый статус доставки:')
        self.status_combo = QComboBox()
        self.status_combo.addItems(['В пути', 'Доставлено', 'Отменено', 'Возвращено'])
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_combo)

        self.update_button = QPushButton('Обновить статус')
        self.update_button.clicked.connect(self.update_delivery_status)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def update_delivery_status(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        new_status = self.status_combo.currentText()

        if not all([organization_id, order_id, new_status]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            result = self.cloud_api.update_delivery_status(
                organization_id,
                order_id,
                new_status
            )
            QMessageBox.information(self, 'Успех', 'Статус доставки успешно обновлен.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось обновить статус доставки: {e}')


class UpdateOrderProblemWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Обновить проблему заказа')
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для ввода данных
        self.organization_label = QLabel('Организация:')
        self.organization_combo = QComboBox()
        self.load_organizations()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_combo)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.problem_description_label = QLabel('Описание проблемы:')
        self.problem_description_input = QTextEdit()
        layout.addWidget(self.problem_description_label)
        layout.addWidget(self.problem_description_input)

        self.problem_type_label = QLabel('Тип проблемы:')
        self.problem_type_combo = QComboBox()
        self.problem_type_combo.addItems(['Оплата', 'Доставка', 'Качество товара', 'Другие'])
        layout.addWidget(self.problem_type_label)
        layout.addWidget(self.problem_type_combo)

        self.update_button = QPushButton('Обновить проблему')
        self.update_button.clicked.connect(self.update_order_problem)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def load_organizations(self):
        try:
            organizations = self.cloud_api.get_organizations()
            self.organization_map = {}
            for org in organizations:
                self.organization_combo.addItem(org['name'])
                self.organization_map[org['name']] = org['id']
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить организации: {e}')

    def update_order_problem(self):
        organization_name = self.organization_combo.currentText()
        organization_id = self.organization_map.get(organization_name)
        order_id = self.order_id_input.text().strip()
        problem_description = self.problem_description_input.toPlainText().strip()
        problem_type = self.problem_type_combo.currentText()

        if not all([organization_id, order_id, problem_description, problem_type]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            result = self.cloud_api.update_order_problem(
                organization_id,
                order_id,
                problem_description,
                problem_type
            )
            QMessageBox.information(self, 'Успех', 'Проблема заказа успешно обновлена.')
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось обновить проблему заказа: {e}')


class GetTerminalGroupsAvailabilityWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Проверить доступность терминалов')
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.organization_label = QLabel('Идентификаторы организаций (через запятую):')
        self.organization_ids_input = QLineEdit()
        layout.addWidget(self.organization_label)
        layout.addWidget(self.organization_ids_input)
        self.terminal_group_ids_label = QLabel('Идентификаторы групп терминалов (через запятую):')
        self.terminal_group_ids_input = QLineEdit()
        layout.addWidget(self.terminal_group_ids_label)
        layout.addWidget(self.terminal_group_ids_input)
        self.check_button = QPushButton('Проверить доступность')
        self.check_button.clicked.connect(self.check_availability)
        layout.addWidget(self.check_button)
        self.setLayout(layout)





    def check_availability(self):
        organization_ids_str = self.organization_ids_input.text().strip()
        terminal_group_ids_str = self.terminal_group_ids_input.text().strip()
        if not all([organization_ids_str, terminal_group_ids_str]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return
        try:
            organization_ids = [id.strip() for id in organization_ids_str.split(',')]
            terminal_group_ids = [id.strip() for id in terminal_group_ids_str.split(',')]
            result = self.cloud_api.get_terminal_groups_availability(organization_ids, terminal_group_ids)
            is_alive_status = result.get('isAliveStatus', [])
            message = '\n'.join([f"Terminal Group ID: {status.get('terminalGroupId')} - Alive: {status.get('isAlive')}" for status in is_alive_status])
            QMessageBox.information(self, 'Результат', message)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось получить доступность: {e}')
