"""
Notification tasks for Celery
"""
from celery_app import celery_app
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def send_email_notification_task(self, user_email: str, subject: str, content: str, template: str = "default") -> Dict[str, Any]:
    """
    Celery task to send email notifications.
    
    Args:
        user_email: Recipient email address
        subject: Email subject
        content: Email content
        template: Email template to use
    
    Returns:
        Dict with send result
    """
    try:
        logger.info(f"Sending email notification to {user_email}")
        
        # This will be implemented with SendGrid integration
        # For now, return a success placeholder
        result = {
            "user_email": user_email,
            "subject": subject,
            "template": template,
            "status": "sent",
            "message_id": f"mock_message_id_{user_email}"
        }
        
        logger.info(f"Successfully sent email to {user_email}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to send email to {user_email}: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "user_email": user_email,
            "subject": subject
        }


@celery_app.task(bind=True)
def send_publication_success_notification_task(self, user_email: str, post_title: str, platform: str, platform_post_id: str) -> Dict[str, Any]:
    """
    Celery task to send publication success notifications.
    
    Args:
        user_email: User email address
        post_title: Title of the published post
        platform: Platform where post was published
        platform_post_id: ID of the post on the platform
    
    Returns:
        Dict with notification result
    """
    subject = f"Post Published Successfully on {platform.title()}"
    content = f"""
    Your post "{post_title}" has been successfully published on {platform.title()}.
    
    Platform Post ID: {platform_post_id}
    
    Thank you for using Quflux!
    """
    
    return send_email_notification_task.delay(
        user_email=user_email,
        subject=subject,
        content=content,
        template="publication_success"
    )


@celery_app.task(bind=True)
def send_publication_failure_notification_task(self, user_email: str, post_title: str, platform: str, error_message: str) -> Dict[str, Any]:
    """
    Celery task to send publication failure notifications.
    
    Args:
        user_email: User email address
        post_title: Title of the failed post
        platform: Platform where publication failed
        error_message: Error message
    
    Returns:
        Dict with notification result
    """
    subject = f"Post Publication Failed on {platform.title()}"
    content = f"""
    Your post "{post_title}" failed to publish on {platform.title()}.
    
    Error: {error_message}
    
    Please check your platform connection and try again.
    
    Quflux Support Team
    """
    
    return send_email_notification_task.delay(
        user_email=user_email,
        subject=subject,
        content=content,
        template="publication_failure"
    )