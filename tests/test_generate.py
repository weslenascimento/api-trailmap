import copy
import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate", ROOT / "scripts/generate.py")
gen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen)


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/inventory.json").read_text(encoding="utf-8"))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "out"

    def test_all_modes_preserve_operations_and_local_links(self):
        for mode in ("general", "category", "endpoint"):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.data)
                data["preferences"]["organization"] = mode
                output = self.output / mode
                gen.render(data, output)
                for doc in output.rglob("*.md"):
                    for link in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
                        path = link.split("#")[0]
                        if path:
                            self.assertTrue((doc.parent / path).exists(), link)
                text = "\n".join(p.read_text(encoding="utf-8") for p in output.rglob("*.md"))
                for op in data["operations"]:
                    self.assertIn(op["path"], text)

    def test_html_without_json_and_injection_is_inert(self):
        self.data["preferences"]["json"] = False
        self.data["operations"][0]["summary"] = '</script><script>window.BAD=true</script>'
        gen.render(self.data, self.output)
        self.assertFalse((self.output / "api-trailmap.json").exists())
        text = (self.output / "api-trailmap.html").read_text(encoding="utf-8")
        embedded = re.search(r'<script id="inventory" type="application/json">(.*?)</script>', text, re.S)[1]
        self.assertNotIn("</script>", embedded)
        self.assertEqual(json.loads(embedded)["operations"][0]["summary"], self.data["operations"][0]["summary"])
        script = re.findall(r"<script>(.*?)</script>", text, re.S)[0]
        js = Path(self.temp.name) / "viewer.js"
        js.write_text(script, encoding="utf-8")
        result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dangling_and_duplicate_references_rejected(self):
        for edit in (lambda d: d["relationships"][0].update(to="missing"), lambda d: d["operations"].append(copy.deepcopy(d["operations"][0]))):
            data = copy.deepcopy(self.data)
            edit(data)
            with self.assertRaises(ValueError):
                gen.validate(data)

    def test_capture_requires_evidence_and_options(self):
        for edit in (lambda d: d["preferences"].update(variables=False), lambda d: d["operations"][0]["captures"][0].update(evidence=[]), lambda d: d["operations"][0]["captures"][0].update(successCodes=[])):
            data = copy.deepcopy(self.data)
            edit(data)
            with self.assertRaises(ValueError):
                gen.validate(data)

    def test_redaction_preserves_schema_and_clears_values(self):
        self.data["operations"][0]["requestBody"]["password"] = "DO-NOT-EXPORT"
        gen.render(self.data, self.output)
        for path in self.output.rglob("*"):
            if path.is_file():
                self.assertNotIn("DO-NOT-EXPORT", path.read_text(encoding="utf-8"))
        exported = json.loads((self.output / "api-trailmap.json").read_text(encoding="utf-8"))
        self.assertEqual(exported["operations"][0]["contract"]["requestBody"]["properties"]["password"]["type"], "string")

    def test_no_overwrite(self):
        self.output.mkdir()
        sentinel = self.output / "user.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            gen.render(self.data, self.output)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_option_independence_and_no_unresolved_variables(self):
        for variables in (False, True):
            for scripts in (False, True):
                data = copy.deepcopy(self.data)
                data["operations"][0].pop("captures")
                data["preferences"].update(variables=variables, scripts=scripts)
                output = self.output / f"{variables}-{scripts}"
                gen.render(data, output)
                self.assertEqual((output / "postman/local.postman_environment.json").exists(), variables)
                collection = json.loads((output / "postman/api.postman_collection.json").read_text())
                text = json.dumps(collection)
                refs = set(re.findall(r"\{\{([^{}]+)\}\}", text))
                if variables:
                    environment = json.loads((output / "postman/local.postman_environment.json").read_text())
                    self.assertTrue(refs.issubset({item["key"] for item in environment["values"]}))
                else:
                    self.assertFalse(refs)

    def test_capture_runtime_success_and_failure_clear_stale_token(self):
        collection, _ = gen.postman(self.data)
        item = collection["item"][0]["item"][0]
        hooks = {event["listen"]: "\n".join(event["script"]["exec"]) for event in item["event"]}
        # Exercise generated hooks with a small Postman API test double, without network.
        js = """
const assert = require('node:assert/strict');
for (const code of [200, 401]) {
  const values = new Map([['access_token','STALE']]); let failed = false;
  const pm = {environment:{unset:k=>values.delete(k),set:(k,v)=>values.set(k,v)},response:{code,json:()=>({access_token:'NEW'})},test:(name,fn)=>{try{fn()}catch(e){failed=true}},expect:v=>({to:{include:x=>assert.ok(v.includes(x)),equal:x=>assert.equal(v,x)}})};
  eval(BEFORE); assert.equal(values.has('access_token'), false);
  eval(AFTER);
  assert.equal(values.get('access_token'), code===200?'NEW':undefined);
  assert.equal(failed, code!==200);
}
""".replace("BEFORE", json.dumps(hooks["prerequest"])).replace("AFTER", json.dumps(hooks["test"]))
        path = Path(self.temp.name) / "hooks.cjs"
        path.write_text(js, encoding="utf-8")
        result = subprocess.run(["node", str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_coverage_dimensions_and_excluded_accounting(self):
        self.data["operations"][1].update(excluded=True, exclusionReason="Outside execution scope", blocked=True)
        gen.render(self.data, self.output)
        self.assertEqual(gen.coverage(self.data), {"discovered": 2, "documented": 2, "executed": 0, "blocked": 1, "excluded": 1})
        collection, _ = gen.postman(self.data)
        self.assertEqual(sum(len(folder["item"]) for folder in collection["item"]), 1)
        text = "\n".join(p.read_text(encoding="utf-8") for p in self.output.rglob("*.md"))
        self.assertIn("Outside execution scope", text)


if __name__ == "__main__":
    unittest.main()
