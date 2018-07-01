from .helper import Helper


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

    def _get_select_clause(self):
        """
        Return select clause

        :rtype: str
        :return:
        """
        select_clause = ''
        attrs = Helper.get_model_attrs(self.model_class)
        table_name = self.meta.db_table
        for attr in attrs:
            select_column = table_name + '.' + attrs.get(attr).db_column
            self.select_cols.append(select_column)
            if select_clause == '':
                select_clause += select_column
            else:
                select_clause += ', ' + select_column

        return select_clause

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
                sub_where_clause = self.build_where_clause(condition)
                if sub_where_clause != '':
                    where_clause += '(' + self.build_where_clause(condition) + ')'
            else:
                self.params_count += 1
                attr = Helper.model_attr_by_prop(self.model_class, condition[0])

                db_field = table_name + '.' + attr.db_column
                operator = condition[1]
                param = 'param' + str(self.params_count)
                if where_clause != '':
                    where_clause += ' AND '

                where_clause += db_field + ' ' + operator + ' @' + param

                self.params[param] = str(condition[2])
                self.param_types[param] = attr.data_type

        return where_clause

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

        where_clause = self.build_where_clause(where_conditions)

        return 'WHERE ' + where_clause if where_clause else ''

    def build_where_clause(self, where_conditions):
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

    def get_query(self):
        """
        Build query base on criteria and return query string

        :rtype: str
        :return: query string
        """
        select_query = 'SELECT ' + self._get_select_clause() + ' FROM ' + self.table_name + ' AS ' + self.meta.db_table + ' ' + self._get_where_clause() + ' ' + self._get_limit_clause()
        print(select_query)
        print(self.params)
        print(self.param_types)
        return select_query

    def get_count(self):
        count_query = 'SELECT COUNT(*) FROM ' + self.table_name + ' AS ' + self.meta.db_table + ' ' + self._get_where_clause()
        print(count_query)
        return count_query
