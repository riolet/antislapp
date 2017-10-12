"""

Endpoints can be explored (and tested) on http://developer.canlii.org/io-docs
Endpoints available:

---  case browser ---

GET Get Databases List (language)
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

GET Get Databases List (language)
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
