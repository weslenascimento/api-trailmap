#!/usr/bin/env python3
"""Offline API Trailmap renderers. Python 3.10+, standard library only."""
import argparse
import copy
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VARIABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SECRET = re.compile(r"^(password|passwd|secret|client_secret|access_token|refresh_token|authorization|api[_-]?key|email|phone|cpf|ssn)$", re.I)
METHODS = set("GET POST PUT PATCH DELETE HEAD OPTIONS TRACE CONNECT".split())
LABELS = {
    "en": dict(scope="Scope", sources="Sources", operations="Operations", map="Dependencies", gaps="Gaps and conflicts", setup="Setup and workflows", coverage="Coverage", contract="Contract", evidence="Evidence", excluded="Excluded", unknown="Not documented", files="Using the package"),
    "pt": dict(scope="Escopo", sources="Fontes", operations="Operações", map="Dependências", gaps="Lacunas e conflitos", setup="Configuração e fluxos", coverage="Cobertura", contract="Contrato", evidence="Evidências", excluded="Excluído", unknown="Não documentado", files="Como usar o pacote"),
}


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(isinstance(data, dict), "Inventory must be an object")
    for key in ("schemaVersion", "api", "language", "scope", "preferences", "sources", "operations", "relationships", "gaps"):
        require(key in data, f"Missing root field: {key}")
    require(data["schemaVersion"] == "1.0", "Unsupported schemaVersion")
    require(isinstance(data["api"], dict) and isinstance(data["api"].get("name"), str) and bool(data["api"]["name"]), "api.name is required")
    require(isinstance(data["api"].get("baseUrl"), str), "api.baseUrl must be a string")
    require(isinstance(data["language"], str) and isinstance(data["scope"], str), "language/scope must be strings")
    pref = data["preferences"]
    require(isinstance(pref, dict), "preferences must be an object")
    require(pref.get("organization") in ("general", "category", "endpoint"), "Invalid organization")
    for key in ("postman", "variables", "scripts", "json", "html"):
        require(type(pref.get(key)) is bool, f"preferences.{key} must be boolean")
    for key in ("sources", "operations", "relationships", "gaps"):
        require(isinstance(data[key], list), f"{key} must be an array")
    require(all(isinstance(x, str) for x in data["gaps"]), "gaps must contain strings")

    def unique(records, kind):
        seen = set()
        for record in records:
            require(isinstance(record, dict), f"{kind} must be objects")
            name = record.get("id", "")
            require(isinstance(name, str) and ID.fullmatch(name), f"Invalid {kind} ID: {name}")
            require(name not in seen, f"Duplicate {kind} ID: {name}")
            seen.add(name)
        return seen

    sources = unique(data["sources"], "source")
    operations = unique(data["operations"], "operation")
    unique(data["relationships"], "relationship")

    def evidence(record):
        refs = record.get("evidence")
        require(isinstance(refs, list) and all(isinstance(x, str) and x in sources for x in refs), "Invalid evidence references")

    for source in data["sources"]:
        require(isinstance(source.get("locator"), str), "Source locator is required")
        require(source.get("status") in ("accessible", "blocked", "excluded", "unsupported"), "Invalid source status")
    for op in data["operations"]:
        require(op.get("method") in METHODS, "Invalid HTTP method")
        require(isinstance(op.get("path"), str) and op["path"].startswith("/"), "Operation path must start with /")
        for key in ("summary", "category"):
            require(isinstance(op.get(key), str), f"Operation {key} must be a string")
        require(isinstance(op.get("contract"), dict), "Operation contract must be an object")
        evidence(op)
        for key in ("documented", "executed", "blocked", "excluded"):
            require(type(op.get(key)) is bool, f"Operation {key} must be boolean")
        if op["excluded"]:
            require(isinstance(op.get("exclusionReason"), str) and bool(op["exclusionReason"]), "Excluded operation needs exclusionReason")
        captures = op.get("captures", [])
        require(isinstance(captures, list), "captures must be an array")
        for capture in captures:
            require(isinstance(capture, dict), "capture must be an object")
            require(pref["variables"] and pref["scripts"], "Captures require variables and scripts; clarify preferences")
            require(isinstance(capture.get("variable"), str) and VARIABLE.fullmatch(capture["variable"]), "Invalid capture variable")
            pointer = capture.get("pointer")
            require(isinstance(pointer, str) and pointer.startswith("/") and not re.search(r"~(?![01])", pointer), "Capture requires an RFC 6901 pointer")
            codes = capture.get("successCodes")
            require(isinstance(codes, list) and bool(codes) and all(type(x) is int and 200 <= x < 300 for x in codes), "Capture requires supported successCodes")
            evidence(capture)
            require(bool(capture["evidence"]), "Capture needs evidence")
        auth = op.get("auth")
        if auth is not None:
            require(isinstance(auth, dict) and auth.get("type") == "bearer", "Baseline exporter supports bearer auth only; extend manually for other schemes")
            require(isinstance(auth.get("variable"), str) and VARIABLE.fullmatch(auth["variable"]), "Invalid auth variable")
        parameters = op.get("parameters", [])
        require(isinstance(parameters, list), "parameters must be an array")
        for parameter in parameters:
            require(isinstance(parameter, dict) and isinstance(parameter.get("name"), str) and bool(parameter["name"]), "Invalid parameter")
            require(parameter.get("in") in ("path", "query", "header", "cookie"), "Invalid parameter location")
        for key in ("preRequestScript", "postResponseScript"):
            if key in op:
                require(isinstance(op[key], list) and all(isinstance(line, str) for line in op[key]), f"{key} must contain script lines")
    for edge in data["relationships"]:
        require(edge.get("from") in operations and edge.get("to") in operations, "Dangling relationship")
        require(edge.get("certainty") in ("documented", "observed", "inferred"), "Invalid certainty")
        require(isinstance(edge.get("kind"), str) and bool(edge["kind"]), "Relationship kind is required")
        require(isinstance(edge.get("description"), str) and bool(edge["description"]), "Relationship explanation is required")
        evidence(edge)
        if edge["certainty"] != "inferred":
            require(bool(edge["evidence"]), "Confirmed relationships need evidence")
    return data


def sanitize(value, schema_context=False):
    """Conservative defense in depth; agent must sanitize prose and custom fields."""
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if SECRET.fullmatch(key) and not isinstance(item, (dict, list)) and not schema_context:
                result[key] = "" if item == "" else "[REDACTED]"
            else:
                result[key] = sanitize(item, key in ("properties", "$defs", "definitions"))
        return result
    if isinstance(value, list):
        return [sanitize(item, schema_context) for item in value]
    return value


def coverage(data):
    return {"discovered": len(data["operations"]), **{key: sum(op[key] for op in data["operations"]) for key in ("documented", "executed", "blocked", "excluded")}}


def fence(value):
    text = dump(value)
    marker = "`" * max(3, max((len(x) for x in re.findall(r"`+", text)), default=0) + 1)
    return f"{marker}json\n{text}\n{marker}"


def md(value):
    return html.escape(str(value)).replace("\n", " ").replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;")


def operation_markdown(op, data, labels):
    edges = [edge for edge in data["relationships"] if op["id"] in (edge["from"], edge["to"])]
    parts = [f'<a id="{op["id"]}"></a>', f'## {md(op["method"])} {md(op["path"])}', md(op["summary"]),
             f'Category: {md(op["category"] or "Uncategorized (generated fallback)")}',
             f'{labels["evidence"]}: {", ".join(md(x) for x in op["evidence"]) or labels["unknown"]}',
             f'Status: documented={op["documented"]}, executed={op["executed"]}, blocked={op["blocked"]}, excluded={op["excluded"]}']
    if op["excluded"]:
        parts.append(f'{labels["excluded"]}: {md(op["exclusionReason"])}')
    parts += [f'### {labels["contract"]}', fence(op["contract"]), f'### {labels["map"]}', fence(edges)]
    extra = {k: v for k, v in op.items() if k not in {"id", "method", "path", "summary", "category", "contract", "evidence"}}
    parts += ["### Metadata / examples", fence(extra)]
    return "\n\n".join(parts)


def markdown_files(data):
    labels = LABELS["pt" if data["language"].startswith("pt") else "en"]
    mode = data["preferences"]["organization"]
    files, links = {}, {}
    if mode == "category":
        groups = {}
        for op in data["operations"]:
            groups.setdefault(op["category"] or "Uncategorized (generated fallback)", []).append(op)
        for category, operations in groups.items():
            suffix = hashlib.sha256(category.encode()).hexdigest()[:12]
            name = f"categories/category-{suffix}.md"
            files[name] = f"# {md(category)}\n\n[INDEX](../INDEX.md)\n\n" + "\n\n".join(operation_markdown(op, data, labels) for op in operations)
            for op in operations:
                links[op["id"]] = f'{name}#{op["id"]}'
    elif mode == "endpoint":
        for op in data["operations"]:
            name = f'endpoints/{op["id"]}.md'
            files[name] = "[INDEX](../INDEX.md)\n\n" + operation_markdown(op, data, labels)
            links[op["id"]] = name
    else:
        links = {op["id"]: f'#{op["id"]}' for op in data["operations"]}
    parts = [f'# {md(data["api"]["name"])}', md(data["api"].get("description", "")),
             f'## {labels["scope"]}', md(data["scope"]),
             f'## {labels["setup"]}', f'Base URL: {md(data["api"]["baseUrl"]) or labels["unknown"]}',
             md(data["api"].get("setup", labels["unknown"])), md(data["api"].get("workflows", labels["unknown"])),
             f'## {labels["coverage"]}', fence(coverage(data)),
             ("Contagens independentes; universo externo desconhecido. Leia este índice, a autenticação e apenas as operações necessárias."
              if data["language"].startswith("pt") else "Counts are independent; undiscovered external scope is unknown. Read this index, authentication, and only the operations needed."),
             f'## {labels["sources"]}', fence(data["sources"]), f'## {labels["operations"]}']
    parts.append("\n".join(f'- [{md(op["method"])} {md(op["path"])}]({links[op["id"]]}) — {md(op["summary"])}' for op in data["operations"]))
    parts.append(f'## {labels["map"]}')
    # Only generated safe IDs appear in Mermaid; untrusted labels stay in the table.
    lines = ["flowchart LR"] + [f'    n{index}["{op["id"]}"]' for index, op in enumerate(data["operations"])]
    indices = {op["id"]: index for index, op in enumerate(data["operations"])}
    for edge in data["relationships"]:
        arrow = "-.->" if edge["certainty"] == "inferred" else "-->"
        lines.append(f'    n{indices[edge["from"]]} {arrow} n{indices[edge["to"]]}')
    if data["operations"]:
        parts.append("```mermaid\n" + "\n".join(lines) + "\n```")
    parts.append(fence(data["relationships"]))
    parts += [f'## {labels["gaps"]}', "\n".join(f'- {md(gap)}' for gap in data["gaps"]) or labels["unknown"], f'## {labels["files"]}']
    pt = data["language"].startswith("pt")
    if data["preferences"]["postman"]:
        parts.append(("Importe `postman/api.postman_collection.json`. Se presente, importe e selecione o ambiente `local`. Preencha valores vazios e revise os efeitos antes de executar. A geração não executa requisições nem valida o runtime do Postman."
                      if pt else "Import `postman/api.postman_collection.json`. If present, import and select the `local` environment. Fill blank values and review side effects before execution. Generation does not execute requests or verify the Postman runtime."))
        parts.append(("Autenticação automática: apenas capturas explicitamente documentadas; configure outros fluxos manualmente. Sem scripts, preencha tokens/IDs manualmente. Sem variáveis, substitua parâmetros e credenciais na requisição."
                      if pt else "Automatic authentication: only explicitly evidenced captures; configure other flows manually. Without scripts, supply tokens/IDs manually. Without variables, edit parameters and credentials in each request."))
    if data["preferences"]["html"]:
        parts.append("[HTML](api-trailmap.html) — " + ("abra localmente no navegador; nenhum servidor necessário." if pt else "open locally in a browser; no server required."))
    if data["preferences"]["json"]:
        parts.append("[JSON](api-trailmap.json) — schemaVersion 1.0")
    if mode == "general":
        parts += [operation_markdown(op, data, labels) for op in data["operations"]]
    files["INDEX.md"] = "\n\n".join(parts) + "\n"
    return files


def postman(data):
    pref = data["preferences"]
    variables = {"base_url": data["api"]["baseUrl"]} if pref["variables"] else {}
    folders = {}
    for op in data["operations"]:
        if op["excluded"]:
            continue
        params = op.get("parameters", [])
        path = op["path"]
        headers, query = [], []
        for param in params:
            name, location = param["name"], param["in"]
            var = re.sub(r"[^A-Za-z0-9_]", "_", f'{op["id"]}_{name}')
            value = "{{" + var + "}}" if pref["variables"] else ""
            if pref["variables"]:
                variables[var] = ""
            if location == "path" and pref["variables"]:
                path = path.replace("{" + name + "}", value)
            elif location == "query":
                query.append((name, value))
            elif location == "header":
                headers.append({"key": name, "value": value})
            elif location == "cookie":
                headers.append({"key": "Cookie", "value": name + "=" + value})
        # Path placeholders not repeated in the optional parameter projection still get configuration entries.
        if pref["variables"]:
            for name in re.findall(r"(?<!\{)\{([^{}]+)\}(?!\})", path):
                var = re.sub(r"[^A-Za-z0-9_]", "_", f'{op["id"]}_{name}')
                variables[var] = ""
                path = path.replace("{" + name + "}", "{{" + var + "}}")
        base = "{{base_url}}" if pref["variables"] else data["api"]["baseUrl"].rstrip("/")
        url = base + path
        if query:
            url += "?" + "&".join(urlencode({key: ""}) + value for key, value in query)
        request = {"method": op["method"], "header": headers, "url": url,
                   "description": op["summary"] + "\n\n" + dump(op["contract"]) + "\n\nReview prerequisites and side effects in INDEX.md. Fill blank configuration before executing."}
        if "requestBody" in op:
            request["body"] = {"mode": "raw", "raw": dump(op["requestBody"]), "options": {"raw": {"language": "json"}}}
            headers.append({"key": "Content-Type", "value": "application/json"})
        if op.get("auth"):
            token = op["auth"]["variable"]
            if pref["variables"]:
                variables[token] = ""
            request["auth"] = {"type": "bearer", "bearer": [{"key": "token", "value": "{{" + token + "}}" if pref["variables"] else "", "type": "string"}]}
        events = []
        if pref["scripts"]:
            before = list(op.get("preRequestScript", []))
            after = list(op.get("postResponseScript", []))
            for capture in op.get("captures", []):
                var = capture["variable"]
                variables[var] = ""
                before.append(f"pm.environment.unset({json.dumps(var)});")
                after += ["{", f"  const key = {json.dumps(var)};", "  pm.environment.unset(key);", "  pm.test('Capture ' + key, function () {",
                          f"    pm.expect({json.dumps(capture['successCodes'])}).to.include(pm.response.code);",
                          f"    const pointer = {json.dumps(capture['pointer'])};",
                          "    const value = pointer.slice(1).split('/').map(s => s.replace(/~1/g, '/').replace(/~0/g, '~')).reduce((v, k) => v != null && Object.prototype.hasOwnProperty.call(v, k) ? v[k] : undefined, pm.response.json());",
                          "    pm.expect(value !== undefined && value !== null && ['string', 'number', 'boolean'].includes(typeof value) && String(value).length > 0).to.equal(true);",
                          "    pm.environment.set(key, String(value));", "  });", "}"]
            for hook, lines in (("prerequest", before), ("test", after)):
                if lines:
                    events.append({"listen": hook, "script": {"type": "text/javascript", "exec": lines}})
        item = {"name": op["id"] + " — " + op["summary"], "request": request, "response": []}
        if events:
            item["event"] = events
        folders.setdefault(op["category"] or "Uncategorized (generated fallback)", []).append(item)
    collection = {"info": {"name": data["api"]["name"], "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json", "description": "Generated offline by API Trailmap. No requests executed. See INDEX.md for scope and gaps."}, "item": [{"name": name, "item": items} for name, items in folders.items()]}
    environment = {"name": "local", "values": [{"key": key, "value": value, "enabled": True, "type": "secret" if SECRET.fullmatch(key) else "default"} for key, value in variables.items()], "_postman_variable_scope": "environment"}
    return collection, environment


def render(data, output):
    validate(data)
    data = sanitize(copy.deepcopy(data))
    output = Path(output)
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())), "Output directory must be new or empty")
    files = markdown_files(data)
    if data["preferences"]["json"]:
        files["api-trailmap.json"] = dump(data) + "\n"
    if data["preferences"]["postman"]:
        collection, environment = postman(data)
        files["postman/api.postman_collection.json"] = dump(collection) + "\n"
        if data["preferences"]["variables"]:
            files["postman/local.postman_environment.json"] = dump(environment) + "\n"
    if data["preferences"]["html"]:
        template = (ROOT / "assets" / "viewer.html").read_text(encoding="utf-8")
        embedded = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        files["api-trailmap.html"] = template.replace("__TRAILMAP_DATA__", embedded)
    # All contents are prepared before creating the destination.
    for name, content in files.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        validate(data)
        if args.validate_only:
            print("Inventory semantic checks passed. " + dump(coverage(data)))
        else:
            require(args.output is not None, "--output is required for generation")
            files = render(data, args.output)
            print("Generated offline; no API operations executed:\n" + "\n".join(files))
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(1, f"API Trailmap: {error}\n")


if __name__ == "__main__":
    main()
