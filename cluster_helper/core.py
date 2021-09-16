import os
import ray

from plnet.util import init_ray


@ray.remote(num_cpus=os.cpu_count())
def install_wheel_local(wheel_path: str, install_deps: bool = False) -> None:
    os.system(f"/snap/bin/gsutil cp {wheel_path} /tmp")
    wheel_filename = os.path.basename(wheel_path)
    pip_cmd = f"sudo /opt/conda/default/bin/pip install /tmp/{wheel_filename} --force-reinstall"
    if not install_deps:
        pip_cmd = f"{pip_cmd} --no-deps"
    os.system(pip_cmd)


def install_wheel_cluster(wheel_path, install_deps: bool) -> None:
    init_ray(distributed=True)
    ray.get([
        install_wheel_local.remote(wheel_path=wheel_path, install_deps=install_deps)
        for _ in range(len(ray.nodes()))
    ])


if __name__ == "__main__":
    install_wheel_cluster("gs://plnet/data/wheel/plnet-0.1-py3-none-any.whl", False)
