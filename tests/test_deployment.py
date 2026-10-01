import pytest
from orchai.deployment.manager import DeploymentManager, DeploymentRequest

def test_deployment_manager_get_target():
    mgr = DeploymentManager()
    target = mgr.get_target("local")
    assert target is not None
    assert target.type == "local_docker"
    
def test_deployment_manager_deploy_success():
    mgr = DeploymentManager()
    req = DeploymentRequest(task_id="test", target_id="local")
    res = mgr.deploy(req)
    assert res.success is True
    assert res.status == "DEPLOYED"

def test_deployment_manager_deploy_unknown_target():
    mgr = DeploymentManager()
    req = DeploymentRequest(task_id="test", target_id="unknown")
    res = mgr.deploy(req)
    assert res.success is False
    assert res.status == "FAILED"
