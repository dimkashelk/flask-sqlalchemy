from flask import jsonify
from data import db_session, users, jobs, departments
from flask_restful import reqparse, abort, Api, Resource


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(jobs.Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):

    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(jobs.Jobs).get(job_id)
        return jsonify({'jobs': job.to_dict(
            only=('id',
                  'team_leader',
                  'jod',
                  'work_size',
                  'collaborators',
                  'start_date',
                  'end_date',
                  'hazard_category',
                  'is_finished'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(jobs.Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):

    def get(self):
        session = db_session.create_session()
        job = session.query(jobs.Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('id',
                  'team_leader',
                  'jod',
                  'work_size',
                  'collaborators',
                  'start_date',
                  'end_date',
                  'hazard_category',
                  'is_finished')) for item in job]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('team_leader', required=True, type=int)
        parser.add_argument('jod', required=True)
        parser.add_argument('work_size', required=True, type=int)
        parser.add_argument('collaborators', required=True)
        parser.add_argument('start_date', required=True)
        parser.add_argument('end_date', required=True)
        parser.add_argument('hazard_category', required=True, type=int)
        parser.add_argument('is_finished', required=True, type=bool)
        args = parser.parse_args()
        session = db_session.create_session()
        job = jobs.Jobs(
            team_leader=args['team_leader'],
            jod=args['jod'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            start_date=args['start_date'],
            end_date=args['end_date'],
            hazard_category=args['hazard_category'],
            is_finished=args['is_finished']
        )
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
