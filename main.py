

# import os
# import hashlib
# from datetime import datetime
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.templating import Jinja2Templates
# from db import *  # Ensure the 'db' module is available
# import uvicorn  # Import uvicorn
# from notify import apobj  # Import the apprise object

# FILES_DIRECTORY = os.getenv("FILES_DIRECTORY", "./monito")

# app = FastAPI()

# templates = Jinja2Templates(directory="templates")

# def calculate_hash(file_path):
#     try:
#         with open(file_path, "rb") as file:
#             sha256_hash = hashlib.sha256()
#             while chunk := file.read(8192):
#                 sha256_hash.update(chunk)
#             return sha256_hash.hexdigest()
#     except Exception as e:
#         print(f"Error calculating hash for {file_path}: {e}")
#         return None

# def on_modified(event):
#     if event.is_directory:
#         return

#     hash_value = calculate_hash(event.src_path)
#     if hash_value is None:
#         return

#     # Send notification using Apprise
#     apobj.notify(
#         body=f"👀 Name: {event.src_path}\n#️⃣ Hash: {hash_value}\n⏰ Date: {str(datetime.now())}",
#         title='⚠️ == File Modified == ⚠️'
#     )

#     path = event.src_path
#     filename = os.path.basename(path)
#     file_info = get_file(filename, path)

#     if not file_info:
#         insert_file(filename, path, hash_value)
#     else:
#         try:
#             if file_info.hash != hash_value:
#                 update_file(filename, path, hash_value)
#         except Exception as e:
#             print(f"Error updating file {filename}: {e}")

# def first_run():
#     for root, dirs, files in os.walk(FILES_DIRECTORY):
#         for file in files:
#             path = os.path.join(root, file)
#             hash_value = calculate_hash(path)
#             if hash_value is None:
#                 continue

#             file_info = get_file(file, path)
#             if not file_info:
#                 insert_file(file, path, hash_value)
#             elif file_info.hash != hash_value:
#                 update_file(file, path, hash_value)

# @app.get("/")
# def dashboard(request: Request):
#     files = get_files()
#     files_final = [
#         {
#             "filename": i.filename,
#             "path": i.path,
#             "hash": i.hash,
#             "old_hash": i.old_hash,
#             "last_modified": i.last_modified
#         }
#         for i in files
#     ]
#     return templates.TemplateResponse("dashboard.html", {"request": request, "files_data": files_final})

# @app.get("/board")
# def board(request: Request):
#     files = get_files()
#     files_final = [
#         {
#             "filename": i.filename,
#             "path": i.path,
#             "hash": i.hash,
#             "old_hash": i.old_hash,
#             "last_modified": i.last_modified
#         }
#         for i in files
#     ]
#     return templates.TemplateResponse("dashboard.html", {"request": request, "files_data": files_final})

# @app.get("/files/{filename:path}")
# def read_file(filename: str):
#     try:
#         secure_filename = werkzeug.utils.secure_filename(filename)
#         path = os.path.join(FILES_DIRECTORY, secure_filename)

#         if not os.path.isfile(path):
#             raise HTTPException(status_code=404, detail="File not found.")

#         hash_value = calculate_hash(path)
#         if hash_value is None:
#             raise HTTPException(status_code=500, detail="Error calculating file hash.")

#         file_info = get_file(secure_filename, path)
#         if not file_info:
#             insert_file(secure_filename, path, hash_value)

#         if file_info.hash != hash_value:
#             update_file(secure_filename, path, hash_value)
#             return {
#                 "status": "File Modified",
#                 "filename": secure_filename,
#                 "path": path,
#                 "hash": hash_value,
#                 "old_hash": file_info.old_hash,
#                 "last_modified": file_info.last_modified
#             }

#         return {
#             "status": "OK",
#             "filename": secure_filename,
#             "path": path,
#             "hash": hash_value,
#             "old_hash": file_info.old_hash,
#             "last_modified": file_info.last_modified
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/files")
# def read_files():
#     files = get_files()
#     files_final = [
#         {
#             "filename": i.filename,
#             "path": i.path,
#             "hash": i.hash,
#             "old_hash": i.old_hash,
#             "last_modified": i.last_modified
#         }
#         for i in files
#     ]
#     return {"files": files_final}

# if __name__ == "__main__":
#     create_table()
#     observer = Observer()
#     event_handler = FileSystemEventHandler()
#     event_handler.on_modified = on_modified
#     observer.schedule(event_handler, path=FILES_DIRECTORY, recursive=True)
#     observer.start()

#     # Run the FastAPI app using Uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uvicorn
from db import *
from notify import apobj

FILES_DIRECTORY = os.getenv("FILES_DIRECTORY", "./monito")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def calculate_hash(file_path):
    try:
        with open(file_path, "rb") as file:
            sha256_hash = hashlib.sha256()
            while chunk := file.read(8192):
                sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def on_modified(event):
    if event.is_directory:
        return

    hash_value = calculate_hash(event.src_path)
    if hash_value is None:
        return

    apobj.notify(
        body=f"👀 Name: {event.src_path}\n#️⃣ Hash: {hash_value}\n⏰ Date: {str(datetime.now())}",
        title='⚠️ == File Modified == ⚠️'
    )

    path = event.src_path
    filename = os.path.basename(path)
    file_info = get_file(filename, path)

    if not file_info:
        insert_file(filename, path, hash_value)
    else:
        try:
            if file_info.hash != hash_value:
                update_file(filename, path, hash_value)
        except Exception as e:
            print(f"Error updating file {filename}: {e}")

def first_run():
    for root, dirs, files in os.walk(FILES_DIRECTORY):
        for file in files:
            path = os.path.join(root, file)
            hash_value = calculate_hash(path)
            if hash_value is None:
                continue

            file_info = get_file(file, path)
            if not file_info:
                insert_file(file, path, hash_value)
            elif file_info.hash != hash_value:
                update_file(file, path, hash_value)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/board", response_class=HTMLResponse)
def dashboard(request: Request):
    files = get_files()
    files_final = [
        {
            "filename": i.filename,
            "path": i.path,
            "hash": i.hash,
            "old_hash": i.old_hash,
            "last_modified": i.last_modified
        }
        for i in files
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "files_data": files_final})

@app.get("/files/{filename:path}", response_class=HTMLResponse)
def read_file(filename: str, request: Request):
    try:
        secure_filename = werkzeug.utils.secure_filename(filename)
        path = os.path.join(FILES_DIRECTORY, secure_filename)

        if not os.path.isfile(path):
            raise HTTPException(status_code=404, detail="File not found.")

        hash_value = calculate_hash(path)
        if hash_value is None:
            raise HTTPException(status_code=500, detail="Error calculating file hash.")

        file_info = get_file(secure_filename, path)
        if not file_info:
            insert_file(secure_filename, path, hash_value)

        if file_info.hash != hash_value:
            update_file(secure_filename, path, hash_value)
            return {
                "status": "File Modified",
                "filename": secure_filename,
                "path": path,
                "hash": hash_value,
                "old_hash": file_info.old_hash,
                "last_modified": file_info.last_modified
            }

        return {
            "status": "OK",
            "filename": secure_filename,
            "path": path,
            "hash": hash_value,
            "old_hash": file_info.old_hash,
            "last_modified": file_info.last_modified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_class=HTMLResponse)
def read_files(request: Request):
    files = get_files()
    files_final = [
        {
            "filename": i.filename,
            "path": i.path,
            "hash": i.hash,
            "old_hash": i.old_hash,
            "last_modified": i.last_modified
        }
        for i in files
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "files_data": files_final})

if __name__ == "__main__":
    create_table()
    observer = Observer()
    event_handler = FileSystemEventHandler()
    event_handler.on_modified = on_modified
    observer.schedule(event_handler, path=FILES_DIRECTORY, recursive=True)
    observer.start()

    # Run the FastAPI app using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
