from __future__ import annotations

import json
import os
import stat
import tarfile
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from case_importer import CaseImportError, ImportLimits, sha256_file, stage_case_bundle


class CaseImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input_root = self.root / "inputs"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def manifest(self, model: str = "model.java", input_sha256: str | None = None) -> bytes:
        payload = {"schema_version": 1, "model_input": model}
        if input_sha256:
            payload["input_sha256"] = input_sha256
        return json.dumps(payload).encode("utf-8")

    def write_zip(self, path: Path, members: dict[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in members.items():
                archive.writestr(name, content)

    def write_tar(self, path: Path, members: dict[str, bytes], mode: str = "w") -> None:
        with tarfile.open(path, mode) as archive:
            for name, content in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                import io
                archive.addfile(info, io.BytesIO(content))

    def test_zip_magic_and_atomic_reuse(self) -> None:
        bundle = self.root / "upload-without-extension"
        model = b"public class Demo { public static Model run() { return null; } }\n"
        self.write_zip(bundle, {"case_manifest.json": self.manifest(), "model.java": model, "params.json": b"{}"})
        expected = sha256_file(bundle)
        first = stage_case_bundle(bundle, self.input_root, "batch_java", expected_bundle_sha256=expected)
        self.assertFalse(first.reused)
        self.assertEqual(first.input_file.read_bytes(), model)
        receipt = json.loads(first.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["bundle_sha256"], expected)
        self.assertEqual(receipt["input_sha256"], first.input_sha256)
        self.assertNotIn("magnus-secret", first.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(first.input_file.stat().st_mode & stat.S_IWUSR, 0)
        second = stage_case_bundle(bundle, self.input_root, "batch_java")
        self.assertTrue(second.reused)
        self.assertEqual(second.input_file, first.input_file)

    def test_tar_and_tgz_are_detected_by_magic(self) -> None:
        members = {"case_manifest.json": self.manifest("model.m"), "model.m": b"disp('ok')"}
        for name, mode in (("plain-upload", "w"), ("gzip-upload", "w:gz")):
            with self.subTest(name=name):
                bundle = self.root / name
                self.write_tar(bundle, members, mode)
                result = stage_case_bundle(bundle, self.input_root / name, "batch_mfile")
                self.assertEqual(result.input_file.read_bytes(), b"disp('ok')")

    def test_single_file_extensionless_requires_explicit_format(self) -> None:
        bundle = self.root / "secret-download"
        bundle.write_bytes(b"class Demo {}\n")
        with self.assertRaisesRegex(CaseImportError, "CASE_INPUT_NAME_REQUIRED"):
            stage_case_bundle(bundle, self.input_root, "batch_java")
        result = stage_case_bundle(bundle, self.input_root, "batch_java", bundle_format="single-file", input_name="model.java")
        self.assertEqual(result.input_file.read_bytes(), bundle.read_bytes())

    def test_mph_zip_container_can_be_single_model(self) -> None:
        bundle = self.root / "model.mph"
        self.write_zip(bundle, {"document.xml": b"COMSOL placeholder"})
        result = stage_case_bundle(bundle, self.input_root, "batch_mph")
        self.assertEqual(result.input_file.read_bytes(), bundle.read_bytes())

    def test_wrong_hash_and_manifest_input_hash_fail(self) -> None:
        bundle = self.root / "case.zip"
        model = b"model"
        self.write_zip(bundle, {"case_manifest.json": self.manifest("model.mph", "0" * 64), "model.mph": model})
        with self.assertRaisesRegex(CaseImportError, "BUNDLE_SHA256_MISMATCH"):
            stage_case_bundle(bundle, self.input_root, "batch_mph", expected_bundle_sha256="1" * 64)
        with self.assertRaisesRegex(CaseImportError, "INPUT_SHA256_MISMATCH"):
            stage_case_bundle(bundle, self.input_root, "batch_mph")
        with self.assertRaisesRegex(CaseImportError, "INVALID_SHA256"):
            stage_case_bundle(bundle, self.input_root, "batch_mph", expected_bundle_sha256="not-a-hash")

    def test_zip_slip_and_duplicate_paths_fail(self) -> None:
        slip = self.root / "slip.zip"
        self.write_zip(slip, {"case_manifest.json": self.manifest(), "../escape.java": b"x"})
        with self.assertRaisesRegex(CaseImportError, "UNSAFE_MEMBER_PATH"):
            stage_case_bundle(slip, self.input_root, "batch_java")
        duplicate = self.root / "duplicate.zip"
        with zipfile.ZipFile(duplicate, "w") as archive:
            archive.writestr("case_manifest.json", self.manifest())
            archive.writestr("dir/model.java", b"a")
            archive.writestr("dir\\model.java", b"b")
        with self.assertRaisesRegex(CaseImportError, "DUPLICATE_MEMBER"):
            stage_case_bundle(duplicate, self.input_root, "batch_java")

    def test_archive_symlink_and_hardlink_fail(self) -> None:
        symlink = self.root / "symlink.tar"
        with tarfile.open(symlink, "w") as archive:
            info = tarfile.TarInfo("case_manifest.json")
            content = self.manifest()
            info.size = len(content)
            import io
            archive.addfile(info, io.BytesIO(content))
            link = tarfile.TarInfo("model.java")
            link.type = tarfile.SYMTYPE
            link.linkname = "elsewhere"
            archive.addfile(link)
        with self.assertRaisesRegex(CaseImportError, "UNSAFE_MEMBER_TYPE"):
            stage_case_bundle(symlink, self.input_root, "batch_java")
        hardlink = self.root / "hardlink.tar"
        with tarfile.open(hardlink, "w") as archive:
            link = tarfile.TarInfo("model.java")
            link.type = tarfile.LNKTYPE
            link.linkname = "other.java"
            archive.addfile(link)
        with self.assertRaisesRegex(CaseImportError, "UNSAFE_MEMBER_TYPE"):
            stage_case_bundle(hardlink, self.input_root, "batch_java")

    def test_manifest_missing_or_conflicting_input_fails(self) -> None:
        bundle = self.root / "missing.zip"
        self.write_zip(bundle, {"model.java": b"x"})
        with self.assertRaisesRegex(CaseImportError, "CASE_MANIFEST_MISSING"):
            stage_case_bundle(bundle, self.input_root, "batch_java")
        bundle2 = self.root / "conflict.zip"
        self.write_zip(bundle2, {"case_manifest.json": self.manifest("model.java"), "model.java": b"x"})
        with self.assertRaisesRegex(CaseImportError, "CASE_INPUT_CONFLICT"):
            stage_case_bundle(bundle2, self.input_root, "batch_java", requested_input="other.java")

    def test_limits_and_directory_symlink(self) -> None:
        bundle = self.root / "many.zip"
        self.write_zip(bundle, {f"{i}.txt": b"x" for i in range(4)})
        with self.assertRaisesRegex(CaseImportError, "ARCHIVE_MEMBER_LIMIT"):
            stage_case_bundle(bundle, self.input_root, "batch_java", limits=ImportLimits(max_members=2))
        directory = self.root / "directory"
        directory.mkdir()
        (directory / "case_manifest.json").write_bytes(self.manifest())
        (directory / "model.java").write_bytes(b"x")
        try:
            os.symlink(directory / "model.java", directory / "link.java")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this Windows host")
        with self.assertRaisesRegex(CaseImportError, "UNSAFE_MEMBER_TYPE"):
            stage_case_bundle(directory, self.input_root, "batch_java")

    def test_compression_ratio_and_member_size_limits(self) -> None:
        bomb = self.root / "bomb.zip"
        self.write_zip(bomb, {"case_manifest.json": self.manifest(), "model.java": b"A" * 100_000})
        with self.assertRaisesRegex(CaseImportError, "ARCHIVE_COMPRESSION_RATIO"):
            stage_case_bundle(bomb, self.input_root, "batch_java", limits=ImportLimits(max_compression_ratio=5.0))
        with self.assertRaisesRegex(CaseImportError, "ARCHIVE_MEMBER_SIZE_LIMIT"):
            stage_case_bundle(bomb, self.input_root, "batch_java", limits=ImportLimits(max_member_bytes=1024))

    def test_same_input_hash_with_different_case_tree_is_rejected(self) -> None:
        model = b"same model"
        first = self.root / "first.zip"
        second = self.root / "second.zip"
        self.write_zip(first, {"case_manifest.json": self.manifest(), "model.java": model, "params.json": b"1"})
        self.write_zip(second, {"case_manifest.json": self.manifest(), "model.java": model, "params.json": b"2"})
        stage_case_bundle(first, self.input_root, "batch_java")
        with self.assertRaisesRegex(CaseImportError, "INPUT_STAGE_COLLISION"):
            stage_case_bundle(second, self.input_root, "batch_java")

    def test_existing_target_extra_file_is_rejected(self) -> None:
        bundle = self.root / "case-extra.zip"
        self.write_zip(bundle, {"case_manifest.json": self.manifest(), "model.java": b"model"})
        result = stage_case_bundle(bundle, self.input_root, "batch_java")
        result.case_root.chmod(result.case_root.stat().st_mode | stat.S_IWUSR)
        (result.case_root / "injected.txt").write_text("bad", encoding="utf-8")
        with self.assertRaisesRegex(CaseImportError, "INPUT_STAGE_CORRUPT"):
            stage_case_bundle(bundle, self.input_root, "batch_java")

    def test_promotion_failure_leaves_no_canonical_or_staging_directory(self) -> None:
        bundle = self.root / "case-promotion.zip"
        self.write_zip(bundle, {"case_manifest.json": self.manifest(), "model.java": b"model"})
        with mock.patch.object(Path, "rename", side_effect=OSError("injected rename failure")):
            with self.assertRaisesRegex(CaseImportError, "PROMOTION_FAILED"):
                stage_case_bundle(bundle, self.input_root, "batch_java")
        leftovers = [path.name for path in self.input_root.iterdir()]
        self.assertFalse(any(".staging-" in name for name in leftovers), leftovers)
        self.assertFalse(any(len(name) == 64 for name in leftovers), leftovers)

    def test_runner_secret_is_connected_to_canonical_input(self) -> None:
        import comsol_runner

        bundle = self.root / "case.zip"
        self.write_zip(bundle, {"case_manifest.json": self.manifest(), "model.java": b"class Demo {}"})
        run_dir = self.root / "run"
        (run_dir / "raw").mkdir(parents=True)
        args = SimpleNamespace(
            case_bundle_secret="magnus-secret:do-not-log",
            run_mode="batch_java",
            input_file=None,
            case_path=None,
            input_root=self.input_root,
            case_bundle_sha256="",
            case_input_sha256="",
            case_input_name="",
            case_bundle_format="auto",
        )
        original = comsol_runner.receive_secret
        try:
            def fake_receive(secret: str, dest: Path) -> Path:
                self.assertEqual(secret, args.case_bundle_secret)
                dest.write_bytes(bundle.read_bytes())
                return dest
            comsol_runner.receive_secret = fake_receive
            info = comsol_runner.import_case_bundle_for_run(args, run_dir)
        finally:
            comsol_runner.receive_secret = original
        self.assertIsNotNone(info)
        self.assertTrue(args.input_file.is_file())
        self.assertEqual(args.input_file, Path(info["canonical_input_file"]))
        self.assertNotIn("do-not-log", (run_dir / "case_import_receipt.json").read_text(encoding="utf-8"))

    def test_runner_rejects_persistent_input_and_secret_conflict(self) -> None:
        import comsol_runner

        run_dir = self.root / "run-conflict"
        (run_dir / "raw").mkdir(parents=True)
        args = SimpleNamespace(
            case_bundle_secret="magnus-secret:fake",
            run_mode="batch_java",
            input_file=str(self.root / "model.java"),
            case_path=None,
            input_root=self.input_root,
            case_bundle_sha256="",
            case_input_sha256="",
            case_input_name="",
            case_bundle_format="auto",
        )
        with self.assertRaises(Exception) as context:
            comsol_runner.import_case_bundle_for_run(args, run_dir)
        self.assertEqual(context.exception.code, "CASE_INPUT_CONFLICT")


if __name__ == "__main__":
    unittest.main()
