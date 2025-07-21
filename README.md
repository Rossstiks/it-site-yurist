# it-site-yurist

This repository contains a minimal FastAPI application skeleton for a document generation service.

## Setup

1. Create a virtual environment and install dependencies manually:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the application manually:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Alternatively, execute the included `install.sh` script to automatically
   install dependencies, initialize the database and start the server. On
   shared hosting environments like REG.RU, you may need to run the script
   explicitly with `bash`:

   ```bash
   bash install.sh
   ```

The API will be available at `http://localhost:8000/`.

On the first start the SQLite database `test.db` will be created automatically.

## Observability

The application emits JSON logs with a unique `request_id` for every request. Prometheus metrics are exposed at `/metrics`.

## Templates API

Templates can be created and listed via `/api/templates`. Example:

> Creation endpoints require an authenticated user with the `editor` or `admin` role.

```bash
curl -X POST http://localhost:8000/api/templates \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"code": "contract", "title": "Contract", "jinja_body": "Hello", "version": "1.0.0"}'
```

Template versions can be managed under `/api/templates/{id}/versions` and `/api/template-versions`.
Preview a version and publish it:

```bash
curl -X POST http://localhost:8000/api/templates/1/versions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"version": "1.1.0", "jinja_body": "Hi {{ name }}"}'

curl -X POST http://localhost:8000/api/template-versions/2/preview \
     -H "Content-Type: application/json" \
     -d '{"params": {"name": "Alice"}}'

curl -X POST http://localhost:8000/api/template-versions/2/publish
     -H "Authorization: Bearer <token>"
```

## Taxonomy API

Nodes can be created and retrieved as a tree via `/api/taxonomy`. Example:

```bash
curl -X POST http://localhost:8000/api/taxonomy \
     -H "Content-Type: application/json" \
     -d '{"slug": "contracts", "title": "Contracts"}'
```

Existing nodes can be updated or removed:

```bash
curl -X PUT http://localhost:8000/api/taxonomy/1 \
     -H "Content-Type: application/json" \
     -d '{"title": "Updated"}'

curl -X DELETE http://localhost:8000/api/taxonomy/1
```

## Generation API

Render the latest template version with provided parameters:

```bash
curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"code": "contract", "params": {"name": "John"}}'
```

### Generation Jobs

You can also create a generation job which stores the result on disk:

```bash
curl -X POST http://localhost:8000/api/generation-jobs \
     -H "Content-Type: application/json" \
     -d '{"code": "contract", "params": {"name": "John"}}'

curl http://localhost:8000/api/generation-jobs/1
```

## Auth API

Register a user (optionally specifying a role) and obtain a JWT token:

```bash
curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "secret", "role": "editor"}'

curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "secret"}'

curl -X POST http://localhost:8000/api/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh>"}'
```

## Users API

Admin users can list and create accounts.

```bash
curl -H "Authorization: Bearer <admin-token>" \
     http://localhost:8000/api/users

curl -X POST http://localhost:8000/api/users \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <admin-token>" \
     -d '{"email": "new@example.com", "password": "secret", "role": "viewer"}'
```

## Fields API

Fields describe input parameters for templates. Create them in bulk and list by template:

> Creating fields requires an authenticated user with the `editor` or `admin` role.

```bash
curl -X POST http://localhost:8000/api/fields/bulk \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '[{"template_id": 1, "name": "name", "label": "Name", "type": "string"}]'

curl "http://localhost:8000/api/fields?template_id=1"
```

## Lookups API

Lookups store simple reference lists. Create or update a lookup and retrieve it:

```bash
curl -X POST http://localhost:8000/api/lookups/currencies \
     -H "Content-Type: application/json" \
     -d '{"items": ["USD", "EUR"]}'

curl http://localhost:8000/api/lookups/currencies
```

## Search API

Search templates by code or title:

```bash
curl "http://localhost:8000/api/search/templates?q=contr"
```

## Audit API

List audit logs to track changes:

```bash
curl "http://localhost:8000/api/audit"
```
