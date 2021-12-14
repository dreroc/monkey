import logging
import threading
import time
from typing import Any, Callable, Dict, List, Tuple

from infection_monkey.i_control_channel import IControlChannel
from infection_monkey.i_master import IMaster
from infection_monkey.i_puppet import IPuppet
from infection_monkey.telemetry.messengers.i_telemetry_messenger import ITelemetryMessenger
from infection_monkey.telemetry.post_breach_telem import PostBreachTelem
from infection_monkey.telemetry.system_info_telem import SystemInfoTelem
from infection_monkey.utils.timer import Timer

from . import IPScanner, Propagator
from .threading_utils import create_daemon_thread

CHECK_ISLAND_FOR_STOP_COMMAND_INTERVAL_SEC = 5
CHECK_FOR_TERMINATE_INTERVAL_SEC = CHECK_ISLAND_FOR_STOP_COMMAND_INTERVAL_SEC / 5
SHUTDOWN_TIMEOUT = 5
NUM_SCAN_THREADS = 16  # TODO: Adjust this to the optimal number of scan threads

logger = logging.getLogger()


class AutomatedMaster(IMaster):
    def __init__(
        self,
        puppet: IPuppet,
        telemetry_messenger: ITelemetryMessenger,
        control_channel: IControlChannel,
    ):
        self._puppet = puppet
        self._telemetry_messenger = telemetry_messenger
        self._control_channel = control_channel

        ip_scanner = IPScanner(self._puppet, NUM_SCAN_THREADS)
        self._propagator = Propagator(self._telemetry_messenger, ip_scanner)

        self._stop = threading.Event()
        self._master_thread = create_daemon_thread(target=self._run_master_thread)
        self._simulation_thread = create_daemon_thread(target=self._run_simulation)

    def start(self):
        logger.info("Starting automated breach and attack simulation")
        self._master_thread.start()
        self._master_thread.join()
        logger.info("The simulation has been shutdown.")

    def terminate(self):
        logger.info("Stopping automated breach and attack simulation")
        self._stop.set()

        if self._master_thread.is_alive():
            self._master_thread.join()

    def _run_master_thread(self):
        self._simulation_thread.start()

        self._wait_for_master_stop_condition()

        logger.debug("Waiting for the simulation thread to stop")
        self._simulation_thread.join(SHUTDOWN_TIMEOUT)

        if self._simulation_thread.is_alive():
            logger.warning("Timed out waiting for the simulation to stop")
            # Since the master thread and all child threads are daemon threads, they will be
            # forcefully killed when the program exits.
            # TODO: Daemon threads to not die when the parent THREAD does, but when the parent
            #       PROCESS does. This could lead to conflicts between threads that refuse to die
            #       and the cleanup() function. Come up with a solution.
            logger.warning("Forcefully killing the simulation")

    def _wait_for_master_stop_condition(self):
        timer = Timer()
        timer.set(CHECK_ISLAND_FOR_STOP_COMMAND_INTERVAL_SEC)

        while self._master_thread_should_run():
            if timer.is_expired():
                # TODO: Handle exceptions in _check_for_stop() once
                #       ControlChannel.should_agent_stop() is refactored.
                self._check_for_stop()
                timer.reset()

            time.sleep(CHECK_FOR_TERMINATE_INTERVAL_SEC)

    def _check_for_stop(self):
        if self._control_channel.should_agent_stop():
            logger.debug('Received the "stop" signal from the Island')
            self._stop.set()

    def _master_thread_should_run(self):
        return (not self._stop.is_set()) and self._simulation_thread.is_alive()

    def _run_simulation(self):
        config = self._control_channel.get_config()

        system_info_collector_thread = create_daemon_thread(
            target=self._run_plugins,
            args=(
                config["system_info_collector_classes"],
                "system info collector",
                self._collect_system_info,
            ),
        )
        pba_thread = create_daemon_thread(
            target=self._run_plugins,
            args=(config["post_breach_actions"].items(), "post-breach action", self._run_pba),
        )

        system_info_collector_thread.start()
        pba_thread.start()

        # Future stages of the simulation require the output of the system info collectors. Nothing
        # requires the output of PBAs, so we don't need to join on that thread here. We will join on
        # the PBA thread later in this function to prevent the simulation from ending while PBAs are
        # still running.
        system_info_collector_thread.join()

        if self._can_propagate():
            self._propagator.propagate(config["propagation"], self._stop)

        payload_thread = create_daemon_thread(
            target=self._run_plugins,
            args=(config["payloads"].items(), "payload", self._run_payload),
        )
        payload_thread.start()
        payload_thread.join()

        pba_thread.join()

        # TODO: This code is just for testing in development. Remove when
        # 		implementation of AutomatedMaster is finished.
        while True:
            time.sleep(2)
            logger.debug("Simulation thread is finished sleeping")
            if self._stop.is_set():
                break

    def _collect_system_info(self, collector: str):
        system_info_telemetry = {}
        system_info_telemetry[collector] = self._puppet.run_sys_info_collector(collector)
        self._telemetry_messenger.send_telemetry(
            SystemInfoTelem({"collectors": system_info_telemetry})
        )

    def _run_pba(self, pba: Tuple[str, Dict]):
        name = pba[0]
        options = pba[1]

        command, result = self._puppet.run_pba(name, options)
        self._telemetry_messenger.send_telemetry(PostBreachTelem(name, command, result))

    def _can_propagate(self):
        return True

    def _run_payload(self, payload: Tuple[str, Dict]):
        name = payload[0]
        options = payload[1]

        self._puppet.run_payload(name, options, self._stop)

    def _run_plugins(self, plugin: List[Any], plugin_type: str, callback: Callable[[Any], None]):
        logger.info(f"Running {plugin_type}s")
        logger.debug(f"Found {len(plugin)} {plugin_type}(s) to run")

        for p in plugin:
            if self._stop.is_set():
                logger.debug(f"Received a stop signal, skipping remaining {plugin_type}s")
                return

            callback(p)

        logger.info(f"Finished running {plugin_type}s")

    def cleanup(self):
        pass