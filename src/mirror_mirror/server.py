import os.path
import SimpleHTTPServer
import SocketServer
import socket
import threading



class HTTPServer(object):
    """
    To serve remote files (e.g. css, javascript, )
    """

    PORT = 4567

    def __init__(self):
        class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

            def do_GET(self, *args):
                return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self, *args)

        httpd = SocketServer.TCPServer(("", HTTPServer.PORT), Handler, bind_and_activate=False)
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        class Thread(threading.Thread):

            def run(self):
                try:
                    dir = os.path.join(os.path.dirname(__file__), "resources")
                    os.chdir(dir)
                    httpd.serve_forever(poll_interval=2.0)
                except:
                    import traceback
                    traceback.print_exc()
                httpd.server_close()

        self.thread = Thread()
        self.thread.start()
        self.httpd = httpd

    def stop(self):
        self.httpd.shutdown()



    @staticmethod
    def start():
        return HTTPServer()