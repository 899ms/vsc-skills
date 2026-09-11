"""Filesystem behavior and catalog integrity; no models or external services."""

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


discovery = load_module("discovery", ROOT / "vsc/scripts/discover_skills.py")
builder = load_module("builder", ROOT / "tools/build_vsc_catalog.py")


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.catalog = discovery.load_catalog(ROOT / "vsc/references/catalog.json")
        self.name = "summer-boyfriend-pov"

    def install(self, root, name=None):
        name = name or self.name
        target = root / name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name / "SKILL.md", target)
        return target

    def item(self, roots, name=None):
        return next(x for x in discovery.discover(self.catalog, roots)["skills"] if x["name"] == (name or self.name))

    def test_committed_catalog_is_current_and_covers_all_leaf_skills(self):
        self.assertEqual(builder.build_catalog(ROOT), self.catalog)
        expected = {p.parent.name for p in ROOT.glob("*/SKILL.md")} - {"vsc"}
        self.assertEqual(expected, {x["name"] for x in self.catalog["skills"]})

    def test_repository_install_all_available(self):
        items = discovery.discover(self.catalog, [ROOT])["skills"]
        self.assertTrue(all(x["status"] == "available" and not x["needs_review"] for x in items))

    def test_partial_install_does_not_claim_missing_skills(self):
        self.install(self.base)
        items = discovery.discover(self.catalog, [self.base])["skills"]
        self.assertEqual([self.name], [x["name"] for x in items if x["status"] == "available"])
        self.assertTrue(all(x["status"] == "missing" for x in items if x["name"] != self.name))

    def test_unregistered_skill_and_router_are_excluded(self):
        for name in ["vsc", "unrelated-photography"]:
            path = self.base / name / "SKILL.md"
            path.parent.mkdir()
            path.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
        items = discovery.discover(self.catalog, [self.base])["skills"]
        self.assertTrue(all(x["status"] == "missing" for x in items))
        self.assertFalse({"vsc", "unrelated-photography"} & {x["name"] for x in items})

    def test_standalone_router_works_without_repository_or_yaml(self):
        root = self.base / "standalone skills"
        shutil.copytree(ROOT / "vsc", root / "vsc")
        self.install(root)
        run = subprocess.run([sys.executable, "-S", str(root / "vsc/scripts/discover_skills.py"), "--root", str(root)], capture_output=True, text=True, cwd=self.base)
        self.assertEqual(0, run.returncode, run.stderr)
        items = json.loads(run.stdout)["skills"]
        available = [x for x in items if x["status"] == "available"]
        self.assertEqual([self.name], [x["name"] for x in available])
        self.assertTrue(Path(available[0]["path"]).is_file())

    def test_symlinked_installs_are_resolved_and_deduplicated(self):
        path = self.install(self.base / "a")
        alias = self.base / "b" / self.name
        alias.parent.mkdir()
        alias.symlink_to(path.parent, target_is_directory=True)
        item = self.item([self.base / "a", self.base / "b"])
        self.assertEqual("available", item["status"])
        self.assertEqual(str(path.resolve()), item["path"])

    def test_identical_copies_do_not_conflict(self):
        self.install(self.base / "a")
        self.install(self.base / "b")
        self.assertEqual("available", self.item([self.base / "a", self.base / "b"])["status"])

    def test_different_versions_conflict_until_root_is_explicit(self):
        self.install(self.base / "a")
        other = self.install(self.base / "b")
        other.write_text(other.read_text() + "\nLocal customization.\n")
        item = self.item([self.base / "a", self.base / "b"])
        self.assertEqual("conflict", item["status"])
        self.assertNotIn("path", item)
        self.assertEqual(2, len(item["paths"]))
        self.assertEqual("available", self.item([self.base / "a"])["status"])

    def test_stale_catalog_requests_review_of_installed_definition(self):
        path = self.install(self.base)
        path.write_text(path.read_text() + "\nUpdated behavior.\n")
        item = self.item([self.base])
        self.assertEqual("available", item["status"])
        self.assertTrue(item["needs_review"])

    def test_windows_line_endings_do_not_create_version_conflict(self):
        self.install(self.base / "a")
        path = self.install(self.base / "b")
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        item = self.item([self.base / "a", self.base / "b"])
        self.assertEqual("available", item["status"])
        self.assertFalse(item["needs_review"])

    def test_broken_link_is_invalid(self):
        (self.base / self.name).symlink_to(self.base / "absent", target_is_directory=True)
        self.assertEqual("invalid", self.item([self.base])["status"])

    def test_wrong_declared_name_and_bad_encoding_are_invalid(self):
        path = self.install(self.base)
        path.write_text("---\nname: other-skill\n---\n")
        self.assertEqual("invalid", self.item([self.base])["status"])
        path.write_bytes(b"\xff")
        self.assertEqual("invalid", self.item([self.base])["status"])

    def test_custom_codex_home_and_project_local_roots(self):
        project = self.base / "project"
        (project / ".git").mkdir(parents=True)
        work = project / "subdirectory"
        work.mkdir()
        custom = self.base / "custom codex"
        self.install(custom / "skills")
        roots = discovery.default_roots(self.base / "router/vsc", self.base / "home", work, {"CODEX_HOME": str(custom)})
        self.assertIn(project / ".agents/skills", roots)
        self.assertIn(custom / "skills", roots)
        self.assertNotIn(self.base / "home/.codex/skills", roots)
        self.assertEqual("available", self.item(roots)["status"])

    def test_catalog_rejects_path_traversal_and_duplicates(self):
        for name in ["../external", "vsc", self.catalog["skills"][1]["name"]]:
            catalog = copy.deepcopy(self.catalog)
            catalog["skills"][0]["name"] = name
            target = self.base / "catalog.json"
            target.write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):
                discovery.load_catalog(target)

    def test_new_skill_requires_routing_metadata(self):
        path = self.base / "new-skill/SKILL.md"
        path.parent.mkdir()
        path.write_text("---\nname: new-skill\ndescription: A new skill.\n---\n")
        with self.assertRaisesRegex(ValueError, "路由字段"):
            builder.build_catalog(self.base)

    def test_multiline_yaml_is_supported_at_build_time(self):
        self.install(self.base)
        path = self.base / self.name / "SKILL.md"
        text = path.read_text()
        lines = text.splitlines()
        lines[2] = "description: >\n  First line\n  second line"
        path.write_text("\n".join(lines) + "\n")
        self.assertEqual("First line second line\n", builder.build_catalog(self.base)["skills"][0]["description"])

    def test_incomplete_catalog_fails_instead_of_exposing_bad_candidates(self):
        for key in ["description", "category", "deliverables", "distinction", "sha256"]:
            catalog = copy.deepcopy(self.catalog)
            del catalog["skills"][0][key]
            target = self.base / "catalog.json"
            target.write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):
                discovery.load_catalog(target)


if __name__ == "__main__":
    unittest.main()
