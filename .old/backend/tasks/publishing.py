"""
Publishing tasks for Celery
"""
from celery import current_task
from celery_app import celery_app
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def publish_post_task(self, schedule_id: str, platform: str) -> Dict[str, Any]:
    """
    Celery task to publish a post to a specific platform.
    
    Args:
        schedule_id: The schedule ID to publish
        platform: Target platform (twitter, linkedin, instagram, facebook)
    
    Returns:
        Dict with publication result
    """
    try:
        logger.info(f"Publishing post for schedule {schedule_id} to {platform}")
        
        # This will be implemented with actual publishing logic
        # For now, return a success placeholder
        result = {
            "schedule_id": schedule_id,
            "platform": platform,
            "status": "success",
            "platform_post_id": f"mock_post_id_{schedule_id}_{platform}",
            "published_at": "2024-01-01T12:00:00Z"
        }
        
        logger.info(f"Successfully published to {platform}: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to publish to {platform}: {exc}")
        
        # Exponential backoff retry
        countdown = min(
            60 * (2 ** self.request.retries),  # 60s, 120s, 240s
            300  # Max 5 minutes
        )
        
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(bind=True)
def publish_to_multiple_platforms_task(self, schedule_id: str, platforms: list) -> Dict[str, Any]:
    """
    Celery task to publish a post to multiple platforms.
    
    Args:
        schedule_id: The schedule ID to publish
        platforms: List of target platforms
    
    Returns:
        Dict with publication results for all platforms
    """
    results = {}
    
    for platform in platforms:
        try:
            # Call individual platform publishing task
            result = publish_post_task.delay(schedule_id, platform)
            results[platform] = {
                "task_id": result.id,
                "status": "queued"
            }
        except Exception as e:
            results[platform] = {
                "status": "failed",
                "error": str(e)
            }
    
    return {
        "schedule_id": schedule_id,
        "platforms": results,
        "overall_status": "processing"
    }