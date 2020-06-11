# Untitled object in Sample Schema

```txt
https://raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks_sample.schema.json#/properties/biospecimen_class
```

Main type of structural unit to be used for classification of the sample


| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                                             |
| :------------------ | ---------- | -------------- | ------------ | :---------------- | --------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [fairtracks_sample.schema.json\*](../json/schema/fairtracks_sample.schema.json "open original schema") |

## biospecimen_class Type

`object` ([Details](fairtracks_sample-properties-biospecimen_class.md))

# undefined Properties

| Property                  | Type     | Required | Nullable       | Defined by                                                                                                                                                                                                                                                         |
| :------------------------ | -------- | -------- | -------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [term_id](#term_id)       | `string` | Required | cannot be null | [Sample](fairtracks_sample-properties-biospecimen_class-properties-term_id.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks_sample.schema.json#/properties/biospecimen_class/properties/term_id")       |
| [term_label](#term_label) | `string` | Optional | cannot be null | [Sample](fairtracks_sample-properties-biospecimen_class-properties-term_label.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks_sample.schema.json#/properties/biospecimen_class/properties/term_label") |

## term_id

URL linking to an ontology term


`term_id`

-   is required
-   Type: `string`
-   cannot be null
-   defined in: [Sample](fairtracks_sample-properties-biospecimen_class-properties-term_id.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks_sample.schema.json#/properties/biospecimen_class/properties/term_id")

### term_id Type

`string`

### term_id Constraints

**enum**: the value of this property must be equal to one of the following values:

| Value                                           | Explanation |
| :---------------------------------------------- | ----------- |
| `"http://purl.obolibrary.org/obo/NCIT_C12508"`  |             |
| `"http://purl.obolibrary.org/obo/NCIT_C12913"`  |             |
| `"http://purl.obolibrary.org/obo/NCIT_C16403"`  |             |
| `"http://purl.obolibrary.org/obo/NCIT_C103199"` |             |

**pattern**: the string must match the following regular expression: 

```regexp
^(https?|ftp)://
```

[try pattern](https://regexr.com/?expression=%5E(https%3F%7Cftp)%3A%2F%2F "try regular expression with regexr.com")

**unknown format**: the value of this string must follow the format: `term`

### term_id Examples

```json
"http://purl.obolibrary.org/obo/NCIT_C16403"
```

## term_label

Exact value according to the ontology used


`term_label`

-   is optional
-   Type: `string`
-   cannot be null
-   defined in: [Sample](fairtracks_sample-properties-biospecimen_class-properties-term_label.md "https&#x3A;//raw.githubusercontent.com/fairtracks/fairtracks_standard/v1/current/json/schema/fairtracks_sample.schema.json#/properties/biospecimen_class/properties/term_label")

### term_label Type

`string`

### term_label Constraints

**enum**: the value of this property must be equal to one of the following values:

| Value             | Explanation |
| :---------------- | ----------- |
| `"Cell"`          |             |
| `"Abnormal Cell"` |             |
| `"Cell Line"`     |             |
| `"Organism Part"` |             |

### term_label Examples

```json
"Cell Line"
```