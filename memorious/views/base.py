import logging
from werkzeug.exceptions import NotFound
from flask import render_template, Blueprint, request

from memorious.index import search_entities, search_links, search_duplicates
from memorious.index import load_entity, Query
from memorious.views.util import dataset_label, entity_schema_label
from memorious.views.util import country, link_schema_label
from memorious.views.util import entity_schema_icon

blueprint = Blueprint('base', __name__)
log = logging.getLogger(__name__)


@blueprint.route('/')
def index():
    query = Query({}, path=request.path, limit=0)
    query.add_facet('dataset', 'Dataset', dataset_label)
    stats = search_entities(query, request.auth)
    return render_template("home.html", stats=stats)


@blueprint.app_errorhandler(403)
def forbidden(e):
    return render_template('forbidden.html'), 404


@blueprint.route('/search')
def search():
    query = Query(request.args, path=request.path)
    query.add_facet('dataset', 'Dataset', dataset_label)
    query.add_facet('countries', 'Countries', country)
    query.add_facet('schemata', 'Types', entity_schema_label,
                    entity_schema_icon)
    results = search_entities(query, request.auth)
    return render_template("search.html", query=query, results=results)


@blueprint.route('/entities/<entity_id>')
def entity(entity_id):
    entity = load_entity(entity_id, request.auth)
    if entity is None:
        raise NotFound()

    # load possible duplicates via fingerprint expansion
    # fingerprints = expand_fingerprints(entity.fingerprints, request.auth)
    query = Query(request.args, prefix='duplicates_', path=request.path,
                  limit=5)
    # query.add_facet('countries', 'Countries', country_label)
    duplicates = search_duplicates(entity.id, entity.fingerprints, query,
                                   request.auth)
    # load links
    query = Query(request.args, prefix='links_', path=request.path,
                  limit=10)
    query.add_facet('schemata', 'Types', link_schema_label)
    query.add_facet('remote.countries', 'Countries', country)
    links = search_links(entity, query, request.auth)

    return render_template("entity.html", entity=entity, links=links,
                           duplicates=duplicates)
