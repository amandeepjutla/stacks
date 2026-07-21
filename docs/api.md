# API Endpoints

## Authentication

Stacks supports three authentication methods with different permission levels:

### Authentication Methods

1. **Session** - Web UI session cookie (automatic after login) - Full admin access
2. **Admin API Key** - Full access to all API endpoints
3. **Downloader API Key** - Limited access (can only add to queue and list subdirectories)

### Getting API Keys

- **Admin Key**: Log in to web UI → Settings → Authentication → API Key (Admin)
- **Downloader Key**: Log in to web UI → Settings → Authentication → Downloader API Key (Limited)

### Key Types Explained

| Key Type           | Permissions                                   | Use Case                                   |
| ------------------ | --------------------------------------------- | ------------------------------------------ |
| **Admin Key**      | Full access to all endpoints                  | Personal use, full control                 |
| **Downloader Key** | Can only add to queue and list subdirectories | Safe to share with others for Tampermonkey |

## API Endpoints

### System

| Endpoint       | Method | Session | Admin Key | DL Key | Description                                               |
| -------------- | ------ | ------- | --------- | ------ | --------------------------------------------------------- |
| `/api/health`  | GET    | ✔️       | ✔️         | ✔️      | Health check - returns `{"status": "ok"}`                 |
| `/api/version` | GET    | ✔️       | ✔️         | ✔️      | Get current Stacks and Tampermonkey script version        |
| `/api/logs`    | GET    | ✔️       | ✔️         | ❌      | Get the last 1000 lines of the system log                 |
| `/api/status`  | GET    | ✔️       | ✔️         | ❌      | Get current queue, downloads, history, fast download info |

### Authentication & Keys

| Endpoint                         | Method | Session | Admin Key | DL Key | Description                                           |
| -------------------------------- | ------ | ------- | --------- | ------ | ----------------------------------------------------- |
| `/api/key`                       | GET    | ✔️       | ❌         | ❌      | Get API keys (web UI only)                            |
| `/api/key/regenerate`            | POST   | ✔️       | ❌         | ❌      | Generate new admin API key (invalidates old one)      |
| `/api/key/disable`               | POST   | ✔️       | ❌         | ❌      | Disable API key (sets to null)                        |
| `/api/key/downloader/regenerate` | POST   | ✔️       | ❌         | ❌      | Generate new downloader API key (invalidates old one) |
| `/api/key/downloader/disable`    | POST   | ✔️       | ❌         | ❌      | Disable downloader API key (sets to null)             |
| `/api/key/test`                  | POST   | ✔️       | ✔️         | ✔️      | Test if an API key is valid and return its type       |

### Queue Management

| Endpoint                    | Method | Session | Admin Key | DL Key | Description                                   |
| --------------------------- | ------ | ------- | --------- | ------ | --------------------------------------------- |
| `/api/queue/add`            | POST   | ✔️       | ✔️         | ✔️      | Add item to download queue                    |
| `/api/queue/remove`         | POST   | ✔️       | ✔️         | ❌      | Remove item from queue by MD5                 |
| `/api/queue/clear`          | POST   | ✔️       | ✔️         | ❌      | Clear entire queue                            |
| `/api/queue/pause`          | POST   | ✔️       | ✔️         | ❌      | Pause/resume the download worker              |
| `/api/queue/current/cancel` | POST   | ✔️       | ✔️         | ❌      | Cancel current download and requeue it        |
| `/api/queue/current/remove` | POST   | ✔️       | ✔️         | ❌      | Cancel current download and remove from queue |
| `/api/subdirs`              | GET    | ✔️       | ✔️         | ✔️      | Get list of available subdirectories          |

### History Management

| Endpoint             | Method | Session | Admin Key | DL Key | Description             |
| -------------------- | ------ | ------- | --------- | ------ | ----------------------- |
| `/api/history/clear` | POST   | ✔️       | ✔️         | ❌      | Clear download history  |
| `/api/history/retry` | POST   | ✔️       | ✔️         | ❌      | Retry a failed download |

### Configuration

| Endpoint                        | Method | Session | Admin Key | DL Key | Description                                    |
| ------------------------------- | ------ | ------- | --------- | ------ | ---------------------------------------------- |
| `/api/config`                   | GET    | ✔️       | ✔️         | ❌      | Get current configuration                      |
| `/api/config`                   | POST   | ✔️       | ✔️         | ❌      | Update configuration (live reload)             |
| `/api/config/test_key`          | POST   | ✔️       | ✔️         | ❌      | Test Anna's Archive fast download key validity |
| `/api/config/test_solver` | POST   | ✔️       | ✔️         | ❌      | Test challenge solver connection               |

## Example Usage

### Test an API Key

```bash
curl -X POST http://localhost:7788/api/key/test \
  -H "Content-Type: application/json" \
  -d '{"key": "YOUR_API_KEY_HERE"}'
```

Response:

```json
{
  "valid": true,
  "type": "admin"
}
```

or for downloader keys:

```json
{
  "valid": true,
  "type": "downloader"
}
```

### Add Item to Queue (works with both Admin and Downloader keys)

```bash
curl -X POST http://localhost:7788/api/queue/add \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "md5": "1d6fd221af5b9c9bffbd398041013de8",
    "source": "manual"
  }'
```

Response:

```json
{
  "success": true,
  "message": "Added to queue",
  "md5": "1d6fd221af5b9c9bffbd398041013de8"
}
```

### Get Subdirectories (works with both Admin and Downloader keys)

```bash
curl -X GET http://localhost:7788/api/subdirs \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

Response:

```json
{
  "success": true,
  "subdirectories": ["/Library 1", "/Library 2", "/Users/Alice"]
}
```