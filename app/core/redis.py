import redis
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from app.models.deployment import DeploymentStatus, Deployment as DeploymentModel
from sqlalchemy.orm import Session

redis_client = redis.StrictRedis(host="localhost", port=8001, decode_responses=True)


def update_deployment_status(db: Session):
    """
    Periodically check Redis for updates and sync with the database.
    """
    redis_key = f"org:{current_user.organization_id}:deployments"

    deployment_ids = redis_client.lrange(redis_key, 0, -1)

    for deployment_id in deployment_ids:
        deployment_data = redis_client.hgetall(f"deployment:{deployment_id}")

        if not deployment_data:
            continue

        status = deployment_data.get("status")
        created_at_str = deployment_data.get("created_at")
        required_time = int(deployment_data.get("required_time", 0))

        created_at = datetime.fromisoformat(created_at_str)

        elapsed_time = datetime.now() - created_at

        if elapsed_time >= timedelta(seconds=required_time):
            if status == DeploymentStatus.RUNNING:
                redis_client.hset(
                    f"deployment:{deployment_id}", "status", DeploymentStatus.COMPLETED
                )

                updated_status = redis_client.hget(
                    f"deployment:{deployment_id}", "status"
                )

                deployment = (
                    db.query(DeploymentModel).filter_by(id=deployment_id).first()
                )
                if deployment:
                    deployment.status = updated_status
                    deployment.completed_at = datetime.now()
                    db.add(deployment)
                    db.commit()

                redis_client.delete(f"deployment:{deployment_id}")
