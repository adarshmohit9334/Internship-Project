import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

def slugify(value):
    return secure_filename(value.lower().replace(' ', '_'))

def upload_attachment(file, bg_request_id, attachment_type):
    ext = Path(file.filename).suffix.lower() or '.bin'
    storage_path = f"{bg_request_id}/{slugify(attachment_type)}{ext}"
    file_bytes = file.read()

    if current_app.extensions.get('supabase_enabled'):
        from extensions import get_supabase_client
        client = get_supabase_client()
        if client:
            client.storage.from_(current_app.config['SUPABASE_STORAGE_BUCKET']).upload(
                storage_path,
                file_bytes,
                file_options={'content-type': file.mimetype}
            )
            return storage_path

    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / str(bg_request_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{slugify(attachment_type)}{ext}"
    file.stream.seek(0)
    file.save(file_path)
    return str(file_path)

def get_signed_url(file_path, expires_in=3600):
    if current_app.extensions.get('supabase_enabled'):
        from extensions import get_supabase_client
        client = get_supabase_client()
        if client:
            response = client.storage.from_(current_app.config['SUPABASE_STORAGE_BUCKET']).create_signed_url(file_path, expires_in)
            return response.get('signedURL') or response.get('data', {}).get('signedURL')
    return file_path

def delete_attachment(file_path):
    if current_app.extensions.get('supabase_enabled'):
        from extensions import get_supabase_client
        client = get_supabase_client()
        if client:
            client.storage.from_(current_app.config['SUPABASE_STORAGE_BUCKET']).remove([file_path])
