from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class ProfileCreate(BaseModel):
    name: str
    age: int
    gender: str
    class_level: int
    stream: Optional[str] = None
    location: Dict[str, Any]
    language_preference: str
    budget_range: str
    reservation_category: str
    mobility: str


class Profile(BaseModel):
    user_id: str
    name: str
    age: int
    gender: str
    class_level: int
    stream: Optional[str] = None
    location: Dict[str, Any]
    language_preference: str
    budget_range: str
    reservation_category: str
    mobility: str
    created_at: datetime


class QuizQuestion(BaseModel):
    id: str
    type: str
    text: str
    options: Optional[List[str]] = None
    language: str


class QuizCreate(BaseModel):
    user_id: str
    quiz_json: Dict[str, Any]
    source: str


class Quiz(BaseModel):
    id: str
    user_id: str
    quiz_json: Dict[str, Any]
    source: str
    created_at: datetime


class QuizResponseCreate(BaseModel):
    user_id: str
    quiz_id: str
    answers: Dict[str, Any]


class QuizResponse(BaseModel):
    id: str
    user_id: str
    quiz_id: str
    answers: Dict[str, Any]
    created_at: datetime


class College(BaseModel):
    college_id: str
    name: str
    state: str
    city: str
    programs: List[str]
    cutoffs: Dict[str, Any]
    facilities: Dict[str, Any]
    medium: List[str]
    source: str
    created_at: datetime


class CollegeRequest(BaseModel):
    user_id: str
    quiz_id: str
    field: Optional[str] = None
    location_type: Optional[str] = "state"


class Timeline(BaseModel):
    id: str
    name: str
    type: str
    for_course: str
    starts_on: str
    ends_on: str
    regions: Optional[Dict[str, Any]] = None


class TimelineRequest(BaseModel):
    user_id: str
    quiz_id: str
