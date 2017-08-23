from __future__ import absolute_import

from celery import shared_task


@shared_task
def extract(user, extract_query):
    from opal.core.search import queries, extract
    query = queries.create_query(user, extract_query["criteria"])
    episodes = query.get_episodes()
    fname = extract.zip_archive(
        episodes, query.description(), user, fields=extract_query.get(
            "data_slice", None
        )
    )
    return fname
