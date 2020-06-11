# Untitled object in FAIRtracks Schema

```txt
https://raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info
```

Version and related information about the current FAIRtracks JSON document


| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                               |
| :------------------ | ---------- | -------------- | ------------ | :---------------- | --------------------- | ------------------- | ---------------------------------------------------------------------------------------- |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [fairtracks.schema.json\*](../json/schema/fairtracks.schema.json "open original schema") |

## doc_info Type

`object` ([Details](fairtracks-properties-doc_info.md))

# undefined Properties

| Property                                        | Type     | Required | Nullable       | Defined by                                                                                                                                                                                                                                                   |
| :---------------------------------------------- | -------- | -------- | -------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [local_id](#local_id)                           | `string` | Optional | cannot be null | [FAIRtracks](fairtracks-properties-doc_info-properties-local_id.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/local_id")                           |
| [doc_url](#doc_url)                             | `string` | Optional | cannot be null | [FAIRtracks](fairtracks-properties-doc_info-properties-doc_url.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_url")                             |
| [doc_ontology_versions](#doc_ontology_versions) | `object` | Required | cannot be null | [FAIRtracks](fairtracks-properties-doc_info-properties-doc_ontology_versions.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_ontology_versions") |
| [doc_version](#doc_version)                     | `string` | Required | cannot be null | [FAIRtracks](fairtracks-properties-doc_info-properties-doc_version.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_version")                     |
| [doc_date](#doc_date)                           | `string` | Required | cannot be null | [FAIRtracks](fairtracks-properties-doc_info-properties-doc_date.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_date")                           |

## local_id

Identifier for this FAIRtracks JSON document (within the TrackFind database)


`local_id`

-   is optional
-   Type: `string`
-   cannot be null
-   defined in: [FAIRtracks](fairtracks-properties-doc_info-properties-local_id.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/local_id")

### local_id Type

`string`

### local_id Examples

```json
"0"
```

## doc_url

URL to this FAIRtracks JSON document


`doc_url`

-   is optional
-   Type: `string`
-   cannot be null
-   defined in: [FAIRtracks](fairtracks-properties-doc_info-properties-doc_url.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_url")

### doc_url Type

`string`

### doc_url Constraints

**pattern**: the string must match the following regular expression: 

```regexp
^(https?|ftp)://
```

[try pattern](https://regexr.com/?expression=%5E(https%3F%7Cftp)%3A%2F%2F "try regular expression with regexr.com")

**URI**: the string must be a URI, according to [RFC 3986](https://tools.ietf.org/html/rfc4291 "check the specification")

### doc_url Examples

```json
"https://raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/examples/fairtracks.example.json"
```

## doc_ontology_versions

URLs to the version of the ontologies used in the JSON document


`doc_ontology_versions`

-   is required
-   Type: `object` ([Details](fairtracks-properties-doc_info-properties-doc_ontology_versions.md))
-   cannot be null
-   defined in: [FAIRtracks](fairtracks-properties-doc_info-properties-doc_ontology_versions.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_ontology_versions")

### doc_ontology_versions Type

`object` ([Details](fairtracks-properties-doc_info-properties-doc_ontology_versions.md))

## doc_version

Version of this FAIRtracks JSON document


`doc_version`

-   is required
-   Type: `string`
-   cannot be null
-   defined in: [FAIRtracks](fairtracks-properties-doc_info-properties-doc_version.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_version")

### doc_version Type

`string`

## doc_date

Creation date of this version of this FAIRtracks document


`doc_date`

-   is required
-   Type: `string`
-   cannot be null
-   defined in: [FAIRtracks](fairtracks-properties-doc_info-properties-doc_date.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks.schema.json#/properties/doc_info/properties/doc_date")

### doc_date Type

`string`

### doc_date Constraints

**date time**: the string must be a date time string, according to [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339 "check the specification")