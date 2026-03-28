from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta, timezone
from app.db.client import get_database
from app.core.security import require_role, TokenData
from app.core.logging import logger
from app.config import settings
import psutil

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health")
async def system_health_check(
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Check system health (admin only)"""
    try:
        # Check database
        try:
            await db.command('ping')
            db_status = "connected"
            db_ping = 1
        except Exception as e:
            db_status = "disconnected"
            db_ping = -1
            logger.error(f"Database health check failed: {e}")

        # Get system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()

        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "status": db_status,
                "ping_ms": db_ping
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "memory_available_mb": memory_info.available / (1024 * 1024)
            }
        }
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking system health"
        )


@router.get("/stats")
async def get_system_statistics(
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Get system statistics (admin only)"""
    try:
        # Database statistics
        total_users = await db.users.count_documents({})
        total_cases = await db.cases.count_documents({})
        total_files = await db.files.count_documents({})

        # Get database size (collection-specific)
        users_size = 0
        cases_size = 0

        # Case statistics
        open_cases = await db.cases.count_documents({"status": "open"})
        closed_cases = await db.cases.count_documents({"status": "closed"})
        high_severity = await db.cases.count_documents({"severity": "high"})

        return {
            "database": {
                "total_users": total_users,
                "total_cases": total_cases,
                "total_files": total_files
            },
            "cases": {
                "open": open_cases,
                "closed": closed_cases,
                "high_severity": high_severity
            },
            "storage": {
                "files_stored": total_files,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting system statistics"
        )


@router.get("/logs")
async def get_api_logs(
    hours: int = Query(24, ge=1, le=168),
    log_type: str = Query("all", enum=["all", "errors", "warnings", "info"]),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Get system logs from MongoDB (admin only)"""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        match: dict = {"timestamp": {"$gte": cutoff_time}}
        if log_type == "errors":
            match["level"] = "ERROR"
        elif log_type == "warnings":
            match["level"] = "WARNING"
        elif log_type == "info":
            match["level"] = "INFO"

        pipeline = [
            {"$match": match},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "timestamp": 1,
                "level": 1,
                "message": 1,
                "logger": 1,
                "module": 1,
                "function": 1,
                "line": 1,
                "exc_info": 1,
            }}
        ]

        logs = await db.system_logs.aggregate(pipeline).to_list(limit)

        # Serialize timestamps
        for log in logs:
            if isinstance(log.get("timestamp"), datetime):
                log["timestamp"] = log["timestamp"].isoformat()

        logger.info(f"System logs retrieved by {current_user.user_id}")

        return {
            "logs": logs,
            "total": len(logs),
            "hours": hours,
            "log_type": log_type,
        }

    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting system logs"
        )


@router.get("/activity")
async def get_user_activity(
    hours: int = Query(24, ge=1, le=720),
    user_id: str = Query(None),
    path: str = Query(None),
    status_code: int = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Get user activity logs from MongoDB (admin only)"""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        match: dict = {"timestamp": {"$gte": cutoff_time}}

        if user_id:
            match["user_id"] = user_id
        if path:
            match["path"] = {"$regex": path, "$options": "i"}
        if status_code:
            match["status_code"] = status_code

        pipeline = [
            {"$match": match},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$project": {"_id": 0}}
        ]

        activities = await db.activity_logs.aggregate(pipeline).to_list(limit)

        for activity in activities:
            if isinstance(activity.get("timestamp"), datetime):
                activity["timestamp"] = activity["timestamp"].isoformat()

        # Summary stats
        total_pipeline = [
            {"$match": match},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "avg_duration_ms": {"$avg": "$duration_ms"},
                "unique_users": {"$addToSet": "$user_id"},
            }}
        ]
        summary_result = await db.activity_logs.aggregate(total_pipeline).to_list(1)
        summary = summary_result[0] if summary_result else {}

        logger.info(f"Activity logs retrieved by {current_user.user_id}")

        return {
            "activities": activities,
            "total": len(activities),
            "hours": hours,
            "summary": {
                "total_requests": summary.get("total_requests", 0),
                "avg_duration_ms": round(summary.get("avg_duration_ms") or 0, 2),
                "unique_users": len([u for u in summary.get("unique_users", []) if u]),
            }
        }

    except Exception as e:
        logger.error(f"Error getting activity logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting activity logs"
        )



@router.post("/backup")
async def trigger_backup(
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Trigger system backup (admin only) - NOT YET IMPLEMENTED"""
    try:
        logger.warning(f"Backup requested by {current_user.user_id} but backup is not implemented")

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Backup functionality is not yet implemented"
        )
    except Exception as e:
        logger.error(f"Error triggering backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error triggering backup"
        )


@router.get("/database-stats")
async def get_database_stats(
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Get detailed database statistics (admin only)"""
    try:
        collections = await db.list_collection_names()

        stats = {
            "collections": {}
        }

        for collection_name in collections:
            if not collection_name.startswith("system"):
                collection = db[collection_name]
                count = await collection.count_documents({})
                stats["collections"][collection_name] = {
                    "count": count
                }

        logger.info(f"Database stats retrieved by {current_user.user_id}")

        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting database stats"
        )


@router.post("/clear-cache")
async def clear_cache(
    pattern: str = Query(None, description="Pattern to match for selective cache clear"),
    current_user: TokenData = Depends(require_role("admin")),
    db=Depends(get_database)
):
    """Clear system cache (admin only)"""
    try:
        from app.core.cache import cache
        
        if pattern:
            cache.invalidate(pattern)
            message = f"Cache cleared for pattern: {pattern}"
        else:
            cache.invalidate()
            message = "All cache cleared"
        
        logger.info(f"Cache clearing initiated by {current_user.user_id}: {message}")

        return {
            "status": "cache_cleared",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "cache_size": cache.size()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing cache"
        )


@router.get("/cache-stats")
async def get_cache_stats(
    current_user: TokenData = Depends(require_role("admin"))
):
    """Get cache statistics (admin only)"""
    try:
        from app.core.cache import cache
        
        return {
            "cache_size": cache.size(),
            "cache_enabled": settings.ENABLE_QUERY_CACHE,
            "cache_ttl": settings.CACHE_TTL,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting cache stats"
        )
