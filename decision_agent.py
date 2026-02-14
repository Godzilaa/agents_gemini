from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from a2a_models import (
    DecisionRequest, FinalDecision, UserContext, Location,
    AgentMessage, AgentType, MessageType, Priority,
    AgentResponse
)
from a2a_communication import comm_handler, orchestrator

app = FastAPI(
    title="Master Decision Agent",
    description="Coordinates all agents to provide unified recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DecisionEngine:
    """Core decision making engine that coordinates all agents"""
    
    def __init__(self):
        self.decision_history: List[FinalDecision] = []
        self.active_requests: Dict[str, Dict] = {}
    
    def calculate_confidence_score(self, agent_responses: Dict[str, Any]) -> float:
        """Calculate overall confidence based on agent responses"""
        total_confidence = 0.0
        agent_count = 0
        
        weights = {
            "food": 0.3,
            "regulatory": 0.4, 
            "transport": 0.2,
            "festival": 0.1
        }
        
        for agent_type, response in agent_responses.items():
            if response and not response.get("error"):
                # Extract confidence from different response structures
                confidence = 0.7  # Default confidence
                
                if agent_type == "food" and "top_recommendations" in response:
                    # Food agent confidence based on number of results
                    num_results = len(response.get("top_recommendations", []))
                    confidence = min(0.9, 0.5 + (num_results * 0.05))
                
                elif agent_type == "regulatory" and "risk_score" in response:
                    # Regulatory confidence based on risk assessment completeness
                    risk_data = response.get("applicable_zones", [])
                    confidence = min(0.95, 0.6 + (len(risk_data) * 0.1))
                
                weight = weights.get(agent_type, 0.25)
                total_confidence += confidence * weight
                agent_count += weight
        
        return total_confidence / agent_count if agent_count > 0 else 0.5
    
    def generate_combined_recommendations(self, agent_responses: Dict[str, Any], 
                                        user_context: UserContext) -> List[str]:
        """Generate unified recommendations from all agent responses"""
        recommendations = []
        
        # Food recommendations
        food_data = agent_responses.get("food", {})
        if food_data and "top_recommendations" in food_data:
            top_restaurants = food_data["top_recommendations"][:3]
            for restaurant in top_restaurants:
                rec = f"🍴 {restaurant.get('name', 'Restaurant')}"
                if restaurant.get('rating'):
                    rec += f" (⭐ {restaurant['rating']})"
                if restaurant.get('label'):
                    rec += f" - {restaurant['label']}"
                recommendations.append(rec)
        
        # Regulatory recommendations  
        regulatory_data = agent_responses.get("regulatory", {})
        if regulatory_data:
            risk_level = regulatory_data.get("risk_level", "").lower()
            
            if risk_level == "high":
                recommendations.append("⚠️ HIGH RISK AREA - Extra caution advised for traffic enforcement")
            elif risk_level == "moderate":
                recommendations.append("⚡ Moderate enforcement area - Follow traffic rules strictly")
            
            # Add specific warnings
            warnings = regulatory_data.get("warnings", [])
            for warning in warnings[:2]:  # Limit to top 2 warnings
                recommendations.append(f"🚨 {warning}")
        
        # Transport recommendations
        transport_data = agent_responses.get("transport", {})
        if transport_data:
            # Add transport-related recommendations when available
            pass
        
        # Festival/Event recommendations
        festival_data = agent_responses.get("festival", {})
        if festival_data:
            # Add event-related recommendations when available
            pass
        
        # Default recommendations if none found
        if not recommendations:
            recommendations = [
                "📍 Location analysis completed",
                "✅ No major concerns detected in the area",
                "🚗 Standard traffic rules apply"
            ]
        
        return recommendations
    
    def extract_warnings(self, agent_responses: Dict[str, Any]) -> List[str]:
        """Extract and prioritize warnings from all agents"""
        warnings = []
        
        # Regulatory warnings (highest priority)
        regulatory_data = agent_responses.get("regulatory", {})
        if regulatory_data and "warnings" in regulatory_data:
            warnings.extend([f"🚨 {w}" for w in regulatory_data["warnings"][:3]])
        
        # Food-related warnings
        food_data = agent_responses.get("food", {})
        if food_data and "top_recommendations" in food_data:
            restaurants = food_data["top_recommendations"]
            low_hygiene = [r for r in restaurants if r.get("hygiene_score", 10) < 5]
            if low_hygiene:
                warnings.append(f"🏥 {len(low_hygiene)} restaurants have low hygiene scores")
        
        # Transport warnings
        transport_data = agent_responses.get("transport", {})
        if transport_data:
            # Add transport warnings when available
            pass
        
        return warnings
    
    async def make_decision(self, request: DecisionRequest) -> FinalDecision:
        """Main decision making function"""
        decision_id = str(uuid.uuid4())
        
        try:
            # Route request based on query type
            if request.query_type == "dining_recommendation":
                agent_responses = await orchestrator.coordinate_dining_recommendation(request.user_context)
                primary_rec = "Restaurant recommendations with safety analysis"
                
            elif request.query_type == "route_planning": 
                agent_responses = await orchestrator.coordinate_route_planning(request.user_context)
                primary_rec = "Route planning with regulatory and event considerations"
                
            elif request.query_type == "area_analysis":
                agent_responses = await orchestrator.coordinate_area_analysis(request.user_context)
                primary_rec = "Comprehensive area analysis"
                
            else:
                # Default comprehensive analysis
                agent_responses = await orchestrator.coordinate_area_analysis(request.user_context)
                primary_rec = f"Analysis for {request.query_type}"
            
            # Generate final decision
            confidence_score = self.calculate_confidence_score(agent_responses)
            combined_recommendations = self.generate_combined_recommendations(
                agent_responses, request.user_context
            )
            warnings = self.extract_warnings(agent_responses)
            
            decision = FinalDecision(
                decision_id=decision_id,
                user_query=request.query_type,
                location=request.user_context.location,
                primary_recommendation=primary_rec,
                confidence_score=confidence_score,
                agent_contributions=agent_responses,
                combined_recommendations=combined_recommendations,
                warnings=warnings,
                additional_info={
                    "processing_agents": list(agent_responses.keys()),
                    "user_vehicle": request.user_context.vehicle_type,
                    "request_priority": request.user_context.urgency_level.value
                },
                timestamp=datetime.now()
            )
            
            # Store decision
            self.decision_history.append(decision)
            
            return decision
            
        except Exception as e:
            # Fallback decision
            return FinalDecision(
                decision_id=decision_id,
                user_query=request.query_type,
                location=request.user_context.location,
                primary_recommendation="Error occurred during analysis",
                confidence_score=0.1,
                agent_contributions={"error": str(e)},
                combined_recommendations=[
                    f"❌ Error: {str(e)}",
                    "🔄 Please try again or contact support"
                ],
                warnings=["System error occurred during processing"],
                additional_info={"error": str(e)},
                timestamp=datetime.now()
            )


# Global decision engine
decision_engine = DecisionEngine()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agent_status = await comm_handler.get_agent_status()
    return {
        "status": "ok",
        "message": "Master Decision Agent is running",
        "agent_status": agent_status,
        "decisions_processed": len(decision_engine.decision_history)
    }


@app.post("/decide", response_model=FinalDecision)
async def make_decision(request: DecisionRequest):
    """Main decision endpoint - coordinates all agents"""
    try:
        decision = await decision_engine.make_decision(request)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision processing failed: {str(e)}")


@app.post("/quick-analysis")
async def quick_analysis(
    latitude: float,
    longitude: float,
    vehicle_type: str = "car",
    analysis_type: str = "area_analysis"
):
    """Quick analysis endpoint with minimal required parameters"""
    
    user_context = UserContext(
        location=Location(latitude=latitude, longitude=longitude),
        vehicle_type=vehicle_type
    )
    
    request = DecisionRequest(
        user_context=user_context,
        query_type=analysis_type
    )
    
    decision = await decision_engine.make_decision(request)
    
    # Return simplified response
    return {
        "location": f"{latitude}, {longitude}",
        "primary_recommendation": decision.primary_recommendation,
        "confidence_score": decision.confidence_score,
        "recommendations": decision.combined_recommendations,
        "warnings": decision.warnings,
        "agent_data": {
            "food_results": len(decision.agent_contributions.get("food", {}).get("top_recommendations", [])),
            "regulatory_risk": decision.agent_contributions.get("regulatory", {}).get("risk_level", "unknown"),
            "analysis_timestamp": decision.timestamp.isoformat()
        }
    }


@app.get("/dining-recommendation")
async def get_dining_recommendation(
    latitude: float,
    longitude: float,
    vehicle_type: str = "car",
    radius: int = 2000,
    cuisine: str = None
):
    """Specialized endpoint for dining recommendations with safety analysis"""
    
    preferences = {"radius": radius, "limit": 10}
    if cuisine:
        preferences["cuisine_type"] = cuisine
    
    user_context = UserContext(
        location=Location(latitude=latitude, longitude=longitude),
        vehicle_type=vehicle_type,
        preferences=preferences,
        activity_type="dining"
    )
    
    request = DecisionRequest(
        user_context=user_context,
        query_type="dining_recommendation"
    )
    
    decision = await decision_engine.make_decision(request)
    return decision


@app.get("/route-safety")
async def get_route_safety(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    vehicle_type: str = "car"
):
    """Route safety analysis between two points"""
    
    user_context = UserContext(
        location=Location(latitude=origin_lat, longitude=origin_lng),
        destination=Location(latitude=dest_lat, longitude=dest_lng),
        vehicle_type=vehicle_type,
        activity_type="route_planning"
    )
    
    request = DecisionRequest(
        user_context=user_context,
        query_type="route_planning"
    )
    
    decision = await decision_engine.make_decision(request)
    return decision


@app.get("/decisions")
async def get_decision_history(limit: int = 10):
    """Get recent decision history"""
    recent_decisions = decision_engine.decision_history[-limit:]
    return {
        "total_decisions": len(decision_engine.decision_history),
        "recent_decisions": [
            {
                "decision_id": d.decision_id,
                "query_type": d.user_query,
                "location": f"{d.location.latitude}, {d.location.longitude}",
                "confidence": d.confidence_score,
                "timestamp": d.timestamp.isoformat()
            }
            for d in recent_decisions
        ]
    }


@app.post("/a2a/receive")
async def receive_a2a_message(message: AgentMessage):
    """Receive messages from other agents (A2A endpoint)"""
    # Log incoming message
    print(f"Received A2A message from {message.sender_agent}: {message.message_type}")
    
    # Process different message types
    if message.message_type == MessageType.STATUS:
        # Handle status updates
        pass
    elif message.message_type == MessageType.NOTIFICATION:
        # Handle notifications
        pass
    
    return {"status": "received", "message_id": message.message_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)