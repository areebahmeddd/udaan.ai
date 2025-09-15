from fastapi import APIRouter
from app.services.college_api import CollegeAPI
#from app.services.college_api import fetch_json, filter_data


router = APIRouter()
service = CollegeAPI()



# ---------------- ALL COLLEGES ----------------
@router.get("/all")
async def all_colleges():
    return await service.fetch("overall_participated.json")

@router.get("/all/nirf")
async def all_colleges_nirf():
    return await service.fetch("overall_ranking.json")

@router.get("/all/nirf/state={state}")
async def all_colleges_nirf_state(state: str):
    data = await service.fetch("overall_ranking.json")
    return service.filter_data(data, state=state)

@router.get("/all/nirf/city={city}")
async def all_colleges_nirf_city(city: str):
    data = await service.fetch("overall_ranking.json")
    return service.filter_data(data, city=city)


# ---------------- ENGINEERING ----------------
@router.get("/engineering_colleges")
async def engineering_colleges():
    return await service.fetch("engineering_participated.json")

@router.get("/engineering_colleges/nirf")
async def engineering_colleges_nirf():
    return await service.fetch("engineering_ranking.json")

@router.get("/engineering_colleges/state={state}")
async def engineering_colleges_state(state: str):
    data = await service.fetch("engineering_participated.json")
    return service.filter_data(data, state=state)

@router.get("/engineering_colleges/city={city}")
async def engineering_colleges_city(city: str):
    data = await service.fetch("engineering_participated.json")
    return service.filter_data(data, city=city)


# ---------------- MEDICAL ----------------
@router.get("/medical_colleges")
async def medical_colleges():
    return await service.fetch("medical_participated.json")

@router.get("/medical_colleges/nirf")
async def medical_colleges_nirf():
    return await service.fetch("medical_ranking.json")

@router.get("/medical_colleges/state={state}")
async def medical_colleges_state(state: str):
    data = await service.fetch("medical_participated.json")
    return service.filter_data(data, state=state)

@router.get("/medical_colleges/city={city}")
async def medical_colleges_city(city: str):
    data = await service.fetch("medical_participated.json")
    return service.filter_data(data, city=city)


# ---------------- MANAGEMENT ----------------
@router.get("/management_colleges")
async def management_colleges():
    return await service.fetch("management_participated.json")

@router.get("/management_colleges/nirf")
async def management_colleges_nirf():
    return await service.fetch("management_ranking.json")

@router.get("/management_colleges/state={state}")
async def management_colleges_state(state: str):
    data = await service.fetch("management_participated.json")
    return service.filter_data(data, state=state)

@router.get("/management_colleges/city={city}")
async def management_colleges_city(city: str):
    data = await service.fetch("management_participated.json")
    return service.filter_data(data, city=city)


# ---------------- PHARMACY ----------------
@router.get("/pharmacy_colleges")
async def pharmacy_colleges():
    return await service.fetch("pharmacy_participated.json")

@router.get("/pharmacy_colleges/nirf")
async def pharmacy_colleges_nirf():
    return await service.fetch("pharmacy_ranking.json")

@router.get("/pharmacy_colleges/state={state}")
async def pharmacy_colleges_state(state: str):
    data = await service.fetch("pharmacy_participated.json")
    return service.filter_data(data, state=state)

@router.get("/pharmacy_colleges/city={city}")
async def pharmacy_colleges_city(city: str):
    data = await service.fetch("pharmacy_participated.json")
    return service.filter_data(data, city=city)


# ---------------- DENTAL ----------------
@router.get("/dental_colleges")
async def dental_colleges():
    return await service.fetch("dental_participated.json")

@router.get("/dental_colleges/nirf")
async def dental_colleges_nirf():
    return await service.fetch("dental_ranking.json")

@router.get("/dental_colleges/state={state}")
async def dental_colleges_state(state: str):
    data = await service.fetch("dental_participated.json")
    return service.filter_data(data, state=state)

@router.get("/dental_colleges/city={city}")
async def dental_colleges_city(city: str):
    data = await service.fetch("dental_participated.json")
    return service.filter_data(data, city=city)


# ---------------- LAW ----------------
@router.get("/law_colleges/nirf")
async def law_colleges_nirf():
    return await service.fetch("law_ranking.json")


# ---------------- ARCHITECTURE ----------------
@router.get("/architecture_colleges")
async def architecture_colleges():
    return await service.fetch("architecture_participated.json")

@router.get("/architecture_colleges/nirf")
async def architecture_colleges_nirf():
    return await service.fetch("architecture_ranking.json")

@router.get("/architecture_colleges/state={state}")
async def architecture_colleges_state(state: str):
    data = await service.fetch("architecture_participated.json")
    return service.filter_data(data, state=state)

@router.get("/architecture_colleges/city={city}")
async def architecture_colleges_city(city: str):
    data = await service.fetch("architecture_participated.json")
    return service.filter_data(data, city=city)


# ---------------- RESEARCH ----------------
@router.get("/research_colleges")
async def research_colleges():
    return await service.fetch("research_ranking.json")

@router.get("/research_colleges/nirf")
async def research_colleges_nirf():
    return await service.fetch("research_ranking.json")

@router.get("/research_colleges/state={state}")
async def research_colleges_state(state: str):
    data = await service.fetch("research_ranking.json")
    return service.filter_data(data, state=state)

@router.get("/research_colleges/city={city}")
async def research_colleges_city(city: str):
    data = await service.fetch("research_ranking.json")
    return service.filter_data(data, city=city)


# ---------------- UNIVERSITIES ----------------
@router.get("/universities")
async def universities():
    return await service.fetch("university_ranking.json")

@router.get("/universities/state={state}")
async def universities_state(state: str):
    data = await service.fetch("university_ranking.json")
    return service.filter_data(data, state=state)

@router.get("/universities/city={city}")
async def universities_city(city: str):
    data = await service.fetch("university_ranking.json")
    return service.filter_data(data, city=city)


# ---------------- ALL COLLEGES (GENERIC) ----------------
@router.get("/colleges")
async def colleges():
    return await service.fetch("college_participated.json")

@router.get("/colleges/nirf")
async def colleges_nirf():
    return await service.fetch("college_ranking.json")

@router.get("/colleges/state={state}")
async def colleges_state(state: str):
    data = await service.fetch("college_participated.json")
    return service.filter_data(data, state=state)

@router.get("/colleges/city={city}")
async def colleges_city(city: str):
    data = await service.fetch("college_participated.json")
    return service.filter_data(data, city=city)


# ---------------- AGRICULTURE ----------------
@router.get("/agriculture_colleges")
async def agriculture_colleges():
    return await service.fetch("allAgriculture.json")

'''
@router.get("/engineering_colleges/nirf")
async def get_engineering_nirf():
    return await service.fetch("engineering_ranking.json")

@router.get("/medical_colleges/nirf")
async def get_medical_nirf():
    return await service.fetch("medical_ranking.json")

@router.get("/colleges/nirf")
async def get_overall_nirf():
    return await service.fetch("overall_ranking.json")


    '''


'''
from fastapi import APIRouter
from app.services.college_api import fetch_json, filter_data

router = APIRouter()

# ---------------- ROOT ----------------
@router.get("/")
def root():
    return {"message": "College API Wrapper running. Visit /docs for interactive API docs."}


# ---------------- ALL COLLEGES ----------------
@router.get("/all")
def all_colleges():
    return fetch_json("overall_participated.json")

@router.get("/all/nirf")
def all_colleges_nirf():
    return fetch_json("overall_ranking.json")

@router.get("/all/nirf/state={state}")
def all_colleges_nirf_state(state: str):
    return filter_data(fetch_json("overall_ranking.json"), state=state)

@router.get("/all/nirf/city={city}")
def all_colleges_nirf_city(city: str):
    return filter_data(fetch_json("overall_ranking.json"), city=city)


# ---------------- ENGINEERING ----------------
@router.get("/engineering_colleges")
def engineering_colleges():
    return fetch_json("engineering_participated.json")

@router.get("/engineering_colleges/nirf")
def engineering_colleges_nirf():
    return fetch_json("engineering_ranking.json")

@router.get("/engineering_colleges/state={state}")
def engineering_colleges_state(state: str):
    return filter_data(fetch_json("engineering_participated.json"), state=state)

@router.get("/engineering_colleges/city={city}")
def engineering_colleges_city(city: str):
    return filter_data(fetch_json("engineering_participated.json"), city=city)


# ---------------- MEDICAL ----------------
@router.get("/medical_colleges")
def medical_colleges():
    return fetch_json("medical_participated.json")

@router.get("/medical_colleges/nirf")
def medical_colleges_nirf():
    return fetch_json("medical_ranking.json")

@router.get("/medical_colleges/state={state}")
def medical_colleges_state(state: str):
    return filter_data(fetch_json("medical_participated.json"), state=state)

@router.get("/medical_colleges/city={city}")
def medical_colleges_city(city: str):
    return filter_data(fetch_json("medical_participated.json"), city=city)


# ---------------- MANAGEMENT ----------------
@router.get("/management_colleges")
def management_colleges():
    return fetch_json("management_participated.json")

@router.get("/management_colleges/nirf")
def management_colleges_nirf():
    return fetch_json("management_ranking.json")

@router.get("/management_colleges/state={state}")
def management_colleges_state(state: str):
    return filter_data(fetch_json("management_participated.json"), state=state)

@router.get("/management_colleges/city={city}")
def management_colleges_city(city: str):
    return filter_data(fetch_json("management_participated.json"), city=city)


# ---------------- PHARMACY ----------------
@router.get("/pharmacy_colleges")
def pharmacy_colleges():
    return fetch_json("pharmacy_participated.json")

@router.get("/pharmacy_colleges/nirf")
def pharmacy_colleges_nirf():
    return fetch_json("pharmacy_ranking.json")

@router.get("/pharmacy_colleges/state={state}")
def pharmacy_colleges_state(state: str):
    return filter_data(fetch_json("pharmacy_participated.json"), state=state)

@router.get("/pharmacy_colleges/city={city}")
def pharmacy_colleges_city(city: str):
    return filter_data(fetch_json("pharmacy_participated.json"), city=city)


# ---------------- DENTAL ----------------
@router.get("/dental_colleges")
def dental_colleges():
    return fetch_json("dental_participated.json")

@router.get("/dental_colleges/nirf")
def dental_colleges_nirf():
    return fetch_json("dental_ranking.json")

@router.get("/dental_colleges/state={state}")
def dental_colleges_state(state: str):
    return filter_data(fetch_json("dental_participated.json"), state=state)

@router.get("/dental_colleges/city={city}")
def dental_colleges_city(city: str):
    return filter_data(fetch_json("dental_participated.json"), city=city)


# ---------------- LAW ----------------
@router.get("/law_colleges/nirf")
def law_colleges_nirf():
    return fetch_json("law_ranking.json")


# ---------------- ARCHITECTURE ----------------
@router.get("/architecture_colleges")
def architecture_colleges():
    return fetch_json("architecture_participated.json")

@router.get("/architecture_colleges/nirf")
def architecture_colleges_nirf():
    return fetch_json("architecture_ranking.json")

@router.get("/architecture_colleges/state={state}")
def architecture_colleges_state(state: str):
    return filter_data(fetch_json("architecture_participated.json"), state=state)

@router.get("/architecture_colleges/city={city}")
def architecture_colleges_city(city: str):
    return filter_data(fetch_json("architecture_participated.json"), city=city)


# ---------------- RESEARCH ----------------
@router.get("/research_colleges")
def research_colleges():
    return fetch_json("research_ranking.json")

@router.get("/research_colleges/nirf")
def research_colleges_nirf():
    return fetch_json("research_ranking.json")

@router.get("/research_colleges/state={state}")
def research_colleges_state(state: str):
    return filter_data(fetch_json("research_ranking.json"), state=state)

@router.get("/research_colleges/city={city}")
def research_colleges_city(city: str):
    return filter_data(fetch_json("research_ranking.json"), city=city)


# ---------------- UNIVERSITIES ----------------
@router.get("/universities")
def universities():
    return fetch_json("university_ranking.json")

@router.get("/universities/state={state}")
def universities_state(state: str):
    return filter_data(fetch_json("university_ranking.json"), state=state)

@router.get("/universities/city={city}")
def universities_city(city: str):
    return filter_data(fetch_json("university_ranking.json"), city=city)


# ---------------- ALL COLLEGES (GENERIC) ----------------
@router.get("/colleges")
def colleges():
    return fetch_json("college_participated.json")

@router.get("/colleges/nirf")
def colleges_nirf():
    return fetch_json("college_ranking.json")

@router.get("/colleges/state={state}")
def colleges_state(state: str):
    return filter_data(fetch_json("college_participated.json"), state=state)

@router.get("/colleges/city={city}")
def colleges_city(city: str):
    return filter_data(fetch_json("college_participated.json"), city=city)


# ---------------- AGRICULTURE ----------------
@router.get("/agriculture_colleges")
def agriculture_colleges():
    return fetch_json("allAgriculture.json")
'''