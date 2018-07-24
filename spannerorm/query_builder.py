import six
import logging
from datetime import date
import spannerorm.criteria
from .helper import Helper
from .relation import Relation


class QueryBuilder:
    def __init__(self, model_class, criteria=None):
        """
        :type model_class: spannerorm.base_model.BaseModel
        :param model_class:
        :type criteria: spannerorm.criteria.Criteria
        :param criteria:
        """
        self.model_class = model_class
        self.criteria = criteria
        self.meta = self.model_class._meta()
        self.table_name = str(self.meta.db_table)
        self.select_cols = []
        self.params_count = 0
        self.params = {}
        self.param_types = {}
        self.with_multi_joins = False
        self.multi_joins = {}
        self.set_multi_joins()

    def set_multi_joins(self):
        """
        Set multi joins data
        """
        join_relations = self.criteria.join_relations
        for join in join_relations:
            join_relation = join.get('relation')
            join_attr = Helper.model_relational_attr_by_prop(self.model_class, join_relation)
            if Helper.is_relational_attr(join_attr) is False:
                raise TypeError('Invalid join with criteria')

            refer_model = Relation.get_refer_model(self.model_class, join_attr.relation_name)

            if join_attr.relation_type == 'OneToMany' or join_attr.relation_type == 'ManyToMany':
                self.with_multi_joins = True
                self._set_multi_join_select_clause(refer_model, join_attr.relation_name)
                self._set_multi_join_data(join_attr.relation_name)

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

            if join_attr.relation_type == 'OneToOne' or join_attr.relation_type == 'ManyToOne':
                if join_select_clause == '':
                    join_select_clause += self._get_model_select_clause(refer_model)
                else:
                    join_select_clause += ', ' + self._get_model_select_clause(refer_model)

        return join_select_clause

    def _get_model_select_clause(self, model_cls):
        """
        Return select clause of model
        :type model_cls: spannerorm.base_model.BaseModel
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

        limit_clause = 'LIMIT {limit}'.format(limit=str(self.criteria.limit))
        if self.criteria.offset:
            limit_clause += ' OFFSET {offset}'.format(offset=str(self.criteria.offset))

        return limit_clause

    def _parse_condition(self, condition_list, condition_type='AND'):
        """
        Parse condition
        :type: dict
        :param condition_list: where condition list
        :rtype: str
        :return:
        """
        where_clause = ''

        for condition in condition_list:
            if isinstance(condition, dict):
                sub_where_clause = self._build_where_clause(condition)
                if where_clause != '':
                    where_clause += ' {condition_type} ({sub_where_clause})'.format(condition_type=condition_type,
                                                                                    sub_where_clause=sub_where_clause)
                else:
                    where_clause = sub_where_clause
            else:
                self.params_count += 1
                prop = condition[0]
                prop_module_cls = Helper.model_cls_by_module_name(prop.fget.__module__)
                attr = Helper.model_attr_by_prop(prop_module_cls, prop)
                table_name = prop_module_cls._meta().db_table
                db_field = table_name + '.' + attr.db_column
                operator = condition[1]
                param = 'param' + str(self.params_count)

                if operator == 'IS' or operator == 'IS NOT':
                    if where_clause != '':
                        where_clause += ' {condition_type} {db_field} {operator} {value}' \
                            .format(condition_type=condition_type, db_field=db_field, operator=operator, value=condition[2])
                    else:
                        where_clause += '{db_field} {operator} {value}' \
                            .format(db_field=db_field, operator=operator, value=condition[2])
                elif operator != 'IN' and operator != 'NOT IN':
                    if where_clause != '':
                        where_clause += ' {condition_type} {db_field} {operator} @{param}' \
                            .format(condition_type=condition_type, db_field=db_field, operator=operator, param=param)
                    else:
                        where_clause += '{db_field} {operator} @{param}' \
                            .format(db_field=db_field, operator=operator, param=param)

                    self.params[param] = condition[2]
                    self.param_types[param] = attr.data_type
                else:
                    if where_clause != '':
                        where_clause += ' {condition_type} {db_field} {operator} {in_clause}' \
                            .format(condition_type=condition_type, db_field=db_field, operator=operator,
                                    in_clause=self._build_in_clause(condition[2]))
                    else:
                        where_clause += '{db_field} {operator} {in_clause}' \
                            .format(db_field=db_field, operator=operator, in_clause=self._build_in_clause(condition[2]))

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
            if isinstance(value, str) or isinstance(value, six.string_types):
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
        and_clause = self._parse_condition(where_conditions.get('and_conditions'), 'AND')
        or_clause = self._parse_condition(where_conditions.get('or_conditions'), 'OR')
        if and_clause != '' and or_clause != '':
            return '{and_clause} OR {or_clause}'.format(and_clause=and_clause, or_clause=or_clause)
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
        order_by_list = self.criteria.order_by
        order_by_clause = ''
        for order_by in order_by_list:
            sub_order_by_clause = ''
            for prop in order_by.get('order_col'):
                prop_module_cls = Helper.model_cls_by_module_name(prop.fget.__module__)
                table_name = prop_module_cls._meta().db_table
                attr = Helper.model_attr_by_prop(prop_module_cls, prop)

                if sub_order_by_clause == '':
                    sub_order_by_clause += '{table_name}.{db_column}' \
                        .format(table_name=table_name, db_column=attr.db_column)
                else:
                    sub_order_by_clause += ', {table_name}.{db_column}' \
                        .format(table_name=table_name, db_column=attr.db_column)

            if order_by_clause == '':
                order_by_clause += '{sub_order_by_clause} {order}' \
                    .format(sub_order_by_clause=sub_order_by_clause, order=order_by.get('order'))
            else:
                order_by_clause += ', {sub_order_by_clause} {order}' \
                    .format(sub_order_by_clause=sub_order_by_clause, order=order_by.get('order'))

        if order_by_clause != '':
            return 'ORDER BY {order_by_clause}'.format(order_by_clause=order_by_clause)
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

    def _set_multi_join_select_clause(self, model_cls, relation_name):
        """
        set OnToMany or ManyToMany Join select clause
        :type model_cls: spannerorm.base_model.BaseModel
        :param model_cls: refer to model class
        :type relation_name: str
        :param relation_name: relation name
        """
        sub_select_clause = ''
        attrs = Helper.get_model_attrs(model_cls)
        table_name = model_cls._meta().db_table

        select_cols = []
        for attr in attrs:
            select_column = table_name + '.' + attrs.get(attr).db_column
            select_cols.append(select_column)
            if sub_select_clause == '':
                sub_select_clause += select_column
            else:
                sub_select_clause += ', ' + select_column

        if relation_name not in self.multi_joins:
            self.multi_joins[relation_name] = {}

        multi_join = self.multi_joins.get(relation_name)
        multi_join['select_cols'] = select_cols
        multi_join['select_clause'] = sub_select_clause

    def _set_multi_join_data(self, relation_name):
        """
        Set join sub query data
        :type relation_name: str
        :param relation_name: Relation name
        :type db_table: str
        :param db_table: db table name
        :type join_clause: str
        :param join_clause: join clause
        :type where_clause: str
        :param where_clause: where clause
        """
        relations = self.model_class._meta().relations()
        refer_to_model = relations.get(relation_name)
        relation_prop = Helper.get_model_prop_by_name(self.model_class, relation_name)

        if relation_name not in self.multi_joins:
            self.multi_joins[relation_name] = {}

        multi_join = self.multi_joins.get(relation_name)
        multi_join['refer_to_model'] = refer_to_model
        multi_join['relation_prop'] = relation_prop

    def get_query(self, in_ids=None):
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
        limit_clause = self._get_limit_clause() if self.with_multi_joins is False else ''
        if in_ids:
            primary_key = self.meta.primary_key
            if where_clause != '':
                where_clause += ' AND {db_table}.{primary_key} IN {in_clause}' \
                    .format(db_table=db_table, primary_key=primary_key, in_clause=self._build_in_clause(in_ids))
            else:
                where_clause = 'WHERE {db_table}.{primary_key} IN {in_clause}' \
                    .format(db_table=db_table, primary_key=primary_key, in_clause=self._build_in_clause(in_ids))

        select_query = 'SELECT {select_clause} FROM {db_table} {join_clause} {where_clause} {order_by_clause} {limit_clause}' \
            .format(select_clause=select_clause, db_table=db_table, join_clause=join_clause, where_clause=where_clause,
                    order_by_clause=order_by_clause, limit_clause=limit_clause)
        logging.debug('\n Query: %s \n Params: %s \n Params Types: %s', select_query, self.params, self.param_types)
        return select_query

    def get_multi_join_query(self, relation_name, in_values):
        multi_join = self.multi_joins.get(relation_name)
        relation_prop = multi_join.get('relation_prop')
        relation_attr = Helper.model_relational_attr_by_prop(self.model_class, relation_prop)
        refer_to_model = multi_join.get('refer_to_model')
        refer_to_attr = Helper.model_attr_by_prop_name(refer_to_model, relation_attr.refer_to)
        refer_table_name = refer_to_model._meta().db_table
        refer_db_field = refer_table_name + '.' + refer_to_attr.db_column
        db_table = self.table_name
        where_clause = self._get_where_clause()
        join_clause = self._get_join_clause()
        order_by_clause = self._get_order_by_clause()

        if where_clause != '':
            where_clause += ' AND {db_field} IN {in_clause}' \
                .format(db_field=refer_db_field, in_clause=self._build_in_clause(in_values))
        else:
            where_clause = 'WHERE {db_field} IN {in_clause}' \
                .format(db_field=refer_db_field, in_clause=self._build_in_clause(in_values))

        select_query = 'SELECT {select_clause} FROM {db_table} {join_clause} {where_clause} {order_by_clause}' \
            .format(select_clause=multi_join.get('select_clause'), db_table=db_table,
                    join_clause=join_clause, where_clause=where_clause, order_by_clause=order_by_clause)
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
        primary_key_prop = self.model_class.primary_key_property()
        primary_key_attr = Helper.model_attr_by_prop(self.model_class, primary_key_prop)
        db_column = primary_key_attr.db_column
        count_query = 'SELECT COUNT(DISTINCT {db_table}.{pk}) FROM {db_table} {join_clause} {where_clause}' \
            .format(db_table=db_table, join_clause=join_clause, where_clause=where_clause, pk=db_column)
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
        join_clause = self._get_join_clause()
        where_clause = self._get_where_clause()
        limit_clause = self._get_limit_clause()

        select_primary_key_query = 'SELECT DISTINCT({db_table}.{primary_key}) FROM {db_table} {join_clause} {where_clause} {limit_clause}' \
            .format(primary_key=primary_key, db_table=db_table, join_clause=join_clause, where_clause=where_clause,
                    limit_clause=limit_clause)
        logging.debug('\n Query: %s \n Params: %s \n Params Types: %s', select_primary_key_query, self.params,
                      self.param_types)
        return select_primary_key_query