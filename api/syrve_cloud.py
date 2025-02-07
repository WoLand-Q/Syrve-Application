# api/syrve_cloud.py

import requests
import json
import logging
import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,  # Уровень логирования
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("syrve_cloud.log"),
                        logging.StreamHandler()
                    ])

class SyrveCloudAPI:
    BASE_URL = 'https://api-eu.syrve.live'  # Основной базовый URL API
    LOYALTY_CLOUD_URL = 'https://loyalty.syrve.live'

    def __init__(self, api_login=None, user_id=None, user_secret=None, organization_id=None, api_key=None):
        """
        Инициализация API клиента.
        """
        self.api_login = api_login
        self.user_id = user_id
        self.user_secret = user_secret
        self.organization_id = organization_id
        self.api_key = api_key
        self.access_token = None

        if self.api_login:
            self.access_token = self.get_access_token()
        elif self.user_id and self.user_secret:
            self.access_token = self.get_access_token_custom(self.user_id, self.user_secret)

    # ------------------- Методы для получения токенов доступа -------------------

    def get_access_token(self):
        """
        Получение токена доступа по API логину.
        """
        url = f"{self.BASE_URL}/api/1/access_token"
        payload = {'apiLogin': self.api_login}
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        logging.debug(f"Запрос токена доступа: {url} с телом запроса: {payload}")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            token = data.get('token')
            if not token:
                logging.error("Access token не найден в ответе.")
                raise Exception("Не удалось получить access token.")
            logging.debug(f"Получен Access Token: {token}")
            return token
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении токена доступа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении токена доступа: {err}")
            raise

    def get_access_token_custom(self, user_id, user_secret):
        """
        Получение токена доступа по пользовательскому ID и секрету.
        """
        url = f"{self.LOYALTY_CLOUD_URL}/api/0/auth/access_token"
        params = {
            "user_id": user_id,
            "user_secret": user_secret
        }
        logging.debug(f"Запрос пользовательского токена доступа: {url} с параметрами: {params}")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            access_token = response.text.strip('"')
            logging.debug(f"Получен пользовательский Access Token: {access_token}")
            return access_token
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении пользовательского токена: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении пользовательского токена: {err}")
            raise

    # ------------------- Методы для работы с OLAP отчетами -------------------

    def get_olap_columns(self, report_type='SALES'):
        """
        Получение доступных колонок для OLAP отчета.
        """
        url = f"{self.BASE_URL}/reports/olap/columns"
        params = {
            'key': self.api_key,
            'reportType': report_type
        }
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        logging.debug(f"Запрос OLAP колонок: {url} с параметрами: {params}")
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            logging.debug(f"Ответ OLAP колонок: {response.json()}")
            return response.json()
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении OLAP колонок: {http_err} - Ответ: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка при получении OLAP колонок: {err}")
        return None

    def get_olap_report(self, report_type='SALES', build_summary=True,
                        group_by_row_fields=None, group_by_col_fields=None,
                        aggregate_fields=None, filters=None):
        """
        Получение OLAP отчета.
        """
        url = f"{self.BASE_URL}/reports/olap"
        params = {
            'key': self.api_key
        }
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        if group_by_row_fields is None:
            group_by_row_fields = []
        if group_by_col_fields is None:
            group_by_col_fields = []
        if aggregate_fields is None:
            aggregate_fields = []
        if filters is None:
            filters = {}

        request_body = {
            "reportType": report_type,
            "buildSummary": str(build_summary).lower(),  # "true" или "false"
            "groupByRowFields": group_by_row_fields,
            "groupByColFields": group_by_col_fields,
            "aggregateFields": aggregate_fields,
            "filters": filters
        }

        logging.debug(f"Запрос OLAP отчета: {url} с телом запроса: {json.dumps(request_body, ensure_ascii=False, indent=4)}")
        try:
            response = requests.post(url, params=params, headers=headers, data=json.dumps(request_body, ensure_ascii=False))
            response.raise_for_status()
            logging.debug(f"Ответ OLAP отчета: {response.json()}")
            return response.json()
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении OLAP отчета: {http_err} - Ответ: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка при получении OLAP отчета: {err}")
        return None

    # ------------------- Методы для получения отчетов по остаткам -------------------

    def get_balance_report(self, store_ids, timestamp):
        """
        Получение отчета по остаткам товаров для указанных магазинов.
        """
        url = f"{self.LOYALTY_CLOUD_URL}/resto/api/v2/reports/balance/stores"
        params = {
            'key': self.api_key,
            'timestamp': timestamp,
            'store': store_ids  # Список ID магазинов
        }
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        logging.debug(f"Запрос отчета по остаткам: {url} с параметрами: {params}")
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            logging.debug(f"Ответ отчета по остаткам: {response.json()}")
            return response.json()
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении отчета по остаткам: {http_err} - Ответ: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка при получении отчета по остаткам: {err}")
        return None





    def update_order_external_data(self, organization_id, order_id, external_data):
        """
        Обновление внешних данных заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_order_external_data"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'externalData': external_data
        }
        logging.debug(f"Запрос обновления внешних данных заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления внешних данных заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении внешних данных заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении внешних данных заказа: {err}")
            raise

    # ------------------- Методы для управления доставками -------------------

    def create_delivery(self, organization_id, order_id, delivery_details):
        """
        Создание новой доставки.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/create_delivery"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'deliveryDetails': delivery_details
        }
        logging.debug(f"Запрос создания доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ создания доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при создании доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при создании доставки: {err}")
            raise

    def add_items_to_order(self, organization_id, order_id, items, combos=None):
        """
        Добавление позиций в заказ.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/add_items"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'items': items
        }
        if combos:
            payload['combos'] = combos
        logging.debug(f"Запрос добавления позиций в заказ: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ добавления позиций в заказ: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при добавлении позиций в заказ: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при добавлении позиций в заказ: {err}")
            raise

    def close_order(self, organization_id, order_id, delivery_date=None):
        """
        Закрытие заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/close_order"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        if delivery_date:
            payload['deliveryDate'] = delivery_date
        logging.debug(f"Запрос закрытия заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ закрытия заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при закрытии заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при закрытии заказа: {err}")
            raise

    def cancel_order(self, organization_id, order_id, cancel_cause_id=None, removal_type_id=None, user_id_for_writeoff=None):
        """
        Отмена заказа с возможностью указания причины и других параметров.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/cancel_order"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        if cancel_cause_id:
            payload['cancelCauseId'] = cancel_cause_id
        if removal_type_id:
            payload['removalTypeId'] = removal_type_id
        if user_id_for_writeoff:
            payload['userIdForWriteoff'] = user_id_for_writeoff
        logging.debug(f"Запрос отмены заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ отмены заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при отмене заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при отмене заказа: {err}")
            raise

    def change_order_complete_before(self, organization_id, order_id, new_complete_before):
        """
        Изменение времени, когда клиент желает получить заказ.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_complete_before"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'newCompleteBefore': new_complete_before
        }
        logging.debug(f"Запрос изменения времени доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения времени доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении времени доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении времени доставки: {err}")
            raise

    def change_order_delivery_point(self, organization_id, order_id, new_delivery_point):
        """
        Изменение адреса доставки заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_delivery_point"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'newDeliveryPoint': new_delivery_point
        }
        logging.debug(f"Запрос изменения адреса доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения адреса доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении адреса доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении адреса доставки: {err}")
            raise

    def change_order_service_type(self, organization_id, order_id, new_service_type, delivery_point):
        """
        Изменение типа доставки заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_service_type"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'newServiceType': new_service_type,
            'deliveryPoint': delivery_point
        }
        logging.debug(f"Запрос изменения типа доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения типа доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении типа доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении типа доставки: {err}")
            raise

    def change_order_payments(self, organization_id, order_id, payments, tips=None):
        """
        Изменение платежей по заказу.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_payments"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'payments': payments
        }
        if tips:
            payload['tips'] = tips
        logging.debug(f"Запрос изменения платежей: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения платежей: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении платежей: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении платежей: {err}")
            raise

    def change_order_comment(self, organization_id, order_id, comment):
        """
        Изменение комментария к заказу.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_comment"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'comment': comment
        }
        logging.debug(f"Запрос изменения комментария: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения комментария: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении комментария: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении комментария: {err}")
            raise

    def print_delivery_bill(self, organization_id, order_id):
        """
        Распечатка счета доставки.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/print_delivery_bill"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        logging.debug(f"Запрос печати счета доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ печати счета доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при печати счета доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при печати счета доставки: {err}")
            raise

    def confirm_delivery(self, organization_id, order_id):
        """
        Подтверждение доставки.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/confirm"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        logging.debug(f"Запрос подтверждения доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ подтверждения доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при подтверждении доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при подтверждении доставки: {err}")
            raise

    def cancel_delivery_confirmation(self, organization_id, order_id):
        """
        Отмена подтверждения доставки.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/cancel_confirmation"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        logging.debug(f"Запрос отмены подтверждения доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ отмены подтверждения доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при отмене подтверждения доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при отмене подтверждения доставки: {err}")
            raise

    def change_order_operator(self, organization_id, order_id, operator_id):
        """
        Изменение оператора заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_operator"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'operatorId': operator_id
        }
        logging.debug(f"Запрос изменения оператора заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения оператора заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении оператора заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении оператора заказа: {err}")
            raise

    def add_order_payments(self, organization_id, order_id, payments, tips=None):
        """
        Добавление оплаты к заказу.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/add_payments"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'payments': payments
        }
        if tips:
            payload['tips'] = tips
        logging.debug(f"Запрос добавления оплаты к заказу: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ добавления оплаты к заказу: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при добавлении оплаты к заказу: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при добавлении оплаты к заказу: {err}")
            raise

    def change_driver_info(self, organization_id, order_id, driver_id=None, estimated_time=None):
        """
        Изменение информации о водителе.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/change_driver_info"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id
        }
        if driver_id:
            payload['driverId'] = driver_id
        if estimated_time:
            payload['estimatedTime'] = estimated_time
        logging.debug(f"Запрос изменения информации о водителе: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ изменения информации о водителе: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при изменении информации о водителе: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при изменении информации о водителе: {err}")
            raise

    def get_terminal_groups(self, organization_ids, include_disabled=False, return_external_data=None):
        """
        Получение групп терминалов для указанных организаций.

        :param organization_ids: Список UUID организаций.
        :param include_disabled: Включать ли отключённые терминальные группы.
        :param return_external_data: Список ключей внешних данных для возврата.
        :return: Словарь с группами терминалов.
        """
        url = f"{self.BASE_URL}/api/1/terminal_groups"
        headers = self.get_headers()
        payload = {
            "organizationIds": organization_ids,
            "includeDisabled": include_disabled
        }
        if return_external_data:
            payload["returnExternalData"] = return_external_data

        logging.debug(f"Запрос групп терминалов: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            terminal_groups = data.get("terminalGroups", [])
            logging.debug(f"Получено групп терминалов: {len(terminal_groups)}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении групп терминалов: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении групп терминалов: {err}")
            raise



    # ------------------- Методы для работы с терминальными группами -------------------

    def get_terminal_groups_availability(self, organization_ids, terminal_group_ids):
        """
        Проверка доступности групп терминалов.
        """
        url = f"{self.BASE_URL}/api/1/terminal_groups/is_alive"
        headers = self.get_headers()
        payload = {
            'organizationIds': organization_ids,
            'terminalGroupIds': terminal_group_ids
        }
        logging.debug(f"Запрос доступности терминальных групп: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ доступности терминальных групп: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при проверке доступности терминальных групп: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при проверке доступности терминальных групп: {err}")
            raise




    # ------------------- Методы для работы с номенклатурой -------------------

    def get_nomenclature(self, organization_id):
        """
        Получение номенклатуры для указанной организации.
        """
        url = f"{self.BASE_URL}/api/1/nomenclature/list"
        headers = self.get_headers()
        params = {
            'organizationId': organization_id
        }
        logging.debug(f"Запрос номенклатуры: {url} с параметрами: {params}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ номенклатуры: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении номенклатуры: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении номенклатуры: {err}")
            raise

    # ------------------- Методы для управления заказами и доставками -------------------

    def get_organizations(self):
        """
        Получение списка организаций.
        """
        url = f"{self.BASE_URL}/api/1/organizations"
        headers = self.get_headers()
        logging.debug(f"Запрос списка организаций: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            organizations = data.get('organizations', [])
            logging.debug(f"Получено организаций: {len(organizations)}")
            return organizations
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении списка организаций: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении списка организаций: {err}")
            raise

    def find_organization_by_id(self, organizations, organization_id):
        """
        Поиск организации по ID.
        """
        for org in organizations:
            if org.get("id") == organization_id:
                logging.debug(f"Найдена организация: {org}")
                return org
        logging.warning(f"Организация с ID {organization_id} не найдена.")
        return None

    # ------------------- Вспомогательные методы -------------------

    def get_headers(self):
        """
        Получение заголовков для запросов.
        """
        if self.access_token:
            return {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Accept": "*/*"
            }
        else:
            return {
                "Content-Type": "application/json",
                "Accept": "*/*"
            }

    # ------------------- Методы для работы с проблемами заказа -------------------

    def update_order_problem(self, organization_id, order_id, problem_description, problem_type):
        """
        Обновление проблемы заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_order_problem"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'problemDescription': problem_description,
            'problemType': problem_type
        }
        logging.debug(f"Запрос обновления проблемы заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления проблемы заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении проблемы заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении проблемы заказа: {err}")
            raise

    # ------------------- Методы для работы с внешними данными заказа -------------------

    def update_order_external_data(self, organization_id, order_id, external_data):
        """
        Обновление внешних данных заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_order_external_data"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'externalData': external_data
        }
        logging.debug(f"Запрос обновления внешних данных заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления внешних данных заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении внешних данных заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении внешних данных заказа: {err}")
            raise

    # ------------------- Методы для управления проблемами доставки -------------------

    def update_delivery_status(self, organization_id, order_id, new_status):
        """
        Обновление статуса доставки.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_status"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'newStatus': new_status
        }
        logging.debug(f"Запрос обновления статуса доставки: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления статуса доставки: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении статуса доставки: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении статуса доставки: {err}")
            raise

    # ------------------- Методы для работы с внешними меню -------------------

    def get_external_menus(self):
        """
        Получение внешних меню.
        """
        url = f"{self.BASE_URL}/api/1/external_menus"
        headers = self.get_headers()
        logging.debug(f"Запрос внешних меню: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ внешних меню: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении внешних меню: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении внешних меню: {err}")
            raise

    # ------------------- Методы для работы с типами платежей -------------------

    def get_payment_types(self, organization_ids):
        """
        Получение типов платежей для указанных организаций.
        """
        url = f"{self.BASE_URL}/api/1/payment_types"
        headers = self.get_headers()
        payload = {
            'organizationIds': organization_ids
        }
        logging.debug(f"Запрос типов платежей: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        logging.debug(f"Headers: {headers}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ типов платежей: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении типов платежей: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении типов платежей: {err}")
            raise

    # ------------------- Методы для работы с номенклатурой -------------------

    def get_nomenclature(self, organization_id, start_revision=0):
        """
        Получение номенклатуры для указанной организации.
        """
        url = f"{self.BASE_URL}/api/1/nomenclature"
        headers = self.get_headers()
        payload = {
            "organizationId": organization_id,
            "startRevision": start_revision
        }
        logging.debug(
            f"Запрос номенклатуры: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False, indent=4)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ номенклатуры: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении номенклатуры: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении номенклатуры: {err}")
            raise

    # ------------------- Методы для работы с внешними данными заказа -------------------

    def update_order_external_data(self, organization_id, order_id, external_data):
        """
        Обновление внешних данных заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_order_external_data"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'externalData': external_data
        }
        logging.debug(f"Запрос обновления внешних данных заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления внешних данных заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении внешних данных заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении внешних данных заказа: {err}")
            raise

    # ------------------- Методы для управления проблемами заказа -------------------

    def update_order_problem(self, organization_id, order_id, problem_description, problem_type):
        """
        Обновление проблемы заказа.
        """
        url = f"{self.BASE_URL}/api/1/deliveries/update_order_problem"
        headers = self.get_headers()
        payload = {
            'organizationId': organization_id,
            'orderId': order_id,
            'problemDescription': problem_description,
            'problemType': problem_type
        }
        logging.debug(f"Запрос обновления проблемы заказа: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Ответ обновления проблемы заказа: {data}")
            return data
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при обновлении проблемы заказа: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при обновлении проблемы заказа: {err}")
            raise



    # ------------------- Методы для работы с историей доставок -------------------

    def get_delivery_history(self, customer_id, revision=0, last_transaction_id=None, page_size=100):
        """
        Получение истории транзакций клиента по ревизии.
        """
        url = f"{self.BASE_URL}/api/1/loyalty/iiko/customer/transactions/by_revision"
        headers = self.get_headers()
        payload = {
            "customerId": customer_id,
            "revision": revision,
            "pageSize": page_size,
            "organizationId": self.organization_id
        }

        if last_transaction_id:
            payload["lastTransactionId"] = last_transaction_id

        logging.debug(f"Запрос истории транзакций: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            transactions = data.get("transactions", [])
            logging.debug(f"Получено транзакций: {len(transactions)}")
            return transactions
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении истории транзакций: {http_err} - Ответ: {response.text}")
            raise
        except Exception as err:
            logging.error(f"Ошибка при получении истории транзакций: {err}")
            raise

    # ------------------- Методы для работы с лояльностью клиентов -------------------

    def get_customer_info(self, phone):
        """
        Получение информации о клиенте по телефону.
        """

        if not self.organization_id:
            logging.error("Organization ID is not set.")
            raise ValueError("Organization ID is not set.")
        url = f"{self.BASE_URL}/api/1/loyalty/iiko/customer/info"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        payload = {
            "phone": phone,
            "type": "phone",
            "organizationId": self.organization_id
        }
        logging.debug(f"Запрос информации о клиенте: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            customer_info = response.json()
            logging.debug(f"Ответ информации о клиенте: {customer_info}")
            return customer_info
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении информации о клиенте: {http_err} - Ответ: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка при получении информации о клиенте: {err}")
        return None

    def get_transactions_by_revision(self, customer_id, revision=0, last_transaction_id=None, page_number=1, page_size=100):
        """
        Получение транзакций клиента по ревизии.
        """
        url = f"{self.BASE_URL}/api/1/loyalty/iiko/customer/transactions/by_revision"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        payload = {
            "customerId": customer_id,
            "pageNumber": page_number,
            "pageSize": page_size,
            "organizationId": self.organization_id
        }

        if last_transaction_id:
            payload["revision"] = revision
            payload["lastTransactionId"] = last_transaction_id

        if page_size < 1:
            logging.error("Некорректное значение pageSize. Оно должно быть не меньше 1.")
            return []

        logging.debug(f"Запрос транзакций по ревизии: {url} с телом запроса: {json.dumps(payload, ensure_ascii=False)}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            transactions = data.get("transactions", [])
            valid_transactions = [
                t for t in transactions
                if not t.get("isIgnored", False) and t.get("isDelivery", False)
            ]
            last_revision = data.get("lastRevision", revision)
            last_transaction_id = data.get("lastTransactionId", last_transaction_id)
            logging.debug(f"Получено транзакций: {len(valid_transactions)} с ревизией: {last_revision} и lastTransactionId: {last_transaction_id}")
            return valid_transactions
        except requests.HTTPError as http_err:
            logging.error(f"HTTP ошибка при получении транзакций по ревизии: {http_err} - Ответ: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка при получении транзакций по ревизии: {err}")
        return []

    def is_new_customer(self, transactions, brand_id):
        """
        Проверка, является ли клиент новым по заданному бренду.
        """
        for transaction in transactions:
            if transaction.get('brandId') == brand_id:
                logging.info(f"Клиент не является новым по бренду {brand_id}.")
                return False
        logging.info(f"Клиент является новым по бренду {brand_id}.")
        return True

    # ------------------- Методы для генерации и сохранения купонов -------------------

    def create_new_coupon(self, prefix, brand, existing_coupons):
        """
        Генерация нового уникального промокода.
        """
        import random
        while True:
            code = str(random.randint(10000, 99999))
            coupon = f"{prefix}{code}{brand}"
            if coupon not in existing_coupons:
                logging.debug(f"Сгенерирован новый промокод: {coupon}")
                return coupon

    def load_existing_coupons(self, file_path):
        """
        Загрузка существующих купонов из файла.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                coupons = [line.strip() for line in f.readlines()]
                logging.debug(f"Загружено {len(coupons)} существующих купонов.")
                return coupons
        except FileNotFoundError:
            logging.warning(f"Файл {file_path} не найден. Возвращается пустой список купонов.")
            return []
        except Exception as e:
            logging.error(f"Ошибка при загрузке существующих купонов: {e}")
            return []

    def save_new_coupon(self, file_path, coupon):
        """
        Сохранение нового промокода в файл.
        """
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{coupon}\n")
            logging.debug(f"Промокод {coupon} успешно сохранён в {file_path}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении нового купона: {e}")
            return False


