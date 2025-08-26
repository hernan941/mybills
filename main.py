from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routes import create_routes
from app.database import close_database
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mybills.log')
    ]
)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI"""

    @asynccontextmanager
    async def lifespan(_):
        yield
        logger.info("Cerrando mybills...")
        close_database()
        logger.info("Aplicación cerrada correctamente")
    
    app = FastAPI(
        title="MyBills",
        description="Gestión personal de gastos e ingresos",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
    )
    
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    create_routes(app)
    
    return app

app = create_app()
