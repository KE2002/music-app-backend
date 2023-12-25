from configurations import *


def index_exists(index_name):
    return es.indices.exists(index=index_name)


def index_search(index_name, query, size=None):
    if size:
        return es.search(index=index_name, body=query, size=size)

    return es.search(index=index_name, body=query)


def index_elastic(index_name, body, id=None):
    if id:
        return es.index(index=index_name, body=body, id=id)

    return es.index(index=index_name, body=body)


def index_update(index_name, id, body):
    es.update(index=index_name, id=id, body=body)


def index_dox_delete(index_name, id):
    es.delete(index=index_name, id=id)

def get_doc(index_name, id):
    return es.get(index=index_name, id=id)