from typing import Optional

from overhave.entities import (
    OverhaveDescriptionManagerSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveReportManagerSettings,
    OverhaveStepContextSettings,
)
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.scenario import OverhaveProjectSettings, OverhaveScenarioCompilerSettings, OverhaveScenarioParserSettings
from overhave.test_execution import OverhaveAdminLinkSettings, OverhaveTestSettings
from overhave.transport import OverhaveS3ManagerSettings


class OverhaveTestExecutionContext(BaseFactoryContext):
    """Overhave test run context, based on application BaseSettings.

    This context defines how Overhave test run will work.
    """

    def __init__(
        self,
        compilation_settings: Optional[OverhaveScenarioCompilerSettings] = None,
        parser_settings: Optional[OverhaveScenarioParserSettings] = None,
        description_manager_settings: Optional[OverhaveDescriptionManagerSettings] = None,
        file_settings: Optional[OverhaveFileSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
        report_manager_settings: Optional[OverhaveReportManagerSettings] = None,
        s3_manager_settings: Optional[OverhaveS3ManagerSettings] = None,
        step_context_settings: Optional[OverhaveStepContextSettings] = None,
        test_settings: Optional[OverhaveTestSettings] = None,
        admin_link_settings: Optional[OverhaveAdminLinkSettings] = None,
    ) -> None:
        super().__init__(
            compilation_settings=compilation_settings or OverhaveScenarioCompilerSettings(),
            parser_settings=parser_settings or OverhaveScenarioParserSettings(),
            file_settings=file_settings or OverhaveFileSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
            report_manager_settings=report_manager_settings or OverhaveReportManagerSettings(),
            s3_manager_settings=s3_manager_settings or OverhaveS3ManagerSettings(),
            test_settings=test_settings or OverhaveTestSettings(),
        )
        self.description_manager_settings = description_manager_settings or OverhaveDescriptionManagerSettings()
        self.step_context_settings = step_context_settings or OverhaveStepContextSettings()
        self.admin_link_settings = admin_link_settings or OverhaveAdminLinkSettings()
