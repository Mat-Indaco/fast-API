from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def read_items():
    return [{"id": 1, "title": "Notebook"}, {"id": 2, "title": "Mouse"}]
