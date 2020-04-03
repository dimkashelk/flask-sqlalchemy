from flask import jsonify
from data import db_session, users, jobs, departments
from flask_restful import reqparse, abort, Api, Resource


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    news = session.query(users.User).get(user_id)
    if not news:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):

    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(users.User).get(user_id)
        return jsonify({'users': user.to_dict(
            only=('id',
                  'surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email',
                  'modified_date',
                  'city_from'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(users.User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):

    def get(self):
        session = db_session.create_session()
        user = session.query(users.User).all()
        return jsonify({'users': [item.to_dict(
            only=('id',
                  'surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email',
                  'modified_date',
                  'city_from')) for item in user]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('surname', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('age', required=True, type=int)
        parser.add_argument('position', required=True)
        parser.add_argument('speciality', required=True)
        parser.add_argument('address', required=True)
        parser.add_argument('email', required=True)
        args = parser.parse_args()
        session = db_session.create_session()
        user = users.User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email']
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
