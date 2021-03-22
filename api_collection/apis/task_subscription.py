# cython: language_level=3

import uuid
from flask import request
from flask import current_app as app
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from celery.result import AsyncResult, GroupResult

from .convert_audio import ConvertAudioAPI


@app.celery.task()
def async_task_subscription(task_ids):
    """This simply stores all task ids in Celery"""
    return task_ids


def get_all_task_results(tasks):
    task_results = []
    for task in tasks:
        task_url = app.api.url_for(ConvertAudioAPI,
                                   task_id=str(task.id),
                                   _external=True)
        if task.successful():
            task_results.append({
                'status': task.status,
                'task_id': str(task.id),
                'task_url': task_url,
                'task_result': task.get()
            })
        else:
            task_results.append({
                'status': task.status,
                'task_id': str(task.id),
                'task_url': task_url
            })
    return task_results


def all_finished(tasks):
    return all(task.status != 'PENDING' for task in tasks)


class TaskSubscriptionAPI(Resource):
    decorators = [jwt_required]

    def post(self):
        task_ids = request.form.getlist('task_ids')
        results = [AsyncResult(tid, app=app.celery)
                   for tid in task_ids]
        group_result = GroupResult(id=str(uuid.uuid4()), results=results)
        group_result.save()
        successful = all_finished(group_result.results)
        return {
            'status': 'SUCCESS' if successful else 'PENDING',
            'bulk_task_id': str(group_result.id),
            'bulk_task_url': app.api.url_for(TaskSubscriptionAPI,
                                             bulk_task_id=str(group_result.id),
                                             _external=True),
            'task_results': get_all_task_results(group_result.results)
        }

    def get(self, bulk_task_id):
        if not bulk_task_id:
            raise BadRequest('The bulk_task_id is not supplied.')
        group_result = GroupResult.restore(bulk_task_id)
        task_url = app.api.url_for(TaskSubscriptionAPI,
                                   bulk_task_id=str(group_result.id),
                                   _external=True)
        successful = all_finished(group_result.results)
        task_results = {}
        if successful:
            task_results = {
                'task_results': get_all_task_results(group_result.results)
            }
        return {
            'status': 'SUCCESS' if successful else 'PENDING',
            'bulk_task_id': str(group_result.id),
            'bulk_task_url': task_url,
            'completed_count': group_result.completed_count(),
            'total_count': len(group_result.results),
            **task_results
        }
