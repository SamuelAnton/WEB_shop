import flask
from flask import jsonify
from . import db_session
from .items import Items

blueprint = flask.Blueprint(
    'items_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/items')
def get_items():
    db_sess = db_session.create_session()
    items = db_sess.query(Items).all()
    return jsonify(
        {
            'items':
                [item.to_dict(only=('name', 'description', 'number', 'price'))
                 for item in items]
        }
    )


@blueprint.route('/api/items/<int:items_id>', methods=['GET'])
def get_one_item(items_id):
    db_sess = db_session.create_session()
    items = db_sess.query(Items).get(items_id)
    if not items:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'items': items.to_dict(only=(
                'name', 'description', 'number', 'price', 'category_id'))
        }
    )
