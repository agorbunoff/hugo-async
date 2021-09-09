import asyncio

from dotenv import load_dotenv
from prometheus_client import start_http_server, Summary

from hugo.exceptions import HttpError
from hugo.request import Request
from hugo.response import Response

CONFIG = load_dotenv()


GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"
HEAD = "HEAD"

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


class Hugo:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.handlers = {}
        start_http_server(CONFIG.PROMETHEUS_PORT)

    @REQUEST_TIME.time()
    async def handle_request(self, reader, writer):
        try:
            data = await reader.read(1024)
            request = Request.from_data(data)

            try:
                handler = self.dispatch(request)
            except KeyError:
                raise HttpError(404)

            controller_response = await handler(request)
            response = Response.from_data(controller_response)

        except HttpError as e:
            response = Response.from_data(
                "Error",
                True,
                status=e.status_code,
            )

        writer.write(response.final_response)
        await writer.drain()
        writer.close()

    async def serve(self):
        print(f"Serving at {self.host}:{self.port}")

        server = await asyncio.start_server(self.handle_request, self.host, self.port)

        async with server:
            await server.serve_forever()

    def dispatch(self, request):
        return self.handlers[(request.path, request.method)]

    def handler(self, path, method=GET):
        def deco(func):
            self.handlers[(path, method)] = func
            return func

        return deco
