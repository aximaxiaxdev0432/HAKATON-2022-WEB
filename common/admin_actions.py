import csv
from datetime import datetime, date

import xlsxwriter

from django.db.models.fields.related_descriptors import (
    ManyToManyDescriptor,
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor
)
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from io import BytesIO


class ConvertExportData:

    def convert_field(self, field):

        if callable(field):
            return field()
        if isinstance(field, datetime):
            return field.strftime("%d.%m.%Y %H:%M:%S")
        if isinstance(field, date):
            return field.strftime("%d.%m.%Y")
        if isinstance(field, bool):
            return field

        return str(field)


class BaseUp:

    def get_action_queryset(self, request, queryset):
        result = queryset
        if request.POST.get('for_all_rows'):
            cl = self.get_changelist_instance(request)
            result = cl.get_queryset(request)
        return result

    __excel_methods = {
        'nonetype': '',
        'str': 'write_string',
        'int': 'write_number',
        'float': 'write_number',
        'date': 'write_date',
        'datetime': 'write_datetime',
    }

    def _slice_excess_fields(self, fields_list, query_first):
        result = []
        for field in fields_list:
            if all([
                hasattr(self.model, field) and isinstance(getattr(self.model, field), (
                        ManyToManyDescriptor,
                        ReverseManyToOneDescriptor,
                        ReverseOneToOneDescriptor
                )),
                not hasattr(query_first, field),
                not hasattr(self, field)
            ]):
                pass
            else:
                result.append(field)
        return result

    def _get_value(self, row, attr):
        value = None
        if hasattr(self, attr):
            value = getattr(self, attr)(row)
        elif hasattr(row, attr):
            value = getattr(row, attr)
        if type(value) not in [int, float, date, datetime, None]:
            value = str(value)
        return value

    def get_fields(self, request):
        return [field[0] for field in self.export_fields] if hasattr(self, 'export_fields') else [f.name for f in self.model._meta.fields]


class ExportExcelMixinUp(ConvertExportData, BaseUp):

    date_format = None
    int_format = None
    float_format = None

    def _format(self, value):
        print(value, type(value))
        result = None
        if isinstance(value, int):
            result = self.int_format
        elif isinstance(value, float):
            result = self.float_format
        elif isinstance(value, (date, datetime)):
            result = self.date_format
        return result

    def _format_cell(self, value):
        result = value,
        if isinstance(value, (date, datetime)):
            return value.strftime('%Y-%m-%d')
        return result

    def save_as_excel(self, request, queryset):
        filename = str(queryset.model.__name__).lower()
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'remove_timezone': True})
        self.date_format = wb.add_format({'num_format': 'yyyy-mm-dd'})
        self.int_format = wb.add_format({'num_format': '0'})
        self.float_format = wb.add_format({'num_format': '0.00'})
        ws = wb.add_worksheet()
        row_num = 0
        bold = wb.add_format({'bold': True})

        fields_for_save = self.get_fields(request)
        local_fields_for_save = self._slice_excess_fields(fields_for_save, queryset.first())

        for col_num in range(len(local_fields_for_save)):
            ws.write(row_num, col_num, fields_for_save[col_num].capitalize(), bold)
        queryset = self.get_action_queryset(request, queryset)
        for ind_row, row in enumerate(queryset):
            ind_row += 1
            for ind_col, attr in enumerate(local_fields_for_save):
                if ind_row == 1:
                    ws.set_column(row_num, ind_col, 20)
                value = self._get_value(row, attr)
                ws.write(ind_row, ind_col, value, self._format(value))

        wb.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/ms-excel')
        disposition = 'attachment; filename="%s.xlsx"' % str(filename)
        response['Content-Disposition'] = disposition
        return response


class ExportCSVMixinUp(ConvertExportData, BaseUp):

    def save_as_csv(self, request, queryset):
        # model = queryset.model
        fields_for_save = self.get_fields(request)
        # Get model name. user, group etc.
        filename = str(self.model.__name__).lower()
        # Not save field with relation (1-to-1, 1-to-M, M-to-M) to Excel file
        local_fields_for_save = self._slice_excess_fields(fields_for_save, queryset.first())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(
            filename
        )
        writer = csv.writer(response)
        writer.writerow([field[1] for field in self.export_fields or local_fields_for_save])
        queryset = self.get_action_queryset(request, queryset)
        for ind_row, row in enumerate(queryset):
            ind_row += 1
            row_data = []
            for attr in local_fields_for_save:
                row_data.append(self._get_value(row, attr))
            writer.writerow(row_data)
        return response

    save_as_csv.short_description = _('Сохранить в CSV файл')


class ExportCSVMixin:

    def save_as_csv(self, request, queryset):
        # model = queryset.model

        fields_for_save = self.fields_for_save if hasattr(self, 'fields_for_save') else [f.name for f in self.model._meta.fields]

        # Get model name. user, group etc.
        filename = str(self.model.__name__).lower()

        # Not save field with relation (1-to-1, 1-to-M, M-to-M) to Excel file
        local_fields_for_save = []
        for m in fields_for_save:
            if isinstance(getattr(self.model, m), ManyToManyDescriptor):
                pass
            elif isinstance(getattr(self.model, m), ReverseManyToOneDescriptor):
                pass
            elif isinstance(getattr(self.model, m), ReverseOneToOneDescriptor):
                pass
            else:
                local_fields_for_save.append(m)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(
            filename
        )
        writer = csv.writer(response)

        writer.writerow(local_fields_for_save)

        rows = queryset.values_list(*local_fields_for_save)

        for row in rows:
            writer.writerow(row)

        return response

    save_as_csv.short_description = _('Сохранить в CSV файл')


class ExportExcelMixin(ConvertExportData):
    def save_as_excel(self, request, queryset):
        model = queryset.model

        fields_for_save = self.fields_for_save if hasattr(self, 'fields_for_save') else [f.name for f in model._meta.fields]

        # Get model name. user, group etc.
        filename = str(model.__name__).lower()

        # Create stream of bytes
        output = BytesIO()

        # Excel file settings
        wb = xlsxwriter.Workbook(output, {'remove_timezone': True})
        ws = wb.add_worksheet()

        # Index of first row for writing
        row_num = 0

        # Create bold style
        bold = wb.add_format({'bold': True})

        # Not save field with relation (1-to-1, 1-to-M, M-to-M) to Excel file
        local_fields_for_save = []
        for m in fields_for_save:
            attr = getattr(model, m)
            if isinstance(attr, ManyToManyDescriptor):
                pass
            elif isinstance(attr, ReverseManyToOneDescriptor):
                pass
            elif isinstance(attr, ReverseOneToOneDescriptor):
                pass
            else:
                local_fields_for_save.append(m)

        # Write column names in row_num (first) row
        for col_num in range(len(local_fields_for_save)):
            ws.write(
                row_num,
                col_num,
                fields_for_save[col_num].capitalize(),
                bold
            )
            ws.set_column(row_num, col_num, 20)  # Set width of column

        rows = queryset.values_list(*local_fields_for_save)

        # write all rows
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, self.convert_field(row[col_num]))

        wb.close()

        output.seek(0)

        # response settings
        response = HttpResponse(output.read(), content_type='application/ms-excel')
        disposition = 'attachment; filename="%s.xlsx"' % str(filename)

        response['Content-Disposition'] = disposition

        # Return file to browser
        return response

    save_as_excel.short_description = _('Сохранить в Excel файл')


class GeneralExportMixin(ExportCSVMixin, ExportExcelMixin):
    pass


class BidExportExcelMixin(ExportExcelMixin):
    def save_as_excel(self, request, queryset):
        model = queryset.model

        if hasattr(self, 'fields_for_export'):
            fields_for_export = [ff[0] for ff in self.fields_for_export]
            fields_for_export_title = [ff[1] for ff in self.fields_for_export]
        else:
            fields_for_export = [f.name for f in model._meta.fields]
            fields_for_export_title = fields_for_export.copy()

        # Get model name. user, group etc.
        filename = str(model.__name__).lower()

        # Create stream of bytes
        output = BytesIO()

        # Excel file settings
        wb = xlsxwriter.Workbook(output, {'remove_timezone': True})
        ws = wb.add_worksheet()

        # Index of first row for writing
        row_num = 0

        # Create bold style
        bold = wb.add_format({'bold': True})

        # Not save field with relation (1-to-1, 1-to-M, M-to-M) to Excel file
        local_fields_for_save = []
        for m in fields_for_export:
            attr = getattr(model, m)
            if isinstance(attr, ManyToManyDescriptor):
                pass
            elif isinstance(attr, ReverseManyToOneDescriptor):
                pass
            elif isinstance(attr, ReverseOneToOneDescriptor):
                pass
            else:
                local_fields_for_save.append(m)

        # Write column names in row_num (first) row
        for col_num in range(len(local_fields_for_save)):
            ws.write(
                row_num,
                col_num,
                fields_for_export_title[col_num],
                bold
            )
            ws.set_column(row_num, col_num, 25)  # Set width of column

        # write all rows
        for obj in queryset:
            row_num += 1
            for col_num in range(len(local_fields_for_save)):
                ws.write(
                    row_num,
                    col_num,
                    self.convert_field(
                        getattr(obj, local_fields_for_save[col_num])
                    )
                )

        wb.close()

        output.seek(0)

        # response settings
        response = HttpResponse(output.read(), content_type='application/ms-excel')
        disposition = 'attachment; filename="%s.xlsx"' % str(filename)

        response['Content-Disposition'] = disposition

        # Return file to browser
        return response

    save_as_excel.short_description = _('Сохранить в Excel файл')


class ExportExcelODBMixin:  # just for odb, can't use in admin actions

    @staticmethod
    def convert_float(value):
        value = round(value, 2)
        if len(str(value).split('.')[1]) == 1:
            value = f'{value}0'
        return str(value)

    def convert_field(self, key, value):
        kopeiki = False
        if self.model.__name__ in ['ResultPercentODB', 'ResultCommissionODB']:
            kopeiki = True
            pass
        if 'date' in key:
            return value.split('T')[0].replace('-', '/')
        elif isinstance(value, (float, int,)):
            if kopeiki:
                value = value / 100
            return self.convert_float(value)
        else:
            return str(value)

    def save_as_excel(self, data_list):

        fields_for_save = [f for f in self.model.EXCEL_FIELDS]

        # Get model name. user, group etc.
        filename = str(self.model.__name__).lower()

        # Create stream of bytes
        output = BytesIO()

        # Excel file settings
        wb = xlsxwriter.Workbook(output, {'remove_timezone': True})
        ws = wb.add_worksheet()
        bold = wb.add_format({'bold': True})

        # Index of first row for writing
        row_num = 0

        # Create bold style
        bold = wb.add_format({'bold': True})

        # Write column names in row_num (first) row
        for col_num, field in enumerate(fields_for_save):
            ws.write(
                row_num,
                col_num,
                field[1],
                bold
            )
            ws.set_column(row_num, col_num, 20)  # Set width of column

        # write all rows
        for row_obj in data_list:
            row_num += 1
            format_col = bold if len(data_list) == row_num else None
            for col_num, key in enumerate(fields_for_save):
                ws.write(row_num, col_num, self.convert_field(key[0], getattr(row_obj, key[0])), format_col)
        wb.close()

        output.seek(0)

        # response settings
        response = HttpResponse(output.read(), content_type='application/ms-excel')
        disposition = f'attachment; filename="{filename}.xlsx"'

        response['Content-Disposition'] = disposition

        # Return file to browser
        return response