"""
Cliente de comunicação HTTP entre o Frontend Streamlit e a API FastAPI.
"""

import os
import requests
from typing import Dict, Any, List, Optional

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")
        self.api_v1 = f"{self.base_url}/api/v1"

    def check_health(self) -> Dict[str, Any]:
        try:
            res = requests.get(f"{self.base_url}/", timeout=3.0)
            if res.status_code == 200:
                return {"online": True, "data": res.json()}
        except Exception:
            pass
        return {"online": False, "data": {}}

    # AOI
    def get_aois(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.api_v1}/aoi/", timeout=5.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def create_aoi(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(f"{self.api_v1}/aoi/", json=payload, timeout=5.0)
            if res.status_code in [200, 201]:
                return res.json()
        except Exception:
            pass
        return None

    # Análises
    def process_analysis(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(f"{self.api_v1}/analysis/process", json=payload, timeout=30.0)
            if res.status_code in [200, 201]:
                return res.json()
        except Exception as e:
            print(f"Erro ao processar análise: {e}")
        return None

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.api_v1}/analysis/history", timeout=5.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def get_analysis_details(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.api_v1}/analysis/{analysis_id}", timeout=10.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    # Clima
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            res = requests.get(
                f"{self.api_v1}/weather/current",
                params={"latitude": lat, "longitude": lon},
                timeout=5.0
            )
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {}

    # INPE & Validação
    def load_inpe_sample(self) -> Dict[str, Any]:
        try:
            res = requests.post(f"{self.api_v1}/validation/inpe/load-default-sample", timeout=10.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {"status": "erro"}

    def run_cross_validation(self, analysis_id: int, tolerance_m: float = 1000.0) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(
                f"{self.api_v1}/validation/inpe/cross-validate/{analysis_id}",
                params={"raio_tolerancia_metros": tolerance_m},
                timeout=15.0
            )
            if res.status_code in [200, 201]:
                return res.json()
        except Exception:
            pass
        return None

    def get_inpe_focos(self, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.api_v1}/validation/inpe/focos", params={"limite": limit}, timeout=5.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def get_validation_history(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.api_v1}/validation/history", timeout=5.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []


api_client = APIClient()
