from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


app = FastAPI(
    title="MatchDay by Swanavi API",
    description="AI matchday planning agent for World Cup 2026 fans.",
    version="0.1.0",
)

# Allows the future frontend website to call this backend.
# For local development, Next.js usually runs on localhost:3000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchdayRequest(BaseModel):
    start_location: str
    kickoff_time: str
    food_preference: str
    budget: str
    walking_tolerance: str
    travel_style: str
    arrival_buffer_minutes: int = 90


class ItineraryItem(BaseModel):
    time: str
    title: str
    location: str
    type: str
    duration_min: int
    estimated_cost: float
    walking_minutes: int
    risk_score: float
    utility_score: float
    reason: str
    can_skip: bool = True


class MatchdayResponse(BaseModel):
    itinerary_id: str
    city: str
    stadium: str
    arrival_risk: str
    time_slack_minutes: int
    total_estimated_cost: float
    total_walking_minutes: int
    itinerary: List[ItineraryItem]
    agent_explanation: str


class ReplanRequest(BaseModel):
    itinerary_id: str
    trigger: str


@app.get("/")
def root():
    return {
        "message": "MatchDay by Swanavi backend is running.",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "matchday-by-swanavi-api",
    }


@app.post("/plan-matchday", response_model=MatchdayResponse)
def plan_matchday(request: MatchdayRequest):
    itinerary = [
        ItineraryItem(
            time="10:30 AM",
            title="Start your matchday in Downtown Seattle",
            location=request.start_location,
            type="start",
            duration_min=15,
            estimated_cost=0,
            walking_minutes=0,
            risk_score=0.05,
            utility_score=0.90,
            reason="Starting early creates enough slack for food, sightseeing, and stadium arrival.",
            can_skip=False,
        ),
        ItineraryItem(
            time="11:15 AM",
            title="Visit Pike Place Market",
            location="Pike Place Market",
            type="attraction",
            duration_min=75,
            estimated_cost=10,
            walking_minutes=12,
            risk_score=0.15,
            utility_score=0.92,
            reason="Iconic Seattle attraction close to downtown and easy to fit before the match.",
            can_skip=True,
        ),
        ItineraryItem(
            time="12:45 PM",
            title="Vegetarian-friendly lunch near downtown",
            location="Downtown Seattle",
            type="food",
            duration_min=60,
            estimated_cost=18,
            walking_minutes=8,
            risk_score=0.12,
            utility_score=0.88,
            reason=f"Selected based on food preference: {request.food_preference}.",
            can_skip=True,
        ),
        ItineraryItem(
            time="2:15 PM",
            title="Waterfront walk and fan photos",
            location="Seattle Waterfront",
            type="activity",
            duration_min=60,
            estimated_cost=0,
            walking_minutes=18,
            risk_score=0.22,
            utility_score=0.80,
            reason="Adds a memorable pre-match activity while still preserving stadium buffer.",
            can_skip=True,
        ),
        ItineraryItem(
            time="3:45 PM",
            title="Head toward Lumen Field",
            location="Lumen Field",
            type="travel",
            duration_min=35,
            estimated_cost=5,
            walking_minutes=10,
            risk_score=0.18,
            utility_score=0.95,
            reason="Leaving early protects the 90-minute stadium arrival buffer.",
            can_skip=False,
        ),
        ItineraryItem(
            time="4:30 PM",
            title="Arrive near Lumen Field",
            location="Lumen Field",
            type="stadium_arrival",
            duration_min=90,
            estimated_cost=0,
            walking_minutes=5,
            risk_score=0.08,
            utility_score=1.00,
            reason="Arriving early reduces crowd, security, and transit risk before kickoff.",
            can_skip=False,
        ),
        ItineraryItem(
            time=request.kickoff_time,
            title="World Cup Match Kickoff",
            location="Lumen Field",
            type="match",
            duration_min=120,
            estimated_cost=0,
            walking_minutes=0,
            risk_score=0.01,
            utility_score=1.00,
            reason="The itinerary is optimized around getting here on time.",
            can_skip=False,
        ),
    ]

    return MatchdayResponse(
        itinerary_id="demo-seattle-001",
        city="Seattle",
        stadium="Lumen Field",
        arrival_risk="Low",
        time_slack_minutes=42,
        total_estimated_cost=sum(item.estimated_cost for item in itinerary),
        total_walking_minutes=sum(item.walking_minutes for item in itinerary),
        itinerary=itinerary,
        agent_explanation=(
            "I created a balanced Seattle matchday plan that includes sightseeing, "
            "vegetarian-friendly food, and a protected stadium arrival buffer. "
            "The plan prioritizes arriving at Lumen Field early while still giving the fan "
            "a strong downtown Seattle experience."
        ),
    )


@app.post("/replan-matchday", response_model=MatchdayResponse)
def replan_matchday(request: ReplanRequest):
    """
    Starter replan endpoint.

    Supported triggers for now:
    - late_30
    - cheaper_food
    - less_walking
    - tired
    - go_straight_to_stadium

    Later, this will use Gemini + MongoDB + scoring logic.
    """

    if request.trigger == "late_30":
        itinerary = [
            ItineraryItem(
                time="11:00 AM",
                title="Start your delayed matchday in Downtown Seattle",
                location="Downtown Seattle",
                type="start",
                duration_min=10,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.08,
                utility_score=0.85,
                reason="The plan was shifted forward because you are 30 minutes late.",
                can_skip=False,
            ),
            ItineraryItem(
                time="11:45 AM",
                title="Visit Pike Place Market briefly",
                location="Pike Place Market",
                type="attraction",
                duration_min=45,
                estimated_cost=8,
                walking_minutes=8,
                risk_score=0.18,
                utility_score=0.82,
                reason="Shortened the visit instead of removing it completely.",
                can_skip=True,
            ),
            ItineraryItem(
                time="12:45 PM",
                title="Quick vegetarian lunch near downtown",
                location="Downtown Seattle",
                type="food",
                duration_min=45,
                estimated_cost=16,
                walking_minutes=6,
                risk_score=0.15,
                utility_score=0.86,
                reason="Kept lunch but selected a faster option to protect stadium arrival time.",
                can_skip=True,
            ),
            ItineraryItem(
                time="3:30 PM",
                title="Head directly toward Lumen Field",
                location="Lumen Field",
                type="travel",
                duration_min=35,
                estimated_cost=5,
                walking_minutes=8,
                risk_score=0.16,
                utility_score=0.95,
                reason="Removed the waterfront stop to preserve the stadium arrival buffer.",
                can_skip=False,
            ),
            ItineraryItem(
                time="4:20 PM",
                title="Arrive near Lumen Field",
                location="Lumen Field",
                type="stadium_arrival",
                duration_min=100,
                estimated_cost=0,
                walking_minutes=5,
                risk_score=0.07,
                utility_score=1.00,
                reason="The updated plan still gets you to the stadium safely before kickoff.",
                can_skip=False,
            ),
            ItineraryItem(
                time="6:00 PM",
                title="World Cup Match Kickoff",
                location="Lumen Field",
                type="match",
                duration_min=120,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.01,
                utility_score=1.00,
                reason="The replan is optimized around not missing kickoff.",
                can_skip=False,
            ),
        ]

        explanation = (
            "You were 30 minutes late, so I removed the waterfront stop and shortened Pike Place. "
            "This keeps your lunch option and protects your stadium arrival buffer."
        )

    elif request.trigger == "cheaper_food":
        itinerary = [
            ItineraryItem(
                time="10:30 AM",
                title="Start your matchday in Downtown Seattle",
                location="Downtown Seattle",
                type="start",
                duration_min=15,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.05,
                utility_score=0.90,
                reason="Starting early creates enough slack for the full matchday plan.",
                can_skip=False,
            ),
            ItineraryItem(
                time="11:15 AM",
                title="Visit Pike Place Market",
                location="Pike Place Market",
                type="attraction",
                duration_min=75,
                estimated_cost=10,
                walking_minutes=12,
                risk_score=0.15,
                utility_score=0.92,
                reason="Kept this high-value Seattle activity.",
                can_skip=True,
            ),
            ItineraryItem(
                time="12:45 PM",
                title="Budget vegetarian lunch",
                location="Downtown Seattle",
                type="food",
                duration_min=45,
                estimated_cost=9,
                walking_minutes=7,
                risk_score=0.14,
                utility_score=0.82,
                reason="Swapped to a cheaper vegetarian-friendly meal while keeping the schedule stable.",
                can_skip=True,
            ),
            ItineraryItem(
                time="2:15 PM",
                title="Waterfront walk and fan photos",
                location="Seattle Waterfront",
                type="activity",
                duration_min=60,
                estimated_cost=0,
                walking_minutes=18,
                risk_score=0.22,
                utility_score=0.80,
                reason="Free activity that keeps the total cost low.",
                can_skip=True,
            ),
            ItineraryItem(
                time="3:45 PM",
                title="Head toward Lumen Field",
                location="Lumen Field",
                type="travel",
                duration_min=35,
                estimated_cost=5,
                walking_minutes=10,
                risk_score=0.18,
                utility_score=0.95,
                reason="Leaving early protects the stadium buffer.",
                can_skip=False,
            ),
            ItineraryItem(
                time="4:30 PM",
                title="Arrive near Lumen Field",
                location="Lumen Field",
                type="stadium_arrival",
                duration_min=90,
                estimated_cost=0,
                walking_minutes=5,
                risk_score=0.08,
                utility_score=1.00,
                reason="Arriving early keeps match arrival risk low.",
                can_skip=False,
            ),
            ItineraryItem(
                time="6:00 PM",
                title="World Cup Match Kickoff",
                location="Lumen Field",
                type="match",
                duration_min=120,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.01,
                utility_score=1.00,
                reason="The itinerary is optimized around getting here on time.",
                can_skip=False,
            ),
        ]

        explanation = (
            "I replaced lunch with a cheaper vegetarian-friendly option and kept the rest of the plan stable. "
            "This lowers cost without increasing arrival risk."
        )

    elif request.trigger == "less_walking":
        itinerary = [
            ItineraryItem(
                time="10:30 AM",
                title="Start your low-walking matchday in Downtown Seattle",
                location="Downtown Seattle",
                type="start",
                duration_min=15,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.05,
                utility_score=0.90,
                reason="The updated plan reduces walking while preserving the matchday experience.",
                can_skip=False,
            ),
            ItineraryItem(
                time="11:30 AM",
                title="Coffee and light sightseeing near downtown",
                location="Downtown Seattle",
                type="activity",
                duration_min=60,
                estimated_cost=8,
                walking_minutes=5,
                risk_score=0.10,
                utility_score=0.80,
                reason="Replaced longer walking activities with a lower-effort stop.",
                can_skip=True,
            ),
            ItineraryItem(
                time="12:45 PM",
                title="Vegetarian-friendly lunch close by",
                location="Downtown Seattle",
                type="food",
                duration_min=60,
                estimated_cost=18,
                walking_minutes=4,
                risk_score=0.12,
                utility_score=0.88,
                reason="Chose a nearby lunch option to reduce walking.",
                can_skip=True,
            ),
            ItineraryItem(
                time="3:45 PM",
                title="Transit or rideshare toward Lumen Field",
                location="Lumen Field",
                type="travel",
                duration_min=30,
                estimated_cost=12,
                walking_minutes=4,
                risk_score=0.15,
                utility_score=0.92,
                reason="Using transit or rideshare reduces walking before the match.",
                can_skip=False,
            ),
            ItineraryItem(
                time="4:30 PM",
                title="Arrive near Lumen Field",
                location="Lumen Field",
                type="stadium_arrival",
                duration_min=90,
                estimated_cost=0,
                walking_minutes=3,
                risk_score=0.07,
                utility_score=1.00,
                reason="This keeps arrival risk low with less physical strain.",
                can_skip=False,
            ),
            ItineraryItem(
                time="6:00 PM",
                title="World Cup Match Kickoff",
                location="Lumen Field",
                type="match",
                duration_min=120,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.01,
                utility_score=1.00,
                reason="The plan still centers around getting to kickoff on time.",
                can_skip=False,
            ),
        ]

        explanation = (
            "I reduced walking by removing the waterfront walk and replacing it with nearby, lower-effort stops. "
            "The plan costs a little more because it assumes more transit or rideshare usage."
        )

    elif request.trigger == "go_straight_to_stadium":
        itinerary = [
            ItineraryItem(
                time="3:30 PM",
                title="Leave Downtown Seattle for Lumen Field",
                location="Downtown Seattle",
                type="travel",
                duration_min=35,
                estimated_cost=5,
                walking_minutes=8,
                risk_score=0.08,
                utility_score=0.95,
                reason="Going directly to the stadium minimizes timing risk.",
                can_skip=False,
            ),
            ItineraryItem(
                time="4:15 PM",
                title="Arrive near Lumen Field",
                location="Lumen Field",
                type="stadium_arrival",
                duration_min=105,
                estimated_cost=0,
                walking_minutes=5,
                risk_score=0.04,
                utility_score=1.00,
                reason="This gives you the safest arrival window before kickoff.",
                can_skip=False,
            ),
            ItineraryItem(
                time="6:00 PM",
                title="World Cup Match Kickoff",
                location="Lumen Field",
                type="match",
                duration_min=120,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.01,
                utility_score=1.00,
                reason="This plan is optimized only around reaching the match safely.",
                can_skip=False,
            ),
        ]

        explanation = (
            "I removed all optional activities and routed you directly to Lumen Field. "
            "This is the safest plan if your priority is avoiding any chance of missing kickoff."
        )

    else:
        itinerary = [
            ItineraryItem(
                time="10:30 AM",
                title="Start your matchday in Downtown Seattle",
                location="Downtown Seattle",
                type="start",
                duration_min=15,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.05,
                utility_score=0.90,
                reason="Default fallback plan generated because the replan trigger was not recognized.",
                can_skip=False,
            ),
            ItineraryItem(
                time="3:45 PM",
                title="Head toward Lumen Field",
                location="Lumen Field",
                type="travel",
                duration_min=35,
                estimated_cost=5,
                walking_minutes=10,
                risk_score=0.18,
                utility_score=0.95,
                reason="Leaving early protects the stadium arrival buffer.",
                can_skip=False,
            ),
            ItineraryItem(
                time="6:00 PM",
                title="World Cup Match Kickoff",
                location="Lumen Field",
                type="match",
                duration_min=120,
                estimated_cost=0,
                walking_minutes=0,
                risk_score=0.01,
                utility_score=1.00,
                reason="The plan remains centered around kickoff.",
                can_skip=False,
            ),
        ]

        explanation = (
            "I did not recognize that replan request yet, so I returned a safe fallback plan."
        )

    return MatchdayResponse(
        itinerary_id=request.itinerary_id,
        city="Seattle",
        stadium="Lumen Field",
        arrival_risk="Low",
        time_slack_minutes=55 if request.trigger == "go_straight_to_stadium" else 35,
        total_estimated_cost=sum(item.estimated_cost for item in itinerary),
        total_walking_minutes=sum(item.walking_minutes for item in itinerary),
        itinerary=itinerary,
        agent_explanation=explanation,
    )