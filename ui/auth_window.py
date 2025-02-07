# ui/auth_window.py

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import pyqtSignal
import hashlib
import requests
from api.syrve_cloud import SyrveCloudAPI
from api.iiko_server import IikoServerAPI

class AuthWindow(QWidget):
    login_successful = pyqtSignal(object)  # Будет передавать разные данные в зависимости от метода авторизации

    def __init__(self, auth_method):
        super().__init__()
        self.auth_method = auth_method  # 'cloud' или 'server'
        self.setWindowTitle('Авторизация')
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        if self.auth_method == 'cloud':
            self.api_login_label = QLabel('API Login:')
            self.api_login_input = QLineEdit()
            self.login_button = QPushButton('Войти')
            self.login_button.clicked.connect(self.handle_cloud_login)

            layout.addWidget(self.api_login_label)
            layout.addWidget(self.api_login_input)
            layout.addWidget(self.login_button)
        elif self.auth_method == 'server':
            self.server_url_label = QLabel('URL сервера:')
            self.server_url_input = QLineEdit()
            self.login_label = QLabel('Логин:')
            self.login_input = QLineEdit()
            self.password_label = QLabel('Пароль:')
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.login_button = QPushButton('Войти')
            self.login_button.clicked.connect(self.handle_server_login)

            layout.addWidget(self.server_url_label)
            layout.addWidget(self.server_url_input)
            layout.addWidget(self.login_label)
            layout.addWidget(self.login_input)
            layout.addWidget(self.password_label)
            layout.addWidget(self.password_input)
            layout.addWidget(self.login_button)
        self.setLayout(layout)

    def handle_cloud_login(self):
        api_login = self.api_login_input.text().strip()
        if not api_login:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите API Login.')
            return
        try:
            # Передаем api_login обратно в главный класс
            self.login_successful.emit(api_login)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить авторизацию: {e}')

    def handle_server_login(self):
        server_url = self.server_url_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text()
        if not all([server_url, login, password]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return
        try:
            # Создаем экземпляр IikoServerAPI и авторизуемся
            self.server_api = IikoServerAPI(server_url, login, password)
            # Передаем экземпляр API-клиента в главный класс
            self.login_successful.emit(self.server_api)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить авторизацию: {e}')

    def authorize_server(self, server_url, login, password):
        # Реализация авторизации по Server API
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        auth_url = f"{server_url}/resto/api/auth"
        params = {'login': login, 'pass': password_hash}
        response = requests.get(auth_url, params=params, verify=False)
        response.raise_for_status()
        token = response.text.strip()
        if not token:
            token = response.cookies.get('key')
        return token
