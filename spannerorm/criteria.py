class Criteria(object):

    def __init__(self):
        self._and_condition = []
        self._or_condition = []
        self._where_condition = {
            'and_conditions': [],
            'or_conditions': []
        }
        self._limit = None
        self._offset = None
        self._order_by = []
        self._join_withs = []

    @property
    def where(self):
        return self._where_condition

    @property
    def limit(self):
        return self._limit

    @property
    def offset(self):
        return self._offset

    @property
    def order_by(self):
        return self._order_by

    @property
    def join_relations(self):
        return self._join_withs

    @limit.setter
    def limit(self, value):
        """
        Setter limit criteria
        :type value: int
        :param value:
        """
        if isinstance(value, int) is False:
            raise TypeError('Limit should be valid integer')
        if value <= 0:
            raise TypeError('Limit value should be >0')

        self._limit = value

    @offset.setter
    def offset(self, value):
        """
        Setter offset criteria
        :type value: int
        :param value:
        :return:
        """
        if isinstance(value, int) is False:
            raise TypeError('Offset should be valid integer')
        if value < 0:
            raise TypeError('Offset value should be >=0')
        self._offset = value

    def condition(self, conditions, operator='AND'):
        """
        Set criteria condition that filter result set
        :type conditions: list
        :param conditions: list of conditions
        :type operator: str
        :param operator: [AND | OR] condition
        """
        if not isinstance(conditions, list) or not isinstance(operator, str):
            raise TypeError('criteria conditions: dataType should be list')

        for condition in conditions:
            self.add_condition(condition, operator)

    def add_condition(self, condition, operator='AND'):
        """
        Add criteria condition that filter result set
        :type condition: tuple
        :param condition: where condition like:
            (User.Id, '=', 1)
            ((User.id, '=', 1), 'AND', (User.name, '=', 'sanish'))
            ((User.id, '=', 1), 'AND', ((User.active, '=', True), 'OR', (User.name, '=', 'sanish')))
            (((User.id, '=', 1), 'AND', ((User.active, '=', True), 'OR', (User.name', '=', 'sanish'))), 'OR', (User.user_name, '=', 'mjsanish')))
            (((User.id, '=', 1), 'AND', ((User.active, '=', True), 'OR', (User.name, '=', 'sanish'))), 'OR', ((User.user_name, '=', 'mjsanish'), 'AND', (User.password, '=', 'pass')))
        :param operator:
        :return:
        """
        CriteriaBuilder.build_where_criteria(self._where_condition, condition, operator)

    def set_order_by(self, order_by_props, order='ASC'):
        """
        Set order by criteria
        :type order_by_props: list | property
        :param order_by_props: order by property or list of order by properties
        :type order: str
        :param order: 'ASC' OR 'DESC'
        """
        if order.upper() not in ['ASC', 'DESC']:
            raise TypeError('order_by criteria order should be [ASC | DESC]')
        if isinstance(order_by_props, property) is False and isinstance(order_by_props, list) is False:
            raise TypeError('order_by_props data type should be [property | list]')

        order_by = {
            'order': order.upper(),
            'order_col': ()
        }

        if isinstance(order_by_props, property):
            order_by['order_col'] += (order_by_props,)
        else:
            for order_by_prop in order_by_props:
                order_by['order_col'] += (order_by_prop,)

        self._order_by.append(order_by)

    def join_with(self, relation, join_type='LEFT'):
        """
        Add join with criteria
        :type relation: property
        :param relation: model relation property
        :type join_type: str
        :param join_type: Join type ['LEFT', 'RIGHT', 'FULL']
        """
        if isinstance(relation, property) is False:
            raise TypeError('join_with: should be relational property')
        if join_type.upper() not in ['LEFT', 'RIGHT', 'FULL']:
            raise TypeError('join_type should be [LEFT | RIGHT | FULL]')

        self._join_withs.append({'relation': relation, 'join_type': join_type})


class CriteriaBuilder(object):

    @classmethod
    def build_where_criteria(cls, where_criteria, condition, operator):
        """
        Build where criteria from condition
        :type where_criteria: dict
        :param where_criteria: sub where criteria {'and_conditions':list, 'or_conditions':list}
        :type condition: tuple
        :param condition: sub condition like:
            (User.active, '=', True)
            ((User.active, '=', True), 'OR', (User.name, '=', 'sanish'))
            ((User.active, '=', True), 'AND', (User.name, '=', 'sanish'))
            ((User.active, '=', True), 'AND', ((User.name, '=', 'sanish'), 'AND', (User.gender, '=', 'Male')))
        :param operator:
        :return:
        """
        valid_where_operator = ['=', '>', '<', '>=', '<=', '<>', 'LIKE', 'IN', 'NOT IN', 'IS', 'IS NOT']

        if isinstance(operator, str) is False or operator.upper() not in ['AND', 'OR']:
            raise TypeError('operator: should be [AND | OR]')
        if isinstance(condition, tuple) is False:
            raise TypeError('criteria condition: dataType should be tuple')
        if len(condition) != 3:
            raise TypeError('Invalid criteria condition: {}'.format(condition))

        # if condition like: ('active', '=', True)
        elif isinstance(condition[0], property) is True:
            if condition[1] not in valid_where_operator:
                raise TypeError('Compare-operator should be in [=, >, <, >=, <=, <>, LIKE, IN, NOT IN, IS, IS NOT]')

            if operator.upper() == 'AND':
                where_criteria.get('and_conditions').append(condition)
            else:
                where_criteria.get('or_conditions').append(condition)

            return where_criteria
        # if condition like: (('active', '=', True), 'OR', ('name', '=', 'sanish'))
        elif isinstance(condition[0], tuple) is True:
            child_where_criteria = {
                'and_conditions': [],
                'or_conditions': []
            }

            cls.build_sub_where_criteria(child_where_criteria, condition)
            if operator.upper() == 'AND':
                where_criteria.get('and_conditions').append(child_where_criteria)
            else:
                where_criteria.get('or_conditions').append(child_where_criteria)
        else:
            raise TypeError('Invalid criteria condition: {}'.format(condition))

    @classmethod
    def build_sub_where_criteria(cls, sub_where_criteria, sub_condition):
        """
        Build sub where criteria form sub_condition ((sub_condition1), operator, (sub_condition2))
        eg. (('active', '=', True), 'OR', ('name', '=', 'sanish'))
        :type sub_where_criteria: dict
        :param sub_where_criteria: sub where criteria {'and_conditions':list, 'or_conditions':list}
        :type sub_condition: tuple
        :param sub_condition: sub condition (('active', '=', True), 'OR', ('name', '=', 'sanish'))
        """
        if isinstance(sub_condition, tuple) is False or len(sub_condition) != 3:
            raise TypeError('Invalid criteria condition: {}'.format(sub_condition))
        if 'and_conditions' not in sub_where_criteria \
                or isinstance(sub_where_criteria.get('and_conditions'), list) is False \
                or 'or_conditions' not in sub_where_criteria \
                or isinstance(sub_where_criteria.get('or_conditions'), list) is False:
            raise TypeError('Invalid where criteria data initialized: {}'.format(sub_where_criteria))

        condition1 = sub_condition[0]
        condition2 = sub_condition[2]
        operator = sub_condition[1]

        if isinstance(condition1, tuple) is False:
            raise TypeError('Invalid criteria condition: {}'.format(condition1))
        if isinstance(condition2, tuple) is False:
            raise TypeError('Invalid criteria condition: {}'.format(condition2))
        if isinstance(operator, str) is False or operator not in ['AND', 'OR']:
            raise TypeError('criteria {} operator: should be [AND | OR]'.format(sub_condition))

        cls.build_where_criteria(sub_where_criteria, condition1, operator.upper())
        cls.build_where_criteria(sub_where_criteria, condition2, operator.upper())
