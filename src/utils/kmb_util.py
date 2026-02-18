# pylint: disable=W0603,E0402,W1203
import os 
import logging 
import json 
from scipy.spatial import KDTree
import numpy as np

from geopy.geocoders import Nominatim

from .env_load_util import EnvLoadUtil
from .httpx_util import get_global_httpx_util



from models.kmb.stop_eta.kmb_stop_eta import KMBStopETAResponse
from models.kmb.stop.stop_response import StopListResponse

logger = logging.getLogger(__name__)

class KMBRouterUtil:

    def __init__(self):
        self._stop_cache = {
            "tree": None,
            "stops": None,
        }

    def _reset_cache(self):
        self._stop_cache["tree"] = None
        self._stop_cache["stops"] = None

    def set_stop_cache(self, stop_list: StopListResponse):
        self._stop_cache["stops"] = stop_list
        coordinates = np.array([[float(stop.lat), float(stop.long)] for stop in stop_list.data])
        self._stop_cache["tree"] = KDTree(coordinates)

    def get_cached_stop_dict(self) -> dict:
        return self._stop_cache

    @staticmethod
    async def fetch_all_kmb_router() -> dict:
        url = EnvLoadUtil.load_env("ALL_KMB_ROUTER_URL")
        httpx_util = get_global_httpx_util()
        response = await httpx_util.get_all(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch KMB router data. Status code: {response.status_code}")
            return ""

    @staticmethod
    async def fetch_kmb_router_by_route_id(route_id: str) -> dict:
        url = EnvLoadUtil.load_env("ALL_KMB_ROUTER_URL")
        httpx_util = get_global_httpx_util()
        response = await httpx_util.get_all(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch KMB router data for route_id {route_id}. Status code: {response.status_code}")
            return ""
        
    @staticmethod
    async def fetch_kmb_eta_stop_by_stop_id(stop_id: str) -> KMBStopETAResponse:
        url = EnvLoadUtil.load_env("KMB_ROUTER_ETA_URL")
        formatted_url = url.format(stop_id=stop_id)
        logger.info(f"Fetching KMB ETA data for stop_id: {stop_id} using URL: {formatted_url}")
        httpx_util = get_global_httpx_util()
        eta_response: KMBStopETAResponse = None
        response = await httpx_util.get_all(formatted_url)
        eta_response = KMBStopETAResponse(**response.json()) if response.status_code == 200 else None
        return eta_response
        
    @staticmethod
    async def fetch_kmb_stop() -> StopListResponse:
        url = EnvLoadUtil.load_env("KMB_STOP_URL")
        httpx_util = get_global_httpx_util()
        response = await httpx_util.get_all(url)
        stop_list: StopListResponse = None
        if response.status_code == 200:
            stop_list = StopListResponse(**response.json())
            logger.info(f"Successfully fetched KMB stop data. Total stops: {len(stop_list.data)}")
        else:
            logger.error(f"Failed to fetch KMB stop data. Status code: {response.status_code} loading from file.")
            stop_list = await KMBRouterUtil.load_stop_data_from_file()
        if stop_list is None:
            return StopListResponse(type="", version="", generated_timestamp="", data=[])
        
        util_instance = get_global_kmb_util()
        util_instance.set_stop_cache(stop_list)


        return stop_list
        
    @staticmethod
    async def load_stop_data_from_file() -> StopListResponse:
        stop_list: StopListResponse = None
        try:
            with open(os.path.join(EnvLoadUtil.load_env("BASE_FOLDER"), "res", EnvLoadUtil.load_env("KMB_STOP_DATA")), "r", encoding="utf-8") as f:
                stop_list = StopListResponse(**json.load(f))
                logger.info(f"Successfully loaded KMB stop data from file. Total stops: {len(stop_list.data)}")
        except Exception as e:
            logger.error(f"Failed to load KMB stop data from file. Error: {str(e)}")
        return stop_list
    
    @staticmethod
    async def load_near_stop_with_lat_lon(lat: str, lon: str) -> list:
        util_instance = get_global_kmb_util()
        if not util_instance._stop_cache["stops"]:
            logger.info("No stop data in cache, fetching from API...")
            if await util_instance.fetch_kmb_stop() is None:
                logger.error("Failed to fetch stop data, cannot find nearby stops.")
                return []
            
        cached_stop_list: StopListResponse = util_instance.get_cached_stop_dict().get("stops")
        
        query_point = [float(lat), float(lon)]
        tree: KDTree = util_instance.get_cached_stop_dict().get("tree")
        distance = float(EnvLoadUtil.load_env("KMB_NEAR_STOP_DISTANCE", 0.003))
        indices = tree.query_ball_point(query_point, distance, p=np.inf)
        
        nearby_stops = [cached_stop_list.data[i] for i in indices]
        
        logger.info(f"Found {len(nearby_stops)} stops near lat: {lat}, lon: {lon}")
        return nearby_stops
    
    @staticmethod
    async def load_near_stop_with_address(address: str) -> list:
        geolocator = Nominatim(user_agent="kmb_router_util")
        location = geolocator.geocode(address)
        logger.info(f"Geocoding address: {address}")
        logger.info(f"Geocoding result: {location}")
        logger.info(f"Geocoding result latitude: {location.latitude if location else 'N/A'}, longitude: {location.longitude if location else 'N/A'}")
        if location is None:
            logger.error(f"Failed to geocode address: {address}. No location found.")
            return []
        
        return await KMBRouterUtil.load_near_stop_with_lat_lon(str(location.latitude), str(location.longitude))

    @staticmethod
    async def get_lat_lon_from_address(address: str) -> dict:
        geolocator = Nominatim(user_agent="kmb_router_util")
        location = geolocator.geocode(address)
        logger.info(f"Geocoding address: {address}")
        logger.info(f"Geocoding result: {location}")
        logger.info(f"Geocoding result latitude: {location.latitude if location else 'N/A'}, longitude: {location.longitude if location else 'N/A'}")
        return {"latitude": location.latitude, "longitude": location.longitude} if location else {"error": "Address not found"}

_GOLBAL_KMB_UTIL_INSTANCE = None
def get_global_kmb_util() -> KMBRouterUtil:
    global _GOLBAL_KMB_UTIL_INSTANCE
    if _GOLBAL_KMB_UTIL_INSTANCE is None:
        _GOLBAL_KMB_UTIL_INSTANCE = KMBRouterUtil()
    return _GOLBAL_KMB_UTIL_INSTANCE
