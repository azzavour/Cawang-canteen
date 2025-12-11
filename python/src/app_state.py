import requests
import os
import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

employee_data = []
tenant_data = {}
device_to_tenant_map = {}
_last_loaded_at: Optional[datetime.datetime] = None


def load_all_data():
    """Loads all necessary data from the API into memory."""
    global employee_data, tenant_data, device_to_tenant_map, _last_loaded_at

    try:
        # Load employees from API
        employees_response = requests.get(f"{API_BASE_URL}/employee")
        employees_response.raise_for_status()
        employee_data = employees_response.json()

        # Load tenants from API
        tenants_response = requests.get(f"{API_BASE_URL}/tenant")
        tenants_response.raise_for_status()
        tenants_list = tenants_response.json()
        tenant_data = {tenant["id"]: tenant for tenant in tenants_list}

        # Load assigned devices with tenant info from API
        assigned_devices_response = requests.get(f"{API_BASE_URL}/device/assigned")
        assigned_devices_response.raise_for_status()
        assigned_devices = assigned_devices_response.json()

        new_map = {}
        for device in assigned_devices:
            device_code = device.get("device_code")
            tenant_info = device.get("tenant")
            if device_code and tenant_info:
                new_map[device_code] = tenant_info
        device_to_tenant_map = new_map
        _last_loaded_at = datetime.datetime.now()

        print("Data loaded from API successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error loading data from API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during data loading: {e}")


def ensure_data_fresh(max_age_seconds: int = 300):
    """
    Ensures tenant/device data is up-to-date by reloading from the API when:
    - It has never been loaded,
    - The date has changed,
    - The cached data is older than `max_age_seconds`.
    """
    global _last_loaded_at

    now = datetime.datetime.now()
    should_reload = False

    if _last_loaded_at is None:
        should_reload = True
    elif now.date() != _last_loaded_at.date():
        should_reload = True
    elif (now - _last_loaded_at).total_seconds() >= max_age_seconds:
        should_reload = True

    if should_reload:
        load_all_data()
