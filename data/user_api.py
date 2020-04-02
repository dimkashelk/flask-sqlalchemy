from flask import jsonify, request, Blueprint
from data import db_session, users, jobs, departments
from datetime import datetime

blueprint = Blueprint('users_api', __name__,
                      template_folder='templates')


@blueprint.route('/api/users', methods=['GET'])
def get_users():
    session = db_session.create_session()
    user = session.query(users.User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id',
                                    'surname',
                                    'name',
                                    'age',
                                    'position',
                                    'speciality',
                                    'address',
                                    'email',
                                    'modified_date',
                                    'city_from'))
                 for item in user]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    user = session.query(users.User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': user.to_dict(only=('id',
                                        'surname',
                                        'name',
                                        'age',
                                        'position',
                                        'speciality',
                                        'address',
                                        'email',
                                        'modified_date',
                                        'city_from'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id',
                  'surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = users.User(
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email'],
        modified_date=datetime.now()
    )
    a = list(map(lambda x: x['id'], list(session.query(users.User).all())))
    if request.json['id'] in a:
        old_user = session.query(users.User).filter(users.User.id == request.json['id'])
        old_user.team_leader = user.team_leader
        old_user.jod = user.jod
        old_user.work_size = user.work_size
        old_user.collaborators = user.collaborators
        old_user.hazard_category = user.hazard_category
        old_user.is_finished = user.is_finished
        old_user.add_by = user.add_by
        session.commit()
    else:
        session.add(user)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_news(users_id):
    session = db_session.create_session()
    user = session.query(users.User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})
