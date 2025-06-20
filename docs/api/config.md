---
title: Configuration API
---

# Configuration API

The Configuration API is responsible for exposing endpoints that manage and manipulate DMB's configuration settings (`dmb_config.json`). These endpoints provide tools for loading, updating, saving, and validating configuration data for all DMB services.

---

## 🧩 Module: `config.py`
Located in: `api/routes/config.py`

---

## 📘 Endpoints

### `GET /config`
**Description:**
Returns the currently loaded in-memory configuration.

**Usage Example:**
```bash
curl http://localhost:8000/config
```

---

### `POST /config`
**Description:**
Accepts an updated config object and applies it in memory.

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d @updated_config.json
```

---

### `POST /config/save`
**Description:**
Saves the current in-memory config to the `dmb_config.json` file.

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config/save
```

---

### `POST /config/validate`
**Description:**
Validates the structure and format of a provided config file (without applying changes).

**Usage Example:**
```bash
curl -X POST http://localhost:8000/config/validate \
  -H "Content-Type: application/json" \
  -d @test_config.json
```

---

## 🧪 Developer Notes

- The config is held in memory for fast access and allows the user to experiment or preview changes before committing them to file.
- Validation uses internal DMB schema checks to ensure required keys and structure.
- Routes include error handling for malformed config data.

---

## 📎 Related Pages
- [Services Overview](../services/index.md)
- [Logs](logs.md)

