from __future__ import absolute_import

from celery import shared_task


@shared_task
def extract(user, criteria):
    from opal.core.search import queries, extract
    query = queries.create_query(user, criteria)
    episodes = query.get_episodes()
    fname = extract.zip_archive(episodes, query.description(), user)
    return fname
