import httpx

BASE_URL = "https://raw.githubusercontent.com/Clueless-Community/collegeAPI/main/data"



class CollegeAPI:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=15.0)

    def _build_url(self, filename: str) -> str:
        return f"{self.base_url}/{filename}"

    async def fetch(self, filename: str):
        url = self._build_url(filename)
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.json()
    def filter_data(self, data, state=None, city=None):
        """
        Filters the data by state or city.
        Args:
            data (list): List of college dicts.
            state (str, optional): State to filter by.
            city (str, optional): City to filter by.
        Returns:
            list: Filtered list of colleges.
        """
        if state:
            return [item for item in data if item.get("state", "").lower() == state.lower()]
        if city:
            return [item for item in data if item.get("city", "").lower() == city.lower()]
        return data