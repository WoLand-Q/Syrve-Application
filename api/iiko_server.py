import requests
import hashlib
import logging
import json

class IikoServerAPI:
    def __init__(self, server_url, login, password):
        self.server_url = server_url.rstrip('/')
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.token = None

        self.authorize()

    def authorize(self):
        password_hash = hashlib.sha1(self.password.encode('utf-8')).hexdigest()
        auth_url = f"{self.server_url}/resto/api/auth"
        params = {'login': self.login, 'pass': password_hash}
        logging.debug(f"Авторизация на сервере по URL: {auth_url} с параметрами: {params}")
        try:
            response = self.session.get(auth_url, params=params, verify=False)
            response.raise_for_status()
            self.token = response.text.strip()
            if not self.token:
                self.token = response.cookies.get('key')
            if not self.token:
                raise ValueError("Не удалось получить токен авторизации")
            logging.debug(f"Токен авторизации получен: {self.token}")
        except Exception as e:
            logging.error(f"Ошибка при авторизации на сервере: {e}")
            raise

    def get_headers(self):
        return {
            'Content-Type': 'application/json; charset=utf-8'
        }

    def get_organizations(self):
        url = f"{self.server_url}/resto/api/corporation/departments"
        params = {
            'key': self.token
        }
        headers = self.get_headers()
        logging.debug(f"Запрос списка организаций: {url} с параметрами: {params}")
        try:
            response = self.session.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            logging.debug(f"Content-Type ответа: {content_type}")
            logging.debug(f"Текст ответа: {response.text}")

            if 'application/json' in content_type:
                data = response.json()
                organizations = data if isinstance(data, list) else []
            elif 'application/xml' in content_type or 'text/xml' in content_type:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                organizations = []
                for item in root.findall('.//corporateItemDto'):
                    type_element = item.find('type')
                    if type_element is not None and type_element.text == 'DEPARTMENT':
                        org_id = item.find('id').text if item.find('id') is not None else ''
                        org_name = item.find('name').text if item.find('name') is not None else ''
                        organizations.append({'id': org_id, 'name': org_name})
            else:
                logging.error(f"Неизвестный Content-Type: {content_type}")
                logging.error(f"Ответ сервера: {response.text}")
                raise ValueError("Неизвестный формат ответа от сервера.")
            logging.debug(f"Получено организаций: {len(organizations)}")
            return organizations
        except Exception as e:
            logging.error(f"Ошибка при получении списка организаций: {e}")
            raise

    def get_olap_columns(self, report_type='SALES'):
        url = f"{self.server_url}/resto/api/v2/reports/olap/columns"
        params = {
            'key': self.token,
            'reportType': report_type
        }
        logging.debug(f"Запрос доступных полей OLAP отчета: {url} с параметрами: {params}")
        try:
            response = self.session.get(url, params=params, headers=self.get_headers(), verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Ошибка при получении полей OLAP отчета: {e}")
            raise

    def get_olap_report(self, report_type='SALES', build_summary=True,
                        group_by_row_fields=None, group_by_col_fields=None,
                        aggregate_fields=None, filters=None):
        url = f"{self.server_url}/resto/api/v2/reports/olap"
        params = {'key': self.token}
        headers = self.get_headers()
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
            "buildSummary": str(build_summary).lower(),
            "groupByRowFields": group_by_row_fields,
            "groupByColFields": group_by_col_fields,
            "aggregateFields": aggregate_fields,
            "filters": filters
        }

        logging.debug(f"Запрос OLAP отчета: {url} с телом запроса: {json.dumps(request_body, ensure_ascii=False)}")
        try:
            response = self.session.post(url, params=params, headers=headers, json=request_body, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Ошибка при получении OLAP отчета: {e}")
            raise
