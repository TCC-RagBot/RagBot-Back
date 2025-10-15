from .application import create_app
from .config.constants import DEFAULT_HOST, DEFAULT_PORT
from .config.settings import settings
import uvicorn

app = create_app()

if __name__ == "__main__":
    
    uvicorn.run(
        "app.main:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        timeout_keep_alive=60,  
        timeout_graceful_shutdown=30
    )