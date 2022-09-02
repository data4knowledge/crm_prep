from rdflib import RDFS, Graph, URIRef, Literal
from rdflib.namespace import RDF, DC, DCTERMS

def fhir_uri(fragment):
  return URIRef("%s%s" % ("http://hl7.org/fhir/", fragment))

def xsd_uri(fragment):
  return URIRef("%s%s" % ("http://www.w3.org/2001/XMLSchema#", fragment))

DATA_TYPES = {
  "date_time": {
    "parent": {
      "predicate_objects": [
        { "predicate": RDFS.label, "object": Literal("date_time") },
        { "predicate": RDF.type, "object": fhir_uri("dateTime") } 
      ]
    },
    "child": {
      "value": { 
        "predicate": fhir_uri("value"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("value") },
          { "predicate": RDF.type, "object": xsd_uri("dateTime") } 
        ]
      }
    }
  },
  "quantity": {
    "parent": {
      "predicate_objects": [
        { "predicate": RDFS.label, "object": Literal("quantity") },
        { "predicate": RDF.type, "object": fhir_uri("Quantity") } 
      ]
    },
    "child": {
      "value": { 
        "predicate": fhir_uri("Quantity.value"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("value") },
          { "predicate": RDF.type, "object": fhir_uri("decimal") } 
        ]
      },
      "code": { 
        "predicate": fhir_uri("Quantity.code"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("code") },
          { "predicate": RDF.type, "object": fhir_uri("code") } 
        ]
      },
      "unit": { 
        "predicate": fhir_uri("Quantity.unit"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("unit") },
          { "predicate": RDF.type, "object": fhir_uri("string") } 
        ]
      },
      "system": { 
        "predicate": fhir_uri("Quantity.system"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("system") },
          { "predicate": RDF.type, "object": fhir_uri("uri") } 
        ]
      },
      "comparator": { 
        "predicate": fhir_uri("Quantity.comparator"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("comparator") },
          { "predicate": RDF.type, "object": fhir_uri("code") } 
        ]
      }
    }
  },
  "codeable_concept": {
    "parent": {
      "predicate_objects": [
        { "predicate": RDFS.label, "object": Literal("codeable concept") },
        { "predicate": RDF.type, "object": fhir_uri("CodeableConcept") } 
      ]
    },
    "child": {
      "text": { 
        "predicate": fhir_uri("CodeableConcept.text"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("text") },
          { "predicate": RDF.type, "object": fhir_uri("string") } 
        ]
      },
      "coding": { 
        "predicate": fhir_uri("CodeableConcept.coding"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("coding") },
          { "predicate": RDF.type, "object": fhir_uri("Coding") }
        ],
        "recurse": "coding"
      }
    }
  },
  "coding": { 
    "parent": {
      "predicate_objects": [
        { "predicate": RDFS.label, "object": Literal("coding") },
        { "predicate": RDF.type, "object": fhir_uri("Coding") } 
      ]
    },
    "child": {
      "code": { 
        "predicate": fhir_uri("Coding.code"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("code") },
          { "predicate": RDF.type, "object": fhir_uri("code") } 
        ]
      },
      "userSelected": { 
        "predicate": fhir_uri("Coding.userSelected"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("user selected") },
          { "predicate": RDF.type, "object": fhir_uri("boolean") } 
        ]
      },
      "version": { 
        "predicate": fhir_uri("Coding.version"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("version") },
          { "predicate": RDF.type, "object": fhir_uri("string") } 
        ]
      },
      "system": { 
        "predicate": fhir_uri("Coding.system"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("system") },
          { "predicate": RDF.type, "object": fhir_uri("uri") } 
        ]
      },
      "display": { 
        "predicate": fhir_uri("Coding.display"), 
        "predicate_objects": [
          { "predicate": RDFS.label, "object": Literal("display") },
          { "predicate": RDF.type, "object": fhir_uri("string") } 
        ]
      }    
    }      
  }
}	

def add_fhir(the_graph, parent_uri, data_type):
  parent = URIRef(parent_uri)
  dt = DATA_TYPES[data_type]
  dt_subject = "%s/%s" % (parent_uri, data_type)
  #print("DT=", dt_subject)
  for item in dt["parent"]["predicate_objects"]:
    the_graph.add((URIRef(dt_subject), item["predicate"], item["object"]))
  for k, v in dt["child"].items():
    child_subject = "%s/%s" % (dt_subject, k)
    the_graph.add((URIRef(dt_subject), URIRef(v["predicate"]), URIRef(child_subject)))
    for item in v["predicate_objects"]:
      if "recurse" in v:
        #print("RECURSE")      
        add_fhir(the_graph, dt_subject, v["recurse"])
      else:
        the_graph.add((URIRef(child_subject), item["predicate"], item["object"]))
  return dt_subject
    
