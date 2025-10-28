"""
Platform connections API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.database import get_database
from middleware.auth import get_current_user
from models.user import User
from models.platform_connection import PlatformConnection
from services.platform_connection_service import platform_connection_service


router = APIRouter(prefix="/platform-connections", tags=["platform-connections"])


# Request/Response models
class InitiateOAuthRequest(BaseModel):
    platform: str
    redirect_uri: str


class InitiateOAuthResponse(BaseModel):
    authorization_url: str
    state: str


class CompleteOAuthRequest(BaseModel):
    code: Optional[str] = None
    state: Optional[str] = None
    oauth_token: Optional[str] = None  # For Twitter OAuth 1.0a
    oauth_verifier: Optional[str] = None  # For Twitter OAuth 1.0a


class PlatformConnectionResponse(BaseModel):
    id: str
    platform: str
    platform_user_id: str
    platform_username: str
    is_active: bool
    created_at: str
    updated_at: str
    expires_at: str = None
    
    class Config:
        from_attributes = True


class DisconnectResponse(BaseModel):
    success: bool
    message: str


@router.post("/oauth/initiate", response_model=InitiateOAuthResponse)
async def initiate_oauth(
    request: InitiateOAuthRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Initiate OAuth flow for a platform
    
    Supported platforms: twitter, linkedin, facebook, instagram
    """
    try:
        auth_url = await platform_connection_service.initiate_oauth(
            platform=request.platform,
            user_id=str(current_user.id),
            redirect_uri=request.redirect_uri
        )
        
        # Extract state from URL for response
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        state = query_params.get('state', [''])[0]
        
        return InitiateOAuthResponse(
            authorization_url=auth_url,
            state=state
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth: {str(e)}")


@router.post("/oauth/callback", response_model=PlatformConnectionResponse)
async def oauth_callback(
    request: CompleteOAuthRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Complete OAuth flow and create/update platform connection
    """
    try:
        connection = await platform_connection_service.complete_oauth(
            code=request.code,
            state=request.state,
            oauth_token=request.oauth_token,
            oauth_verifier=request.oauth_verifier,
            db=db
        )
        
        return PlatformConnectionResponse(
            id=str(connection.id),
            platform=connection.platform,
            platform_user_id=connection.platform_user_id,
            platform_username=connection.platform_username,
            is_active=connection.is_active,
            created_at=connection.created_at.isoformat(),
            updated_at=connection.updated_at.isoformat(),
            expires_at=connection.expires_at.isoformat() if connection.expires_at else None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth: {str(e)}")


@router.get("/", response_model=List[PlatformConnectionResponse])
async def get_user_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get all platform connections for the current user
    """
    try:
        print(f"🔍 Getting connections for user: {current_user.id}")
        
        connections = await platform_connection_service.get_user_connections(
            user_id=str(current_user.id),
            db=db
        )
        
        print(f"🔍 Found {len(connections)} connections")
        
        result = []
        for conn in connections:
            try:
                connection_response = PlatformConnectionResponse(
                    id=str(conn.id),
                    platform=conn.platform,
                    platform_user_id=conn.platform_user_id,
                    platform_username=conn.platform_username,
                    is_active=conn.is_active,
                    created_at=conn.created_at.isoformat(),
                    updated_at=conn.updated_at.isoformat(),
                    expires_at=conn.expires_at.isoformat() if conn.expires_at else None
                )
                result.append(connection_response)
                print(f"✅ Processed connection: {conn.platform}")
            except Exception as conn_error:
                print(f"❌ Error processing connection {conn.id}: {conn_error}")
                raise conn_error
        
        print(f"✅ Returning {len(result)} connections")
        return result
    
    except Exception as e:
        print(f"❌ Error in get_user_connections: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")


@router.get("/{connection_id}", response_model=PlatformConnectionResponse)
async def get_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get a specific platform connection
    """
    try:
        connection = await platform_connection_service.get_connection_by_id(
            connection_id=connection_id,
            user_id=str(current_user.id),
            db=db
        )
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return PlatformConnectionResponse(
            id=str(connection.id),
            platform=connection.platform,
            platform_user_id=connection.platform_user_id,
            platform_username=connection.platform_username,
            is_active=connection.is_active,
            created_at=connection.created_at.isoformat(),
            updated_at=connection.updated_at.isoformat(),
            expires_at=connection.expires_at.isoformat() if connection.expires_at else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connection: {str(e)}")


@router.post("/{connection_id}/refresh", response_model=PlatformConnectionResponse)
async def refresh_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Refresh access token for a platform connection
    """
    try:
        # Verify connection belongs to user
        connection = await platform_connection_service.get_connection_by_id(
            connection_id=connection_id,
            user_id=str(current_user.id),
            db=db
        )
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Refresh the token
        updated_connection = await platform_connection_service.refresh_connection_token(
            connection_id=connection_id,
            db=db
        )
        
        return PlatformConnectionResponse(
            id=str(updated_connection.id),
            platform=updated_connection.platform,
            platform_user_id=updated_connection.platform_user_id,
            platform_username=updated_connection.platform_username,
            is_active=updated_connection.is_active,
            created_at=updated_connection.created_at.isoformat(),
            updated_at=updated_connection.updated_at.isoformat(),
            expires_at=updated_connection.expires_at.isoformat() if updated_connection.expires_at else None
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh connection: {str(e)}")


@router.delete("/{connection_id}", response_model=DisconnectResponse)
async def disconnect_platform(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Disconnect a platform connection
    """
    try:
        success = await platform_connection_service.disconnect_platform(
            connection_id=connection_id,
            user_id=str(current_user.id),
            db=db
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return DisconnectResponse(
            success=True,
            message="Platform disconnected successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect platform: {str(e)}")


@router.get("/platforms/supported")
async def get_supported_platforms():
    """
    Get list of supported platforms
    """
    return {
        "platforms": [
            {
                "id": "twitter",
                "name": "Twitter/X",
                "description": "Connect your Twitter/X account to publish tweets"
            },
            {
                "id": "linkedin", 
                "name": "LinkedIn",
                "description": "Connect your LinkedIn account to publish posts"
            },
            {
                "id": "facebook",
                "name": "Facebook",
                "description": "Connect your Facebook page to publish posts"
            },
            {
                "id": "instagram",
                "name": "Instagram",
                "description": "Connect your Instagram account to publish posts"
            }
        ]
    }


@router.get("/debug/test")
async def debug_test():
    """
    Simple test endpoint to verify the router is working
    """
    return {"status": "ok", "message": "Platform connections router is working"}


@router.get("/debug/auth-test")
async def debug_auth_test(current_user: User = Depends(get_current_user)):
    """
    Test authentication without database queries
    """
    return {
        "status": "ok", 
        "message": "Authentication is working",
        "user_id": str(current_user.id),
        "user_email": current_user.email
    }


@router.get("/debug/db-test")
async def debug_db_test(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Test database connection without platform connections table
    """
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        return {
            "status": "ok",
            "message": "Database connection is working",
            "test_query_result": test_value,
            "user_id": str(current_user.id)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }