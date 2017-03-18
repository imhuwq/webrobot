import sys
import time
import signal
import logging

from tornado import httpserver, ioloop, options

from server.api_v1 import apiv1
from server.tests import UnitTest
from server.application import create_app

if __name__ == '__main__':
    cmd = sys.argv[1]

    if cmd == 'runserver':
        options.define('port', default=8000, type=int, help='server port, default to 8000')
        options.define('mode', default='production', type=str, help='server mode, default to production')
        options.parse_command_line(sys.argv[1:])


        def sig_handler(sig, frame):
            logging.warning('Caught signal: %s', sig)
            ioloop.IOLoop.instance().add_callback(shutdown)


        def shutdown():
            logging.info('shutting down server...')
            http_server.stop()

            logging.info('shutting down server in 3 seconds ...')
            io_loop = ioloop.IOLoop.instance()

            deadline = time.time() + 3

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    logging.info('shutting down IO Loop...')
                    io_loop.stop()

            stop_loop()


        port = options.options.port
        mode = options.options.mode
        app = create_app(apiv1.handlers, mode=mode)
        app.settings['login_url'] = app.reverse_url('api_v1.user.UserLogin')

        global http_server
        http_server = httpserver.HTTPServer(app)
        http_server.listen(port)

        signal.signal(signal.SIGQUIT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        logging.info('Tornado server has been started in %s mode, listening port %s' % (mode, port))
        ioloop.IOLoop.instance().start()

        logging.info("Tornado server has been shut down completely")

    elif cmd == 'unittest':
        unit_test = UnitTest()
        unit_test.run()
