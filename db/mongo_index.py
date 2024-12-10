import os
from db.mongo import connect_mongo, save_to_mongodb

if __name__ == "__main__":
    client, db = connect_mongo()
    xml_directory = "resources/"

    for file_name in os.listdir(xml_directory):
        if file_name.endswith(".xml"):
            file_path = os.path.join(xml_directory, file_name)
            save_to_mongodb(db, file_path)
