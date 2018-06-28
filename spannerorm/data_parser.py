import time
import base_model
from .helper import Helper
from google.cloud.spanner_v1.streamed import StreamedResultSet
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


class DataParser(object):
    @classmethod
    def parse_result_set(cls, result_set, select_cols):
        """
        Parse result set

        :type result_set: StreamedResultSet
        :param result_set:

        :type select_cols: list
        :param select_cols:

        :rtype: list
        :return: parsed results
        """
        data = []
        for row in result_set:
            row_data = {}
            index = 0

            for field in select_cols:
                if isinstance(row[index], unicode):
                    value = str(row[index])
                elif isinstance(row[index], DatetimeWithNanoseconds):
                    value = time.mktime(row[index].timetuple())
                else:
                    value = row[index]

                row_data[field] = value
                index += 1
            data.append(row_data)

        return data

    @classmethod
    def map_model(cls, result_set, select_cols, model_class):
        """
        Map result set to model

        :type result_set: StreamedResultSet
        :param result_set: result set

        :type select_cols: list
        :param select_cols:

        :type model_class: base_model.BaseModel
        :param model_class:

        :rtype: list
        :return: list of result set
        """
        parse_results = cls.parse_result_set(result_set, select_cols)
        column_prop_maps = cls.model_column_prop_maps(model_class)

        data_list = []
        for result in parse_results:
            model_object = model_class()
            for column_name in column_prop_maps:
                model_prop = getattr(model_object, column_prop_maps.get(column_name))
                model_prop.value = result.get(column_name)

            data_list.append(model_object)

        return data_list

    @classmethod
    def model_column_prop_maps(cls, model_class):
        """
        Map model props with db columns

        :type model_class: base_model.BaseModel
        :param model_class:

        :rtype: dict
        :return: db column mapper to model attrs
        """
        attrs = Helper.get_model_attrs(model_class)
        table_name = model_class._meta().db_table
        property_column_map = {}
        for attr_name, attr in attrs.items():
            property_column_map[table_name + '.' + attr.db_column] = attr_name

        return property_column_map
