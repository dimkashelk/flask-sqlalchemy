from flask import jsonify, request, Blueprint
from data import db_session, users, jobs, departments

blueprint = Blueprint('jobs_api', __name__,
                      template_folder='templates')


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    session = db_session.create_session()
    job = session.query(jobs.Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('team_leader', 'jod', 'work_size',
                                    'collaborators', 'hazard_category', 'is_finished'))
                 for item in job]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    session = db_session.create_session()
    news = session.query(jobs.Jobs).get(job_id)
    if not news:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'news': news.to_dict(only=('team_leader', 'jod', 'work_size',
                                       'collaborators', 'hazard_category', 'is_finished'))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'team_leader', 'jod', 'work_size',
                  'collaborators', 'hazard_category', 'is_finished', 'add_by']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    job = jobs.Jobs(
        team_leader=request.json['team_leader'],
        jod=request.json['jod'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        hazard_category=request.json['hazard_category'],
        is_finished=request.json['is_finished'],
        add_by=request.json['add_by']
    )
    a = list(map(lambda x: x['id'], list(session.query(jobs.Jobs).all())))
    if request.json['id'] in a:
        old_job = session.query(jobs.Jobs).filter(jobs.Jobs.id == request.json['id'])
        old_job.team_leader = job.team_leader
        old_job.jod = job.jod
        old_job.work_size = job.work_size
        old_job.collaborators = job.collaborators
        old_job.hazard_category = job.hazard_category
        old_job.is_finished = job.is_finished
        old_job.add_by = job.add_by
        session.commit()
    else:
        session.add(job)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/job/<int:jobs_id>', methods=['DELETE'])
def delete_news(jobs_id):
    session = db_session.create_session()
    job = session.query(jobs.Jobs).get(jobs_id)
    if not job:
        return jsonify({'error': 'Not found'})
    session.delete(job)
    session.commit()
    return jsonify({'success': 'OK'})
