import abc
import logging
from typing import Iterable, List, Optional, cast

import sqlalchemy.orm as so
from pydantic.tools import parse_obj_as

from overhave import db
from overhave.storage.converters import FeatureModel
from overhave.utils import get_current_time

logger = logging.getLogger(__name__)


class BaseFeatureStorageException(Exception):
    """Base exception for :class:`FeatureStorage`."""


class FeatureNotExistsError(BaseFeatureStorageException):
    """Error for situation when feature not found."""


class FeatureTagNotExistsError(BaseFeatureStorageException):
    """Error for situation when tag not found."""


class IFeatureStorage(abc.ABC):
    """Abstract class for feature storage."""

    @staticmethod
    @abc.abstractmethod
    def get_feature(feature_id: int) -> Optional[FeatureModel]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_feature(model: FeatureModel) -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_feature(model: FeatureModel) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_features_by_tag(tag_id: int) -> List[FeatureModel]:
        pass


def _append_tags_to_feature(session: so.Session, feature: db.Feature, tag_ids: Iterable[int]) -> None:
    db_tags: List[db.Tags] = []
    for tag_id in tag_ids:
        db_tag = session.query(db.Tags).get(tag_id)
        if db_tag is None:
            raise FeatureTagNotExistsError(f"Feature tag with id={tag_id} does not exist!")
        logger.info("Append tag with id=%s and value=%s", tag_id, db_tag.value)
        db_tags.append(db_tag)
    feature.feature_tags.extend(db_tags)


class FeatureStorage(IFeatureStorage):
    """Class for feature storage."""

    @staticmethod
    def get_feature(feature_id: int) -> Optional[FeatureModel]:
        with db.create_session() as session:
            feature: Optional[db.Feature] = session.query(db.Feature).get(feature_id)
            if feature is not None:
                return cast(FeatureModel, FeatureModel.from_orm(feature))
            return None

    @staticmethod
    def create_feature(model: FeatureModel) -> int:
        with db.create_session() as session:
            feature = db.Feature(
                name=model.name,
                author=model.author,
                type_id=model.feature_type.id,
                file_path=model.file_path,
                task=model.task,
                severity=model.severity,
                last_edited_at=get_current_time(),
            )
            feature.last_edited_at = model.last_edited_at
            feature.released = model.released
            _append_tags_to_feature(session=session, feature=feature, tag_ids=(tag.id for tag in model.feature_tags))
            session.add(feature)
            session.flush()
            return cast(int, feature.id)

    @staticmethod
    def update_feature(model: FeatureModel) -> None:
        with db.create_session() as session:
            feature: db.Feature = session.query(db.Feature).get(model.id)
            if feature is None:
                raise FeatureNotExistsError(f"Feature with id {model.id} does not exist!")
            feature.name = model.name
            feature.file_path = model.file_path
            feature.task = model.task
            feature.severity = model.severity
            feature.last_edited_by = model.last_edited_by
            feature.last_edited_at = get_current_time()
            feature.released = True
            session.flush()

            existing_tags = {tag.id for tag in feature.feature_tags}
            model_tags = {tag.id for tag in model.feature_tags}
            tags_to_delete = existing_tags.difference(model_tags)
            for tag_id in tags_to_delete:
                db_tag = next(tag for tag in feature.feature_tags if tag.id == tag_id)
                logger.info("Remove tag with id=%s and value=%s", tag_id, db_tag.value)
                feature.feature_tags.remove(db_tag)
            tags_to_append = model_tags.difference(existing_tags)
            _append_tags_to_feature(session=session, feature=feature, tag_ids=tags_to_append)

    @staticmethod
    def get_features_by_tag(tag_id: int) -> List[FeatureModel]:
        with db.create_session() as session:
            feature_ids_query = (
                session.query(db.FeatureTagsAssociationTable)
                .with_entities(db.FeatureTagsAssociationTable.feature_id)
                .filter(db.FeatureTagsAssociationTable.tags_id == tag_id)
                .scalar_subquery()
            )
            features = session.query(db.Feature).filter(db.Feature.id == feature_ids_query).all()
            return parse_obj_as(List[FeatureModel], features)
