from ag2_example.api.routes.chat import router as chat_router
from ag2_example.api.routes.health import router as health_router
from ag2_example.api.routes.notes import router as notes_router

routers = [health_router, notes_router, chat_router]

__all__ = ["routers"]
