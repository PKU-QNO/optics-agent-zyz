"""Hardened local importer for Magnus FileSecret COMSOL case bundles.

The importer is deliberately deterministic: archives are inspected before any
member is written, a case manifest names the one model input, and the complete
sanitised case tree is promoted atomically under a content-addressed directory.
No Magnus API calls are made here; the runner owns the receive operation.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class CaseImportError(RuntimeError):
    """A user-visible, stable importer failure."""

    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ImportLimits:
    max_members: int = 512
    max_member_bytes: int = 256 * 1024 * 1024
    max_total_bytes: int = 1024 * 1024 * 1024
    max_manifest_bytes: int = 1024 * 1024
    max_compression_ratio: float = 1000.0


@dataclass(frozen=True)
class StageResult:
    bundle_kind: str
    bundle_sha256: str
    input_sha256: str
    case_root: Path
    input_file: Path
    receipt_path: Path
    reused: bool


_SHA256 = 64
_ALLOWED_SUFFIXES = {
    "batch_java": {".java"},
    "batch_mph": {".mph"},
    "batch_mfile": {".m"},
}
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def _fail(code: str, message: str) -> None:
    raise CaseImportError(code, message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value.strip()) != _SHA256:
        _fail("INVALID_SHA256", f"{label} must be a 64-character hexadecimal SHA-256")
    value = value.strip().lower()
    try:
        int(value, 16)
    except ValueError:
        _fail("INVALID_SHA256", f"{label} must be a 64-character hexadecimal SHA-256")
    return value


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("CASE_MANIFEST_INVALID", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def safe_relative_path(raw: object, *, label: str = "path") -> PurePosixPath:
    """Normalise an archive/manifest path while rejecting traversal forms."""

    if not isinstance(raw, str) or not raw or "\x00" in raw:
        _fail("UNSAFE_MEMBER_PATH", f"{label} is not a valid relative path")
    candidate = raw.replace("\\", "/")
    if len(candidate) > 4096:
        _fail("UNSAFE_MEMBER_PATH", f"{label} is too long")
    if candidate.startswith("/") or candidate.startswith("//"):
        _fail("UNSAFE_MEMBER_PATH", f"{label} is absolute")
    if len(candidate) >= 2 and candidate[1] == ":" and candidate[0].isalpha():
        _fail("UNSAFE_MEMBER_PATH", f"{label} contains a drive prefix")
    parts = []
    for part in candidate.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            _fail("UNSAFE_MEMBER_PATH", f"{label} contains parent traversal")
        if len(part) > 255 or any(ord(char) < 32 for char in part):
            _fail("UNSAFE_MEMBER_PATH", f"{label} contains an invalid path component")
        if ":" in part or part.endswith((" ", ".")):
            _fail("UNSAFE_MEMBER_PATH", f"{label} is unsafe on Windows")
        if part.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
            _fail("UNSAFE_MEMBER_PATH", f"{label} uses a reserved device name")
        parts.append(part)
    if not parts or len(parts) > 128:
        _fail("UNSAFE_MEMBER_PATH", f"{label} is empty")
    return PurePosixPath(*parts)


def _is_within(root: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _ensure_regular_path(root: Path, relative: PurePosixPath) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            _fail("UNSAFE_MEMBER_PATH", f"symlink in selected path: {relative.as_posix()}")
    if not _is_within(root, current):
        _fail("UNSAFE_MEMBER_PATH", f"selected path escapes case root: {relative.as_posix()}")
    return current


def _validate_member_count(count: int, limits: ImportLimits) -> None:
    if count > limits.max_members:
        _fail("ARCHIVE_MEMBER_LIMIT", f"archive contains {count} members; limit is {limits.max_members}")


def _validate_size(size: int, total: int, limits: ImportLimits) -> int:
    if size < 0 or size > limits.max_member_bytes:
        _fail("ARCHIVE_MEMBER_SIZE_LIMIT", f"archive member size {size} exceeds limit")
    total += size
    if total > limits.max_total_bytes:
        _fail("ARCHIVE_TOTAL_SIZE_LIMIT", f"archive expands beyond {limits.max_total_bytes} bytes")
    return total


def _zip_entries(path: Path, limits: ImportLimits) -> list[tuple[zipfile.ZipInfo, PurePosixPath, bool]]:
    entries = []
    seen: set[str] = set()
    total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            _validate_member_count(len(infos), limits)
            for info in infos:
                relative = safe_relative_path(info.filename, label="zip member")
                key = relative.as_posix()
                if key in seen:
                    _fail("DUPLICATE_MEMBER", f"duplicate archive member: {key}")
                seen.add(key)
                mode = (info.external_attr >> 16) & 0xFFFF
                member_type = stat.S_IFMT(mode)
                is_dir = info.is_dir() or info.filename.endswith(("/", "\\"))
                if member_type == stat.S_IFLNK or (member_type not in (0, stat.S_IFREG, stat.S_IFDIR)):
                    _fail("UNSAFE_MEMBER_TYPE", f"unsupported zip member type: {key}")
                if not is_dir:
                    total = _validate_size(info.file_size, total, limits)
                    compressed = max(info.compress_size, 1)
                    if info.file_size / compressed > limits.max_compression_ratio:
                        _fail("ARCHIVE_COMPRESSION_RATIO", f"zip member compression ratio is excessive: {key}")
                entries.append((info, relative, is_dir))
    except zipfile.BadZipFile as exc:
        _fail("INVALID_ARCHIVE", f"invalid ZIP archive: {exc}")
    return entries


def _extract_zip(path: Path, target: Path, limits: ImportLimits) -> None:
    entries = _zip_entries(path, limits)
    try:
        with zipfile.ZipFile(path) as archive:
            for info, relative, is_dir in entries:
                destination = target.joinpath(*relative.parts)
                if not _is_within(target, destination):
                    _fail("UNSAFE_MEMBER_PATH", f"zip member escapes staging: {relative.as_posix()}")
                if is_dir:
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info, "r") as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    except CaseImportError:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        _fail("CASE_BUNDLE_UNPACK_FAILED", f"ZIP extraction failed: {exc}")


def _tar_entries(path: Path, limits: ImportLimits) -> list[tuple[tarfile.TarInfo, PurePosixPath, bool]]:
    entries = []
    seen: set[str] = set()
    total = 0
    try:
        with tarfile.open(path, mode="r:*") as archive:
            for index, member in enumerate(archive, start=1):
                _validate_member_count(index, limits)
                relative = safe_relative_path(member.name, label="tar member")
                key = relative.as_posix()
                if key in seen:
                    _fail("DUPLICATE_MEMBER", f"duplicate archive member: {key}")
                seen.add(key)
                if member.issym() or member.islnk() or member.isdev() or member.isfifo() or member.ischr() or member.isblk():
                    _fail("UNSAFE_MEMBER_TYPE", f"unsupported tar member type: {key}")
                is_dir = member.isdir()
                if not is_dir:
                    if not member.isreg():
                        _fail("UNSAFE_MEMBER_TYPE", f"unsupported tar member type: {key}")
                    total = _validate_size(member.size, total, limits)
                entries.append((member, relative, is_dir))
            archive_size = max(path.stat().st_size, 1)
            if total / archive_size > limits.max_compression_ratio:
                _fail("ARCHIVE_COMPRESSION_RATIO", "tar archive compression ratio is excessive")
    except (tarfile.TarError, EOFError) as exc:
        _fail("INVALID_ARCHIVE", f"invalid TAR archive: {exc}")
    return entries


def _extract_tar(path: Path, target: Path, limits: ImportLimits) -> None:
    entries = _tar_entries(path, limits)
    try:
        with tarfile.open(path, mode="r:*") as archive:
            for member, relative, is_dir in entries:
                destination = target.joinpath(*relative.parts)
                if not _is_within(target, destination):
                    _fail("UNSAFE_MEMBER_PATH", f"tar member escapes staging: {relative.as_posix()}")
                if is_dir:
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                source = archive.extractfile(member)
                if source is None:
                    _fail("CASE_BUNDLE_UNPACK_FAILED", f"tar member could not be read: {relative.as_posix()}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    except CaseImportError:
        raise
    except (OSError, RuntimeError, tarfile.TarError, EOFError) as exc:
        _fail("CASE_BUNDLE_UNPACK_FAILED", f"TAR extraction failed: {exc}")


def detect_bundle_kind(path: Path, requested_format: str = "auto") -> str:
    if path.is_dir():
        return "directory"
    if not path.is_file():
        _fail("BUNDLE_MISSING", f"received bundle does not exist: {path}")
    if requested_format in {"single", "single-file"}:
        return "single-file"
    if requested_format not in {"auto", "zip", "tar", "tgz"}:
        _fail("UNSUPPORTED_BUNDLE_FORMAT", f"unsupported case bundle format: {requested_format}")
    # A COMSOL .mph file is itself a ZIP container.  Preserve it as a single
    # model when the caller retained the extension; extensionless downloads
    # must use the explicit ``single-file`` format to avoid guessing.
    if requested_format == "auto" and path.suffix.lower() == ".mph":
        return "single-file"
    with path.open("rb") as handle:
        magic = handle.read(8)
    if requested_format == "zip":
        if not magic.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
            _fail("INVALID_ARCHIVE", "bundle_format=zip but input is not a ZIP archive")
        return "zip"
    if requested_format in {"tar", "tgz"}:
        try:
            if not tarfile.is_tarfile(path):
                _fail("INVALID_ARCHIVE", f"bundle_format={requested_format} but input is not a TAR archive")
        except (OSError, tarfile.TarError) as exc:
            _fail("INVALID_ARCHIVE", f"cannot inspect TAR archive: {exc}")
        if requested_format == "tgz" and not magic.startswith(b"\x1f\x8b"):
            _fail("INVALID_ARCHIVE", "bundle_format=tgz but input is not gzip-compressed")
        return requested_format
    if magic.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return "zip"
    if magic.startswith(b"\x1f\x8b"):
        try:
            if tarfile.is_tarfile(path):
                return "tgz"
        except (OSError, tarfile.TarError):
            pass
        _fail("UNSUPPORTED_BUNDLE_FORMAT", "gzip input is not a TAR archive")
    try:
        if tarfile.is_tarfile(path):
            return "tar"
    except (OSError, tarfile.TarError):
        pass
    return "single-file"


def _directory_digest(root: Path, limits: ImportLimits) -> tuple[str, list[dict]]:
    records = _file_records(root, limits)
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(record["size"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), records


def _file_records(root: Path, limits: ImportLimits) -> list[dict]:
    records: list[dict] = []
    total = 0
    member_count = 0
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(dirs)
        files = sorted(files)
        member_count += len(dirs) + len(files)
        _validate_member_count(member_count, limits)
        for name in dirs + files:
            candidate = current_path / name
            if candidate.is_symlink():
                _fail("UNSAFE_MEMBER_TYPE", f"symlink is not allowed: {candidate.relative_to(root)}")
        for name in files:
            candidate = current_path / name
            if not candidate.is_file():
                _fail("UNSAFE_MEMBER_TYPE", f"non-regular file is not allowed: {candidate.relative_to(root)}")
            info = candidate.lstat()
            if getattr(info, "st_nlink", 1) > 1:
                _fail("UNSAFE_MEMBER_TYPE", f"hard-linked file is not allowed: {candidate.relative_to(root)}")
            size = info.st_size
            total = _validate_size(size, total, limits)
            relative = PurePosixPath(candidate.relative_to(root).as_posix())
            records.append({"path": relative.as_posix(), "size": size, "sha256": sha256_file(candidate)})
    records.sort(key=lambda item: item["path"])
    return records


def _manifest_root(extracted: Path) -> Path:
    candidates = sorted(p for p in extracted.rglob("case_manifest.json") if p.is_file() and not p.is_symlink())
    if len(candidates) != 1:
        if not candidates:
            _fail("CASE_MANIFEST_MISSING", "archive case_manifest.json is required")
        _fail("CASE_MANIFEST_AMBIGUOUS", "archive contains multiple case_manifest.json files")
    return candidates[0].parent


def _load_manifest(case_root: Path, run_mode: str, limits: ImportLimits) -> tuple[PurePosixPath, str | None]:
    manifest_path = case_root / "case_manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        _fail("CASE_MANIFEST_MISSING", "archive case_manifest.json is required")
    if manifest_path.stat().st_size > limits.max_manifest_bytes:
        _fail("CASE_MANIFEST_TOO_LARGE", "case_manifest.json exceeds the manifest size limit")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_json_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("CASE_MANIFEST_INVALID", f"invalid case_manifest.json: {exc}")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        _fail("CASE_MANIFEST_INVALID", "case_manifest.json schema_version must be 1")
    model_value = payload.get("model_input")
    if not isinstance(model_value, str):
        _fail("CASE_MANIFEST_INVALID", "case_manifest.json must name one model_input")
    model_input = safe_relative_path(model_value, label="model_input")
    allowed = _ALLOWED_SUFFIXES.get(run_mode)
    if allowed and Path(model_input.name).suffix.lower() not in allowed:
        _fail("CASE_INPUT_TYPE_MISMATCH", f"model_input suffix is not valid for {run_mode}")
    input_path = _ensure_regular_path(case_root, model_input)
    if not input_path.is_file():
        _fail("INPUT_MISSING", f"manifest model_input does not exist: {model_input.as_posix()}")
    expected_input = payload.get("input_sha256")
    if expected_input is not None:
        expected_input = _validate_sha256(expected_input, "input_sha256")
    return model_input, expected_input


def _verify_receipt(target: Path, expected_input_sha256: str) -> dict:
    receipt_path = target / "staging_receipt.json"
    if not receipt_path.is_file():
        _fail("INPUT_STAGE_CORRUPT", f"canonical input staging is missing its receipt: {target}")
    if receipt_path.stat().st_mode & 0o222:
        _fail("INPUT_STAGE_CORRUPT", "canonical staging receipt is writable")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_STAGE_CORRUPT", f"invalid canonical staging receipt: {exc}")
    if not isinstance(receipt, dict) or receipt.get("schema_version") != 1:
        _fail("INPUT_STAGE_CORRUPT", "canonical staging receipt schema_version must be 1")
    try:
        receipt_input_sha256 = _validate_sha256(receipt.get("input_sha256"), "receipt input_sha256")
        _validate_sha256(receipt.get("bundle_sha256"), "receipt bundle_sha256")
    except CaseImportError as exc:
        _fail("INPUT_STAGE_CORRUPT", exc.message)
    if receipt_input_sha256 != expected_input_sha256:
        _fail("INPUT_STAGE_COLLISION", f"canonical input hash collision at {target}")
    model_rel = safe_relative_path(receipt.get("model_input"), label="receipt model_input")
    model_path = _ensure_regular_path(target, model_rel)
    if not model_path.is_file() or sha256_file(model_path) != expected_input_sha256:
        _fail("INPUT_STAGE_CORRUPT", f"canonical model input hash mismatch at {target}")
    records = receipt.get("files")
    if not isinstance(records, list):
        _fail("INPUT_STAGE_CORRUPT", "canonical staging receipt has no file inventory")
    expected_paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            _fail("INPUT_STAGE_CORRUPT", "canonical staging receipt has an invalid file record")
        rel = safe_relative_path(record.get("path"), label="receipt file")
        expected_paths.add(rel.as_posix())
        path = _ensure_regular_path(target, rel)
        if path.stat().st_mode & 0o222:
            _fail("INPUT_STAGE_CORRUPT", f"canonical staged file is writable: {rel.as_posix()}")
        if not path.is_file() or path.stat().st_size != record.get("size") or sha256_file(path) != record.get("sha256"):
            _fail("INPUT_STAGE_CORRUPT", f"canonical staged file mismatch: {rel.as_posix()}")
    actual_paths: set[str] = set()
    for candidate in target.rglob("*"):
        if _is_reparse_or_symlink(candidate):
            _fail("INPUT_STAGE_CORRUPT", f"canonical staging contains a symlink/junction: {candidate}")
        if candidate.is_file() and candidate.name != "staging_receipt.json":
            actual_paths.add(candidate.relative_to(target).as_posix())
    if actual_paths != expected_paths:
        _fail("INPUT_STAGE_CORRUPT", "canonical staged file inventory does not match its receipt")
    if target.stat().st_mode & 0o222:
        _fail("INPUT_STAGE_CORRUPT", "canonical staging directory is writable")
    return receipt


def _assert_same_case_tree(receipt: dict, incoming_records: list[dict], input_rel: PurePosixPath) -> None:
    if receipt.get("model_input") != input_rel.as_posix() or receipt.get("files") != incoming_records:
        _fail("INPUT_STAGE_COLLISION", "canonical input hash already exists with a different case tree")


def _is_reparse_or_symlink(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return bool(getattr(info, "st_file_attributes", 0) & reparse)


def _assert_no_reparse_chain(path: Path, *, label: str) -> None:
    current = Path(path)
    while True:
        if os.path.lexists(current) and _is_reparse_or_symlink(current):
            _fail("UNSAFE_SOURCE_PATH", f"{label} contains a symlink/junction: {current}")
        parent = current.parent
        if parent == current:
            return
        current = parent


def _cleanup_tree(path: Path) -> None:
    if not path.exists() and not os.path.lexists(path):
        return
    try:
        for child in path.rglob("*"):
            try:
                child.chmod(child.stat().st_mode | 0o200)
            except OSError:
                pass
        path.chmod(path.stat().st_mode | 0o700)
    except OSError:
        pass
    shutil.rmtree(path, ignore_errors=True)


def _copy_tree_verified(source_root: Path, records: list[dict], target: Path) -> None:
    for record in records:
        relative = safe_relative_path(record["path"], label="staged file")
        source = _ensure_regular_path(source_root, relative)
        destination = target.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if destination.stat().st_size != record["size"] or sha256_file(destination) != record["sha256"]:
            _fail("SOURCE_CHANGED", f"source changed while staging: {relative.as_posix()}")


def _freeze_readonly(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        try:
            mode = path.stat().st_mode
            path.chmod(mode & ~0o222)
        except OSError as exc:
            _fail("INPUT_STAGE_FREEZE_FAILED", f"cannot freeze canonical staging: {exc}")
    try:
        root.chmod(root.stat().st_mode & ~0o222)
    except OSError as exc:
        _fail("INPUT_STAGE_FREEZE_FAILED", f"cannot freeze canonical staging root: {exc}")


def stage_case_bundle(
    source: Path,
    input_root: Path,
    run_mode: str,
    *,
    expected_bundle_sha256: str | None = None,
    expected_input_sha256: str | None = None,
    requested_input: str | None = None,
    input_name: str | None = None,
    bundle_format: str = "auto",
    limits: ImportLimits = ImportLimits(),
) -> StageResult:
    """Receive-independent importer used by the runner and local tests."""

    source = Path(source)
    input_root = Path(input_root)
    _assert_no_reparse_chain(source, label="bundle source")
    if not source.exists():
        _fail("BUNDLE_MISSING", f"received bundle does not exist: {source}")
    _assert_no_reparse_chain(input_root, label="canonical input root")
    input_root.mkdir(parents=True, exist_ok=True)
    _assert_no_reparse_chain(input_root, label="canonical input root")
    if not input_root.is_dir():
        _fail("INPUT_ROOT_UNSAFE", f"canonical input root is not a directory: {input_root}")
    try:
        input_root.chmod(0o700)
    except OSError as exc:
        _fail("INPUT_ROOT_UNSAFE", f"canonical input root cannot be secured: {exc}")
    if expected_bundle_sha256 is not None:
        expected_bundle_sha256 = _validate_sha256(expected_bundle_sha256, "expected bundle SHA-256")
    if expected_input_sha256 is not None:
        expected_input_sha256 = _validate_sha256(expected_input_sha256, "expected input SHA-256")

    with tempfile.TemporaryDirectory(prefix=".case-import-", dir=str(input_root)) as temporary:
        workspace = Path(temporary)
        if source.is_dir():
            source_records = _file_records(source, limits)
            bundle_source = workspace / "bundle.snapshot"
            bundle_source.mkdir()
            _copy_tree_verified(source, source_records, bundle_source)
            snapshot_records = _file_records(bundle_source, limits)
            if snapshot_records != source_records:
                _fail("SOURCE_CHANGED", "directory bundle changed while creating its private snapshot")
        else:
            if not source.is_file():
                _fail("UNSAFE_SOURCE_PATH", f"bundle source is not a regular file: {source}")
            _validate_size(source.stat().st_size, 0, limits)
            suffix = source.suffix if source.suffix else ""
            bundle_source = workspace / f"bundle.snapshot{suffix}"
            shutil.copyfile(source, bundle_source)
        kind = detect_bundle_kind(bundle_source, bundle_format)
        extracted = workspace / "extracted"
        extracted.mkdir()
        bundle_sha256 = sha256_file(bundle_source) if kind != "directory" else ""
        if kind == "directory":
            bundle_sha256, _ = _directory_digest(bundle_source, limits)
        if expected_bundle_sha256 is not None and bundle_sha256 != expected_bundle_sha256:
            _fail("BUNDLE_SHA256_MISMATCH", "received case bundle SHA-256 does not match expected value")
        if kind == "zip":
            _extract_zip(bundle_source, extracted, limits)
            _file_records(extracted, limits)
            case_root = _manifest_root(extracted)
            input_rel, manifest_input_sha = _load_manifest(case_root, run_mode, limits)
        elif kind in {"tar", "tgz"}:
            _extract_tar(bundle_source, extracted, limits)
            _file_records(extracted, limits)
            case_root = _manifest_root(extracted)
            input_rel, manifest_input_sha = _load_manifest(case_root, run_mode, limits)
        elif kind == "directory":
            case_root = _manifest_root(bundle_source)
            input_rel, manifest_input_sha = _load_manifest(case_root, run_mode, limits)
        else:
            bundle_sha256 = sha256_file(bundle_source)
            selected_name = input_name or requested_input or source.name
            selected_path = safe_relative_path(selected_name, label="single-file input")
            suffix = Path(selected_path.name).suffix.lower()
            allowed = _ALLOWED_SUFFIXES.get(run_mode, set())
            if allowed and suffix not in allowed:
                if input_name is None:
                    _fail("CASE_INPUT_NAME_REQUIRED", f"single-file input needs an explicit input_name with a valid {run_mode} suffix")
                _fail("CASE_INPUT_TYPE_MISMATCH", f"single-file bundle suffix is not valid for {run_mode}")
            case_root = extracted
            input_rel = selected_path
            single_target = extracted.joinpath(*selected_path.parts)
            single_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundle_source, single_target)
            manifest_input_sha = None

        if requested_input is not None:
            requested_rel = safe_relative_path(requested_input, label="requested input_file")
            if requested_rel != input_rel:
                _fail("CASE_INPUT_CONFLICT", "input_file conflicts with case_manifest.json model_input")
        if input_name is not None:
            input_name_rel = safe_relative_path(input_name, label="input_name")
            if input_name_rel != input_rel:
                _fail("CASE_INPUT_CONFLICT", "input_name conflicts with case_manifest.json model_input")

        records = _file_records(case_root, limits)
        input_path = _ensure_regular_path(case_root, input_rel)
        input_sha256 = sha256_file(input_path)
        if manifest_input_sha is not None and input_sha256 != manifest_input_sha:
            _fail("INPUT_SHA256_MISMATCH", "model input SHA-256 does not match case_manifest.json")
        if expected_input_sha256 is not None and input_sha256 != expected_input_sha256:
            _fail("INPUT_SHA256_MISMATCH", "model input SHA-256 does not match expected value")
        target = input_root / input_sha256
        if os.path.lexists(target):
            if _is_reparse_or_symlink(target):
                _fail("INPUT_STAGE_COLLISION", f"canonical input path is a symlink/junction: {target}")
            if not target.is_dir():
                _fail("INPUT_STAGE_COLLISION", f"canonical input path is not a directory: {target}")
            receipt = _verify_receipt(target, input_sha256)
            _assert_same_case_tree(receipt, records, input_rel)
            return StageResult(kind, bundle_sha256, input_sha256, target, target.joinpath(*input_rel.parts), target / "staging_receipt.json", True)

        staging = input_root / f".{input_sha256}.staging-{uuid.uuid4().hex}"
        try:
            staging.mkdir()
            _copy_tree_verified(case_root, records, staging)
            if _file_records(staging, limits) != records:
                _fail("SOURCE_CHANGED", "staged case tree does not match the verified source tree")
            receipt = {
                "schema_version": 1,
                "bundle_kind": kind,
                "bundle_sha256": bundle_sha256,
                "expected_bundle_sha256": expected_bundle_sha256,
                "model_input": input_rel.as_posix(),
                "input_sha256": input_sha256,
                "input_size": input_path.stat().st_size,
                "source_name": source.name,
                "files": records,
                "promotion_path": str(target),
                "created_at_unix": int(time.time()),
            }
            (staging / "staging_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
            # Freeze before publication so there is no writable canonical
            # window and a freeze failure cannot leave a half-promoted target.
            _freeze_readonly(staging)
            try:
                staging.rename(target)
            except FileExistsError:
                if _is_reparse_or_symlink(target):
                    _fail("INPUT_STAGE_COLLISION", f"canonical input path is a symlink/junction: {target}")
                existing = _verify_receipt(target, input_sha256)
                _assert_same_case_tree(existing, records, input_rel)
                _cleanup_tree(staging)
                return StageResult(kind, bundle_sha256, input_sha256, target, target.joinpath(*input_rel.parts), target / "staging_receipt.json", True)
        except CaseImportError:
            _cleanup_tree(staging)
            raise
        except OSError as exc:
            _cleanup_tree(staging)
            _fail("PROMOTION_FAILED", f"atomic canonical input promotion failed: {exc}")

        return StageResult(kind, bundle_sha256, input_sha256, target, target.joinpath(*input_rel.parts), target / "staging_receipt.json", False)
