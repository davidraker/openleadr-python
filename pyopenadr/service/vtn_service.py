from asyncio import iscoroutine
from http import HTTPStatus
import os

from aiohttp import web
from jinja2 import Environment, PackageLoader, select_autoescape

from .. import errors
from ..messaging import create_message, parse_message

class VTNService:

    def __init__(self, vtn_id):
        self.vtn_id = vtn_id
        self.handlers = {}
        for method in [getattr(self, attr) for attr in dir(self) if callable(getattr(self, attr))]:
            if hasattr(method, '__message_type__'):
                self.handlers[method.__message_type__] = method

    async def handler(self, request):
        """
        Handle all incoming POST requests.
        """
        content = await request.read()
        print(f"Received: {content.decode('utf-8')}")
        message_type, message_payload = parse_message(content)
        print(f"Interpreted message: {message_type}: {message_payload}")

        if message_type in self.handlers:
            handler = self.handlers[message_type]
            response_type, response_payload = await handler(message_payload)
            response_payload['vtn_id'] = self.vtn_id

            # Create the XML response
            msg = create_message(response_type, **response_payload)
            response = web.Response(text=msg,
                                    status=HTTPStatus.OK,
                                    content_type='application/xml')

        else:
            template = templates.get_template('oadrResponse.xml')
            response = web.Response(
                text=template.render(status_code=errorcodes.COMPLIANCE_ERROR,
                                     status_description=f'A message of type {message_type} should not be sent to this endpoint'),
                status=HTTPStatus.BAD_REQUEST,
                content_type='application/xml')
        print(f"Sending {response.text}")
        return response
