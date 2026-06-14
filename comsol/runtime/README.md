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

The active Magnus image was administrator-imported and is about 1.38G. Do not
refresh, pull, overwrite, retag, or rebuild it unless the administrator asks.
