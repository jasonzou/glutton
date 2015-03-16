import asyncio
import logging

from random import randint
import rdflib
from rdflib.namespace import RDF, FOAF
from rdflib import URIRef, Namespace

LDP = Namespace("http://www.w3.org/ns/ldp#")

LOG = logging.getLogger(__name__)

"""
You can add your business logic here
"""

@asyncio.coroutine
def node_has_type(container, subject, rdftype):
    store = yield from container.engines['sparql']

    LOG.debug("checking if <{0}> is of type <{1}>...".format(subject, rdftype))
    return (subject, RDF.type, rdftype) in store

@asyncio.coroutine
def make_root_basic_container(container):
    store = yield from container.engines['sparql']

    LOG.debug("checking root container...")

    root_ref = URIRef("http://localhost:8000") # FIXME Hardcoded

    if not (root_ref, RDF.type, LDP.Container) in store:
        store.add((root_ref, RDF.type, LDP.Container))
        store.add((root_ref, RDF.type, LDP.BasicContainer))
        store.add((root_ref, RDF.type, LDP.RDFSource))
        LOG.debug("created a root container.")

    return True

@asyncio.coroutine
def node_exists(container, subject):
    store = yield from container.engines['sparql']

    LOG.debug("checking if {0} exists".format(subject))
    exists = (subject, None, None) in store

    return exists



@asyncio.coroutine
def get_ldpc_content(container, ldpc_ref):
    rdfstore = yield from container.engines['sparql']

    results = yield from rdfstore.triples((ldpc_ref, None, None))

    return results

@asyncio.coroutine
def ldpr_new(container, ldpr_ref, ldpr_graph, ldpc_ref):
    """
    Add a new resource (graph) to a LDPC
    """
    rdfstore = yield from container.engines['sparql']

    # Mark this new LDPR as a RDF Source
    ldpr_graph.add((ldpr_ref, RDF.type, LDP.RDFSource))

    # Copy temp graph to datastore
    for triple in ldpr_graph.triples((ldpr_ref, None, None)):
        rdfstore.add(triple)

    # Add this LDPR to the LDPC
    rdfstore.add((ldpc_ref, LDP.contains, ldpr_ref))

    LOG.debug("Made new LDPR {0}".format(ldpr_ref))

    return True

@asyncio.coroutine
def ldpr_delete(container, ldpr_ref):
    """
    Delete a LDPR and its containement triples
    FIXME Should be transactional
    """
    rdfstore = yield from container.engines['sparql']

    # Remove any containment triplet
    rdfstore.remove((None, LDP.contains, ldpr_ref))

    # Remove actual LDPR
    rdfstore.remove((ldpr_ref, None, None))

    return True

@asyncio.coroutine
def get_model_subjects(container, ontology):
    rdf = yield from container.engines['sparql']

    matches = yield from rdf.subjects(RDF.type, ontology)

    return matches

@asyncio.coroutine
def get_subject_value(container, subject, predicate):
    rdf = yield from container.engines['sparql']
    value = rdf.value(subject, predicate, any=True)

    return value
