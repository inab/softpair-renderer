import copy
from bson import ObjectId


def fix_galaxy_links(doc):
    """Replace old Galaxy Freiburg tool_runner links with usegalaxy.eu root links."""
    new_doc = copy.deepcopy(doc)
    if new_doc.get("data") and new_doc["data"].get("webpage"):
        new_doc["data"]["webpage"] = [
            link.replace(
                "https://galaxy.bi.uni-freiburg.de/tool_runner?",
                "https://usegalaxy.eu/root?"
            )
            for link in new_doc["data"]["webpage"]
        ]
    return new_doc


def build_instances_keys_dict():
    from db.mongo.mongo_db_singleton import mongo_adapter

    # Step 1: Build a publication lookup dict with stringified ObjectIds
    publication_dict = {
        str(doc['_id']): {**doc, "_id": str(doc['_id'])}
        for doc in mongo_adapter.fetch_entries( "publicationsMetadataDev", {})
    }
    # Step 2: Build the main document dictionary and replace data.publication
    doc_dict = {}
    for doc in mongo_adapter.fetch_entries( "pretoolsDev", {}):
        pub_ids= doc.get('data', {}).get('publication')
        pubs = []
        for pub_id in pub_ids:
            if isinstance(pub_id, ObjectId):
                pubs.append(pub_id)
        
        doc['data']['publication'] = pubs
        doc['_id'] = str(doc['_id'])

        doc_dict[doc['_id']] = doc

    return doc_dict


def replace_with_full_entries(conflict, instances_dict):
    from db.mongo.mongo_db_singleton import mongo_adapter
    new_conflict = {
        "disconnected": [],
        "remaining": [],
    }
    for entry in conflict['disconnected']:
        entry_id = entry["id"]
        new_entry = mongo_adapter.fetch_entry("pretoolsDev", entry_id)
        new_conflict['disconnected'].append(new_entry)

    
    for entry in conflict['remaining']:
        entry_id = entry["id"]
        new_entry = mongo_adapter.fetch_entry("pretoolsDev", entry_id)
        new_conflict['remaining'].append(new_entry)

    return new_conflict
