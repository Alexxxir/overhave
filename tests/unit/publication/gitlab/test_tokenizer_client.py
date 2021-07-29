from typing import Callable

import pytest
from pydantic import ValidationError

from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings


class TestTokenizerClient:
    """ Tests for :class:`TokenizerClient`. """

    @pytest.mark.parametrize(("initiator", "vault_server_name"), [("kek", None), (None, "lol"), (None, None)])
    def test_tokenizer_settings_validation_raises_error(
        self, test_tokenizer_client_settings_factory: Callable[[], TokenizerClientSettings]
    ) -> None:
        with pytest.raises(ValidationError):
            test_tokenizer_client_settings_factory()

    @pytest.mark.parametrize(("initiator", "vault_server_name"), [("peka", "pepe")])
    def test_tokenizer_settings_validation_not_raises_error(
        self, test_tokenizer_client_settings_factory: Callable[[], TokenizerClientSettings]
    ) -> None:
        test_tokenizer_client_settings_factory()
