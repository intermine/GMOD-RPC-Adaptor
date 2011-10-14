#!/usr/bin/python

from intermine.webservice import Service
from interminebio import RegionQuery
import suds.client
import time

class GMODAdapter(object):

    API_VERSION = 1.1

    service_urls = {
        'flymine': "http://www.flymine.org/query",
        'yeastmine': "http://yeastmine.yeastgenome.org/yeastmine",
        'ratmine': "http://ratmine.mcw.edu/ratmine",
        'metabolicmine': "http://metabolicmine.org/test",
        }

    default_species = {
        'flymine': "D. melanogaster",
        'yeastmine': "S. cerevisiae",
        'ratmine': "R. norvegicus",
        'metabolicmine': "H. sapiens"
        }

    EBI = "http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl"

    def __init__(self):
        self.services = dict(map(lambda x: (x[0], Service(x[1])), self.service_urls.items()))
        self.ebi = suds.client.Client(self.EBI)

    def organisms(self, mine):
        service = self.services[mine]
        query = service.new_query("Organism").select("species", "genus", "taxonId")
        orgs = [{"organism": {"genus": row["genus"], "species": row["species"], "taxonomy_id": row["taxonId"]}} for row in query.rows()]
        result = {"data_provider": mine, "api_version": GMODAdapter.API_VERSION, "data_version": service.release, "result": orgs}
        return result

    def search(self, mine, term, type="Gene", taxid=None, genus=None, species=None):
        service = self.services[mine]
        if type.startswith("SO:"):
            type = self._resolve_so_id(type).capitalize()
        query = service.new_query(type).select("*").where(type, "LOOKUP", term)
        if taxid is not None:
            query = query.where(type + ".organism.taxonId", "=", taxon)
        else:
            if genus is not None:
                query = query.where(type + ".organism.genus", "=", genus)
            if species is not None:
                query = query.where(type + ".organisms.species", "=", species)

        results = [dict(map(lambda x: (x[0].split('.')[-1], x[1]), row.to_d().items())) for row in query.rows()]
        for r in results:
            r["accession"] = r["primaryIdentifier"]
        result = {"query_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "data_provider": mine, "api_version": GMODAdapter.API_VERSION, "data_version": service.release, "result": results}
        return result

    def location(self, mine, chromsome, strand=None, fmin=None, fmax=None, type=["SequenceFeature"], taxid=None, genus=None, species=None, organism=None):
        service = self.services[mine]
        if type[0].startswith("SO:"):
            className = self._resolve_so_id(type[0]).capitalize()
        else:
            className = type[0]
        query = service.new_query(className).select("primaryIdentifier").where("chromosome.primaryIdentifier", '=', chromsome)
        if fmin is not None:
            query = query.where("chromosomeLocation.start", '>=', fmin[0])
        if fmax is not None:
            query = query.where("chromosomeLocation.end", '>=', fmax[0])
        if strand is not None:
            query = query.where("chromosomeLocation.strand", '=', strand)
        if taxid is not None:
            query = query.where(type + ".organism.taxonId", "=", taxid)
        else:
            if genus is not None:
                query = query.where(type + ".organism.genus", "=", genus)
            if species is not None:
                query = query.where(type + ".organisms.species", "=", species)
            if species is None and genus is None:
                organism = self.default_species[mine]

        results = [{"accession": row["primaryIdentifier"]} for row in query.rows()]

        result = {"query_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "data_provider": mine, "api_version": GMODAdapter.API_VERSION, "data_version": service.release, "result": results}
        return result

    def _resolve_so_id(self, so_id): 
        return self.ebi.service.getTermById(so_id, "SO")





