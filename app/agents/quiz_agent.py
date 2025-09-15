import os
import json
import uuid
import google.generativeai as genai
from app.db import get_supabase
from app.models import Profile, Quiz, QuizCreate
from app.agents.profile_agent import get_profile
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


async def generate_question(user_id: str) -> Dict[str, Any]:
    profile = await get_profile(user_id)
    if not profile:
        raise Exception("profile not found")

    quiz_id = str(uuid.uuid4())
    question = await call_gemini(profile, [])
    quiz_data = {"history": [], "current_question": question, "question_count": 1}
    quiz_create = QuizCreate(user_id=user_id, quiz_json=quiz_data, source="gemini")

    await save_quiz(quiz_id, quiz_create)

    return {
        "quiz_id": quiz_id,
        "question": question,
        "question_number": 1,
        "total_questions": 10,
        "class_level": profile.class_level,
    }


async def submit_answer(
    quiz_id: str, answer: str, max_questions: int = 10
) -> Dict[str, Any]:
    quiz = await get_quiz(quiz_id)
    if not quiz:
        raise Exception("quiz not found")

    quiz_data = quiz.quiz_json
    current_question = quiz_data["current_question"]
    history = quiz_data.get("history", [])
    question_count = quiz_data.get("question_count", 1)

    history.append(
        {
            "question": current_question,
            "answer": answer,
            "question_number": question_count,
        }
    )

    if question_count >= max_questions:
        await update_history(quiz_id, history)
        return {
            "done": True,
            "total_questions": max_questions,
            "question_count": question_count,
        }

    profile = await get_profile(quiz.user_id)
    next_question = await call_gemini(profile, history)
    new_quiz_data = {
        "history": history,
        "current_question": next_question,
        "question_count": question_count + 1,
    }

    await update_data(quiz_id, new_quiz_data)

    return {
        "done": False,
        "question": next_question,
        "question_number": question_count + 1,
        "total_questions": max_questions,
        "question_count": question_count + 1,
    }


async def call_gemini(profile: Profile, history: List[Dict]) -> Dict[str, Any]:
    prompt = build_prompt(profile, history)
    response = model.generate_content(prompt)

    try:
        question_json = json.loads(response.text.strip())
        return validate_question(question_json)
    except (json.JSONDecodeError, KeyError):
        raise Exception("invalid gemini response")


def build_prompt(profile: Profile, history: List[Dict]) -> str:
    context = {
        "class_level": profile.class_level,
        "stream": profile.stream,
        "age": profile.age,
        "language_preference": profile.language_preference,
        "budget_range": profile.budget_range,
        "reservation_category": profile.reservation_category,
        "mobility": profile.mobility,
        "location": profile.location,
    }

    if history:
        previous_qa = "\\n".join(
            [
                f"Q{item['question_number']}: {item['question']['text']} - Answer: {item['answer']}"
                for item in history
            ]
        )
        context_text = f"Previous Q&A: {previous_qa}"
    else:
        context_text = "This is the first question"

    language = profile.language_preference
    prompt = f"""You are a career guidance expert for Indian students. Generate exactly ONE personalized question in JSON format.

Student Context: {json.dumps(context)}
{context_text}

Requirements:
- Generate a single question that is VERY SPECIFIC and PERSONALIZED based on the student's profile and previous answers
- Make it like Akinator - each question should narrow down interests/aptitudes significantly
- Use {language} language
- Return ONLY valid JSON in this exact format:

{{
  "id": "q{len(history) + 1}",
  "type": "mcq",
  "text": "your personalized question here",
  "options": ["option1", "option2", "option3", "option4"],
  "language": "{language}"
}}

The question should be:
- Highly specific to their profile (class, location, budget, etc.)
- Different from generic career questions
- Focused on discovering unique interests/skills
- Progressive based on previous answers"""

    return prompt


def validate_question(question_json: Dict) -> Dict[str, Any]:
    required_fields = ["id", "type", "text", "options", "language"]
    for field in required_fields:
        if field not in question_json:
            raise ValueError(f"missing field: {field}")

    if (
        not isinstance(question_json["options"], list)
        or len(question_json["options"]) != 4
    ):
        raise ValueError("options must be a list of 4 items")

    return question_json


async def save_quiz(quiz_id: str, quiz_create: QuizCreate):
    supabase = get_supabase()
    quiz_dict = quiz_create.model_dump()
    quiz_dict["id"] = quiz_id

    supabase.table("quizzes").insert(quiz_dict).execute()


async def get_quiz(quiz_id: str) -> Quiz:
    supabase = get_supabase()
    result = supabase.table("quizzes").select("*").eq("id", quiz_id).execute()

    if result.data:
        return Quiz(**result.data[0])
    return None


async def update_data(quiz_id: str, quiz_data: Dict[str, Any]):
    supabase = get_supabase()
    supabase.table("quizzes").update({"quiz_json": quiz_data}).eq(
        "id", quiz_id
    ).execute()


async def update_history(quiz_id: str, history: List[Dict]):
    supabase = get_supabase()
    quiz_data = {"history": history, "completed": True}
    supabase.table("quizzes").update({"quiz_json": quiz_data}).eq(
        "id", quiz_id
    ).execute()
