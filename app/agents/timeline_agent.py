import os
import json
import google.generativeai as genai
from app.db import get_supabase
from app.models import Profile
from app.agents import recommendation_agent, college_agent
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


async def fetch_timeline(user_id: str, quiz_id: str) -> Dict[str, Any]:
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
    colleges_data = await college_agent.fetch_colleges(user_id, quiz_id)

    timeline_data = await create_timeline(
        profile, quiz_data, recommendations, colleges_data
    )

    await store_timeline(user_id, timeline_data)

    return timeline_data


async def create_timeline(
    profile: Profile,
    quiz_data: Dict[str, Any],
    recommendations: Dict[str, Any],
    colleges_data: Dict[str, Any],
) -> Dict[str, Any]:
    current_date = datetime.now()
    current_year = current_date.year

    if profile.class_level == 9 or profile.class_level == 10:
        streams = recommendations.get("streams", [])
        timeline_milestones = generate_streams(profile, streams, current_date)
    else:
        courses = recommendations.get("courses", [])
        timeline_milestones = generate_courses(
            profile, courses, colleges_data, current_date
        )

    intelligent_timeline = await generate_recommendations(
        profile, recommendations, colleges_data, timeline_milestones
    )

    return {
        "timeline_milestones": timeline_milestones,
        "intelligent_timeline": intelligent_timeline,
        "profile_context": {
            "class_level": profile.class_level,
            "age": profile.age,
            "current_academic_year": f"{current_year}-{current_year + 1}",
            "location": profile.location,
            "budget_range": profile.budget_range,
        },
        "recommendations_context": {
            "streams": recommendations.get("streams", []),
            "courses": recommendations.get("courses", []),
            "colleges_found": colleges_data.get("total_colleges_found", 0),
            "top_colleges": colleges_data.get("intelligent_recommendations", {}).get(
                "top_colleges", []
            )[:3],
        },
        "academic_plan": {
            "current_focus": f"Class {profile.class_level} completion",
            "next_milestone": timeline_milestones[0] if timeline_milestones else None,
            "target_goal": recommendations.get(
                "courses", recommendations.get("streams", ["Future Education"])
            )[0]
            if recommendations.get("courses") or recommendations.get("streams")
            else "Academic Success",
        },
    }


def generate_streams(
    profile: Profile, streams: List[str], current_date: datetime
) -> List[Dict[str, Any]]:
    milestones = []
    current_year = current_date.year

    if profile.class_level == 9:
        milestones.extend(
            [
                {
                    "title": "Complete Class 9",
                    "type": "academic",
                    "date": f"March {current_year + 1}",
                    "priority": "high",
                    "description": "Focus on building strong fundamentals in chosen streams",
                    "related_streams": streams,
                },
                {
                    "title": "Stream Selection for Class 11",
                    "type": "decision",
                    "date": f"April-May {current_year + 1}",
                    "priority": "critical",
                    "description": f"Finalize stream selection: {', '.join(streams)}",
                    "related_streams": streams,
                },
                {
                    "title": "Class 11 Admission",
                    "type": "admission",
                    "date": f"June {current_year + 1}",
                    "priority": "high",
                    "description": "Secure admission in chosen stream",
                    "related_streams": streams,
                },
                {
                    "title": "Entrance Exam Preparation Begins",
                    "type": "preparation",
                    "date": f"July {current_year + 1}",
                    "priority": "medium",
                    "description": "Start early preparation for relevant entrance exams",
                    "related_streams": streams,
                },
            ]
        )

    elif profile.class_level == 10:
        milestones.extend(
            [
                {
                    "title": "Class 10 Board Exams",
                    "type": "exam",
                    "date": f"February-March {current_year + 1}",
                    "priority": "critical",
                    "description": "Achieve good marks for stream eligibility",
                    "related_streams": streams,
                },
                {
                    "title": "Stream Selection",
                    "type": "decision",
                    "date": f"April {current_year + 1}",
                    "priority": "critical",
                    "description": f"Choose from recommended streams: {', '.join(streams)}",
                    "related_streams": streams,
                },
                {
                    "title": "Class 11 Admission",
                    "type": "admission",
                    "date": f"May-June {current_year + 1}",
                    "priority": "high",
                    "description": "Secure admission in preferred schools",
                    "related_streams": streams,
                },
            ]
        )

    return milestones


def generate_courses(
    profile: Profile,
    courses: List[str],
    colleges_data: Dict[str, Any],
    current_date: datetime,
) -> List[Dict[str, Any]]:
    milestones = []
    current_year = current_date.year

    top_colleges = colleges_data.get("intelligent_recommendations", {}).get(
        "top_colleges", []
    )

    if profile.class_level == 11:
        milestones.extend(
            [
                {
                    "title": "Focus on Class 11 Foundation",
                    "type": "academic",
                    "date": f"Current - March {current_year + 1}",
                    "priority": "high",
                    "description": "Build strong foundation for entrance exam preparation",
                    "related_courses": courses,
                },
                {
                    "title": "Entrance Exam Registration",
                    "type": "registration",
                    "date": f"September {current_year + 1} - February {current_year + 2}",
                    "priority": "critical",
                    "description": "Register for relevant entrance exams",
                    "related_courses": courses,
                },
                {
                    "title": "Intensive Preparation Phase",
                    "type": "preparation",
                    "date": f"April {current_year + 1} - January {current_year + 2}",
                    "priority": "high",
                    "description": "Intensive preparation for entrance exams",
                    "related_courses": courses,
                },
            ]
        )

    elif profile.class_level == 12:
        milestones.extend(
            [
                {
                    "title": "Class 12 Board Exams",
                    "type": "exam",
                    "date": f"February-March {current_year + 1}",
                    "priority": "critical",
                    "description": "Achieve required percentage for course eligibility",
                    "related_courses": courses,
                },
                {
                    "title": "Entrance Exams",
                    "type": "exam",
                    "date": f"April-June {current_year + 1}",
                    "priority": "critical",
                    "description": "Appear for relevant entrance examinations",
                    "related_courses": courses,
                },
                {
                    "title": "College Applications",
                    "type": "application",
                    "date": f"May-July {current_year + 1}",
                    "priority": "high",
                    "description": "Apply to recommended colleges from system analysis",
                    "related_courses": courses,
                    "target_colleges": [c.get("name", "") for c in top_colleges[:3]]
                    if top_colleges
                    else [],
                },
                {
                    "title": "Counseling & Admission",
                    "type": "admission",
                    "date": f"June-August {current_year + 1}",
                    "priority": "critical",
                    "description": "Participate in counseling and secure admission",
                    "related_courses": courses,
                },
            ]
        )

    for course in courses:
        if "engineering" in course.lower() or "b.tech" in course.lower():
            milestones.append(
                {
                    "title": "JEE Main/Advanced",
                    "type": "exam",
                    "date": f"April-May {current_year + 1}",
                    "priority": "critical",
                    "description": "Engineering entrance examinations",
                    "related_courses": [course],
                }
            )
        elif "medical" in course.lower() or "mbbs" in course.lower():
            milestones.append(
                {
                    "title": "NEET Examination",
                    "type": "exam",
                    "date": f"May {current_year + 1}",
                    "priority": "critical",
                    "description": "Medical entrance examination",
                    "related_courses": [course],
                }
            )
        elif "management" in course.lower() or "mba" in course.lower():
            milestones.append(
                {
                    "title": "CAT/MAT Preparation",
                    "type": "preparation",
                    "date": f"June {current_year} - November {current_year}",
                    "priority": "high",
                    "description": "Management entrance exam preparation",
                    "related_courses": [course],
                }
            )

    return sorted(milestones, key=lambda x: x["date"])


async def generate_recommendations(
    profile: Profile,
    recommendations: Dict[str, Any],
    colleges_data: Dict[str, Any],
    timeline_milestones: List[Dict[str, Any]],
) -> Dict[str, Any]:
    prompt = f"""You are an expert academic timeline counselor for Indian students. Based on the student's profile, career recommendations, college options, and milestone timeline, create a comprehensive action plan for academic success.

STUDENT PROFILE:
- Class: {profile.class_level}
- Age: {profile.age}
- Location: {profile.location}
- Budget Range: {profile.budget_range}
- Mobility: {profile.mobility}
- Reservation Category: {profile.reservation_category}

CAREER RECOMMENDATIONS FROM SYSTEM:
{json.dumps(recommendations, indent=2)}

COLLEGE OPTIONS IDENTIFIED:
{json.dumps(colleges_data.get("intelligent_recommendations", {}), indent=2)}

GENERATED TIMELINE MILESTONES:
{json.dumps(timeline_milestones, indent=2)}

INSTRUCTIONS:
Create a comprehensive timeline plan that helps the student track their progress and achieve their recommended goals. Focus on:
1. Immediate actionable steps based on current class level
2. Monthly planning aligned with college recommendations
3. Entrance exam schedules for their recommended fields
4. Application deadlines for suggested colleges
5. Success tracking metrics

Generate timeline plan in this JSON format:
{{
  "immediate_actions": [
    {{
      "action": "Specific action aligned with recommendations",
      "deadline": "When to complete",
      "priority": "high/medium/low",
      "reason": "How this supports their college/career goals"
    }}
  ],
  "monthly_plan": {{
    "current_month": ["Action tied to timeline milestones"],
    "next_3_months": ["Action supporting college prep"],
    "next_6_months": ["Action for entrance exam readiness"]
  }},
  "exam_calendar": [
    {{
      "exam_name": "Specific exam for their recommended fields",
      "registration_deadline": "Date",
      "exam_date": "Date",
      "relevance": "How it connects to their college/course recommendations"
    }}
  ],
  "critical_deadlines": [
    {{
      "event": "Milestone from timeline",
      "deadline": "When",
      "impact": "Effect on college admission chances"
    }}
  ],
  "progress_tracking": [
    "Measurable goal tied to recommendations",
    "Academic milestone with timeline",
    "Entrance exam preparation target"
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

        intelligent_timeline = json.loads(response_text)
        return intelligent_timeline
    except (json.JSONDecodeError, KeyError):
        return {
            "immediate_actions": [
                {
                    "action": f"Focus on Class {profile.class_level} studies with emphasis on recommended subjects",
                    "deadline": "Daily",
                    "priority": "high",
                    "reason": "Build foundation for recommended streams/courses",
                }
            ],
            "monthly_plan": {
                "current_month": [
                    "Complete current syllabus",
                    "Research recommended fields",
                ],
                "next_3_months": [
                    "Entrance exam preparation",
                    "College research from recommendations",
                ],
                "next_6_months": ["Application preparation", "Final exam readiness"],
            },
            "exam_calendar": [],
            "critical_deadlines": [
                {
                    "event": f"Class {profile.class_level} academic year completion",
                    "deadline": "March",
                    "impact": "Progression to next academic level",
                }
            ],
            "progress_tracking": [
                f"Achieve 85%+ in Class {profile.class_level}",
                "Complete preparation for recommended entrance exams",
                "Research and shortlist colleges from recommendations",
            ],
        }


async def store_timeline(user_id: str, timeline_data: Dict[str, Any]) -> None:
    supabase = get_supabase()

    try:
        timeline_record = {
            "user_id": user_id,
            "timeline_json": timeline_data,
            "source": "timeline_agent",
            "updated_at": "now()",
        }

        existing = (
            supabase.table("timelines").select("*").eq("user_id", user_id).execute()
        )

        if existing.data:
            supabase.table("timelines").update(timeline_record).eq(
                "user_id", user_id
            ).execute()
        else:
            supabase.table("timelines").insert(timeline_record).execute()
    except Exception:
        pass


async def get_timeline(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase()

    try:
        result = (
            supabase.table("timelines").select("*").eq("user_id", user_id).execute()
        )
        if result.data:
            return result.data[0]["timeline_json"]
        return {}
    except Exception:
        return {}
