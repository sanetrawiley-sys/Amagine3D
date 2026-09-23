from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEXT = ROOT / "skills" / "a3d-text"
PUBLIC = ROOT / "skills" / "a3d-public"
COLOR = PUBLIC / "color"


class SharedSkillFileTests(unittest.TestCase):
    def test_shared_runtime_is_not_a_third_skill(self):
        self.assertTrue((PUBLIC / "cad_compile.py").is_file())
        self.assertTrue((PUBLIC / "build_session.py").is_file())
        self.assertTrue((PUBLIC / "geometry_binding.py").is_file())
        self.assertFalse((PUBLIC / "SKILL.md").exists())
        body = (TEXT / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(body, r"(?m)^name:\s*a3d-text\s*$")
        self.assertIn("$AMAGINE3D_SKILL_DIR/SKILL.md", body)
        self.assertFalse((TEXT / "cad_compile.py").exists())
        self.assertFalse((TEXT / "color").exists())
        self.assertFalse((TEXT / "references").exists())

    def test_shared_entrypoints_exist_only_in_runtime(self):
        shared_entrypoints = (
            "bambu_profile.py",
            "cad_diagnostics.py",
            "compare_silhouette.py",
            "cpu_z_buffer.py",
            "freshness_check.py",
            "mesh_topology.py",
            "reference_analyze.py",
            "render_preview.py",
        )
        for relative in shared_entrypoints:
            with self.subTest(path=relative):
                self.assertTrue((PUBLIC / relative).is_file())
                self.assertFalse((TEXT / relative).exists())
                self.assertFalse((COLOR / relative).exists())

    def test_shared_profiles_and_printability_reference_exist_only_in_runtime(self):
        shared_resources = (
            "references/bambu-printability.md",
            "references/bambu-profiles.json",
            "references/evidence-contract.md",
            "references/multipart-connections.md",
        )
        for relative in shared_resources:
            with self.subTest(path=relative):
                self.assertTrue((PUBLIC / relative).is_file())
        self.assertTrue((TEXT / "examples" / "bambu-a1-mini-0.4-standard.example.json").is_file())

    def test_color_runtime_is_one_shared_namespace(self):
        command = (
            "import sys; "
            f"sys.path.insert(0, {str(PUBLIC)!r}); "
            "import cad_helpers; "
            "from color import cad_helpers as color_helpers; "
            "assert hasattr(cad_helpers, 'export_assembly'); "
            "assert hasattr(color_helpers, 'export_regions'); "
            "assert cad_helpers.__file__ != color_helpers.__file__"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command], capture_output=True, check=False, text=True
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_text_skill_is_pure_brep(self):
        skill = (TEXT / "SKILL.md").read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", skill)
        for fragment in (
            "BuildSession",
            "constructionFeatures",
            "a3d-workflow:v2",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized)
        for forbidden in (
            "Blender",
            "blender-mesh",
            "HybridBuildSession",
            "build_blender_shell",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, skill)
        self.assertTrue((TEXT / "examples" / "simple_brep_build.py").is_file())
        self.assertTrue((TEXT / "examples" / "installed_module_draft.py").is_file())

    def test_common_references_are_loaded_from_runtime(self):
        for relative in (
            "references/authoring-example.md",
            "references/bambu-printability.md",
            "references/bambu-profiles.json",
            "references/evidence-contract.md",
            "references/multipart-connections.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((PUBLIC / relative).is_file())
        body = (TEXT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("$AMAGINE3D_RUNTIME_DIR/references/", body)
        self.assertIn("$AMAGINE3D_RUNTIME_DIR/color/BACKEND.md", body)

    def test_skill_workflow_structure_and_example_routing(self):
        skill = (TEXT / "SKILL.md").read_text(encoding="utf-8")
        marker = (
            "a3d-workflow:v2 classify > functional-draft > feedback > contract > "
            "compile > evidence-repair"
        )
        self.assertEqual(skill.count(marker), 1)
        self.assertEqual(skill.count("$AMAGINE3D_SKILL_DIR/SKILL.md"), 1)
        normalized = re.sub(r"\s+", " ", skill)
        self.assertIn("never substitute a cwd or global namesake", normalized)

        headings = (
            "## 1. Classify and draft visible construction",
            "## 2. Use visible and functional feedback",
            "## 3. Finalize the contract and construction",
            "## 4. Run the initial full compile",
            "## 5. Diagnose and make evidence-gated repairs",
        )
        positions = [skill.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertGreater(skill.index("\na3d compile "), positions[2])

        early = skill[positions[0]:positions[2]]
        contract = skill[positions[2]:positions[3]]
        self.assertIn("simple_brep_build.py", early)
        self.assertIn("installed_module_draft.py", early)
        self.assertIn("**functional skeleton**", early)
        self.assertIn("constructionFeatures", early)
        self.assertNotIn("installed_module_build.py", early)
        self.assertIn("installed_module_build.py", contract)

    def test_skill_local_links_exist(self):
        skill = (TEXT / "SKILL.md").read_text(encoding="utf-8")
        references = set(
            re.findall(
                r"(?:references|examples|color)/[A-Za-z0-9_.\-/]+",
                skill,
            )
        )
        self.assertTrue(references)
        for relative in references:
            with self.subTest(path=relative):
                base = TEXT if relative.startswith("examples/") else PUBLIC
                self.assertTrue((base / relative).is_file())

    def test_authoring_example_runs_with_separate_skill_and_runtime_roots(self):
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            shutil.copyfile(
                TEXT / "examples" / "simple_brep_intent.py",
                workspace / "model_intent.py",
            )
            shutil.copyfile(
                TEXT / "examples" / "bambu-a1-mini-0.4-standard.example.json",
                workspace / "model_printer-profile.json",
            )
            completed = subprocess.run(
                [sys.executable, str(workspace / "model_intent.py")],
                capture_output=True,
                check=False,
                env={
                    **os.environ,
                    "AMAGINE3D_RUNTIME_DIR": str(PUBLIC),
                    "AMAGINE3D_SKILL_DIR": str(TEXT),
                    "PYTHONPATH": str(PUBLIC),
                },
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((workspace / "model_intent.json").is_file())


if __name__ == "__main__":
    unittest.main()
