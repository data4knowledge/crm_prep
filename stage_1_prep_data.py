import yaml
import os
import csv
from stringcase import pascalcase, snakecase
from uuid import uuid4
from fhir.fhir import add_data_type
from utility.utility import format_name, extend_uri
from utility.ra_server import RaServer

id_number = 1
uuid_or_uri_to_id = {}
nodes = { 
  "ModelRoot": [], "ModelNode": [], "DataType": [], "DataTypeProperty": [], 
  'ScopedIdentifier': [], 'Namespace': [], 'RegistrationStatus': [], 'RegistrationAuthority': [], 
}
relationships = { 
  "HAS_SUB_MODEL": [], "HAS_NODE": [], "HAS_DATA_TYPE": [], "HAS_PROPERTY": [],
  "IDENTIFIED_BY": [], "HAS_STATUS": [], "SCOPED_BY": [], "MANAGED_BY": [],
}
repeat = {}

def process_nodes(node_set, parent_uri, rel_type, link_to_parent=True):
  for node in node_set:
    print("Node:", node["name"])
    uri_name = format_name(node["name"])
    node_uri = "%s/%s" % (parent_uri, uri_name)
    if not node["name"] in repeat:
      nodes["ModelNode"].append({ "name": node["name"], "uri": node_uri })
      repeat[node["name"]] = node_uri
    else:
      node_uri = repeat[node["name"]]
    if link_to_parent:
      relationships[rel_type].append({"from": parent_uri, "to": node_uri})
    if "nodes" in node:
      process_nodes(node["nodes"], node_uri, "HAS_NODE")
    else:
      if "data_types" in node:
        for data_type in node["data_types"]: 
          dt_uri = add_data_type(node_uri, data_type, nodes, relationships) 
          relationships["HAS_DATA_TYPE"].append({"from": node_uri, "to": dt_uri})

with open("source_data/clinical_recording_model.yaml") as file:
    model = yaml.load(file, Loader=yaml.FullLoader)

    ns_s_json = RaServer().namespace_by_name("d4k CRM namespace")
    print(ns_s_json)
    ra_s_json = RaServer().registration_authority_by_namespace_uuid(ns_s_json['uuid'])
    print(ra_s_json)

    si = { 'version': 1, 'version_label': "1", 'identifier': "CRMODEL", 'semantic_version': '1.0.0', 'uuid': str(uuid4()) }
    ns = { 'uri': ns_s_json['uri'] , 'uuid': str(uuid4()) }
    rs = { 'registration_status': "Draft", 'effective_date': "2022-09-01", 'until_date': "", 'uuid': str(uuid4()) }
    ra = { 'uri': ra_s_json['uri'] , 'uuid': str(uuid4()) }

    base_uri = extend_uri(ns_s_json['value'], 'dataset')
    common_uri = extend_uri(base_uri, 'common')
    nodes["ModelRoot"].append({ "name": model["root"]["name"], "uri": base_uri })
    nodes['ScopedIdentifier'].append(si)
    nodes['Namespace'].append(ns)
    nodes['RegistrationStatus'].append(rs)
    nodes['RegistrationAuthority'].append(ra)
    relationships["IDENTIFIED_BY"].append({"from": base_uri, "to": si['uuid']})
    relationships["HAS_STATUS"].append({"from": base_uri, "to": rs['uuid']})
    relationships["SCOPED_BY"].append({"from": si['uuid'], "to": ns['uuid']})
    relationships["MANAGED_BY"].append({"from": rs['uuid'], "to": ra['uuid']})
    parent_uri = base_uri
    process_nodes(model["common"]["nodes"], common_uri, "HAS_NODE", False)
    process_nodes(model["root"]["nodes"], base_uri, "HAS_SUB_MODEL")

def delete_dir(dir_path):
    target_dir = "load_data"
    files = os.listdir(target_dir)
    for f in files:
      os.remove("%s/%s" % (target_dir, f))
      print("Deleted %s" % (f))

def write_nodes(the_data, csv_filename, id_field="id:ID"):
  if len(the_data) == 0:
    return 
  global id_number
  with open(csv_filename, mode='w', newline='') as csv_file:
    fields = list(the_data[0].keys())
    fieldnames = [id_field] + fields
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    for row in the_data:
      row[id_field] = id_number
      if 'uri' in row:
        uuid_or_uri_to_id[row["uri"]] = id_number
      if 'uuid' in row:
        uuid_or_uri_to_id[row["uuid"]] = id_number
      id_number += 1
      writer.writerow(row)

def write_relationships(the_data, csv_filename, id_field="id:ID"):
  if len(the_data) == 0:
    return 
  global id_number
  with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = [ ":START_ID", ":END_ID" ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    for row in the_data:
      new_row = { ":START_ID": uuid_or_uri_to_id[row["from"]], ":END_ID": uuid_or_uri_to_id[row["to"]] }
      writer.writerow(new_row)

delete_dir("load_data")

for k, v in nodes.items():
  csv_filename = "load_data/node-%s-1.csv" % (snakecase(k))
  write_nodes(v, csv_filename)

for k, v in relationships.items():
  csv_filename = "load_data/relationship-%s-1.csv" % (k.lower())
  write_relationships(v, csv_filename)
