from math import log
from typing import List, Dict, Any
from sqlalchemy import inspect, MetaData
from sqlalchemy.orm import foreign 
from db.dependencies import DB_dependency
from db.session import engine

from schemas.table_graph_schema import TableGraph, RelationDetail, GraphSchema
from utils.logger import get_logger

logger = get_logger("graph_builder_logger")

def build_table_dependency_graph(db: DB_dependency, tables: List[str]) -> GraphSchema:
    """
    Build a graph schema for the given tables.
    """
    metadata = MetaData()
    metadata.reflect(bind=engine, only=tables)

    graph: GraphSchema = {}
    logger.debug(f"Building graph for tables: {tables}")

    for table_name in tables:
        logger.debug(f"Building graph for table: {table_name}")
        graph.setdefault(table_name, TableGraph(
            parents=[],
            children=[]
        ))

    for table in metadata.tables.values():
        logger.debug(f"Processing table: {table_name}")
        for foreign_key in table.foreign_keys:
            logger.debug(f"Processing foreign key: {foreign_key}")
            parent_table = foreign_key.column.table.name
            child_table = foreign_key.parent.table.name

            logger.debug(f"Parent table: {parent_table}, Child table: {child_table}")
            if child_table in graph and parent_table in graph:
                logger.debug(f"Adding relation between {parent_table} and {child_table}")
                relation = RelationDetail(
                    table=parent_table,
                    fk_column=foreign_key.parent.name,
                    pk_column=foreign_key.column.name,
                    relation_type='N:1',
                    fk_constraint_name=foreign_key.constraint.name,
                    on_delete=foreign_key.ondelete
                )
                graph[child_table].parents.append(relation)

                reverse_relation = RelationDetail(
                    table=child_table,
                    fk_column=foreign_key.column.name,
                    pk_column=foreign_key.parent.name,
                    relation_type='1:N',
                    fk_constraint_name=foreign_key.constraint.name,
                    on_delete=foreign_key.ondelete
                )
                graph[parent_table].children.append(reverse_relation)
                logger.debug(f"Added relation between {parent_table} and {child_table}")
    return graph


