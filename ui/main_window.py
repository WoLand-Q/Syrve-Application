# ui/main_window.py
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMessageBox, QLabel,
    QStackedWidget, QWidget, QVBoxLayout, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QSize
from ui.auth_window import AuthWindow
from ui.external_menus_window import ExternalMenusWindow, PaymentTypesWindow
from ui.reports_window import ReportsWindow
from api.syrve_cloud import SyrveCloudAPI
# from api.iiko_server import IikoServerAPI  # Раскомментируйте, если используете
from ui.cloud_windows import LoyaltyManagementWindow, DeliveryHistoryWindow
from ui.server_windows import OlapReportWindow, BalanceReportWindow


from ui.delivery_windows import (
    AddItemsWindow,
    CloseOrderWindow,
    CancelOrderWindow,
    ChangeOrderCompleteBeforeWindow,
    ChangeOrderDeliveryPointWindow,
    ChangeOrderServiceTypeWindow,
    ChangeOrderPaymentsWindow,
    ChangeOrderCommentWindow,
    PrintDeliveryBillWindow,
    ConfirmDeliveryWindow,
    CancelDeliveryConfirmationWindow,
    ChangeOrderOperatorWindow,
    AddOrderPaymentsWindow,
    ChangeDriverInfoWindow,
    GetTerminalGroupsAvailabilityWindow,
    UpdateOrderExternalDataWindow,
    CreateDeliveryWindow,
    UpdateOrderProblemWindow,
    UpdateDeliveryStatusWindow
)

import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Syrve Application')
        self.setFixedSize(1280, 800)
        self.cloud_api = None
        self.server_api = None
        self.init_ui()

    def init_ui(self):
        # Настройка логирования
        logging.basicConfig(level=logging.DEBUG)

        # Создаем меню
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #34495e; /* Темно-синий цвет */
                color: white;
                font-size: 14px;
            }
            QMenuBar::item {
                background-color: #34495e;
                color: white;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #2c3e50;
            }
            QMenu {
                background-color: #2c3e50;
                color: white;
                font-size: 14px;
            }
            QMenu::item {
                background-color: #2c3e50;
                color: white;
                padding: 5px 10px;
            }
            QMenu::item:selected {
                background-color: #34495e;
            }
        """)

        # Функция для создания иконки из смайлика
        def create_icon_from_emoji(emoji_char):
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont('Segoe UI Emoji', 24))  # Шрифт, поддерживающий эмодзи
            painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji_char)
            painter.end()
            return QIcon(pixmap)

        # Смайлики для меню
        emoji_icons = {
            'organizations': '🏢',
            'terminal_groups': '🖥️',
            'send_notification': '📢',
            'nomenclature': '📋',
            'reports': '📈',
            'logout': '🚪',
            'delivery': '🚚',
            'menu': '📂',
            'payment_type': '💳'  # Смайлик для типов платежей
        }

        # Меню авторизации
        auth_menu = menubar.addMenu('Авторизация')

        cloud_auth_action = QAction('Авторизация по Cloud API', self)
        cloud_auth_action.triggered.connect(self.cloud_api_auth)
        cloud_auth_action.setIcon(create_icon_from_emoji(emoji_icons['menu']))  # Смайлик меню
        auth_menu.addAction(cloud_auth_action)

        server_auth_action = QAction('Авторизация по Server API', self)
        server_auth_action.triggered.connect(self.server_api_auth)
        server_auth_action.setIcon(create_icon_from_emoji(emoji_icons['menu']))  # Используем тот же смайлик меню
        auth_menu.addAction(server_auth_action)

        # Создаем новое меню "Custom API"
        custom_api_menu = menubar.addMenu('Custom API')

        # Добавляем действия для каждого скрипта
        olap_report_action = QAction('OLAP Отчет', self)
        olap_report_action.triggered.connect(self.open_olap_report_window)
        custom_api_menu.addAction(olap_report_action)

        balance_report_action = QAction('Отчет по Остаткам', self)
        balance_report_action.triggered.connect(self.open_balance_report_window)
        custom_api_menu.addAction(balance_report_action)

        loyalty_management_action = QAction('Управление Лояльностью', self)
        loyalty_management_action.triggered.connect(self.open_loyalty_management_window)
        custom_api_menu.addAction(loyalty_management_action)

        delivery_history_action = QAction('История Доставок', self)
        delivery_history_action.triggered.connect(self.open_delivery_history_window)
        custom_api_menu.addAction(delivery_history_action)
        # Меню Cloud API
        cloud_menu = menubar.addMenu('Cloud API')

        payment_types_action = QAction('Типы платежей', self)
        payment_types_action.triggered.connect(self.show_payment_types)
        payment_types_action.setIcon(create_icon_from_emoji(emoji_icons['payment_type']))
        cloud_menu.addAction(payment_types_action)

        organizations_action = QAction('Организации', self)
        organizations_action.triggered.connect(self.show_organizations)
        organizations_action.setIcon(create_icon_from_emoji(emoji_icons['organizations']))
        cloud_menu.addAction(organizations_action)

        external_menus_action = QAction('Внешние меню', self)
        external_menus_action.triggered.connect(self.show_external_menus)
        external_menus_action.setIcon(create_icon_from_emoji(emoji_icons['menu']))
        cloud_menu.addAction(external_menus_action)

        terminal_groups_action = QAction('Группы терминалов', self)
        terminal_groups_action.triggered.connect(self.show_terminal_groups)
        terminal_groups_action.setIcon(create_icon_from_emoji(emoji_icons['terminal_groups']))
        cloud_menu.addAction(terminal_groups_action)

        send_notification_action = QAction('Отправить уведомление', self)
        send_notification_action.triggered.connect(self.send_notification)
        send_notification_action.setIcon(create_icon_from_emoji(emoji_icons['send_notification']))
        cloud_menu.addAction(send_notification_action)

        nomenclature_action = QAction('Номенклатура', self)
        nomenclature_action.triggered.connect(self.show_nomenclature)
        nomenclature_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        cloud_menu.addAction(nomenclature_action)

        # Меню доставок
        deliveries_menu = menubar.addMenu('Доставки Cloud API')

        # Добавляем пункты меню для всех методов доставки
        create_delivery_action = QAction('Создать доставку', self)
        create_delivery_action.triggered.connect(self.create_delivery)
        create_delivery_action.setIcon(create_icon_from_emoji(emoji_icons['delivery']))
        deliveries_menu.addAction(create_delivery_action)

        update_order_external_data_action = QAction('Обновить внешние данные заказа', self)
        update_order_external_data_action.triggered.connect(self.update_order_external_data)
        update_order_external_data_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        deliveries_menu.addAction(update_order_external_data_action)

        update_order_problem_action = QAction('Обновить проблему заказа', self)
        update_order_problem_action.triggered.connect(self.update_order_problem)
        update_order_problem_action.setIcon(create_icon_from_emoji(emoji_icons['send_notification']))
        deliveries_menu.addAction(update_order_problem_action)

        update_delivery_status_action = QAction('Обновить статус доставки', self)
        update_delivery_status_action.triggered.connect(self.update_delivery_status)
        update_delivery_status_action.setIcon(create_icon_from_emoji(emoji_icons['reports']))
        deliveries_menu.addAction(update_delivery_status_action)

        add_items_to_order_action = QAction('Добавить позиции в заказ', self)
        add_items_to_order_action.triggered.connect(self.add_items_to_order)
        add_items_to_order_action.setIcon(create_icon_from_emoji(emoji_icons['payment_type']))  # Смайлик для платежей
        deliveries_menu.addAction(add_items_to_order_action)

        close_order_action = QAction('Закрыть заказ', self)
        close_order_action.triggered.connect(self.close_order)
        close_order_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        deliveries_menu.addAction(close_order_action)

        cancel_order_action = QAction('Отменить заказ', self)
        cancel_order_action.triggered.connect(self.cancel_order)
        cancel_order_action.setIcon(create_icon_from_emoji(emoji_icons['send_notification']))
        deliveries_menu.addAction(cancel_order_action)

        change_order_complete_before_action = QAction('Изменить время доставки', self)
        change_order_complete_before_action.triggered.connect(self.change_order_complete_before)
        change_order_complete_before_action.setIcon(create_icon_from_emoji(emoji_icons['reports']))
        deliveries_menu.addAction(change_order_complete_before_action)

        change_order_delivery_point_action = QAction('Изменить адрес доставки', self)
        change_order_delivery_point_action.triggered.connect(self.change_order_delivery_point)
        change_order_delivery_point_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        deliveries_menu.addAction(change_order_delivery_point_action)

        change_order_service_type_action = QAction('Изменить тип доставки', self)
        change_order_service_type_action.triggered.connect(self.change_order_service_type)
        change_order_service_type_action.setIcon(create_icon_from_emoji(emoji_icons['delivery']))
        deliveries_menu.addAction(change_order_service_type_action)

        change_order_payments_action = QAction('Изменить платежи заказа', self)
        change_order_payments_action.triggered.connect(self.change_order_payments)
        change_order_payments_action.setIcon(create_icon_from_emoji(emoji_icons['payment_type']))
        deliveries_menu.addAction(change_order_payments_action)

        change_order_comment_action = QAction('Изменить комментарий к заказу', self)
        change_order_comment_action.triggered.connect(self.change_order_comment)
        change_order_comment_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        deliveries_menu.addAction(change_order_comment_action)

        print_delivery_bill_action = QAction('Распечатать счет доставки', self)
        print_delivery_bill_action.triggered.connect(self.print_delivery_bill)
        print_delivery_bill_action.setIcon(create_icon_from_emoji(emoji_icons['reports']))
        deliveries_menu.addAction(print_delivery_bill_action)

        confirm_delivery_action = QAction('Подтвердить доставку', self)
        confirm_delivery_action.triggered.connect(self.confirm_delivery)
        confirm_delivery_action.setIcon(create_icon_from_emoji(emoji_icons['reports']))
        deliveries_menu.addAction(confirm_delivery_action)

        cancel_delivery_confirmation_action = QAction('Отменить подтверждение доставки', self)
        cancel_delivery_confirmation_action.triggered.connect(self.cancel_delivery_confirmation)
        cancel_delivery_confirmation_action.setIcon(create_icon_from_emoji(emoji_icons['send_notification']))
        deliveries_menu.addAction(cancel_delivery_confirmation_action)

        change_order_operator_action = QAction('Изменить оператора заказа', self)
        change_order_operator_action.triggered.connect(self.change_order_operator)
        change_order_operator_action.setIcon(create_icon_from_emoji(emoji_icons['nomenclature']))
        deliveries_menu.addAction(change_order_operator_action)

        add_order_payments_action = QAction('Добавить оплату к заказу', self)
        add_order_payments_action.triggered.connect(self.add_order_payments)
        add_order_payments_action.setIcon(create_icon_from_emoji(emoji_icons['payment_type']))
        deliveries_menu.addAction(add_order_payments_action)

        change_driver_info_action = QAction('Изменить информацию о водителе', self)
        change_driver_info_action.triggered.connect(self.change_driver_info)
        change_driver_info_action.setIcon(create_icon_from_emoji(emoji_icons['delivery']))
        deliveries_menu.addAction(change_driver_info_action)

        get_terminal_groups_availability_action = QAction('Проверить доступность терминалов', self)
        get_terminal_groups_availability_action.triggered.connect(self.get_terminal_groups_availability)
        get_terminal_groups_availability_action.setIcon(create_icon_from_emoji(emoji_icons['terminal_groups']))
        deliveries_menu.addAction(get_terminal_groups_availability_action)

        # Меню отчётов для Server API
        reports_menu = menubar.addMenu('Отчёты Server API')

        reports_action = QAction('Отчёты', self)
        reports_action.triggered.connect(self.show_reports)
        reports_action.setIcon(create_icon_from_emoji(emoji_icons['reports']))
        reports_menu.addAction(reports_action)

        # Действие выхода
        logout_action = QAction('Выйти', self)
        logout_action.triggered.connect(self.logout)
        logout_action.setIcon(create_icon_from_emoji(emoji_icons['logout']))
        menubar.addAction(logout_action)

        # Создаем центральный виджет с красивым цветом
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ecf0f1;")  # Светло-серый цвет фона
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(central_widget)
        self.setCentralWidget(self.stacked_widget)

        # Приветственный экран с красивым цветом и смайликом
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel('Добро пожаловать в Syrve Application! 😊')
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont('Arial', 24, QFont.Bold))
        welcome_label.setStyleSheet('color: #2c3e50;')  # Темно-синий цвет текста

        welcome_layout.addWidget(welcome_label)
        welcome_widget.setLayout(welcome_layout)
        self.stacked_widget.addWidget(welcome_widget)

        # Анимация появления приветственного текста
        opacity_effect = QGraphicsOpacityEffect()
        welcome_label.setGraphicsEffect(opacity_effect)
        self.opacity_animation = QPropertyAnimation(opacity_effect, b'opacity')
        self.opacity_animation.setDuration(2000)  # Продолжительность в миллисекундах
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.start()

    # Методы для действий меню

    def show_external_menus(self):
        if self.cloud_api:
            self.external_menus_window = ExternalMenusWindow(self.cloud_api)
            self.external_menus_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def cloud_api_auth(self):
        self.auth_window = AuthWindow('cloud')
        self.auth_window.login_successful.connect(self.handle_cloud_login)
        self.auth_window.show()

    def handle_cloud_login(self, api_login):
        try:
            self.cloud_api = SyrveCloudAPI(api_login)
            QMessageBox.information(self, 'Успех', 'Успешная авторизация по Cloud API')
            self.auth_window.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить авторизацию: {e}')

    def server_api_auth(self):
        self.auth_window = AuthWindow('server')
        self.auth_window.login_successful.connect(self.handle_server_login)
        self.auth_window.show()

    def handle_server_login(self, server_api):
        try:
            self.server_api = server_api
            QMessageBox.information(self, 'Успех', 'Успешная авторизация по Server API')
            self.auth_window.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить авторизацию: {e}')

    def show_organizations(self):
        if self.cloud_api:
            from ui.organizations_window import OrganizationsWindow
            self.organizations_window = OrganizationsWindow(self.cloud_api)
            self.organizations_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def show_terminal_groups(self):
        if self.cloud_api:
            from ui.terminal_groups_window import TerminalGroupsWindow
            self.terminal_groups_window = TerminalGroupsWindow(self.cloud_api)
            self.terminal_groups_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def send_notification(self):
        if self.cloud_api:
            from ui.send_notification_window import SendNotificationWindow
            self.send_notification_window = SendNotificationWindow(self.cloud_api)
            self.send_notification_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def show_nomenclature(self):
        if self.cloud_api:
            from ui.nomenclature_window import NomenclatureWindow
            self.nomenclature_window = NomenclatureWindow(self.cloud_api)
            self.nomenclature_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def show_reports(self):
        if self.server_api:
            self.reports_window = ReportsWindow(self.server_api)
            self.reports_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Server API для просмотра отчётов.')

    def add_items_to_order(self):
        if self.cloud_api:
            self.add_items_window = AddItemsWindow(self.cloud_api)
            self.add_items_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def close_order(self):
        if self.cloud_api:
            self.close_order_window = CloseOrderWindow(self.cloud_api)
            self.close_order_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def cancel_order(self):
        if self.cloud_api:
            self.cancel_order_window = CancelOrderWindow(self.cloud_api)
            self.cancel_order_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_complete_before(self):
        if self.cloud_api:
            self.change_order_complete_before_window = ChangeOrderCompleteBeforeWindow(self.cloud_api)
            self.change_order_complete_before_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_delivery_point(self):
        if self.cloud_api:
            self.change_order_delivery_point_window = ChangeOrderDeliveryPointWindow(self.cloud_api)
            self.change_order_delivery_point_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_service_type(self):
        if self.cloud_api:
            self.change_order_service_type_window = ChangeOrderServiceTypeWindow(self.cloud_api)
            self.change_order_service_type_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_payments(self):
        if self.cloud_api:
            self.change_order_payments_window = ChangeOrderPaymentsWindow(self.cloud_api)
            self.change_order_payments_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_comment(self):
        if self.cloud_api:
            self.change_order_comment_window = ChangeOrderCommentWindow(self.cloud_api)
            self.change_order_comment_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def print_delivery_bill(self):
        if self.cloud_api:
            self.print_delivery_bill_window = PrintDeliveryBillWindow(self.cloud_api)
            self.print_delivery_bill_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def confirm_delivery(self):
        if self.cloud_api:
            self.confirm_delivery_window = ConfirmDeliveryWindow(self.cloud_api)
            self.confirm_delivery_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def cancel_delivery_confirmation(self):
        if self.cloud_api:
            self.cancel_delivery_confirmation_window = CancelDeliveryConfirmationWindow(self.cloud_api)
            self.cancel_delivery_confirmation_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_order_operator(self):
        if self.cloud_api:
            self.change_order_operator_window = ChangeOrderOperatorWindow(self.cloud_api)
            self.change_order_operator_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def add_order_payments(self):
        if self.cloud_api:
            self.add_order_payments_window = AddOrderPaymentsWindow(self.cloud_api)
            self.add_order_payments_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def change_driver_info(self):
        if self.cloud_api:
            self.change_driver_info_window = ChangeDriverInfoWindow(self.cloud_api)
            self.change_driver_info_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def get_terminal_groups_availability(self):
        if self.cloud_api:
            self.get_terminal_groups_availability_window = GetTerminalGroupsAvailabilityWindow(self.cloud_api)
            self.get_terminal_groups_availability_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def update_order_external_data(self):
        if self.cloud_api:
            self.update_order_external_data_window = UpdateOrderExternalDataWindow(self.cloud_api)
            self.update_order_external_data_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def create_delivery(self):
        if self.cloud_api:
            self.create_delivery_window = CreateDeliveryWindow(self.cloud_api)
            self.create_delivery_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def update_order_problem(self):
        if self.cloud_api:
            self.update_order_problem_window = UpdateOrderProblemWindow(self.cloud_api)
            self.update_order_problem_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def update_delivery_status(self):
        if self.cloud_api:
            self.update_delivery_status_window = UpdateDeliveryStatusWindow(self.cloud_api)
            self.update_delivery_status_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def show_payment_types(self):
        if self.cloud_api:
            self.payment_types_window = PaymentTypesWindow(self.cloud_api)
            self.payment_types_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def open_olap_report_window(self):
        if self.server_api:
            self.olap_report_window = OlapReportWindow(self.server_api)
            self.olap_report_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Server API.')

    def open_balance_report_window(self):
        if self.server_api:
            self.balance_report_window = BalanceReportWindow(self.server_api)
            self.balance_report_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Server API.')

    def open_loyalty_management_window(self):
        if self.cloud_api:
            self.loyalty_management_window = LoyaltyManagementWindow(self.cloud_api)
            self.loyalty_management_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def open_delivery_history_window(self):
        if self.cloud_api:
            self.delivery_history_window = DeliveryHistoryWindow(self.cloud_api)
            self.delivery_history_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, авторизуйтесь по Cloud API.')

    def logout(self):
        self.cloud_api = None
        self.server_api = None
        QMessageBox.information(self, 'Выход', 'Вы вышли из системы.')
