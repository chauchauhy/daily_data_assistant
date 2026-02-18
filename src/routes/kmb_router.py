# pylint: disable=W0613,W1203,E1136,W0718
import logging

from fastapi import APIRouter
from utils import kmb_util
from utils.env_load_util import EnvLoadUtil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kmb_router", tags=["kmb_router"])

@router.get("/")
async def get_kmb_router():
    return {"message": "This is the KMB Router endpoint"}

@router.get("/route/{route_id}")
async def get_kmb_router_by_route_id(route_id: str):
    logger.info(f"Fetching KMB router data for route_id: {route_id}...")
    try:
        data = await kmb_util.KMBRouterUtil.fetch_kmb_router_by_route_id(route_id)
        return data
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/near_stop/ll/{lat}/{lon}")
async def get_near_stop(lat: str, lon: str):
    logger.info(f"Fetching KMB stop data near lat: {lat}, lon: {lon}...")
    try:
        data = await kmb_util.KMBRouterUtil.fetch_kmb_stop()
        logger.info(f"Fetched {len(data.data)} stops from API.")
        nearby_stops = await kmb_util.KMBRouterUtil.load_near_stop_with_lat_lon(lat, lon)
        
        return {"nearby_stops": nearby_stops}
    except Exception as e:
        logger.error(f"Error in get_near_stop: {str(e)}")
        return {"error": str(e)}
    
@router.get("/near_stop/address/{address}")
async def get_ll_from_address(address: str):
    logger.info(f"Fetching latitude and longitude for address: {address}...")
    try:
        data = await kmb_util.KMBRouterUtil.load_near_stop_with_address(address)
        return data
    except Exception as e:
        logger.error(f"Error in get_ll_from_address: {str(e)}")
        return {"error": str(e)}

@router.get("/eta/address/{address}")
async def get_eta_by_address(address: str):
    """
    Complete workflow: Address -> Lat/Lon -> Nearby Stops -> ETAs
    
    1. Geocodes the address to latitude/longitude
    2. Finds nearby bus stops within configured distance
    3. Fetches ETA data for each nearby stop
    4. Returns combined results with location and ETA information
    """
    logger.info(f"Starting ETA lookup workflow for address: {address}")
    
    try:
        # Step 1: Geocode address to lat/lon
        logger.info("Step 1: Geocoding address...")
        lat_lon = await kmb_util.KMBRouterUtil.get_lat_lon_from_address(address)
        
        if "error" in lat_lon:
            logger.error(f"Geocoding failed for address: {address}")
            return {
                "error": "Address not found",
                "address": address,
                "details": "Could not geocode the provided address. Please check the address and try again."
            }
        
        latitude = lat_lon["latitude"]
        longitude = lat_lon["longitude"]
        logger.info(f"Geocoded to: lat={latitude}, lon={longitude}")
        
        # Step 2: Find nearby bus stops
        logger.info("Step 2: Finding nearby bus stops...")
        nearby_stops = await kmb_util.KMBRouterUtil.load_near_stop_with_lat_lon(
            str(latitude), str(longitude)
        )
        
        if not nearby_stops:
            logger.warning(f"No nearby stops found for lat={latitude}, lon={longitude}")
            return {
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "nearby_stops_count": 0,
                "stops_with_eta": [],
                "message": "No bus stops found nearby. Try a different address or increase search radius."
            }
        
        logger.info(f"Found {len(nearby_stops)} nearby stops")
        
        # Step 3: Fetch ETA data for each nearby stop
        logger.info("Step 3: Fetching ETA data for each stop...")
        stops_with_eta = []
        
        for stop in nearby_stops:
            try:
                eta_response = await kmb_util.KMBRouterUtil.fetch_kmb_eta_stop_by_stop_id(stop.stop)
                
                stop_info = {
                    "stop_id": stop.stop,
                    "stop_name_en": stop.name_en,
                    "stop_name_tc": stop.name_tc,
                    "stop_name_sc": stop.name_sc,
                    "latitude": stop.lat,
                    "longitude": stop.long,
                    "eta_data": []
                }
                
                if eta_response and eta_response.data:
                    # Process ETA data
                    for eta in eta_response.data:
                        stop_info["eta_data"].append({
                            "route": eta.route,
                            "destination_en": eta.dest_en,
                            "destination_tc": eta.dest_tc,
                            "destination_sc": eta.dest_sc,
                            "eta": eta.eta,
                            "eta_seq": eta.eta_seq,
                            "direction": eta.dir,
                            "service_type": eta.service_type,
                            "remarks_en": eta.rmk_en,
                            "remarks_tc": eta.rmk_tc,
                            "remarks_sc": eta.rmk_sc
                        })
                    logger.info(f"Stop {stop.stop}: Found {len(eta_response.data)} ETA entries")
                else:
                    logger.info(f"Stop {stop.stop}: No ETA data available")
                
                stops_with_eta.append(stop_info)
                
            except Exception as eta_error:
                logger.error(f"Failed to fetch ETA for stop {stop.stop}: {str(eta_error)}")
                # Include stop info even if ETA fetch fails
                stops_with_eta.append({
                    "stop_id": stop.stop,
                    "stop_name_en": stop.name_en,
                    "stop_name_tc": stop.name_tc,
                    "stop_name_sc": stop.name_sc,
                    "latitude": stop.lat,
                    "longitude": stop.long,
                    "eta_data": [],
                    "error": f"Failed to fetch ETA: {str(eta_error)}"
                })
        
        # Step 4: Return complete results
        logger.info(f"Workflow complete. Returning data for {len(stops_with_eta)} stops")
        return {
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "nearby_stops_count": len(nearby_stops),
            "stops_with_eta": stops_with_eta,
            "search_radius_degrees": float(EnvLoadUtil.load_env("KMB_NEAR_STOP_DISTANCE", "0.003"))
        }
        
    except Exception as e:
        logger.error(f"Error in get_eta_by_address workflow: {str(e)}")
        return {
            "error": str(e),
            "address": address,
            "details": "An error occurred during the ETA lookup workflow"
        }