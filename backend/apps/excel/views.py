from django.utils.timezone import make_aware, localtime
from django.http import HttpResponse
from openpyxl.styles import Font
from rest_framework import generics, status
from backend.apps.space.models import Space
from backend.apps.account.permissions import IsSpaceMember
from backend.apps.history.models import HistoryIncome, HistoryExpense
from rest_framework.response import Response
import openpyxl
from datetime import datetime
import pytz
from backend.apps.account.models import Account


class ExportHistoryView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def post(request, *args, **kwargs):
        highest_role = request.user.roles[0]
        if highest_role == 'free':
            return Response("Error: You are not allowed to export history data with a free role.", status=status.HTTP_403_FORBIDDEN)
        
        space = Space.objects.get(pk=kwargs['space_pk'])
        expenses = HistoryExpense.objects.filter(father_space=space)
        incomes = HistoryIncome.objects.filter(father_space=space)

        filters = request.data.get("filters", {})
        if "dates" in filters:
            tz = pytz.timezone('UTC')
            start_date = request.data.get("from_date")
            end_date = request.data.get("to_date")
            if start_date and end_date:
                start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'), tz)
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'), tz)
                expenses = expenses.filter(created__range=(start_date, end_date))
                incomes = incomes.filter(created__range=(start_date, end_date))

        if "accounts" in filters:
            account_ids = request.data.get("account_ids", [])
            if account_ids:
                expenses = expenses.filter(from_acc__id__in=account_ids)
                incomes = incomes.filter(account__id__in=account_ids)

        export_type = request.data.get("export_type", "both")

        if export_type == "expenses":
            incomes = []
        elif export_type == "incomes":
            expenses = []

        # Определяем заголовки
        default_headers = {
            'amount': 'Amount',
            'comment': 'Comment',
            'date': 'Date & Time',
            'account': 'Account',
            'category': 'Category'
        }

        # Если export_type == 'both', добавляем колонку 'type' в начало
        if export_type == "both":
            default_headers = {'type': 'Type', **default_headers}

        fields = request.data.get("fields", list(default_headers.keys()))
        headers = [default_headers[field] for field in fields if field in default_headers]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "History Data"

        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for expense in expenses:
            row = []
            for field in fields:
                try:
                    cat_title, cat_icon, history_type = expense.to_cat["title"], expense.to_cat["icon"], "expense"
                except TypeError:
                    cat_title, cat_icon, history_type = "", "", "loss"
                print(history_type)
                if field == 'type' and export_type == "both":
                    row.append(history_type)
                elif field == 'amount':
                    row.append(expense.amount)
                elif field == 'comment':
                    row.append(expense.comment or '')
                elif field == 'date':
                    row.append(localtime(expense.created).strftime('%d %b %Y @ %H:%M'))
                elif field == 'account':
                    row.append(expense.from_acc.get('title', '') if expense.from_acc else '')
                elif field == 'category':
                    row.append(expense.to_cat.get('title', '') if expense.to_cat else '')
            ws.append(row)

        for income in incomes:
            row = []
            for field in fields:
                if field == 'type' and export_type == "both":
                    row.append('income')
                elif field == 'amount':
                    row.append(income.amount)
                elif field == 'comment':
                    row.append(income.comment or '')
                elif field == 'date':
                    row.append(localtime(income.created).strftime('%d %b %Y @ %H:%M'))
                elif field == 'account':
                    row.append(income.account.get('title', '') if income.account else '')
                elif field == 'category':
                    row.append('')
            ws.append(row)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename="history_data.xlsx"'
        wb.save(response)
        return response


class ImportHistoryView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def post(request, *args, **kwargs):
        highest_role = request.user.roles[0]
        if highest_role == 'free':
            return Response("Error: You are not allowed to export history data with a free role.", status=status.HTTP_403_FORBIDDEN)
        
        space_id = kwargs.get("space_pk")
        try:
            father_space = Space.objects.get(pk=space_id)
        except Space.DoesNotExist:
            return Response(
                {"error": "Space with the given ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        uploaded_file = request.FILES.get("file")
        record_type = request.data.get("type")
        account_id = request.data.get("account_id")

        if not uploaded_file or not record_type or not account_id:
            return Response(
                {"error": "file, type, and account_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if record_type not in ["expense", "income"]:
            return Response(
                {"error": "Invalid type. Must be 'expense' or 'income'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = Account.objects.get(pk=account_id, father_space=father_space)
        except Account.DoesNotExist:
            return Response(
                {"error": "Account with the given ID does not exist or does not belong to this space."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Валидация файла: проверка, что это действительно Excel-файл
            wb = openpyxl.load_workbook(uploaded_file, read_only=True)
            ws = wb.active
            print(ws)
        except Exception as e:
            return Response(
                {"error": "Invalid file format. Please upload a valid Excel file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ws.max_row is None:
            pass
        elif ws.max_row < 2:
            return Response(
                {"error": "The file must contain at least one row of data."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Определяем индексы колонок для обязательных полей
        try:
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
        except StopIteration:
            return Response(
                {"error": "The file is empty or does not contain any data."},
                status=status.HTTP_400_BAD_REQUEST
            )
        column_indices = {
            'amount': None,
            'created': None
        }

        for idx, header in enumerate(header_row):
            if header and isinstance(header, str):
                header_lower = header.strip().lower()
                if header_lower == 'amount':
                    column_indices['amount'] = idx
                elif header_lower in ['date', 'created']:
                    column_indices['created'] = idx

        # Проверяем, что обязательные колонки найдены
        if column_indices['amount'] is None or column_indices['created'] is None:
            return Response(
                {"error": "The file must contain 'amount' and 'created' columns."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Импорт данных
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                amount = row[column_indices['amount']]
                created = row[column_indices['created']]
            except (IndexError, TypeError):
                return Response(
                    {"error": f"Invalid data format in row {row_idx}. Missing required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not amount or not created:
                return Response(
                    {"error": f"Missing required fields in row {row_idx}. 'amount' and 'created' are mandatory."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Преобразуем дату в формат datetime
                if isinstance(created, str):
                    created = make_aware(datetime.strptime(created, '%Y-%m-%d %H:%M:%S'))
                elif isinstance(created, datetime):
                    created = make_aware(created)
                else:
                    return Response(
                        {"error": f"Invalid date format in row {row_idx}. Expected 'YYYY-MM-DD HH:MM:SS' or datetime object."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"error": f"Invalid date format in row {row_idx}. Expected 'YYYY-MM-DD HH:MM:SS'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Создаем запись в базе данных
            if record_type == "expense":
                HistoryExpense.objects.create(
                    amount=amount,
                    currency=account.currency,
                    amount_in_default_currency=amount,
                    comment=row[column_indices.get('comment', -1)] or '',
                    from_acc={"id": account.id, "title": account.title, "balance": str(account.balance)},
                    father_space=father_space,
                    created=created
                )
            elif record_type == "income":
                HistoryIncome.objects.create(
                    amount=amount,
                    currency=account.currency,
                    amount_in_default_currency=amount,
                    comment=row[column_indices.get('comment', -1)] or '',
                    account={"id": account.id, "title": account.title, "balance": str(account.balance)},
                    father_space=father_space,
                    created=created
                )

        return Response({"message": "Import completed successfully."}, status=status.HTTP_200_OK)


class PreviewHistoryView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    @staticmethod
    def post(request, *args, **kwargs):
        space = Space.objects.get(pk=kwargs['space_pk'])
        expenses = HistoryExpense.objects.filter(father_space=space)
        incomes = HistoryIncome.objects.filter(father_space=space)

        filters = request.data.get("filters", {})
        if "dates" in filters:
            tz = pytz.timezone('UTC')
            start_date = request.data.get("from_date")
            end_date = request.data.get("to_date")
            if start_date and end_date:
                start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'), tz)
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'), tz)
                expenses = expenses.filter(created__range=(start_date, end_date))
                incomes = incomes.filter(created__range=(start_date, end_date))

        if "accounts" in filters:
            account_ids = request.data.get("account_ids", [])
            if account_ids:
                expenses = expenses.filter(from_acc__id__in=account_ids)
                incomes = incomes.filter(account__id__in=account_ids)

        preview_data = []

        for expense in expenses[:5]:
            preview_data.append({
                "type": "expense",
                "amount": float(expense.amount),
                "comment": expense.comment or "",
                "date": localtime(expense.created).strftime('%Y-%m-%d %H:%M:%S'),
                "account": expense.from_acc.title if expense.from_acc else "",
                "category": expense.to_cat.title if expense.to_cat else ""
            })

        for income in incomes[:5]:
            preview_data.append({
                "type": "income",
                "amount": float(income.amount),
                "comment": income.comment or "",
                "date": localtime(income.created).strftime('%Y-%m-%d %H:%M:%S'),
                "account": income.account.title if income.account else "",
                "category": ""
            })

        # Ограничиваем общий результат до 10 записей
        preview_data = preview_data[:10]

        return Response(preview_data, status=200)
