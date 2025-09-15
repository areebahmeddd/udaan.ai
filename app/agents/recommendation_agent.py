import os
import json
import google.generativeai as genai
from app.db import get_supabase
from app.models import Profile
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


async def fetch_recommendations(user_id: str, quiz_id: str) -> Dict[str, Any]:
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

    if profile.class_level == 9 or profile.class_level == 10:
        return await create_streams(profile, quiz_data)
    else:
        return await create_careers(profile, quiz_data)


async def create_streams(profile: Profile, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
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

    prompt = f"""You are a career guidance expert for Indian students. You need to recommend academic streams for a Class {profile.class_level} student.

STUDENT PROFILE:
- Class: {profile.class_level}
- Age: {profile.age}
- Language: {profile.language_preference}
- Budget: {profile.budget_range}
- Reservation Category: {profile.reservation_category}
- Mobility: {profile.mobility}
- Location: {profile.location}

QUIZ RESPONSES:
{json.dumps(quiz_qa, indent=2)}

Based on this information, recommend the top 3 academic streams (Science PCM, Science PCB, Commerce with Math, Commerce, Arts/Humanities, etc.)
that would be best suited for this student. Also provide detailed reasons for each recommendation.

Return the response as a valid JSON object with the following structure:
{{
  "streams": ["Stream 1", "Stream 2", "Stream 3"],
  "reasons": {{
    "Stream 1": "Detailed reason for Stream 1 recommendation",
    "Stream 2": "Detailed reason for Stream 2 recommendation",
    "Stream 3": "Detailed reason for Stream 3 recommendation"
  }},
  "message": "A personalized message about these recommendations"
}}
"""

    response = model.generate_content(prompt)

    try:
        recommendations = json.loads(response.text.strip())

        streams = recommendations.get("streams", [])
        reasons = recommendations.get("reasons", {})
        message = recommendations.get(
            "message",
            "These streams align with your interests, strengths, and preferences",
        )

        detailed_paths = {}
        for stream in streams:
            detailed_paths[stream] = {
                "courses": fetch_courses(stream),
                "example_careers": fetch_careers(stream),
            }

        return {
            "streams": streams,
            "reasons": reasons,
            "detailed_paths": detailed_paths,
            "message": message,
        }
    except (json.JSONDecodeError, KeyError):
        raise Exception("invalid gemini response")


async def create_careers(profile: Profile, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
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

    prompt = f"""You are a career guidance expert for Indian students. You need to recommend specific courses and careers for a Class {profile.class_level} student with stream {profile.stream}.

STUDENT PROFILE:
- Class: {profile.class_level}
- Stream: {profile.stream}
- Age: {profile.age}
- Language: {profile.language_preference}
- Budget: {profile.budget_range}
- Reservation Category: {profile.reservation_category}
- Mobility: {profile.mobility}
- Location: {profile.location}

QUIZ RESPONSES:
{json.dumps(quiz_qa, indent=2)}

Based on this information, recommend the top 3 specific courses and related careers that would be best suited for this student.
Also provide detailed reasons for each recommendation.

Return the response as a valid JSON object with the following structure:
{{
  "courses": ["Course 1", "Course 2", "Course 3"],
  "careers": {{
    "Course 1": ["Career 1", "Career 2", "Career 3"],
    "Course 2": ["Career 1", "Career 2", "Career 3"],
    "Course 3": ["Career 1", "Career 2", "Career 3"]
  }},
  "reasons": {{
    "Course 1": "Detailed reason for Course 1 recommendation",
    "Course 2": "Detailed reason for Course 2 recommendation",
    "Course 3": "Detailed reason for Course 3 recommendation"
  }},
  "message": "A personalized message about these recommendations"
}}
"""

    response = model.generate_content(prompt)

    try:
        recommendations = json.loads(response.text.strip())

        courses = recommendations.get("courses", [])
        careers = recommendations.get("careers", {})
        reasons = recommendations.get("reasons", {})
        message = recommendations.get(
            "message",
            "These specialized paths align with your specific interests and aptitudes",
        )

        return {
            "courses": courses,
            "careers": careers,
            "reasons": reasons,
            "additional_resources": fetch_resources(careers),
            "message": message,
        }
    except (json.JSONDecodeError, KeyError):
        raise Exception("invalid gemini response")


def fetch_courses(stream: str) -> List[str]:
    stream_courses = {
        "Science (PCM)": ["B.Tech", "B.Sc Mathematics/Physics", "BCA", "B.Arch"],
        "Science (PCB)": ["MBBS", "B.Sc Biology", "B.Pharmacy", "B.Sc Nursing"],
        "Science with Computer Science": [
            "B.Tech CSE",
            "BCA",
            "B.Sc IT",
            "B.Sc Computer Science",
        ],
        "Commerce with Mathematics": [
            "B.Com",
            "BBA",
            "CA Foundation",
            "Actuarial Science",
        ],
        "Commerce with Business Studies": [
            "B.Com",
            "BBA",
            "Hotel Management",
            "Retail Management",
        ],
        "Commerce": ["B.Com", "BBA", "Banking & Insurance", "Office Management"],
        "Arts with Fine Arts": ["BA Fine Arts", "Design", "Animation", "Visual Arts"],
        "Arts with Languages/Mass Comm": [
            "BA in Languages",
            "Mass Communication",
            "Journalism",
            "Content Creation",
        ],
        "Arts/Humanities": ["BA", "B.Ed", "Law", "Social Work"],
        "Vocational/Skill-based courses": [
            "Diploma",
            "ITI",
            "Paramedical",
            "Hospitality",
        ],
    }

    return stream_courses.get(
        stream, ["Undergraduate Degree", "Diploma", "Certificate Course"]
    )


def fetch_careers(stream: str) -> List[str]:
    stream_careers = {
        "Science (PCM)": ["Engineer", "Scientist", "IT Professional", "Professor"],
        "Science (PCB)": [
            "Doctor",
            "Pharmacist",
            "Biologist",
            "Healthcare Professional",
        ],
        "Science with Computer Science": [
            "Software Developer",
            "Data Scientist",
            "System Analyst",
            "AI/ML Engineer",
        ],
        "Commerce with Mathematics": [
            "Chartered Accountant",
            "Investment Banker",
            "Actuary",
            "Financial Analyst",
        ],
        "Commerce with Business Studies": [
            "Business Manager",
            "Marketing Executive",
            "Entrepreneur",
            "Consultant",
        ],
        "Commerce": [
            "Accountant",
            "Bank Professional",
            "Administrator",
            "Tax Consultant",
        ],
        "Arts with Fine Arts": [
            "Graphic Designer",
            "Artist",
            "Art Director",
            "UI/UX Designer",
        ],
        "Arts with Languages/Mass Comm": [
            "Journalist",
            "Content Writer",
            "Translator",
            "Public Relations",
        ],
        "Arts/Humanities": [
            "Teacher",
            "Civil Services",
            "Social Worker",
            "Content Developer",
        ],
        "Vocational/Skill-based courses": [
            "Technician",
            "Skilled Professional",
            "Self-employed",
            "Service Provider",
        ],
    }

    return stream_careers.get(
        stream, ["Professional", "Entrepreneur", "Government Sector"]
    )


def fetch_resources(
    careers: Dict[str, List[str]],
) -> Dict[str, List[Dict[str, str]]]:
    resources = {}

    for course, career_list in careers.items():
        course_resources = []

        course_resources.append(
            {
                "type": "course_info",
                "title": f"About {course}",
                "description": "Degree details, duration, and eligibility",
            }
        )

        if "Government" in course or any(c in course for c in ["B.Sc", "B.A", "B.Com"]):
            course_resources.append(
                {
                    "type": "scholarship",
                    "title": "Government Scholarships",
                    "description": "Scholarships for eligible students in government colleges",
                }
            )

        if "B.Tech" in course or "Engineering" in course:
            course_resources.append(
                {
                    "type": "exam",
                    "title": "JEE and State Engineering Entrance Exams",
                    "description": "Information about engineering entrance examinations",
                }
            )
        elif "MBBS" in course or "Medical" in course:
            course_resources.append(
                {
                    "type": "exam",
                    "title": "NEET Examination",
                    "description": "Information about medical entrance examination",
                }
            )

        career_specific = []
        for career in career_list:
            if "Engineer" in career or "Developer" in career:
                career_specific.append(
                    {
                        "type": "career_path",
                        "title": f"{career} Career Path",
                        "description": f"Skills, certifications, and growth opportunities in {career}",
                    }
                )
            elif "Doctor" in career or "Medical" in career:
                career_specific.append(
                    {
                        "type": "career_path",
                        "title": "Medical Career Specializations",
                        "description": "Options for specialization and career growth in medicine",
                    }
                )

        if career_specific:
            course_resources.extend(career_specific[:2])

        resources[course] = course_resources

    return resources
