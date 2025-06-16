from dramatiq import actor
from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker()

@actor
def example_task(x):
    print(f"Processing {x}") 