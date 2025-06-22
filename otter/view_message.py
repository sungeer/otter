from flask import request, Blueprint

from otter.model_message import MessageModel
from otter.util_resp import jsonify, abort

route = Blueprint('message', __name__)


@route.post('/messages')
def get_messages():
    messages = MessageModel().get_messages()
    return jsonify(messages)
