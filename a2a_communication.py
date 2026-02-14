import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from a2a_models import (
    AgentMessage, AgentResponse, AgentType, MessageType,
    Priority, AGENT_REGISTRY, UserContext
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2ACommunicationHandler:
    """Handles agent-to-agent communication via HTTP/REST"""
    
    def __init__(self):
        self.agent_endpoints = {
            AgentType.FOOD: "http://localhost:8000",
            AgentType.REGULATORY: "http://localhost:8001", 
            AgentType.TRANSPORT: "http://localhost:8002",
            AgentType.FESTIVAL: "http://localhost:8003",
            AgentType.DECISION: "http://localhost:8004"
        }
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3
        
    async def send_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Send a message to another agent"""
        endpoint = self.agent_endpoints.get(message.receiver_agent)
        if not endpoint:
            logger.error(f"No endpoint configured for agent: {message.receiver_agent}")
            return None
            
        url = f"{endpoint}/a2a/receive"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Sending message to {message.receiver_agent}: {message.message_id}")
                    
                    async with session.post(
                        url, 
                        json=message.model_dump(),
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"Successfully sent message {message.message_id}")
                            return result
                        else:
                            logger.warning(f"Failed to send message, status: {response.status}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on attempt {attempt + 1} for message {message.message_id}")
                except Exception as e:
                    logger.error(f"Error sending message {message.message_id}: {str(e)}")
                    
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        logger.error(f"Failed to send message {message.message_id} after {self.max_retries} attempts")
        return None
    
    async def query_agent(self, agent_type: AgentType, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Direct query to an agent's specific endpoint"""
        base_url = self.agent_endpoints.get(agent_type)
        if not base_url:
            logger.error(f"No endpoint configured for agent: {agent_type}")
            return None
            
        url = f"{base_url}{endpoint}"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                if endpoint.startswith("/recommendations") or endpoint.startswith("/regulatory-analysis"):
                    # POST request
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            return await response.json()
                else:
                    # GET request with query params
                    async with session.get(url, params=payload) as response:
                        if response.status == 200:
                            return await response.json()
                            
                logger.warning(f"Query failed for {agent_type}{endpoint}, status: {response.status}")
                return None
                
            except Exception as e:
                logger.error(f"Error querying {agent_type}{endpoint}: {str(e)}")
                return None
    
    async def broadcast_message(self, message: AgentMessage, target_agents: List[AgentType]) -> Dict[AgentType, Optional[Dict[str, Any]]]:
        """Send message to multiple agents simultaneously"""
        tasks = []
        for agent in target_agents:
            if agent != message.sender_agent:  # Don't send to self
                msg_copy = message.model_copy()
                msg_copy.receiver_agent = agent
                tasks.append(self.send_message(msg_copy))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        response_dict = {}
        for i, agent in enumerate([a for a in target_agents if a != message.sender_agent]):
            if isinstance(results[i], Exception):
                logger.error(f"Error sending to {agent}: {results[i]}")
                response_dict[agent] = None
            else:
                response_dict[agent] = results[i]
                
        return response_dict
    
    async def health_check(self, agent_type: AgentType) -> bool:
        """Check if an agent is healthy and responding"""
        base_url = self.agent_endpoints.get(agent_type)
        if not base_url:
            return False
            
        url = f"{base_url}/health"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            try:
                async with session.get(url) as response:
                    return response.status == 200
            except:
                return False
    
    async def get_agent_status(self) -> Dict[AgentType, bool]:
        """Get health status of all agents"""
        tasks = [self.health_check(agent_type) for agent_type in AgentType]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        status = {}
        for i, agent_type in enumerate(AgentType):
            status[agent_type] = results[i] is True
            
        return status


class AgentOrchestrator:
    """Orchestrates multi-agent interactions for complex requests"""
    
    def __init__(self, comm_handler: A2ACommunicationHandler):
        self.comm_handler = comm_handler
        
    async def coordinate_dining_recommendation(self, user_context: UserContext) -> Dict[str, Any]:
        """Coordinate between food, regulatory, and transport agents for dining recommendation"""
        
        results = {}
        
        # 1. Get food recommendations
        food_payload = {
            "latitude": user_context.location.latitude,
            "longitude": user_context.location.longitude,
            "radius": user_context.preferences.get("radius", 2000),
            "limit": user_context.preferences.get("limit", 10)
        }
        
        food_result = await self.comm_handler.query_agent(
            AgentType.FOOD, 
            "/recommendations", 
            food_payload
        )
        results["food"] = food_result
        
        # 2. Get regulatory analysis for the area
        if user_context.vehicle_type:
            regulatory_payload = {
                "latitude": user_context.location.latitude,
                "longitude": user_context.location.longitude,
                "vehicle_type": user_context.vehicle_type
            }
            
            regulatory_result = await self.comm_handler.query_agent(
                AgentType.REGULATORY,
                "/regulatory-analysis",
                regulatory_payload
            )
            results["regulatory"] = regulatory_result
        
        # 3. Check for events/festivals that might affect the area
        festival_payload = {
            "location": f"{user_context.location.latitude},{user_context.location.longitude}"
        }
        
        # Note: Festival agent might need different integration
        # results["festival"] = await self.comm_handler.query_agent(...) 
        
        return results
    
    async def coordinate_route_planning(self, user_context: UserContext) -> Dict[str, Any]:
        """Coordinate transport, regulatory, and festival agents for route planning"""
        
        if not user_context.destination:
            return {"error": "Destination required for route planning"}
        
        results = {}
        
        # 1. Get transport analysis
        transport_payload = {
            "origin_latitude": user_context.location.latitude,
            "origin_longitude": user_context.location.longitude,
            "destination_latitude": user_context.destination.latitude,
            "destination_longitude": user_context.destination.longitude,
            "vehicle_type": user_context.vehicle_type or "car",
            "current_time": datetime.now().isoformat()
        }
        
        # Note: Transport agent endpoint might need to be implemented
        # transport_result = await self.comm_handler.query_agent(...)
        
        # 2. Get regulatory analysis for both origin and destination
        if user_context.vehicle_type:
            # Origin regulatory analysis
            origin_regulatory = await self.comm_handler.query_agent(
                AgentType.REGULATORY,
                "/regulatory-analysis",
                {
                    "latitude": user_context.location.latitude,
                    "longitude": user_context.location.longitude, 
                    "vehicle_type": user_context.vehicle_type
                }
            )
            results["origin_regulatory"] = origin_regulatory
            
            # Destination regulatory analysis
            dest_regulatory = await self.comm_handler.query_agent(
                AgentType.REGULATORY,
                "/regulatory-analysis",
                {
                    "latitude": user_context.destination.latitude,
                    "longitude": user_context.destination.longitude,
                    "vehicle_type": user_context.vehicle_type
                }
            )
            results["destination_regulatory"] = dest_regulatory
        
        return results
    
    async def coordinate_area_analysis(self, user_context: UserContext) -> Dict[str, Any]:
        """Comprehensive area analysis using all available agents"""
        
        tasks = []
        
        # Food analysis
        food_task = self.comm_handler.query_agent(
            AgentType.FOOD,
            "/recommendations",
            {
                "latitude": user_context.location.latitude,
                "longitude": user_context.location.longitude,
                "radius": 1000,
                "limit": 5
            }
        )
        tasks.append(("food", food_task))
        
        # Regulatory analysis
        if user_context.vehicle_type:
            regulatory_task = self.comm_handler.query_agent(
                AgentType.REGULATORY,
                "/regulatory-analysis", 
                {
                    "latitude": user_context.location.latitude,
                    "longitude": user_context.location.longitude,
                    "vehicle_type": user_context.vehicle_type
                }
            )
            tasks.append(("regulatory", regulatory_task))
        
        # Execute all tasks concurrently
        results = {}
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                logger.error(f"Error in {name} analysis: {str(e)}")
                results[name] = {"error": str(e)}
        
        return results


# Singleton instances
comm_handler = A2ACommunicationHandler()
orchestrator = AgentOrchestrator(comm_handler)