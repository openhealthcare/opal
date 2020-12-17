from __future__ import absolute_import
from django.contrib.auth.models import User
from celery import shared_task


@shared_task
def extract(user_id, criteria):
    from opal.core.search import queries, extract
    user = User.objects.get(id=user_id)
    query = queries.create_query(user, criteria)
    episodes = query.get_episodes()
    fname = extract.zip_archive(episodes, query.description(), user)
    return fname
