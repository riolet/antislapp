# coding=utf-8
import os
import re
import requests
import urllib
import pprint
"""

Endpoints can be explored (and tested) on http://developer.canlii.org/io-docs
Endpoints available:

---  case browser ---

GET Get Case Databases List (language)
    /v1/caseBrowse/:language/
    List all the databases supported by the API

GET Get Case List (language, database) [offset, resultCount, published before, published after, decision before, decision after)
    /v1/caseBrowse/:language/:databaseId/
    List all the cases within a database

GET Get Case Metadata (language, database, case)
    /v1/caseBrowse/:language/:databaseId/:caseId/
    Get the metadata for a given case

---  case citations  ---

GET Get Citing Cases (language, database, case)
    /v1/caseCitator/:language/:databaseId/:caseId/citingCases
    Get a list of all cases citing the selected case

GET Get Citing Cases Teaser (language, database, case)
    /v1/caseCitatorTease/:language/:databaseId/:caseId/citingCases
    Get a maximim of 5 cases citing the selected case

GET Get Cited Cases (language, database, case)
    /v1/caseCitator/:language/:databaseId/:caseId/citedCases
    Get a list of all cases cited by the selected case

GET Get Cited Cases Teaser (language, database, case)
    /v1/caseCitatorTease/:language/:databaseId/:caseId/citedCases
    Get a maximim of 5 cases cited by the selected case

GET Get Cited Legislations (language, database, case)
    /v1/caseCitator/:language/:databaseId/:caseId/citedLegislations
    Get a list legislation cited by the selected case

GET Get Cited Legislations Teaser (language, database, case)
    /v1/caseCitatorTease/:language/:databaseId/:caseId/citedLegislations
    Get a maximim of 5 legislations cite by the selected case

---  legislation browse  ---

GET Get Legislation Databases List (language)
    /v1/legislationBrowse/:language/
    List all the databases supported by the API

GET Get Legislation List (language, database)
    /v1/legislationBrowse/:language/:databaseid/
    List all the legislation within a database

GET Get Legislation Metadata (language, database, legislation)
    /v1/legislationBrowse/:language/:databaseid/:legislationid/
    Get the metadata for a given legislation

---  search ---

GET Search (language) [offset, resultCount, fulltext]
    /v1/search/:language/
    The search endpoint allow the user to search for cases and legislations matching a search query

"""


# function to do search

# function to get case details

# function to retrieve case text via URL

# function to filter case text to remove header, footer, etc.  (And divide into paragraphs??)

#...or should I just manually find a few cases for each category?


class CanLIIError(Exception):
    def __init__(self, status, body):
        self.args = [status, body]
        self.message = body


class CanLII:
    PATTERN_DATE = re.compile(r'^\d{4}-[01]\d-\d\d$')  # YYYY-MM-DD, loosely.
    CASE_DATABASE_LIST = '/v1/caseBrowse/{language}/'
    CASE_LIST = '/v1/caseBrowse/{language}/{database}/'
    CASE_METADATA = '/v1/caseBrowse/{language}/{database}/{case_id}/'

    CITING_CASES = '/v1/caseCitator/{language}/{database}/{case_id}/citingCases'
    CITING_CASES_TEASER = '/v1/caseCitatorTease/{language}/{database}/{case_id}/citingCases'
    CITED_CASES = '/v1/caseCitator/{language}/{database}/{case_id}/citedCases'
    CITED_CASES_TEASER = '/v1/caseCitatorTease/{language}/{database}/{case_id}/citedCases'
    CITED_LEGISLATION = '/v1/caseCitator/{language}/{database}/{case_id}/citedLegislations'
    CITED_LEGISLATION_TEASER = '/v1/caseCitatorTease/{language}/{database}/{case_id}/citedLegislations'

    LEGISLATION_DATABASE_LIST = '/v1/legislationBrowse/{language}/'
    LEGISLATION_LIST = '/v1/legislationBrowse/{language}/{database}/'
    LEGISLATION_METADATA = '/v1/legislationBrowse/{language}/{database}/{legislation_id}/'

    SEARCH = '/v1/search/{language}/'

    def __init__(self):
        self.domain = 'http://api.canlii.org'
        self.api_key = os.environ.get("CANLII_KEY", "")

    def get_canlii_data(self, url, **kwargs):
        kwargs['api_key'] = self.api_key
        response = requests.get(self.domain + url, params=kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            raise CanLIIError(response.status_code, response.content)

    # --- cases ---

    def get_case_database_list(self, language='en'):
        """
        Get the metadata for a given legislation
        :param language: 'en' or 'fr'
        :return:
        {caseDatabases: [
            {"databaseId": "nlpc",
             "jurisdiction": "nl",
             "name": "Provincial Court of Newfoundland and Labrador"},
            {"databaseId": "nbls",
             "jurisdiction": "nb",
             "name": "Law Society of New Brunswick"},
            ...
            ]
        }
        """
        url = CanLII.CASE_DATABASE_LIST.format(language=language)
        return self.get_canlii_data(url)

    def get_case_list(self, database, language='en', offset=0, resultCount=10, publishedBefore=None, publishedAfter=None, decisionBefore=None, decisionAfter=None):
        """
        List all the cases within a database.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param offset: Starting record number for the list. First value is 0.
        :param resultCount: Number of cases listed in each response. Maximum value is 10 000.
        :param publishedBefore: date, YYYY-MM-DD
        :param publishedAfter: date, YYYY-MM-DD
        :param decisionBefore: date, YYYY-MM-DD
        :param decisionAfter: date, YYYY-MM-DD
        :return:
        {"cases": [
            {"caseId": {"en": "2009canlii70456"},
             "citation": "2009 CanLII 70456 (NL PC)",
             "databaseId": "nlpc",
             "title": "R. v. Saunders"},
            {"caseId": {"en": "2009canlii69063"},
             "citation": "2009 CanLII 69063 (NL PC)",
             "databaseId": "nlpc",
             "title": "R. v. Walsh"},
            ...
            ]
        }
        """
        assert offset >= 0
        assert 0 < resultCount <= 10000
        try:
            assert decisionAfter is None or CanLII.PATTERN_DATE.match(decisionAfter)
            assert decisionBefore is None or CanLII.PATTERN_DATE.match(decisionBefore)
            assert publishedAfter is None or CanLII.PATTERN_DATE.match(publishedAfter)
            assert publishedBefore is None or CanLII.PATTERN_DATE.match(publishedBefore)
        except:
            raise AssertionError("Decision and publish dates must be in the 'YYYY-MM-DD' format.")

        url = CanLII.CASE_LIST.format(language=language, database=database)
        params = {
            'offset': offset,
            'resultCount': resultCount
        }
        if decisionAfter:
            params['decisionAfter'] = decisionAfter
        if decisionBefore:
            params['decisionBefore'] = decisionBefore
        if publishedAfter:
            params['publishedAfter'] = publishedAfter
        if publishedBefore:
            params['publishedBefore'] = publishedBefore
        return self.get_canlii_data(url, **params)

    def get_case_metadata(self, database, case_id, language='en'):
        """
        Get the metadata for a given case.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
            {
                "databaseId": "bcsc",
                "caseId": "2002bcsc1840",
                "url": "http://canlii.ca/t/59xz",
                "title": "Jay v. Hollinger canadian Newspapers",
                "citation": "2002 BCSC 1840 (CanLII)",
                "language": "en",
                "docketNumber": "9395",
                "decisionDate": "2002-05-08",
                "keywords": "defamatory — truth — published — sting — evidence"
            }
            or CanLIIError:
            {
                "error": "MISSING",
                "message": "The specified object was not found in the database."
            }
        """
        url = CanLII.CASE_METADATA.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    # --- citations ---

    def get_citing_cases(self, database, case_id, language='en'):
        """
        Get a list of all cases citing the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
            {"citingCases": [
                {"databaseId": "csc-scc",
                 "caseId": {"en": "2008scc44"},
                 "title": "Canada (Privacy Commissioner) v. Blood Tribe Department of Health",
                 "citation": "[2008] 2 SCR 574, 2008 SCC 44 (CanLII)"
                }, ... ]
            }
        """
        url = CanLII.CITING_CASES.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    def get_citing_cases_teaser(self, database, case_id, language='en'):
        """
        Get a MAX OF 5 cases citing the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
            {"citingCases": [
                {"databaseId": "csc-scc",
                 "caseId": {"en": "2008scc44"},
                 "title": "Canada (Privacy Commissioner) v. Blood Tribe Department of Health",
                 "citation": "[2008] 2 SCR 574, 2008 SCC 44 (CanLII)"
                }, ... ]
            }
        """
        url = CanLII.CITING_CASES_TEASER.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    def get_cited_cases(self, database, case_id, language='en'):
        """
        Get a list of all cases cited by the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
        {"citedCases": [
            {"databaseId": "csc-scc",
             "caseId": {"en": "1974canlii12"},
             "title": "McLeod v. Egan",
             "citation": "[1975] 1 SCR 517, 1974 CanLII 12 (SCC)"
            }, ... ]
        }
        """
        url = CanLII.CITED_CASES.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    def get_cited_cases_teaser(self, database, case_id, language='en'):
        """
        Get a MAX OF 5 cases cited by the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
        {"citedCases": [
            {"databaseId": "csc-scc",
             "caseId": {"en": "1974canlii12"},
             "title": "McLeod v. Egan",
             "citation": "[1975] 1 SCR 517, 1974 CanLII 12 (SCC)"
            }, ... ]
        }
        """
        url = CanLII.CITED_CASES_TEASER.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    def get_cited_legislation(self, database, case_id, language='en'):
        """
        Get a list legislation cited by the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
        {"citedLegislations": [
            {"databaseId": "nbs",
             "legislationId": "snb-1984-c-c-5.1",
             "title": "Civil Service Act",
             "citation": "SNB 1984, c C-5.1",
             "type": "STATUTE"
            }, ... ]
        }
        """
        url = CanLII.CITED_LEGISLATION.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    def get_cited_legislation_teaser(self, database, case_id, language='en'):
        """
        Get a MAX OF 5 legislation cited by the selected case. May be empty list.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :param case_id: Unique identifier of a case as provided in the case list.
        :return:
        {"citedLegislations": [
            {"databaseId": "nbs",
             "legislationId": "snb-1984-c-c-5.1",
             "title": "Civil Service Act",
             "citation": "SNB 1984, c C-5.1",
             "type": "STATUTE"
            }, ... ]
        }
        """
        url = CanLII.CITED_LEGISLATION_TEASER.format(language=language, database=database, case_id=case_id)
        return self.get_canlii_data(url)

    # --- legislation ---

    def get_legislation_database_list(self, language='en'):
        """
        List all the databases supported by the API.

        :param language: 'en' or 'fr'
        :return:
            {
                "legislationDatabases": [{
                    "databaseId": "caa",
                    "type": "ANNUAL_STATUTE",
                    "jurisdiction": "ca",
                    "name": "Annual Statutes of Canada"
                }, ... ]
            }
        """
        url = CanLII.LEGISLATION_DATABASE_LIST.format(language=language)
        return self.get_canlii_data(url)

    def get_legislation_list(self, database, language='en'):
        """
        List all the legislation within a database.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :return:
        {"legislations": [{
            "databaseId": "nus",
            "legislationId": "snwt-nu-1994-c-26",
            "title": "Aboriginal Custom Adoption Recognition Act",
            "citation": "SNWT (Nu) 1994, c 26",
            "type": "STATUTE"
            }, ... ]
        }
        """
        url = CanLII.LEGISLATION_LIST.format(language=language, database=database)
        return self.get_canlii_data(url)

    def get_legislation_metadata(self, database, language='en'):
        """
        Get the metadata for a given legislation.
        :param language: 'en' or 'fr'
        :param database: Unique identifier of a database as provided in the database list.
        :return:
        {
            "legislationId": "snwt-nu-1994-c-26",
            "url": "http://canlii.ca/t/8l34",
            "title": "Aboriginal Custom Adoption Recognition Act",
            "citation": "SNWT (Nu) 1994, c 26",
            "type": "STATUTE",
            "language": "en",
            "dateScheme": "ENTRY_INTO_FORCE",
            "startDate": "2011-03-10",
            "endDate": "",
            "repealed": "NO",
            "content": [{
                "partId": "1",
                "partName": "Main"
            }]
        }
        """
        url = CanLII.LEGISLATION_METADATA.format(language=language, database=database)
        return self.get_canlii_data(url)

    # --- search ---

    def search(self, fullText, language='en', offset=0, resultCount=10):
        """
        The search endpoint allow the user to search for cases and legislations matching a search query
        :param language: 'en' or 'fr'
        :param offset: Starting record number for the list. First value is 0.
        :param resultCount: Number of cases listed in each response. Maximum value is 100.
        :param fullText: key words to search for.
        :return:
        {
            "resultCount": 1053487,
            "results": [{
                "case": {
                    "databaseId": "bcsc",
                    "caseId": {
                        "en": "2002bcsc1840"},
                    "title": "Jay v. Hollinger canadian Newspapers",
                    "citation": "2002 BCSC 1840 (CanLII)"}
                },
                ...
                ]
        }
        """
        assert 0 <= offset
        assert 0 < resultCount <= 100
        url = CanLII.LEGISLATION_METADATA.format(language=language)
        return self.get_canlii_data(url, fullText=urllib.unquote_plus(fullText), offset=offset, resultCount=resultCount)
