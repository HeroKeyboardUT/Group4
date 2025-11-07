#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""

from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict

import json

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Handle an incoming client connection.

        This method reads the request from the socket, prepares the request object,
        invokes the appropriate route handler if available, builds the response,
        and sends it back to the client.

        :param conn (socket): The client socket connection.
        :param addr (tuple): The client's address.
        :param routes (dict): The route mapping for dispatching requests.
        """

        # Connection handler.
        self.conn = conn        
        # Connection address.
        self.connaddr = addr
        # Request handler
        req = self.request
        # Response handler
        resp = self.response

        # Handle the request
        msg = conn.recv(1024).decode()
        req.prepare(msg, routes)

        # Handle request hook
        if req.hook:
            print("[HttpAdapter] hook in route-path METHOD {} PATH {}".format(req.hook._route_path,req.hook._route_methods))
            # ????
            # req.hook(headers = "bksysnet",body = "get in touch")
            
            #
            # TODO: handle for App hook here
            #

            try:
                # Call hook handler and get result
                hook_result = req.hook(headers=req.headers, body=req.body)
                
                if hook_result is not None:
                    print("[HttpAdapter] Hook returned data: {}...".format(
                        str(hook_result)[:80]))
                    
                    # Determine Content-Type based on return type
                    if isinstance(hook_result, str):
                        # Check if it's JSON string
                        if hook_result.strip().startswith('{') or hook_result.strip().startswith('['):
                            content_type = 'application/json'
                        elif hook_result.strip().startswith('<'):
                            content_type = 'text/html; charset=utf-8'
                        else:
                            content_type = 'text/plain; charset=utf-8'
                        
                        content_bytes = hook_result.encode('utf-8')
                    else:
                        # For dict, list, etc - convert to JSON
                        content_type = 'application/json'
                        content_bytes = json.dumps(hook_result).encode('utf-8')
                    
                    # Build response header
                    response_header = "HTTP/1.1 200 OK\r\n"
                    response_header += "Content-Type: {}\r\n".format(content_type)
                    response_header += "Content-Length: {}\r\n".format(len(content_bytes))
                    response_header += "Connection: close\r\n"
                    response_header += "\r\n"
                    
                    # Combine header + body
                    response = response_header.encode('utf-8') + content_bytes
                    
                    # Send response
                    conn.sendall(response)
                    conn.close()
                    return
                    
                else:
                    print("[HttpAdapter] Hook executed but returned None")
                    
            except Exception as e:
                print("[HttpAdapter] Hook execution error: {}".format(e))
                # Return JSON error response
                error_body = json.dumps({
                    'status': 'error',
                    'message': 'Internal Server Error: {}'.format(str(e))
                })
                
                response_header = "HTTP/1.1 500 Internal Server Error\r\n"
                response_header += "Content-Type: application/json\r\n"
                response_header += "Content-Length: {}\r\n".format(len(error_body))
                response_header += "Connection: close\r\n"
                response_header += "\r\n"
                
                response = response_header.encode('utf-8') + error_body.encode('utf-8')
                conn.sendall(response)
                conn.close()
                return

            
        # Task 1A
        if req.method == "POST" and req.path == "/login":
            if req.auth == True:
                req.path = "/index.html"
                req.method = "GET"
            else:
                req.path="/401.html"
                resp.status_code = 401
                resp.reason = "Unauthorized"
        # Task 1B
        if req.method == "GET" and req.path == "/index.html":
            if req.auth == False:
                print("[HttpAdapter] Unauthorized access, return 401")
                req.path = "/401.html"
                resp.status_code = 401
                resp.reason = "Unauthorized"
        if req.method == "GET" and req.path == "/chat.html":
            if req.auth == False:
                print("[HttpAdapter] Unauthorized access, return 401")
                req.path = "/401.html"
                resp.status_code = 401
                resp.reason = "Unauthorized"


        # Build response
        response = resp.build_response(req)
        # print(response)
        conn.sendall(response)
        conn.close()

    @property
    def extract_cookies(self, req, resp):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :param resp: (Response) The res:class:`Response <Response>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies

    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = self.extract_cookies(req)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    # def get_connection(self, url, proxies=None):
    #     """Returns a url connection for the given URL. 

    #     :param url: The URL to connect to.
    #     :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
    #     :rtype: int
    #     """

    #     proxy = select_proxy(url, proxies)

    #     if proxy:
    #         proxy = prepend_scheme_if_needed(proxy, "http")
    #         proxy_url = parse_url(proxy)
    #         if not proxy_url.host:
    #             raise InvalidProxyURL(
    #                 "Please check proxy URL. It is malformed "
    #                 "and could be missing the host."
    #             )
    #         proxy_manager = self.proxy_manager_for(proxy)
    #         conn = proxy_manager.connection_from_url(url)
    #     else:
    #         # Only scheme should be lower case
    #         parsed = urlparse(url)
    #         url = parsed.geturl()
    #         conn = self.poolmanager.connection_from_url(url)

    #     return conn


    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers