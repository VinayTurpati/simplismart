import argparse
import redis
import time
from threading import Thread
from app import create_app, db
from app.models.models import *
from app.redis_client import r

from threading import Lock
import redis_lock
import signal, os

def get_cluster_lock(cluster_id):
    lock_name = f"cluster_lock_{cluster_id}"
    return redis_lock.Lock(r, lock_name)

def handle_expired_key(message):
    print("Handling expired key: ", message)

    try:
        data = message['data'].decode()
        print("Data: ", data)
        if data.startswith('deployment:'):
            deployment_id = message['data'].decode().split(':')[1]
            with app.app_context():
                try:
                    deployment = Deployment.query.get(deployment_id)
                    print(f"Attempting to acquire lock for cluster_id={deployment.cluster.id}")
                    cluster_lock = get_cluster_lock(deployment.cluster.id)
                    with cluster_lock:
                        print(f"LOCK acquired for cluster_id: {deployment.cluster.id}")
                        from app.services.deployment_service import DeploymentService
                        DeploymentService.handle_expire_deployment(deployment_id)
                        print(f"UNLOCKING cluster: {deployment.cluster.id}")
                except Exception as e:
                    print("Error expired deployment: ", e)
    except Exception as e:
        print("Error handling expired key: ", e)


        
def start_redis_listener():
    try:
        pubsub = r.pubsub()
        pubsub.psubscribe(**{'__keyevent@0__:expired': handle_expired_key})
        print("Listening for expired keys...")
        thread = pubsub.run_in_thread(sleep_time=0.1)
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down Redis listener...")
        thread.stop()  # Gracefully stop the Pub/Sub thread
    except redis.exceptions.ConnectionError as e:
        print("Redis connection error: ", e)
        time.sleep(5)  # Wait for 5 seconds before retrying


# Flask app initialization
app = create_app()

def shutdown_redis(signal, frame):
    print("Shutting down Redis listener...")
    # Add any additional cleanup logic for Redis here
    exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flask app with a specified port.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the Flask app on")
    args = parser.parse_args()


    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        redis_listener_thread = Thread(target=start_redis_listener)
        redis_listener_thread.daemon = True
        redis_listener_thread.start()

    # Start Flask app
    signal.signal(signal.SIGINT, shutdown_redis)
    app.run(debug=True, host='0.0.0.0', port=args.port)