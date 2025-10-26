from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_database, supabase
from services.ai_agent import ai_content_service

api_router = APIRouter()


@api_router.get("/")
async def root():
    return {"message": "Quflux API v1"}


@api_router.get("/status")
async def status():
    return {"status": "ok", "version": "1.0.0"}


@api_router.get("/health")
async def health_check(db: AsyncSession = Depends(get_database)):
    """Comprehensive health check for all services."""
    health_status = {
        "status": "healthy",
        "services": {
            "database": "unknown",
            "supabase": "unknown",
            "ai_service": "unknown"
        }
    }
    
    # Check database connection
    try:
        await db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Supabase connection
    try:
        if supabase:
            # Simple test query to check Supabase connection
            result = supabase.table("cache_store").select("key").limit(1).execute()
            health_status["services"]["supabase"] = "healthy"
        else:
            health_status["services"]["supabase"] = "not configured"
    except Exception as e:
        health_status["services"]["supabase"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI service
    try:
        # Test AI service availability
        if ai_content_service.agent:
            health_status["services"]["ai_service"] = "healthy"
        else:
            health_status["services"]["ai_service"] = "unhealthy: agent not initialized"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["ai_service"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@api_router.post("/ai/test-caption")
async def test_ai_caption():
    """Test endpoint for AI caption generation."""
    try:
        caption = await ai_content_service.generate_caption(
            content_type="image",
            topic="technology",
            platform="twitter",
            tone="professional"
        )
        return {"caption": caption, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}