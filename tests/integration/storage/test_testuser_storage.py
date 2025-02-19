import pytest
from faker import Faker

from overhave import db
from overhave.storage import (
    FeatureTypeModel,
    SystemUserModel,
    TestUserDoesNotExistError,
    TestUserModel,
    TestUserSpecification,
    TestUserStorage,
    TestUserUpdatingNotAllowedError,
)


class TestTestUserStorage:
    """Integration tests for :class:`TestUserStorage`."""

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_test_user_by_id(self, test_user_storage: TestUserStorage, test_testuser: TestUserModel) -> None:
        test_user = test_user_storage.get_test_user_by_id(test_testuser.id)
        assert test_user is not None
        assert test_user == test_testuser

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_user_by_name(self, test_user_storage: TestUserStorage, test_testuser: TestUserModel) -> None:
        test_user = test_user_storage.get_test_user_by_name(test_testuser.name)
        assert test_user is not None
        assert test_user == test_testuser

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("feature_type_id", [1234])
    def test_get_user_list_empty(
        self, test_user_storage: TestUserStorage, test_testuser: TestUserModel, feature_type_id: int
    ) -> None:
        test_users = test_user_storage.get_test_users(
            feature_type_id=feature_type_id, allow_update=test_testuser.allow_update
        )
        assert not test_users

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_user_list(self, test_user_storage: TestUserStorage, test_testuser: TestUserModel) -> None:
        test_users = test_user_storage.get_test_users(
            feature_type_id=test_testuser.feature_type_id, allow_update=test_testuser.allow_update
        )
        assert len(test_users) == 1
        assert test_users[0] == test_testuser

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("allow_update", [True, False])
    def test_create_test_user(
        self,
        test_user_storage: TestUserStorage,
        test_user_name: str,
        test_specification: TestUserSpecification,
        test_feature_type: FeatureTypeModel,
        test_system_user: SystemUserModel,
        allow_update: bool,
    ) -> None:
        assert test_user_storage.get_test_user_by_name(test_user_name) is None
        test_user_storage.create_test_user(
            name=test_user_name,
            specification=test_specification,
            feature_type_id=test_feature_type.id,
            created_by=test_system_user.login,
            allow_update=allow_update,
        )
        test_user = test_user_storage.get_test_user_by_name(test_user_name)
        assert test_user is not None
        assert test_user.name == test_user_name
        assert test_user.specification == test_specification
        assert test_user.allow_update == allow_update

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("new_specification", [{"kek": "lol", "overhave": "test"}, {}, {"test": "new_value"}])
    @pytest.mark.parametrize("testuser_allow_update", [False], indirect=True)
    def test_update_test_user_specification_not_allowed(
        self,
        test_user_storage: TestUserStorage,
        test_testuser: TestUserModel,
        test_specification: TestUserSpecification,
        new_specification: TestUserSpecification,
    ) -> None:
        assert test_testuser.specification == test_specification
        with pytest.raises(TestUserUpdatingNotAllowedError):
            test_user_storage.update_test_user_specification(test_testuser.id, new_specification)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize("new_specification", [{"kek": "lol", "overhave": "test"}, {}, {"test": "new_value"}])
    @pytest.mark.parametrize("testuser_allow_update", [True], indirect=True)
    def test_update_test_user_specification(
        self,
        test_user_storage: TestUserStorage,
        test_testuser: TestUserModel,
        test_specification: TestUserSpecification,
        new_specification: TestUserSpecification,
    ) -> None:
        assert test_testuser.specification == test_specification
        test_user_storage.update_test_user_specification(test_testuser.id, new_specification)
        test_user = test_user_storage.get_test_user_by_name(test_testuser.name)
        assert test_user is not None
        assert test_user.specification == new_specification

    def test_delete_test_user_by_id_empty(
        self, database: None, test_user_storage: TestUserStorage, faker: Faker
    ) -> None:
        with pytest.raises(TestUserDoesNotExistError):
            test_user_storage.delete_test_user(faker.random_int())

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_delete_test_user_by_id(self, test_user_storage: TestUserStorage, test_testuser: TestUserModel) -> None:
        test_user_storage.delete_test_user(test_testuser.id)
        assert test_user_storage.get_test_user_by_id(test_testuser.id) is None
