#!/usr/bin/env python3
''''supporting parsers to transpile query'''

# import os
import re_utils


def parse_node(node):
    '''returns python obj type to save into db and refer easily from cypher node entity'''
    re_property = re_utils.regex_property(node)
    node_id, node_property = re_property or (node.strip(), {})
    node_property = parse_property(node_property)
    node_name, *node_label = node_id.strip().split(":", 1)
    if node_label:
        node_label = node_label[0].strip()
    else:
        node_label = None

    mapping = {"id": node_name, "label": node_label, }
    if node_property:
        mapping.update(node_property)
    cypher_node = ["node:{}".format(node_id), mapping]
    return cypher_node


def parse_relation(relation):
    '''returns python obj type to save into db and refer easily from cypher relation entity'''
    re_property = re_utils.regex_property(relation)
    reln_id, reln_property = re_property or (relation.strip(), {})
    reln_property = parse_property(reln_property)

    reln_id, *reln_type = reln_id.split(":")
    if reln_type:
        reln_type = reln_type[0].strip()

    mapping = {"id": reln_id, "type": reln_type, }

    if reln_property:
        mapping.update(reln_property)
    cypher_reln = ["relation:{}".format(reln_id or reln_type), mapping]
    return cypher_reln


def parse_relationship(re_relationship):
    '''process cypher relationship between nodes'''
    directed, nodes, relation = re_relationship
    target_node, source_node = parse_nodes(nodes)
    relation = parse_relation(relation)

    if directed:
        relation[1]["target_node"] = target_node
        relation[1]["source_node"] = source_node
    else:
        relation[1]["conn_nodes"] = target_node, source_node
    relation[1]["directed"] = directed
    # return relation
    return target_node, source_node, relation


def parse_nodes(nodes):
    return [parse_node(node) for node in nodes]


def parse_relationships(relationships):
    return [parse_relationship(relationship) for relationship in relationships]


def parse_match(match_query):
    nodes, relations = re_utils.regex_entities(match_query)
    match_nodes = parse_nodes(nodes)
    if relations:
        relations = parse_relationships(relations)
    return match_nodes, relations


def parse_where(where_query):
    where_conditions = [cond.split("=") for cond in where_query]
    where_conditions = [i.split(".") + [j] for i, j in where_conditions]
    parsed_WHERE = {parse_item(mid): {parse_item(mk): parse_item(mv)}
                    for mid, mk, mv in where_conditions}
    return parsed_WHERE


def parse_return(re_return):
    if "type" in re_return:
        re_return["type"] = re_return["type"][1:-1]
    if "ORDER BY" in re_return:
        return_order = re_return["ORDER BY"]
    if "SKIP" in re_return:
        return_skip = re_return["SKIP"].strip()
        try:
            re_return["SKIP"] = int(return_skip)
        except ValueError:
            pass
    if "LIMIT" in re_return:
        return_limit = re_return["LIMIT"]
        try:
            re_return["LIMIT"] = int(return_limit)
        except ValueError:
            pass

    re_return["RETURN"] = [[i.strip() for i in cond.split(".")]
                           for cond in re_return["RETURN"].split(",")]
    return re_return


def parse_set(set_query):
    nodes, relations = re_utils.regex_entities(set_query)


def parse_property(prty):
    ''''converts property in cypher syntax to python dict object '''
    if prty:
        prty = dict([[parse_item(j.strip(" '\"")) for j in i.split(":")]
                     for i in prty[1:-1].split(",")])
        return prty
    return {}


def parse_item(item):
    '''returns input dict with parsing numbers'''
    # if item[0] in "'\"":
    #     return item.strip("'\"")
    item = item.strip(" '\"")

    # checks between number/string type
    try:
        item = float(item)
    except ValueError:
        return item  # item is string

    # checks between int/float type of number class
    try:
        item = int(item)
    except ValueError:
        item = float(item)
    return item
