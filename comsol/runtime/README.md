# COMSOL Runtime Code Folder

This folder is staged in the Gustation public data area for administrator installation:

```text
/data/public/zhangyuanzheng/comsol-runtime
```

The public Magnus blueprint only calls `comsol_runner.py`. Put the COMSOL license on the server at:

```text
/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

Magnus job outputs should go to the writable job data area:

```text
/home/magnus/data/optics_agent/comsol/runs
```

Do not commit or share the license file. The folder includes a `.gitignore` that ignores `secrets/`.

Upload from Windows:

```powershell
python comsol\automation\sync_comsol_runtime_to_gustation.py --license-file "D:\docker-base\LMCOMSOL_Multiphysics_SSQ.lic"
```

After upload, the runner must exist at:

```text
/data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py
```

The blueprint default env check uses:

```text
code_root=/data/public/zhangyuanzheng/comsol-runtime
license_path=/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
output_root=/home/magnus/data/optics_agent/comsol/runs
container_image=docker://magnus-local/comsol-runtime:latest
```

Temporary `case_bundle_secret` inputs are staged by `comsol_runner.py` under:

```text
/home/magnus/data/optics_agent/comsol/inputs/<model_input_sha256>/
```

ZIP/TAR/TGZ bundles must contain a single `case_manifest.json` at the case
root, for example `{"schema_version": 1, "model_input": "model.java"}`.
The importer records `staging_receipt.json`, rejects traversal/link/device
members and archive limits, verifies optional bundle/input SHA-256 values, and
only then atomically publishes a read-only canonical tree. A single model with
an extensionless FileSecret download requires `case_bundle_format=single-file`
and `case_input_name=model.java` (or `.mph`/`.m`).

The active Magnus image was administrator-imported and is about 1.38G. Do not
refresh, pull, overwrite, retag, or rebuild it unless the administrator asks.
