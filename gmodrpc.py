#!/usr/bin/python

from intermine.webservice import Service

class GMODAdapter(object):

    API_VERSION = 1.1

    service_urls = {
        'flymine': "http://www.flymine.org/query",
        'yeastmine': "http://yeastmine.yeastgenome.org/yeastmine",
        'ratmine': "http://ratmine.mcw.edu/ratmine",
        'metabolicmine': "http://metabolicmine.org/test",
        }

    def __init__(self):
        self.services = dict(map(lambda x: (x[0], Service(x[1])), self.service_urls.items()))

    def organisms(self, mine):
        service = self.services[mine]
        query = service.new_query("Organism").select("species", "genus", "taxonId")
        orgs = [{"organism": {"genus": row["genus"], "species": row["species"], "taxonomy_id": row["taxonId"]}} for row in query.rows()]
        result = {"data_provider": mine, "api_version": GMODAdapter.API_VERSION, "data_version": service.release, "result": orgs}
        return result


