import pytest
from tests.monkey_island import InMemoryAgentPluginRepository
from tests.unit_tests.common.agent_plugins.test_agent_plugin_manifest import FAKE_NAME, FAKE_NAME2
from tests.unit_tests.monkey_island.cc.fake_agent_plugin_data import (
    FAKE_AGENT_PLUGIN_1,
    FAKE_AGENT_PLUGIN_2,
)

from monkey_island.cc.repositories import IAgentPluginRepository
from monkey_island.cc.services.agent_configuration_service.agent_configuration_schema_compiler import (  # noqa: E501
    AgentConfigurationSchemaCompiler,
)


@pytest.fixture
def agent_plugin_repository() -> IAgentPluginRepository:
    return InMemoryAgentPluginRepository()


@pytest.fixture
def config_schema_compiler(
    agent_plugin_repository: IAgentPluginRepository,
) -> AgentConfigurationSchemaCompiler:
    return AgentConfigurationSchemaCompiler(agent_plugin_repository)


def test_get_schema__adds_exploiter_plugins_to_schema(
    config_schema_compiler, agent_plugin_repository
):
    agent_plugin_repository.save_plugin(FAKE_AGENT_PLUGIN_1)
    agent_plugin_repository.save_plugin(FAKE_AGENT_PLUGIN_2)
    expected_fake_schema1 = FAKE_AGENT_PLUGIN_1.config_schema
    expected_fake_schema1.update(FAKE_AGENT_PLUGIN_1.plugin_manifest.dict(simplify=True))

    expected_fake_schema2 = FAKE_AGENT_PLUGIN_2.config_schema
    expected_fake_schema2.update(FAKE_AGENT_PLUGIN_2.plugin_manifest.dict(simplify=True))

    actual_config_schema = config_schema_compiler.get_schema()

    assert (
        actual_config_schema["definitions"]["ExploitationConfiguration"]["properties"][
            "exploiters"
        ]["properties"][FAKE_NAME]
        == expected_fake_schema1
    )
    assert (
        actual_config_schema["definitions"]["ExploitationConfiguration"]["properties"][
            "exploiters"
        ]["properties"][FAKE_NAME2]
        == expected_fake_schema2
    )
