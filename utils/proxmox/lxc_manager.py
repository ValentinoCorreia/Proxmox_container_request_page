import requests

from os import getenv

from models.connection import db


NETWORK = "name=eth0,bridge=vmbr0,ip=dhcp,type=veth"
VERIFY_SSL = False

# conf env
PVE_NODE = getenv("PROXMOX_NODE","pve1")
ARCH = getenv("PROXMOX_ARCH","amd64")
CONTAINER_ROOT_STORAGE = getenv("PROXMOX_CONTAINER_ROOT_STORAGE","local-lvm")
PVE_ADDRESS = getenv("PROXMOX_ADDRESS", "192.168.56.130:8006")

if getenv("PROXMOX_API_TOKEN") == None:
    print("PROXMOX_API_TOKEN variable is not set.")
    exit()
else:
    API_TOKEN = getenv("PROXMOX_API_TOKEN")


# api request methods

def getNextVMID():
    url = f"https://{PVE_ADDRESS}/api2/json/cluster/nextid"

    headers = {
        "Authorization": "PVEAPIToken=" + API_TOKEN
    }

    response = requests.request("GET", url, headers=headers, verify=VERIFY_SSL)
    if (response.status_code != 200):
        raise Exception("error while getting next VMID")
    return response.json()["data"]

def createLXCContainer(container):
    url = f"https://{PVE_ADDRESS}/api2/json/nodes/{PVE_NODE}/lxc"

    next_lxc_id = getNextVMID()

    querystring = {
        "ostemplate": container.template.proxmox_os_template,
        "vmid": next_lxc_id,
        "arch": ARCH,
        "cpulimit": int(container.cpu_limit),
        "memory": int(container.ram),
        "hostname": str(container.name),
        "password": str(container.initial_root_password),
        "start": "0",
        "storage": CONTAINER_ROOT_STORAGE,
        "net0": NETWORK,
    }
    print(querystring)
    headers = {
        "Authorization": "PVEAPIToken=" + API_TOKEN
    }

    response = requests.request(
        "POST", url, headers=headers, params=querystring, verify=VERIFY_SSL
    )
    if (response.status_code == 200):
        return next_lxc_id
    else:
        raise Exception("Error while creating the new container: \n" + response.text)



def getLXCContainerStatus(lxc_id: int):
    url = f"https://{PVE_ADDRESS}/api2/json/nodes/{PVE_NODE}/lxc/{lxc_id}/status/current"

    headers = {"Authorization": "PVEAPIToken=" + API_TOKEN}

    response = requests.request("GET", url, headers=headers, verify=VERIFY_SSL)

    if (response.status_code == 200):
      return response.json()["data"]
    else:
        raise Exception("Error while getting the container status: \n" + response.text)


def StartLXCContainer(lxc_id: int):
    return LXCContainerAction(lxc_id, "start")

def StopLXCContainer(lxc_id: int):
    return LXCContainerAction(lxc_id, "shutdown")


def LXCContainerAction(lxc_id: int, action: str):
    url = f"https://{PVE_ADDRESS}/api2/json/nodes/{PVE_NODE}/lxc/{lxc_id}/status/{action}"

    headers = {"Authorization": "PVEAPIToken=" + API_TOKEN}

    response = requests.request("POST", url, headers=headers, verify=VERIFY_SSL)
    if (not response.status_code == 200):
        print(response.text, url)
    return response.status_code == 200

def getLXCContainerSpiceProxy(lxc_id: int):
    url = f"https://{PVE_ADDRESS}/api2/json/nodes/{PVE_NODE}/lxc/{lxc_id}/spiceproxy"

    headers = {
        "Authorization": "PVEAPIToken=" + API_TOKEN,
    }

    response = requests.request("POST", url, headers=headers, verify=VERIFY_SSL)

    if (response.status_code == 200):
      return response.json()["data"]
    else:
        raise Exception("Error while getting the container Spice Proxy: \n" + response.text)
