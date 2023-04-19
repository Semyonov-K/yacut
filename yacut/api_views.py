from re import match

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id


@app.route('/api/id/<string:short_id>/')
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage(
            'Указанный id не найден', 404)
    return jsonify({'url': url_map.original})


@app.route('/api/id/', methods=['POST'])
def create_url():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if not data.get('custom_id'):
        data['custom_id'] = get_unique_short_id()
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if URLMap.query.filter_by(short=data['custom_id']).first() is not None:
        raise InvalidAPIUsage(f'Имя "{data["custom_id"]}" уже занято.')
    if not match(
            r'^[a-z]+://[^\/\?:]+(:[0-9]+)?(\/.*?)?(\?.*)?$', data['url']):
        raise InvalidAPIUsage('Указан недопустимый URL')
    if not match(r'^[A-Za-z0-9]{1,16}$', data['custom_id']):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки', 400)
    urlmap = URLMap()
    urlmap.from_dict(data)
    db.session.add(urlmap)
    db.session.commit()
    return jsonify(urlmap.to_dict()), 201
