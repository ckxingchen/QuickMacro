from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager
from common.rpc_dispatcher import CusDispatcher


@Request.application
def application(request):
    """
    服务的主方法，handle里面的dispatcher就是代理的rpc方法，可以写多个dispatcher
    :param request:
    :return:
    """
    response = JSONRPCResponseManager.handle(
        request.get_data(cache=False, as_text=True), CusDispatcher())
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('127.0.0.1', 9876, application)
