# ui/send_notification_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt5.QtCore import Qt

class SendNotificationWindow(QWidget):
    def __init__(self, cloud_api):
        super().__init__()
        self.cloud_api = cloud_api
        self.setWindowTitle('Отправить уведомление')
        self.setFixedSize(400, 400)
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

        self.message_type_label = QLabel('Тип сообщения:')
        self.message_type_input = QLineEdit()
        layout.addWidget(self.message_type_label)
        layout.addWidget(self.message_type_input)

        self.order_id_label = QLabel('ID заказа:')
        self.order_id_input = QLineEdit()
        layout.addWidget(self.order_id_label)
        layout.addWidget(self.order_id_input)

        self.order_source_label = QLabel('Источник заказа:')
        self.order_source_input = QLineEdit()
        layout.addWidget(self.order_source_label)
        layout.addWidget(self.order_source_input)

        self.additional_info_label = QLabel('Дополнительная информация:')
        self.additional_info_input = QLineEdit()
        layout.addWidget(self.additional_info_label)
        layout.addWidget(self.additional_info_input)

        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_notification)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_notification(self):
        organization_id = self.organization_combo.currentData()
        message_type = self.message_type_input.text().strip()
        order_id = self.order_id_input.text().strip()
        order_source = self.order_source_input.text().strip()
        additional_info = self.additional_info_input.text().strip()

        if not all([organization_id, message_type, order_id, order_source]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

        try:
            response = self.cloud_api.send_notification(
                organization_id=organization_id,
                message_type=message_type,
                order_id=order_id,
                order_source=order_source,
                additional_info=additional_info
            )
            QMessageBox.information(self, 'Успех', f'Уведомление отправлено. Correlation ID: {response.get("correlationId")}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось отправить уведомление: {e}')
