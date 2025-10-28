"""
AI content generation tasks for Celery
"""
from celery_app import celery_app
from services.ai_agent import ai_content_service
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_caption_task(self, content_type: str, topic: str, platform: str, tone: str = "professional") -> Dict[str, Any]:
    """
    Celery task to generate social media captions.
    
    Args:
        content_type: Type of content (image, video, link, text)
        topic: Main topic or theme
        platform: Target platform
        tone: Desired tone
    
    Returns:
        Dict with generated caption
    """
    try:
        logger.info(f"Generating caption for {content_type} about {topic} for {platform}")
        
        caption = await ai_content_service.generate_caption(
            content_type=content_type,
            topic=topic,
            platform=platform,
            tone=tone
        )
        
        result = {
            "caption": caption,
            "content_type": content_type,
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "status": "success"
        }
        
        logger.info(f"Successfully generated caption: {caption[:50]}...")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to generate caption: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "content_type": content_type,
            "topic": topic,
            "platform": platform
        }


@celery_app.task(bind=True)
def generate_hashtags_task(self, content: str, platform: str, max_hashtags: int = 10) -> Dict[str, Any]:
    """
    Celery task to generate hashtag suggestions.
    
    Args:
        content: The post content to analyze
        platform: Target platform
        max_hashtags: Maximum number of hashtags
    
    Returns:
        Dict with suggested hashtags
    """
    try:
        logger.info(f"Generating hashtags for {platform} content")
        
        hashtags = await ai_content_service.get_hashtag_suggestions(
            content=content,
            platform=platform,
            max_hashtags=max_hashtags
        )
        
        result = {
            "hashtags": hashtags,
            "platform": platform,
            "max_hashtags": max_hashtags,
            "status": "success"
        }
        
        logger.info(f"Successfully generated {len(hashtags)} hashtags")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to generate hashtags: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "platform": platform
        }


@celery_app.task(bind=True)
def generate_image_task(self, prompt: str, style: str = "realistic", dimensions: str = "1024x1024") -> Dict[str, Any]:
    """
    Celery task to generate images using AI.
    
    Args:
        prompt: Description of the image to generate
        style: Image style
        dimensions: Image dimensions
    
    Returns:
        Dict with generated image URL
    """
    try:
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        
        image_url = await ai_content_service.generate_image(
            prompt=prompt,
            style=style,
            dimensions=dimensions
        )
        
        result = {
            "image_url": image_url,
            "prompt": prompt,
            "style": style,
            "dimensions": dimensions,
            "status": "success"
        }
        
        logger.info(f"Successfully generated image: {image_url}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to generate image: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "prompt": prompt
        }