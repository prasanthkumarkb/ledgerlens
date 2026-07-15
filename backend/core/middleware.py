import time

from starlette.middleware.base import BaseHTTPMiddleware

from core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start = time.time()

        response = await call_next(request)

        duration = round(time.time() - start, 3)

        logger.info(
            "%s %s %s %ss",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response
