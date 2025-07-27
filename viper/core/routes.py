from viper.utils.util_log import logger
from viper.wrappers.response import jsonify, abort
from viper.views.view_todo import route_dict as todo_route

routes = {}
routes.update(todo_route)


async def error_404(request):
    return abort(404)


async def response_for_path(request):
    path = request.url.path
    view_func = routes.get(path, error_404)
    try:
        response = await view_func(request)
    except (Exception,):
        logger.exception('Internal Server Error')
        return abort(500)
    return response
