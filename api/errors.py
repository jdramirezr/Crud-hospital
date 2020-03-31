from flask import jsonify

# 400 Bad Request
def custom400(error):
    return jsonify({'msg': error.description}), 400


# 401 Unauthorized
def custom401(error):
    return jsonify({'msg': error.description}), 401


# 403 Forbidden
def custom403(error):
    return jsonify({'msg': error.description}), 403


# 404 Not Found
def custom404(error):
    return jsonify({'msg': error.description}), 404


# 405 Method Not Allowed
def custom405(error):
    return jsonify({'msg': error.description}), 405


# 406 Not Acceptable
def custom406(error):
    return jsonify({'msg': error.description}), 406


# 422 Unprocessable Entity, for flask-apispec, webargs
def custom422(error):
    return jsonify(
        {'msg': error.description, 'errors': error.exc.messages}
    ), 422


# 500 Internal Server Error
def custom500(error):
    return jsonify({'msg': error.description}), 500


def register_errors(app):
    app.register_error_handler(400, custom400)
    app.register_error_handler(401, custom401)
    app.register_error_handler(403, custom403)
    app.register_error_handler(404, custom404)
    app.register_error_handler(405, custom405)
    app.register_error_handler(406, custom406)
    app.register_error_handler(422, custom422)
    app.register_error_handler(500, custom500)
