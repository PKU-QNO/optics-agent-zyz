# COMSOL Runtime Admin Install Notes

Staging root:

```text
/data/public/zhangyuanzheng
```

Expected files:

```text
/data/public/zhangyuanzheng/
  comsol-runtime-6.3-zyz-v1.docker.tar
  comsol-runtime-image-manifest.json
  Optics_COMSOL_Runtime_zyz.magnus
  comsol-runtime/
    comsol_runner.py
    README.md
    secrets/comsol/license.dat
```

Current active image:

```text
docker://magnus-local/comsol-runtime:latest
```

This image was imported by the administrator through a different build/install
route than the original archive plan. It is about 1.38G and has passed COMSOL
smoke and solve jobs. Do not refresh, pull, overwrite, retag, or rebuild it
unless the administrator explicitly requests that.

Validated active-image jobs:

```text
de368ea77db7da7f  comsol-smoke-minimal                  Success
deb10848cb99128a  comsol-universal-licensemount-solve   Success
3681f26d40ccbf7b  comsol-Lmembrane-eigenmodes           Success
```

Load the Docker image on the target Magnus Docker/registry host:

```bash
docker load -i /data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar
docker image inspect comsol-runtime:6.3-zyz-v1
```

The original archive tag would be:

```text
docker://comsol-runtime:6.3-zyz-v1
```

The current blueprint default container image is:

```text
docker://magnus-local/comsol-runtime:latest
```

If Magnus requires another internal URI later, update the blueprint
`container_image` default or pass the final URI at launch time without
refreshing the active local image.

Runtime paths used by the blueprint:

```text
code_root=/data/public/zhangyuanzheng/comsol-runtime
license_path=/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
output_root=/home/magnus/data/optics_agent/comsol/runs
```

The blueprint mounts:

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
```

License file permission should remain private:

```bash
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol
chmod 600 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

Local validation already passed before staging:

```text
comsol -version
comsol batch -help
Python imports: numpy scipy pandas matplotlib h5py meshio mph jpype
comsol_runner.py env_check
```
