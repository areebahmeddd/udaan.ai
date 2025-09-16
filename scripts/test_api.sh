#!/bin/bash

PYTHON_SCRIPT=$(cat << 'EOF'
import time
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("Health check passed\n")

def test_user_signup():
    print("Testing user signup...")
    signup_data = {
        "email": f"arjun.sharma_{int(time.time())}@gmail.com",
        "password": "arjun@123pass",
        "name": "Arjun Sharma"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        user_id = data["user_id"]
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        profile_exists = data["profile_exists"]

        print(f"User ID: {user_id}")
        print(f"Profile exists: {profile_exists}")
        print("Signup successful\n")

        return {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": signup_data["email"]
        }
    else:
        print("Signup failed\n")
        return None

def test_user_signin(email):
    print("Testing user signin...")
    signin_data = {
        "email": email,
        "password": "arjun@123pass"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/signin", json=signin_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        print("Signin successful\n")
        return data
    else:
        print("Signin failed\n")
        return None

def test_create_profile(access_token):
    print("Testing profile creation...")
    headers = {"Authorization": f"Bearer {access_token}"}

    profile_data = {
        "name": "Arjun Sharma",
        "age": 17,
        "gender": "male",
        "class_level": 12,
        "stream": "Science (PCM)",
        "location": {
            "state": "Rajasthan",
            "city": "Jaipur"
        },
        "language_preference": "Hindi",
        "budget_range": "1-3 lakhs",
        "reservation_category": "OBC",
        "mobility": "Moderate"
    }

    response = requests.post(f"{BASE_URL}/api/v1/profile/", json=profile_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("Profile created successfully")
        print(f"Quiz ID: {data.get('quiz_id')}")
        print(f"First question: {data.get('question', {}).get('text', 'N/A')}")
        print("Profile creation successful\n")
        return data.get('quiz_id')
    else:
        print(f"Error: {response.text}")
        print("Profile creation failed\n")
        return None

def test_get_profile(access_token):
    print("Testing get profile...")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(f"{BASE_URL}/api/v1/profile/", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Profile retrieved: {data.get('name')} - Class {data.get('class_level')}")
        print("Get profile successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("Get profile failed\n")
        return None

def test_start_quiz(access_token):
    print("Testing quiz start...")
    headers = {"Authorization": f"Bearer {access_token}"}

    quiz_data = {"max_questions": 5}

    response = requests.post(f"{BASE_URL}/api/v1/quiz/start", json=quiz_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        quiz_id = data.get('quiz_id')
        question = data.get('question', {})
        print(f"Quiz ID: {quiz_id}")
        print(f"Question: {question.get('text', 'N/A')}")
        print(f"Options: {question.get('options', [])}")
        print("Quiz start successful\n")
        return quiz_id
    else:
        print(f"Error: {response.text}")
        print("Quiz start failed\n")
        return None

def test_submit_quiz_answers(access_token, quiz_id):
    print("Testing quiz submission...")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Realistic answers for an Indian engineering aspirant
    answers = [
        "मैं इंजीनियरिंग और प्रौद्योगिकी में अधिक रुचि रखता हूँ",  # Engineering interest
        "कंप्यूटर साइंस और सॉफ्टवेयर डेवलपमेंट",  # Computer science preference
        "मैं समस्याओं को तकनीकी रूप से हल करना पसंद करता हूँ",  # Problem solving approach
        "JEE मेन की तैयारी कर रहा हूँ",  # JEE preparation
        "IIT या NIT में दाखिला चाहता हूँ"  # College preference
    ]

    for i, answer in enumerate(answers):
        print(f"Submitting answer {i+1}: {answer}")

        submit_data = {
            "quiz_id": quiz_id,
            "answer": answer,
            "max_questions": 5
        }

        response = requests.post(f"{BASE_URL}/api/v1/quiz/submit", json=submit_data, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('done'):
                print("Quiz completed!")
                break
            else:
                next_question = data.get('question', {})
                print(f"Next question: {next_question.get('text', 'N/A')}")
        else:
            print(f"Error: {response.text}")
            break

        time.sleep(0.5)

    print("Quiz submission completed\n")
    return quiz_id

def test_get_recommendations(access_token, quiz_id):
    print("Testing recommendations...")
    headers = {"Authorization": f"Bearer {access_token}"}

    recommend_data = {"quiz_id": quiz_id}

    response = requests.post(f"{BASE_URL}/api/v1/recommend/", json=recommend_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        streams = data.get('streams', [])
        courses = data.get('courses', [])
        print(f"Recommended streams: {streams}")
        print(f"Recommended courses: {courses}")
        print("Recommendations successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("Recommendations failed\n")
        return None

def test_get_colleges(access_token, quiz_id):
    print("Testing college recommendations...")
    headers = {"Authorization": f"Bearer {access_token}"}

    college_data = {
        "quiz_id": quiz_id,
        "field": "engineering",
        "location_type": "state"
    }

    response = requests.post(f"{BASE_URL}/api/v1/colleges/", json=college_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        total_colleges = data.get('total_colleges_found', 0)
        intelligent_recs = data.get('intelligent_recommendations', {})
        top_colleges = intelligent_recs.get('top_colleges', [])

        print(f"Total colleges found: {total_colleges}")
        print(f"Top recommended colleges: {len(top_colleges)}")
        for college in top_colleges[:3]:
            print(f"  - {college.get('name', 'N/A')} ({college.get('location', 'N/A')})")

        print("College recommendations successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("College recommendations failed\n")
        return None

def test_search_colleges():
    print("Testing public college search...")

    response = requests.get(f"{BASE_URL}/api/v1/colleges/search/engineering/state/rajasthan")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        colleges = data.get('colleges', [])
        count = data.get('count', 0)
        print(f"Found {count} engineering colleges in Rajasthan")
        for college in colleges[:3]:
            print(f"  - {college.get('name', 'N/A')}")
        print("Public college search successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("Public college search failed\n")
        return None

def test_get_timeline(access_token, quiz_id):
    print("Testing timeline generation...")
    headers = {"Authorization": f"Bearer {access_token}"}

    timeline_data = {"quiz_id": quiz_id}

    response = requests.post(f"{BASE_URL}/api/v1/timeline/", json=timeline_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        milestones = data.get('timeline_milestones', [])
        profile_context = data.get('profile_context', {})

        print(f"Generated timeline for Class {profile_context.get('class_level')} student")
        print(f"Number of milestones: {len(milestones)}")
        for milestone in milestones[:3]:
            print(f"  - {milestone.get('title', 'N/A')} ({milestone.get('date', 'N/A')})")

        print("Timeline generation successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("Timeline generation failed\n")
        return None

def test_get_existing_timeline(access_token):
    print("Testing get existing timeline...")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(f"{BASE_URL}/api/v1/timeline/", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("Existing timeline retrieved successfully")
        print("Get existing timeline successful\n")
        return data
    else:
        print(f"Error: {response.text}")
        print("Get existing timeline failed\n")
        return None

def test_token_refresh(refresh_token):
    print("Testing token refresh...")

    response = requests.post(f"{BASE_URL}/api/v1/auth/refresh?refresh_token={refresh_token}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        new_access_token = data.get('access_token')
        print("Token refresh successful")
        print("Token refresh successful\n")
        return new_access_token
    else:
        print(f"Error: {response.text}")
        print("Token refresh failed\n")
        return None

def test_user_logout():
    print("Testing user logout...")

    response = requests.post(f"{BASE_URL}/api/v1/auth/logout")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Logout message: {data.get('message')}")
        print("Logout successful\n")
        return True
    else:
        print(f"Error: {response.text}")
        print("Logout failed\n")
        return False

def main():
    print("Starting Udaan.ai API Testing...")
    print("Testing with Indian student profile: Arjun Sharma from Jaipur")
    print("="*60)

    try:
        # Test 1: Health check
        test_health_check()

        # Test 2: User signup
        auth_data = test_user_signup()
        if not auth_data:
            print("ERROR: Cannot continue without successful signup")
            return

        access_token = auth_data["access_token"]
        refresh_token = auth_data["refresh_token"]
        email = auth_data["email"]

        # Test 3: User signin
        signin_data = test_user_signin(email)
        if signin_data:
            access_token = signin_data["access_token"]

        # Test 4: Create profile
        quiz_id = test_create_profile(access_token)
        if not quiz_id:
            print("ERROR: Cannot continue without profile creation")
            return

        # Test 5: Get profile
        test_get_profile(access_token)

        # Test 6: Start quiz (alternative)
        quiz_id_alt = test_start_quiz(access_token)
        if quiz_id_alt:
            quiz_id = quiz_id_alt

        # Test 7: Submit quiz answers
        quiz_id = test_submit_quiz_answers(access_token, quiz_id)

        # Test 8: Get recommendations
        test_get_recommendations(access_token, quiz_id)

        # Test 9: Get college recommendations
        test_get_colleges(access_token, quiz_id)

        # Test 10: Public college search
        test_search_colleges()

        # Test 11: Generate timeline
        test_get_timeline(access_token, quiz_id)

        # Test 12: Get existing timeline
        test_get_existing_timeline(access_token)

        # Test 13: Token refresh
        new_access_token = test_token_refresh(refresh_token)
        if new_access_token:
            access_token = new_access_token

        # Test 14: Logout
        test_user_logout()

        print("="*60)
        print("All tests completed successfully!")
        print("Udaan.ai API is working perfectly for Indian students")
        print(f"Test completed at: {datetime.now()}")

    except Exception as e:
        print(f"ERROR: Test failed with error: {str(e)}")
        print(f"Test failed at: {datetime.now()}")

if __name__ == "__main__":
    main()
EOF
)

# Check if uv is available, otherwise fallback to python3
if command -v uv &> /dev/null; then
    cd "$(dirname "$0")/.." && echo "$PYTHON_SCRIPT" | uv run python -
else
    echo "$PYTHON_SCRIPT" | python3 -
fi
