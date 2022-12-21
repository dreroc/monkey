import logging
import random
from ipaddress import IPv4Address
from threading import Event
from typing import Any, Dict, Sequence

import mock_dependency

from common.agent_events import ExploitationEvent, PropagationEvent
from common.event_queue import IAgentEventPublisher
from common.types import AgentID
from infection_monkey.exploit import IAgentBinaryRepository
from infection_monkey.i_puppet import ExploiterResultData
from infection_monkey.model import TargetHost

logger = logging.getLogger(__name__)


class Plugin:
    def __init__(
        self,
        agent_id: AgentID,
        agent_binary_repository: IAgentBinaryRepository,
        agent_event_publisher: IAgentEventPublisher,
        plugin_name="",
    ):
        self._agent_id = agent_id
        self._agent_binary_repository = agent_binary_repository
        self._agent_event_publisher = agent_event_publisher

    def run(
        self,
        host: TargetHost,
        servers: Sequence[str],
        current_depth: int,
        options: Dict[str, Any],
        interrupt: Event,
    ) -> ExploiterResultData:

        logger.info(f"Mock dependency package version: {mock_dependency.__version__}")

        event_fields = {
            "source": self._agent_id,
            "target": host.ip,
            "exploiter_name": "MockExploiter",
        }

        exploitation_success = self._exploit(options, event_fields)
        propagation_success = (
            False if not exploitation_success else self._propagate(options, event_fields)
        )

        logger.debug(f"Exploit success: {exploitation_success}")
        logger.debug(f"Prop success: {propagation_success}")
        logger.debug("OS: str(host.os)")
        exploiter_result_data = ExploiterResultData(
            exploitation_success=exploitation_success,
            propagation_success=propagation_success,
            os=str(host.operating_system),
        )
        logger.debug(f"Returning ExploiterResultData: {exploiter_result_data}")

        return exploiter_result_data

    def _exploit(self, options: Dict[str, Any], event_fields: Dict[str, Any]) -> bool:
        exploitation_success = _get_random_result_from_success_rate("exploitation", options)
        self._agent_event_publisher.publish(
            ExploitationEvent(
                success=exploitation_success,
                tags=frozenset(["mock-plugin-exploitation"]),
                **event_fields,
            )
        )

        return exploitation_success

    def _propagate(self, options: Dict[str, Any], event_fields: Dict[str, Any]) -> bool:
        propagation_success = _get_random_result_from_success_rate("propagation", options)
        self._agent_event_publisher.publish(
            PropagationEvent(
                success=propagation_success,
                tags=frozenset(["mock-plugin-propagation"]),
                **event_fields,
            )
        )

        return propagation_success


def _get_random_result_from_success_rate(result_name: str, options: Dict[str, Any]) -> bool:
    success_rate = options.get(f"{result_name}_success_rate", 50)
    success_weights = [success_rate, 100 - success_rate]

    return random.choices([True, False], success_weights)[0]  # noqa: DUO102
