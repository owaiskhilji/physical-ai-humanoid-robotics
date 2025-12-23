from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from prometheus_client import make_asgi_app
from fastapi_utils.tasks import repeat_every

from src.api.v1.chat import router as chat_router
from src.api.v1.content import router as content_router
from src.core.config import settings
from src.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    logging.info("Application starting up...")
    await init_db()

    # Shutdown
    yield

    logging.info("Application shutting down...")


from prometheus_client import Counter, Histogram, Gauge
import time

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_SESSIONS = Gauge(
    'active_chat_sessions',
    'Number of active chat sessions'
)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Create rate limiter
    limiter = Limiter(key_func=get_remote_address)

    app = FastAPI(
        title="RAG Chatbot API",
        description="API for RAG-based chatbot integrated with textbook content",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    app.include_router(content_router, prefix="/api/v1", tags=["content"])

    # Add Prometheus metrics middleware
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    @app.middleware("http")
    async def add_monitoring_middleware(request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)

        return response

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "rag-chatbot-api"}

    @app.get("/")
    async def root():
        return {"message": "RAG Chatbot API", "version": "1.0.0"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)