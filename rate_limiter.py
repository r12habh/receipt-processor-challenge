from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import asyncio


class RateLimiter:
    def __init__(self, max_requests=10, per_minute=1):
        self.request_counts = {}
        self.max_requests = max_requests
        self.per_minute = per_minute
        self.lock = asyncio.Lock()

    async def limit_request(self, request: Request):
        """
        Limit requests for a client based on IP address
        :param request: The incoming HTTP request
        :return:

        Raises:
        HTTPException: If the client has exceeded the allowed number of requests in a minute
        """
        # Get client IP
        client_ip = request.client.host
        current_minute = datetime.now().minute

        async with self.lock:
            # Initialize or update request count
            if client_ip not in self.request_counts:
                self.request_counts[client_ip] = {
                    'count': 1,
                    'minute': current_minute
                }
                return

            # Check if we're in the same minute
            if self.request_counts[client_ip]['minute'] == current_minute:
                # Increment request count
                self.request_counts[client_ip]['count'] += 1

                # Block if exceeding max requests
                if self.request_counts[client_ip]['count'] > self.max_requests:
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests. Please slow down"
                    )
                else:
                    # Reset for new minute
                    self.request_counts[client_ip] = {
                        'count': 1,
                        'minute': current_minute
                    }
