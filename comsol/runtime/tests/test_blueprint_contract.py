from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class BlueprintContractTests(unittest.TestCase):
    def test_file_secret_and_importer_parameters_are_declared_and_forwarded(self) -> None:
        source = (PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py").read_text(encoding="utf-8")
        self.assertIn("Optional[FileSecret]", source)
        for name in ("case_bundle_sha256", "case_input_sha256", "case_input_name", "case_bundle_format"):
            self.assertIn(name, source)
            self.assertIn(f"--{name.replace('_', '-')}", source)

    def test_launch_does_not_save_file_secret_preferences(self) -> None:
        source = (PROJECT_ROOT / "comsol" / "automation" / "submit_comsol.py").read_text(encoding="utf-8")
        self.assertIn("use_preference=False", source)
        self.assertIn("save_preference=False", source)


if __name__ == "__main__":
    unittest.main()
