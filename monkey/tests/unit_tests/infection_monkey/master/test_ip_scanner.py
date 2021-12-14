from threading import Barrier, Event
from typing import Set
from unittest.mock import MagicMock

import pytest

from infection_monkey.i_puppet import FingerprintData, PortScanData, PortStatus
from infection_monkey.master import IPScanner
from infection_monkey.puppet.mock_puppet import MockPuppet

WINDOWS_OS = "windows"
LINUX_OS = "linux"


@pytest.fixture
def scan_config():
    return {
        "tcp": {
            "timeout_ms": 3000,
            "ports": [
                22,
                445,
                3389,
                443,
                8008,
                3306,
            ],
        },
        "icmp": {
            "timeout_ms": 1000,
        },
        "fingerprinters": {"HTTPFinger", "SMBFinger", "SSHFinger"},
    }


@pytest.fixture
def stop():
    return Event()


@pytest.fixture
def callback():
    return MagicMock()


def assert_port_status(port_scan_data, expected_open_ports: Set[int]):
    for psd in port_scan_data.values():
        if psd.port in expected_open_ports:
            assert psd.status == PortStatus.OPEN
        else:
            assert psd.status == PortStatus.CLOSED


def assert_scan_results(ip, scan_results):
    ping_scan_data = scan_results.ping_scan_data
    port_scan_data = scan_results.port_scan_data
    fingerprint_data = scan_results.fingerprint_data

    if ip == "10.0.0.1":
        assert_scan_results_no_1(ping_scan_data, port_scan_data, fingerprint_data)
    elif ip == "10.0.0.3":
        assert_scan_results_no_3(ping_scan_data, port_scan_data, fingerprint_data)
    else:
        assert_scan_results_host_down(ip, ping_scan_data, port_scan_data, fingerprint_data)


def assert_scan_results_no_1(ping_scan_data, port_scan_data, fingerprint_data):
    assert ping_scan_data.response_received is True
    assert ping_scan_data.os == WINDOWS_OS

    assert len(port_scan_data.keys()) == 6

    psd_445 = port_scan_data[445]
    psd_3389 = port_scan_data[3389]

    assert psd_445.port == 445
    assert psd_445.banner == "SMB BANNER"
    assert psd_445.service == "tcp-445"

    assert psd_3389.port == 3389
    assert psd_3389.banner == ""
    assert psd_3389.service == "tcp-3389"

    assert_port_status(port_scan_data, {445, 3389})
    assert_fingerprint_results_no_1(fingerprint_data)


def assert_fingerprint_results_no_1(fingerprint_data):
    assert len(fingerprint_data.keys()) == 3
    assert fingerprint_data["SSHFinger"].services == {}
    assert fingerprint_data["HTTPFinger"].services == {}

    assert fingerprint_data["SMBFinger"].os_type == WINDOWS_OS
    assert fingerprint_data["SMBFinger"].os_version == "vista"

    assert len(fingerprint_data["SMBFinger"].services.keys()) == 1
    assert fingerprint_data["SMBFinger"].services["tcp-445"]["name"] == "smb_service_name"


def assert_scan_results_no_3(ping_scan_data, port_scan_data, fingerprint_data):
    assert ping_scan_data.response_received is True
    assert ping_scan_data.os == LINUX_OS
    assert len(port_scan_data.keys()) == 6

    psd_443 = port_scan_data[443]
    psd_22 = port_scan_data[22]

    assert psd_443.port == 443
    assert psd_443.banner == "HTTPS BANNER"
    assert psd_443.service == "tcp-443"

    assert psd_22.port == 22
    assert psd_22.banner == "SSH BANNER"
    assert psd_22.service == "tcp-22"

    assert_port_status(port_scan_data, {22, 443})
    assert_fingerprint_results_no_3(fingerprint_data)


def assert_fingerprint_results_no_3(fingerprint_data):
    assert len(fingerprint_data.keys()) == 3
    assert fingerprint_data["SMBFinger"].services == {}

    assert fingerprint_data["SSHFinger"].os_type == LINUX_OS
    assert fingerprint_data["SSHFinger"].os_version == "ubuntu"

    assert len(fingerprint_data["SSHFinger"].services.keys()) == 1
    assert fingerprint_data["SSHFinger"].services["tcp-22"]["name"] == "SSH"
    assert fingerprint_data["SSHFinger"].services["tcp-22"]["banner"] == "SSH BANNER"

    assert len(fingerprint_data["HTTPFinger"].services.keys()) == 2
    assert fingerprint_data["HTTPFinger"].services["tcp-80"]["name"] == "http"
    assert fingerprint_data["HTTPFinger"].services["tcp-80"]["data"] == ("SERVER_HEADERS", False)
    assert fingerprint_data["HTTPFinger"].services["tcp-443"]["name"] == "http"
    assert fingerprint_data["HTTPFinger"].services["tcp-443"]["data"] == ("SERVER_HEADERS_2", True)


def assert_scan_results_host_down(ip, ping_scan_data, port_scan_data, fingerprint_data):
    assert ip not in {"10.0.0.1", "10.0.0.3"}

    assert ping_scan_data.response_received is False
    assert len(port_scan_data.keys()) == 6
    assert_port_status(port_scan_data, set())

    assert fingerprint_data == {}


def test_scan_single_ip(callback, scan_config, stop):
    ips = ["10.0.0.1"]

    ns = IPScanner(MockPuppet(), num_workers=1)
    ns.scan(ips, scan_config, callback, stop)

    callback.assert_called_once()

    (ip, scan_results) = callback.call_args_list[0][0]
    assert_scan_results(ip, scan_results)


def test_scan_multiple_ips(callback, scan_config, stop):
    ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]

    ns = IPScanner(MockPuppet(), num_workers=4)
    ns.scan(ips, scan_config, callback, stop)

    assert callback.call_count == 4

    (ip, scan_results) = callback.call_args_list[0][0]
    assert_scan_results(ip, scan_results)

    (ip, scan_results) = callback.call_args_list[1][0]
    assert_scan_results(ip, scan_results)

    (ip, scan_results) = callback.call_args_list[2][0]
    assert_scan_results(ip, scan_results)

    (ip, scan_results) = callback.call_args_list[3][0]
    assert_scan_results(ip, scan_results)


def test_scan_lots_of_ips(callback, scan_config, stop):
    ips = [f"10.0.0.{i}" for i in range(0, 255)]

    ns = IPScanner(MockPuppet(), num_workers=4)
    ns.scan(ips, scan_config, callback, stop)

    assert callback.call_count == 255


def test_stop_after_callback(scan_config, stop):
    def _callback(*_):
        # Block all threads here until 2 threads reach this barrier, then set stop
        # and test that neither thread continues to scan.
        _callback.barrier.wait()
        stop.set()

    _callback.barrier = Barrier(2)

    stopable_callback = MagicMock(side_effect=_callback)

    ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]

    ns = IPScanner(MockPuppet(), num_workers=2)
    ns.scan(ips, scan_config, stopable_callback, stop)

    assert stopable_callback.call_count == 2


def test_interrupt_port_scanning(callback, scan_config, stop):
    def stopable_scan_tcp_port(port, *_):
        # Block all threads here until 2 threads reach this barrier, then set stop
        # and test that neither thread scans any more ports
        stopable_scan_tcp_port.barrier.wait()
        stop.set()

        return PortScanData(port, False, None, None)

    stopable_scan_tcp_port.barrier = Barrier(2)

    puppet = MockPuppet()
    puppet.scan_tcp_port = MagicMock(side_effect=stopable_scan_tcp_port)

    ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]

    ns = IPScanner(puppet, num_workers=2)
    ns.scan(ips, scan_config, callback, stop)

    assert puppet.scan_tcp_port.call_count == 2


def test_interrupt_fingerprinting(callback, scan_config, stop):
    def stopable_fingerprint(*_):
        # Block all threads here until 2 threads reach this barrier, then set stop
        # and test that neither thread scans any more ports
        stopable_fingerprint.barrier.wait()
        stop.set()

        return FingerprintData(None, None, {})

    stopable_fingerprint.barrier = Barrier(2)

    puppet = MockPuppet()
    puppet.fingerprint = MagicMock(side_effect=stopable_fingerprint)

    ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"]

    ns = IPScanner(puppet, num_workers=2)
    ns.scan(ips, scan_config, callback, stop)

    assert puppet.fingerprint.call_count == 2