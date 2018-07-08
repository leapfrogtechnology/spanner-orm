import logging
import base_model
from datetime import date
from .helper import Helper
from .relation import Relation


class QueryBuilder:
    def __init__(self, model_class, criteria=None):
        self.model_class = model_class
        self.criteria = criteria
        self.meta = self.model_class._meta()
        self.table_name = str(self.meta.db_table)
        self.select_cols = []
        self.params_count = 0
        self.params = {}
        self.param_types = {}
        self.join_with = {}

    def _get_select_clause(self):
        """
        Return select clause

        :rtype: str
        :return:
        """
        select_clause = self._get_model_select_clause(self.model_class)
        join_select_clause = self._get_join_select_clause()
        if join_select_clause != '':
            return select_clause + ', ' + join_select_clause

        return select_clause

    def _get_join_select_clause(self):
        """
        Return join select clause

        :rtype: str
        :return:
        """
        join_select_clause = ''
        join_relations = self.criteria.join_relations
        for join in join_relations:
            join_relation = join.get('relation')
            join_attr = Helper.model_relational_attr_by_prop(self.model_class, join_relation)
            if Helper.is_relational_attr(join_attr) is False:
                raise TypeError('Invalid join with criteria')

            refer_model = Relation.get_refer_model(self.model_class, join_attr.relation_name)
            if join_select_clause == '':
                join_select_clause += self._get_model_select_clause(refer_model)
            else:
                join_select_clause += ', ' + self._get_model_select_clause(refer_model)

        return join_select_clause

    def _get_model_select_clause(self, model_cls):
        """
        Return select clause of model

        :type model_cls: base_model.BaseModel
        :param model_cls:
        :return:
        """
        sub_select_clause = ''
        attrs = Helper.get_model_attrs(model_cls)
        table_name = model_cls._meta().db_table
        for attr in attrs:
            select_column = table_name + '.' + attrs.get(attr).db_column
            self.select_cols.append(select_column)
            if sub_select_clause == '':
                sub_select_clause += select_column
            else:
                sub_select_clause += ', ' + select_column

        return sub_select_clause

    def _get_limit_clause(self):
        """
        Return limit clause

        :rtype: str
        :return:
        """
        if self.criteria.limit is None and self.criteria.offset is not None:
            raise RuntimeError('Limit criteria not set')

        if self.criteria.limit is None:
            return ''

        limit_clause = 'LIMIT ' + str(self.criteria.limit)
        if self.criteria.offset:
            limit_clause += ' OFFSET ' + str(self.criteria.offset)

        return limit_clause

    def _parse_condition(self, condition_list):
        """
        Parse condition

        :type: dict
        :param condition_list: where condition list

        :rtype: str
        :return:
        """
        where_clause = ''
        table_name = self.meta.db_table

        for condition in condition_list:
            if isinstance(condition, dict):
                sub_where_clause = self._build_where_clause(condition)
                if sub_where_clause != '':
                    where_clause += '(' + self._build_where_clause(condition) + ')'
            else:
                self.params_count += 1
                attr = Helper.model_attr_by_prop(self.model_class, condition[0])

                db_field = table_name + '.' + attr.db_column
                operator = condition[1]
                param = 'param' + str(self.params_count)
                if where_clause != '':
                    where_clause += ' AND '

                if operator != 'IN' and operator != 'NOT IN':
                    where_clause += db_field + ' ' + operator + ' @' + param

                    self.params[param] = condition[2]
                    self.param_types[param] = attr.data_type
                else:
                    where_clause += db_field + ' ' + operator + ' ' + self._build_in_clause(condition[2])

        return where_clause

    def _build_in_clause(self, in_values):
        """
        Build in clause

        :type in_values: list
        :param in_values: in values

        :rtype: str
        :return:
        """
        in_clause = ''
        for value in in_values:
            if isinstance(value, str):
                if in_clause == '':
                    in_clause += "'" + value + "'"
                else:
                    in_clause += ", '" + value + "'"
            elif isinstance(value, date):
                if in_clause == '':
                    in_clause += "'" + value.strftime('%Y-%m-%d') + "'"
                else:
                    in_clause += ", '" + value.strftime('%Y-%m-%d') + "'"

            else:
                if in_clause == '':
                    in_clause += value
                else:
                    in_clause += ', ' + value

        return '(' + in_clause + ')'

    def _get_where_clause(self):
        """
        Return where clause string

        :rtype: str
        :return:
        """
        where_conditions = self.criteria.where
        self.params_count = 0
        self.params = {}
        self.param_types = {}

        where_clause = self._build_where_clause(where_conditions)

        return 'WHERE ' + where_clause if where_clause else ''

    def _build_where_clause(self, where_conditions):
        """
        Build where clause

        :type where_conditions: dict
        :param where_conditions:

        :rtype: str
        :return: where clause
        """
        and_clause = self._parse_condition(where_conditions.get('and_conditions'))
        or_clause = self._parse_condition(where_conditions.get('or_conditions'))

        if and_clause != '' and or_clause != '':
            return '(' + and_clause + ') OR (' + or_clause + ')'
        elif and_clause != '' and or_clause == '':
            return and_clause
        elif and_clause == '' and or_clause != '':
            return or_clause
        else:
            return ''

    def _get_order_by_clause(self):
        """
        Build order clause

        :rtype: str
        :return: order clause
        """
        order_by = self.criteria.order_by
        table_name = self.meta.db_table
        order_by_clause = ''

        for prop in order_by.get('order_col'):
            attr = Helper.model_attr_by_prop(self.model_class, prop)
            if order_by_clause == '':
                order_by_clause += table_name + '.' + attr.db_column
            else:
                order_by_clause += ', ' + table_name + '.' + attr.db_column

        if order_by_clause != '':
            return 'ORDER BY ' + order_by_clause + ' ' + order_by.get('order')
        else:
            return ''

    def _get_join_clause(self):
        join_clause = ''
        join_relations = self.criteria.join_relations

        for join in join_relations:
            relation = join.get('relation')
            join_attr = Helper.model_relational_attr_by_prop(self.model_class, relation)
            if Helper.is_relational_attr(join_attr) is False:
                raise TypeError('Invalid join with criteria')

            table_name = self.meta.db_table
            refer_model = Relation.get_refer_model(self.model_class, join_attr.relation_name)
            refer_table = refer_model._meta().db_table
            join_on = join_attr.join_on
            refer_to = join_attr.refer_to

            if join_clause != '':
                join_clause += ' '

            join_clause += '{} JOIN {} on {}.{}={}.{}' \
                .format(join.get('join_type'), refer_table, table_name, join_on, refer_table, refer_to)

        return join_clause

    def get_query(self):
        """
        Build query base on criteria and return query string

        :rtype: str
        :return: query string
        """
        select_clause = self._get_select_clause()
        db_table = self.table_name
        join_clause = self._get_join_clause()
        where_clause = self._get_where_clause()
        order_by_clause = self._get_order_by_clause()
        limit_clause = self._get_limit_clause()

        select_query = 'SELECT {select_clause} FROM {db_table} {join_clause} {where_clause} {order_by_clause} {limit_clause}' \
            .format(select_clause=select_clause, db_table=db_table, join_clause=join_clause, where_clause=where_clause,
                    order_by_clause=order_by_clause, limit_clause=limit_clause)
        logging.debug('\n Query: %s \n Params: %s \n Params Types: %s', select_query, self.params, self.param_types)
        return select_query

    def get_count(self):
        """
        Build count query string

        :rtype: str
        :return: query string
        """
        db_table = self.table_name
        join_clause = self._get_join_clause()
        where_clause = self._get_where_clause()

        count_query = 'SELECT COUNT(*) FROM {db_table} {join_clause} {where_clause}' \
            .format(db_table=db_table, join_clause=join_clause, where_clause=where_clause)
        logging.debug('\n Query: %s \n Params: %s \n Params Types: %s', count_query, self.params, self.param_types)
        return count_query

    def get_primary_keys(self):
        """
        Build query string that return primaries key base on criteria

        :rtype: str
        :return: query string
        """
        primary_key = self.meta.primary_key
        db_table = self.table_name
        where_clause = self._get_where_clause()
        limit_clause = self._get_limit_clause()

        select_primary_key_query = 'SELECT {primary_key} FROM {db_table} {where_clause} {limit_clause}' \
            .format(primary_key=primary_key, db_table=db_table, where_clause=where_clause, limit_clause=limit_clause)
        logging.debug('\n Query: %s \n Params: %s \n Params Types: %s', select_primary_key_query, self.params,
                      self.param_types)
        return select_primary_key_query
