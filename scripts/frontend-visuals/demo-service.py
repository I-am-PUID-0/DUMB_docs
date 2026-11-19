#!/usr/bin/env python3
"""Run a disposable real Sonarr for embedded-UI documentation captures."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid

IMAGE = "lscr.io/linuxserver/sonarr@sha256:c7d1df25e428da6c9ace05daea0d34e59522978a3843ea1944812f855af4086c"
SONARR_VERSION = "4.0.20.3014"
LABEL = "io.dumb.docs.demo"
EXAMPLE_KEY = "0123456789abcdef0123456789abcdef"


def docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args], text=True, capture_output=True, check=check
    )


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(state, stream, indent=2)
        stream.write("\n")


def validate_owned(state: dict) -> None:
    identity = state.get("identity", "")
    if not re.fullmatch(r"[0-9a-f]{32}", identity):
        raise ValueError("Invalid demo identity")
    root = Path(state["data_root"])
    if root.is_symlink() or not root.name.startswith("dumb-docs-sonarr-"):
        raise ValueError("Demo directory is not task-owned")
    if (root / ".docs-demo").read_text().strip() != identity:
        raise ValueError("Demo directory marker does not match")
    identifier = state.get("container_id", "")
    if not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise ValueError("Invalid demo container identity")
    result = docker("inspect", identifier, check=False)
    if result.returncode:
        return
    records = json.loads(result.stdout)
    if len(records) != 1 or records[0]["Id"] != identifier:
        raise ValueError("Ambiguous demo container")
    record = records[0]
    if record["Config"].get("Labels", {}).get(LABEL) != identity:
        raise ValueError("Refusing to remove a container without its exact task label")
    binds = [
        mount for mount in record.get("Mounts", []) if mount.get("Type") == "bind"
    ]
    if len(binds) != 1 or binds[0].get("Source") != str(root / "config"):
        raise ValueError("Unexpected demo bind mounts")


def stop(path: Path) -> None:
    if not path.exists():
        print(json.dumps({"stopped": True, "already_absent": True}))
        return
    state = json.loads(path.read_text())
    validate_owned(state)
    identifier = state["container_id"]
    if docker("inspect", identifier, check=False).returncode == 0:
        docker("rm", "--force", "--volumes", identifier)
    if docker("inspect", identifier, check=False).returncode == 0:
        raise RuntimeError("Demo container still exists")
    shutil.rmtree(state["data_root"])
    path.unlink()
    print(json.dumps({"stopped": True, "application": "Sonarr"}))


def start(args: argparse.Namespace) -> None:
    if args.state.exists():
        raise ValueError("Use a new state file; an existing demo will not be replaced")
    if args.network_container:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.network_container):
            raise ValueError("Invalid network container name")
        network = "container:" + args.network_container
    else:
        network = "host"
    if not 1024 <= args.port <= 65535:
        raise ValueError("Use a nonprivileged loopback port")
    identity = uuid.uuid4().hex
    # The Docker daemon must see the same bind source: use the shared workspace
    # state directory rather than an execution sandbox's private /tmp.
    args.state.parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="dumb-docs-sonarr-", dir=args.state.parent)).resolve()
    config = root / "config"
    config.mkdir()
    (root / ".docs-demo").write_text(identity + "\n")
    (config / "config.xml").write_text(
        "<Config><BindAddress>127.0.0.1</BindAddress>"
        f"<Port>{args.port}</Port><SslPort>19898</SslPort>"
        "<EnableSsl>False</EnableSsl><LaunchBrowser>False</LaunchBrowser>"
        "<AuthenticationMethod>External</AuthenticationMethod>"
        "<AuthenticationRequired>Enabled</AuthenticationRequired>"
        f"<ApiKey>{EXAMPLE_KEY}</ApiKey><UrlBase>/sonarr</UrlBase>"
        "<InstanceName>Sonarr demonstration</InstanceName>"
        "<LogLevel>info</LogLevel><UpdateMechanism>Docker</UpdateMechanism>"
        "<UpdateAutomatically>False</UpdateAutomatically>"
        "<AnalyticsEnabled>False</AnalyticsEnabled></Config>\n"
    )
    state = {
        "schema_version": 1,
        "identity": identity,
        "data_root": str(root),
        "image": IMAGE,
        "network": network,
        "origin": f"http://127.0.0.1:{args.port}/sonarr",
    }
    try:
        result = docker(
            "run", "--detach", "--name", "dumb-docs-sonarr-" + identity[:12],
            "--label", LABEL + "=" + identity, "--network", network,
            "--memory", "768m", "--cpus", "0.5", "--pids-limit", "192",
            "--security-opt", "no-new-privileges:true",
            "--env", "PUID=" + str(os.getuid()),
            "--env", "PGID=" + str(os.getgid()), "--env", "TZ=UTC",
            "--env", "DOTNET_PROCESSOR_COUNT=2",
            "--mount", f"type=bind,source={config},target=/config",
            "--tmpfs", "/downloads", "--tmpfs", "/tv", IMAGE, check=False,
        )
        identifier = result.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{64}", identifier):
            found = docker("ps", "--all", "--quiet", "--no-trunc", "--filter", "label=" + LABEL + "=" + identity).stdout.splitlines()
            if len(found) == 1:
                identifier = found[0]
        if not re.fullmatch(r"[0-9a-f]{64}", identifier):
            raise RuntimeError("Docker could not create the isolated demo: " + result.stderr.strip())
        state["container_id"] = identifier
        write_state(args.state, state)
        if result.returncode:
            raise RuntimeError("Docker could not start the isolated demo: " + result.stderr.strip())
        status_url = state["origin"] + "/api/v3/system/status"
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            response = docker(
                "exec", state["container_id"], "curl", "--fail", "--silent",
                "--connect-timeout", "2", "--max-time", "3",
                "--header", "X-Api-Key: " + EXAMPLE_KEY, status_url, check=False,
            )
            if response.returncode == 0:
                status = json.loads(response.stdout)
                if status.get("version") == SONARR_VERSION and status.get("appName") == "Sonarr":
                    state["application"] = "Sonarr"
                    state["version"] = status["version"]
                    # Replace only the private task state created above.
                    args.state.write_text(json.dumps(state, indent=2) + "\n")
                    print(json.dumps({
                        "ready": True, "application": "Sonarr",
                        "version": state["version"], "image": IMAGE,
                        "origin": state["origin"],
                    }))
                    return
            time.sleep(1)
        raise RuntimeError("The isolated Sonarr did not become ready")
    except Exception:
        if args.state.exists():
            stop(args.state)
        elif not state.get("container_id"):
            shutil.rmtree(root)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "stop", "status"))
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--port", type=int, default=18989)
    network = parser.add_mutually_exclusive_group()
    network.add_argument("--network-host", action="store_true")
    network.add_argument("--network-container")
    args = parser.parse_args()
    if args.action == "start":
        if not (args.network_host or args.network_container):
            parser.error("Choose --network-host or --network-container explicitly")
        start(args)
    elif args.action == "stop":
        stop(args.state)
    else:
        state = json.loads(args.state.read_text())
        validate_owned(state)
        print(json.dumps({key: state[key] for key in ("origin", "image", "version")}))


if __name__ == "__main__":
    main()
