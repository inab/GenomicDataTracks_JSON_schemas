# Version URL to "Experimental Factor Ontology" Schema

```txt
https://raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_ontology_versions/properties/http://www.ebi.ac.uk/efo/efo.owl
```

URL to the version of "Experimental Factor Ontology" used in the JSON document


| Abstract            | Extensible | Status         | Identifiable            | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                               |
| :------------------ | ---------- | -------------- | ----------------------- | :---------------- | --------------------- | ------------------- | ---------------------------------------------------------------------------------------- |
| Can be instantiated | No         | Unknown status | Unknown identifiability | Forbidden         | Allowed               | none                | [fairtracks.schema.json\*](../json/schema/fairtracks.schema.json "open original schema") |

## efo.owl Type

`string` ([Version URL to "Experimental Factor Ontology"](fairtracks-properties-document-info-properties-version-urls-to-ontologies-used-properties-version-url-to-experimental-factor-ontology.md))

## efo.owl Constraints

**pattern**: the string must match the following regular expression: 

```regexp
^http://www.ebi.ac.uk/efo/releases/v[0-9]+.[0-9]+.[0-9]+/efo.owl$
```

[try pattern](https://regexr.com/?expression=%5Ehttp%3A%2F%2Fwww.ebi.ac.uk%2Fefo%2Freleases%2Fv%5B0-9%5D%2B.%5B0-9%5D%2B.%5B0-9%5D%2B%2Fefo.owl%24 "try regular expression with regexr.com")

**URI**: the string must be a URI, according to [RFC 3986](https://tools.ietf.org/html/rfc4291 "check the specification")

## efo.owl Examples

```json
"http://www.ebi.ac.uk/efo/releases/v3.20.0/efo.owl"
```
