from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/")
async def getUser():
	return {'user': 'authenticated'}