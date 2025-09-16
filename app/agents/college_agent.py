import os
import json
import httpx
import google.generativeai as genai
from app.db import get_supabase
from app.models import Profile
from app.agents import recommendation_agent
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

BASE_URL = "https://raw.githubusercontent.com/Clueless-Community/collegeAPI/main/data"


async def fetch_colleges(user_id: str, quiz_id: str) -> Dict[str, Any]:
    supabase = get_supabase()

    profile_result = (
        supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    )
    if not profile_result.data:
        raise Exception("profile not found")

    profile = Profile(**profile_result.data[0])

    quiz_result = supabase.table("quizzes").select("*").eq("id", quiz_id).execute()
    if not quiz_result.data:
        raise Exception("quiz not found")

    quiz_data = quiz_result.data[0]["quiz_json"]
    recommendations = await recommendation_agent.fetch_recommendations(user_id, quiz_id)
    colleges_data = await create_recommendations(profile, quiz_data, recommendations)

    await store_colleges(user_id, colleges_data)

    return colleges_data


async def create_recommendations(
    profile: Profile, quiz_data: Dict[str, Any], recommendations: Dict[str, Any]
) -> Dict[str, Any]:
    history = quiz_data.get("history", [])

    quiz_qa = []
    for qa in history:
        quiz_qa.append(
            {
                "question": qa["question"]["text"],
                "answer": qa["answer"],
                "question_number": qa.get("question_number", 0),
            }
        )

    location_state = profile.location.get("state", "")
    location_city = profile.location.get("city", "")

    if profile.class_level == 9 or profile.class_level == 10:
        streams = recommendations.get("streams", [])
        field_mapping = map_streams(streams)
        print(f"Mapped streams {streams} to fields: {field_mapping}")
    else:
        courses = recommendations.get("courses", [])
        field_mapping = map_courses(courses)
        print(f"Mapped courses {courses} to fields: {field_mapping}")

    college_data = {}
    for field in field_mapping:
        try:
            colleges_by_state = await fetch_data(field, "state", location_state)
            colleges_by_city = await fetch_data(field, "city", location_city)

            college_data[field] = {
                "state_colleges": colleges_by_state[:10],
                "city_colleges": colleges_by_city[:5],
                "total_state": len(colleges_by_state),
                "total_city": len(colleges_by_city),
                "recommendation_source": streams
                if profile.class_level in [9, 10]
                else courses,
            }
            print(
                f"Found {len(colleges_by_state)} colleges in {location_state} for {field}"
            )
        except Exception as e:
            print(f"Error fetching {field} colleges: {e}")
            college_data[field] = {
                "state_colleges": [],
                "city_colleges": [],
                "total_state": 0,
                "total_city": 0,
                "recommendation_source": streams
                if profile.class_level in [9, 10]
                else courses,
            }

    intelligent_recommendations = await generate_recommendations(
        profile, quiz_qa, recommendations, college_data
    )

    return {
        "college_data": college_data,
        "intelligent_recommendations": intelligent_recommendations,
        "location": {"state": location_state, "city": location_city},
        "profile_context": {
            "class_level": profile.class_level,
            "stream": getattr(profile, "stream", None),
            "budget_range": profile.budget_range,
            "mobility": profile.mobility,
            "reservation_category": profile.reservation_category,
            "language_preference": profile.language_preference,
        },
        "source_recommendations": {
            "streams": recommendations.get("streams", []),
            "courses": recommendations.get("courses", []),
            "reasons": recommendations.get("reasons", {}),
            "message": recommendations.get("message", ""),
        },
        "field_mapping": field_mapping,
        "total_colleges_found": sum(
            data.get("total_state", 0) + data.get("total_city", 0)
            for data in college_data.values()
        ),
    }


async def fetch_data(
    field: str, filter_type: str, location: str
) -> List[Dict[str, Any]]:
    if not location:
        return []

    file_mapping = {
        "engineering": "engineering_ranking.json",
        "medical": "medical_ranking.json",
        "management": "management_ranking.json",
        "agriculture": "allAgriculture.json",
        "dental": "dental_ranking.json",
        "law": "law_ranking.json",
        "pharmacy": "pharmacy_ranking.json",
        "architecture": "architecture_ranking.json",
    }

    filename = file_mapping.get(field)
    if not filename:
        return []

    url = f"{BASE_URL}/{filename}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            colleges = response.json()

        filtered_colleges = []
        location_lower = location.lower()

        for college in colleges:
            if field == "agriculture":
                college_state = college.get("State", "").lower()
                college_city = college.get("City", "").lower()
            else:
                college_state = college.get("state", "").lower()
                college_city = college.get("city", "").lower()

            if filter_type == "state" and college_state == location_lower:
                filtered_colleges.append(college)
            elif filter_type == "city" and college_city == location_lower:
                filtered_colleges.append(college)

        return filtered_colleges

    except httpx.RequestError:
        return []
    except httpx.HTTPStatusError:
        return []
    except json.JSONDecodeError:
        return []


def map_streams(streams: List[str]) -> List[str]:
    stream_mapping = {
        "Science (PCM)": ["engineering"],
        "Science (PCB)": ["medical"],
        "Science with Computer Science": ["engineering"],
        "Commerce with Mathematics": ["management"],
        "Commerce with Business Studies": ["management"],
        "Commerce": ["management"],
        "Arts with Fine Arts": ["architecture"],
        "Arts with Languages/Mass Comm": ["law"],
        "Arts/Humanities": ["law"],
        "Vocational/Skill-based courses": ["engineering", "medical", "management"],
    }

    mapped_fields = []
    for stream in streams:
        if stream in stream_mapping:
            mapped_fields.extend(stream_mapping[stream])
        else:
            if "science" in stream.lower():
                if "pcm" in stream.lower() or "physics" in stream.lower():
                    mapped_fields.append("engineering")
                elif "pcb" in stream.lower() or "biology" in stream.lower():
                    mapped_fields.append("medical")
                else:
                    mapped_fields.extend(["engineering", "medical"])
            elif "commerce" in stream.lower():
                mapped_fields.append("management")
            elif "arts" in stream.lower() or "humanities" in stream.lower():
                mapped_fields.append("law")

    return (
        list(set(mapped_fields))
        if mapped_fields
        else ["engineering", "medical", "management"]
    )


def map_courses(courses: List[str]) -> List[str]:
    course_mapping = {
        "B.Tech": ["engineering"],
        "B.Tech CSE": ["engineering"],
        "MBBS": ["medical"],
        "B.Pharmacy": ["pharmacy"],
        "B.Sc Nursing": ["medical"],
        "B.Com": ["management"],
        "BBA": ["management"],
        "CA Foundation": ["management"],
        "Banking & Insurance": ["management"],
        "BA": ["law"],
        "B.Ed": ["law"],
        "Law": ["law"],
        "B.Arch": ["architecture"],
        "BA Fine Arts": ["architecture"],
        "Design": ["architecture"],
        "Mass Communication": ["law"],
        "Journalism": ["law"],
        "Diploma": ["engineering"],
        "ITI": ["engineering"],
        "Paramedical": ["medical"],
        "Hospitality": ["management"],
        "Hotel Management": ["management"],
    }

    mapped_fields = []
    for course in courses:
        course_found = False
        for key in course_mapping:
            if key.lower() in course.lower():
                mapped_fields.extend(course_mapping[key])
                course_found = True
                break

        if not course_found:
            if any(
                word in course.lower()
                for word in [
                    "tech",
                    "engineer",
                    "computer",
                    "mechanical",
                    "civil",
                    "electrical",
                ]
            ):
                mapped_fields.append("engineering")
            elif any(
                word in course.lower()
                for word in ["medical", "mbbs", "doctor", "nurse", "pharmacy", "dental"]
            ):
                mapped_fields.append("medical")
            elif any(
                word in course.lower()
                for word in [
                    "commerce",
                    "management",
                    "business",
                    "finance",
                    "economics",
                ]
            ):
                mapped_fields.append("management")
            elif any(
                word in course.lower()
                for word in ["architecture", "design", "fine arts"]
            ):
                mapped_fields.append("architecture")
            elif any(
                word in course.lower()
                for word in ["law", "legal", "arts", "humanities", "social"]
            ):
                mapped_fields.append("law")

    return (
        list(set(mapped_fields))
        if mapped_fields
        else ["engineering", "medical", "management"]
    )


async def generate_recommendations(
    profile: Profile,
    quiz_qa: List[Dict[str, Any]],
    recommendations: Dict[str, Any],
    college_data: Dict[str, Any],
) -> Dict[str, Any]:
    prompt = f"""You are an expert college counselor for Indian students. Based on the student's comprehensive profile, quiz responses, career recommendations, and available colleges, provide intelligent and personalized college recommendations.

STUDENT PROFILE:
- Class: {profile.class_level}
- Age: {profile.age}
- Location: {profile.location}
- Budget Range: {profile.budget_range}
- Mobility: {profile.mobility}
- Reservation Category: {profile.reservation_category}
- Language Preference: {profile.language_preference}
- Stream: {getattr(profile, "stream", "Not specified")}

QUIZ RESPONSES & PERSONALITY:
{json.dumps(quiz_qa, indent=2)}

CAREER GUIDANCE RESULTS:
{json.dumps(recommendations, indent=2)}

AVAILABLE COLLEGES BY FIELD:
{json.dumps(college_data, indent=2)}

INSTRUCTIONS:
1. Prioritize colleges that match the student's recommended streams/courses from career guidance
2. Consider budget constraints and suggest appropriate options within their range
3. Factor in location preferences and mobility limitations from profile
4. Account for reservation category benefits if applicable
5. Provide realistic admission chances based on their current class level
6. Focus on colleges that align with their personality traits from quiz responses

Provide specific, actionable recommendations based strictly on their profile and recommendations:
{{
  "top_colleges": [
    {{
      "name": "College Name",
      "field": "engineering/medical/management/etc",
      "location": "City, State",
      "rank": "NIRF rank if available",
      "reason": "Why this college specifically fits their profile, stream/course recommendations, and quiz responses",
      "fit_score": 0.85,
      "estimated_fees": "Annual fee range matching their budget",
      "admission_requirements": "Specific requirements considering their class level and stream",
      "considerations": ["Important factor considering their profile"]
    }}
  ],
  "budget_strategy": "Financial planning advice tailored to their specific budget range and reservation category",
  "location_advice": "Location guidance based on their mobility preferences and current location",
  "admission_timeline": {{
    "immediate": "Actions based on their current class level",
    "short_term": "3-6 months preparation aligned with their stream/courses",
    "application_period": "Timeline considering their academic year and recommended fields"
  }},
  "next_steps": [
    "Action item 1 based on their recommended stream/course",
    "Action item 2 considering their profile constraints",
    "Action item 3 aligned with their career guidance"
  ]
}}
"""

    response = model.generate_content(prompt)

    try:
        response_text = response.text.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()

        intelligent_recs = json.loads(response_text)
        return intelligent_recs
    except (json.JSONDecodeError, KeyError):
        return {
            "top_colleges": [],
            "budget_strategy": f"Plan for {profile.budget_range} budget considering your {profile.reservation_category} category benefits",
            "location_advice": f"Focus on colleges in {profile.location.get('state', 'your state')} based on your {profile.mobility} mobility preference",
            "admission_timeline": {
                "immediate": f"Research entrance exams for Class {profile.class_level} students",
                "short_term": "Prepare for entrance tests in your recommended fields",
                "application_period": "Apply according to your class level timeline",
            },
            "next_steps": [
                f"Focus on {', '.join(recommendations.get('streams', []) or recommendations.get('courses', []))} related entrance exams",
                f"Research colleges within {profile.budget_range} budget in {profile.location.get('state', 'your area')}",
                "Prepare documents considering your reservation category benefits",
            ],
        }


async def search_colleges(
    field: str, location: str, location_type: str = "state"
) -> List[Dict[str, Any]]:
    try:
        return await fetch_data(field, location_type, location)
    except Exception:
        return []


async def store_colleges(user_id: str, colleges_data: Dict[str, Any]) -> None:
    supabase = get_supabase()

    try:
        college_record = {
            "user_id": user_id,
            "colleges_json": colleges_data,
            "source": "college_api",
            "updated_at": "now()",
        }

        existing = (
            supabase.table("colleges").select("*").eq("user_id", user_id).execute()
        )

        if existing.data:
            supabase.table("colleges").update(college_record).eq(
                "user_id", user_id
            ).execute()
        else:
            supabase.table("colleges").insert(college_record).execute()
    except Exception:
        pass
