from bson import ObjectId



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
