import redis
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from app.models.deployment import DeploymentStatus, Deployment as DeploymentModel
from sqlalchemy.orm import Session

# Connect to Redis
redis_client = redis.StrictRedis(host="localhost", port=8001, decode_responses=True)


def store_deployment_in_redis(deployment_id: int, status: str, required_time: int):
    """
    Store deployment in Redis with its status and required execution time.
    """
    key = f"deployment:{deployment_id}"
    created_at = datetime.now()
    redis_client.hmset(
        key,
        {
            "status": status,
            "required_time": required_time,
            "created_at": created_at.isoformat(),
        },
    )
    # Set expiry for required time in seconds
    redis_client.expire(key, required_time)


def update_deployment_status(db: Session):
    """
    Periodically check Redis for updates and sync with the database.
    """
    deployments = fetch_deployments_from_redis()
    for deployment_data in deployments:
        deployment_id = deployment_data["deployment_id"]
        status = deployment_data["status"]

        # Check if deployment time has elapsed
        created_at = deployment_data["created_at"]
        required_time = deployment_data["required_time"]
        elapsed_time = datetime.now() - created_at

        if elapsed_time >= timedelta(seconds=required_time):
            # Update status to COMPLETED if not already FAILED
            if status == DeploymentStatus.RUNNING:
                redis_client.hset(
                    f"deployment:{deployment_id}", "status", DeploymentStatus.COMPLETED
                )

            # Sync the status with the database
            deployment = db.query(DeploymentModel).filter_by(id=deployment_id).first()
            if deployment:
                deployment.status = redis_client.hget(
                    f"deployment:{deployment_id}", "status"
                )
                deployment.completed_at = datetime.now()
                db.add(deployment)
                db.commit()

            # Remove the key from Redis
            redis_client.delete(f"deployment:{deployment_id}")
