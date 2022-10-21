from uuid import uuid4
from utility.utility import *

DATA_TYPES = {
  "date_time": {
    "parent": {
      "name": "date_time",
    },
    "child": {
      "value": { 
        "name": "value" ,
      }
    }
  },
  "date": {
    "parent": {
      "name": "date",
    },
    "child": {
      "value": { 
        "name": "value" ,
      }
    }
  },
  "boolean": {
    "parent": {
      "name": "boolean",
    },
    "child": {
      "value": { 
        "name": "value" ,
      }
    }
  },
  "string": {
    "parent": {
      "name": "string",
    },
    "child": {
      "value": { 
        "name": "text" ,
      }
    }
  },
  "quantity": {
    "parent": {
      "name": "quantity",
    },
    "child": {
      "value": { 
        "name": "value",
      },
      "code": { 
        "name": "code",
      },
      "unit": { 
        "name": "unit" ,
      },
      "system": { 
        "name": "system" ,
      },
      "comparator": { 
        "name": "comparator" ,
      }
    }
  },
  "codeable_concept": {
    "parent": {
      "name": "codeable concept" ,
    },
    "child": {
      "text": { 
        "name": "text" ,
      },
      "coding": { 
        "recurse": True,
      },
    }
  },
  "coding": { 
    "parent": {
      "name": "coding",
    },
    "child": {
      "code": { 
        "name": "code",
      },
      "userSelected": { 
        "name": "user selected",
      },
      "version": { 
        "name": "version",
      },
      "system": { 
        "name": "system",
      },
      "display": { 
        "name": "display",
      }    
    }      
  }
}	

def add_data_type(parent_uri, data_type, nodes, relationships):
  print("1:", DATA_TYPES)
  print("2:", data_type)
  dt = DATA_TYPES[data_type]
  name = format_name(dt['parent']['name'])
  item_uri = "%s/%s" % (parent_uri, name)
  record = {
    "name": name,
    "uri": item_uri,
    "uuid": uuid4() 
  }
  nodes["DataType"].append(record)
  for k, v in dt["child"].items():
    if 'recurse' in v:
      child_uri = add_data_type(item_uri, k, nodes, relationships)
    else:
      name = v['name']
      child_uri = "%s/%s" % (item_uri, format_name(name))
      record = {
        "name": name,
        "uri": child_uri,
        "uuid": uuid4()
      }
      nodes["DataTypeProperty"].append(record)
    relationships["HAS_PROPERTY"].append({"from": item_uri, "to": child_uri})
  return item_uri
    
