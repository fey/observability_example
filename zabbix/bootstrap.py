import json
import sys
import time
from urllib import error, request

API_URL = "http://zabbix-web:8080/api_jsonrpc.php"
USERNAME = "Admin"
PASSWORD = "zabbix"
HOST_NAME = "zabbix-agent"
GROUP_NAME = "Observability Demo"
TEMPLATE_NAME = "Linux by Zabbix agent"


def rpc(method, params, auth=None, req_id=1):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": req_id,
    }
    if auth:
        payload["auth"] = auth

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        API_URL,
        data=body,
        headers={"Content-Type": "application/json-rpc"},
        method="POST",
    )

    with request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    if "error" in data:
        raise RuntimeError(f"API error in {method}: {data['error']}")
    return data["result"]


def wait_for_api():
    for _ in range(120):
        try:
            rpc("apiinfo.version", {}, req_id=0)
            return
        except Exception:
            time.sleep(2)
    raise TimeoutError("Zabbix API did not become ready in time")


def ensure_group(auth):
    groups = rpc(
        "hostgroup.get",
        {
            "filter": {"name": [GROUP_NAME]},
            "output": ["groupid", "name"],
        },
        auth=auth,
        req_id=2,
    )
    if groups:
        return groups[0]["groupid"]
    result = rpc("hostgroup.create", {"name": GROUP_NAME}, auth=auth, req_id=3)
    return result["groupids"][0]


def get_template_id(auth):
    templates = rpc(
        "template.get",
        {
            "filter": {"host": [TEMPLATE_NAME]},
            "output": ["templateid", "host"],
        },
        auth=auth,
        req_id=4,
    )
    if not templates:
        raise RuntimeError(f"Template not found: {TEMPLATE_NAME}")
    return templates[0]["templateid"]


def ensure_host(auth, group_id, template_id):
    hosts = rpc(
        "host.get",
        {
            "filter": {"host": [HOST_NAME]},
            "output": ["hostid", "host"],
        },
        auth=auth,
        req_id=5,
    )
    if hosts:
        print(f"Host already exists: {HOST_NAME}")
        return hosts[0]["hostid"]

    result = rpc(
        "host.create",
        {
            "host": HOST_NAME,
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 0,
                    "ip": "",
                    "dns": "zabbix-agent",
                    "port": "10050",
                }
            ],
            "groups": [{"groupid": group_id}],
            "templates": [{"templateid": template_id}],
        },
        auth=auth,
        req_id=6,
    )
    host_id = result["hostids"][0]
    print(f"Created host {HOST_NAME} with id={host_id}")
    return host_id


def main():
    try:
        wait_for_api()
        token = rpc(
            "user.login",
            {"username": USERNAME, "password": PASSWORD},
            req_id=1,
        )
        group_id = ensure_group(token)
        template_id = get_template_id(token)
        ensure_host(token, group_id, template_id)
        rpc("user.logout", [], auth=token, req_id=7)
        print("Zabbix bootstrap completed")
    except (TimeoutError, RuntimeError, error.URLError) as exc:
        print(f"Bootstrap failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
