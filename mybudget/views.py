# -*- coding: utf-8 -*-
from string import split


from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db import transaction
from django.views.generic import UpdateView

from mybudget.lib import disposable_income

from apps.budget.forms import ExpensesForm, EnvelopesForm, ExpenseSelectForm
from apps.budget.models import Envelopes, Incomes, Accounts, Expenses, RegularMonthlyExpenses


def home(request):
    form = ExpensesForm(request.POST or None, initial={'envelope': '1'})
    envelopes = Envelopes.objects.all().order_by('cash', 'name')
    account = Accounts.objects.all().aggregate(total=Sum('current_amount'))
    if account['total'] is None:
        account_total = 0
    else:
        account_total = account['total']
    if form.is_valid():
        form.save()
        return redirect('/expenses/')
    return render(request, 'home.html',
                  {'form': form,
                  'envelopes': envelopes,
                  'account': account_total})


def dashboard(request):
    form = EnvelopesForm(request.POST or None, initial={'account': '1'})
    envelopes = Envelopes.objects.all().order_by('name', 'cash')
    income = Incomes.objects.all().aggregate(total=Sum('amount'))
    available_amount = disposable_income()
    if income['total'] is None:
        income_total = 0
    else:
        income_total = income['total']
    if form.is_valid():
        form.save()
        return redirect('/envelopes/')
    return render(request, 'dashboard.html',
                  {'form': form,
                  'envelopes': envelopes,
                  'income': income_total,
                  'available_amount': available_amount})


class EnvelopeUpdate(UpdateView):
    model = Envelopes
    success_url = '/envelopes/'
    template_name = 'envelopes/envelope_update.html'
    form_class = EnvelopesForm

    def post(self, request, pk):
        envelope = Envelopes.objects.get(pk=pk)
        form = EnvelopesForm(request.POST or None, instance=envelope)
        if form.is_valid():
            envelope.save()
            return redirect('/envelopes/')
        else:
            message = "Envelope didn't update, some problem occurred"
            return redirect('/envelopes/', message=message)


def expenses(request):
    all_expenses = Expenses.objects.all().order_by('-created_date', 'name')
    form = ExpenseSelectForm(request.POST or None)
    if form.is_valid():
        envelope = form.cleaned_data['envelope'].name
        return redirect('filtered_expenses', envelope=envelope)
    return render(request, 'expenses/expenses.html', {'expenses': all_expenses, 'form': form})


class ExpenseUpdate(UpdateView):
    model = Expenses
    success_url = '/expenses/'
    template_name = 'expenses/expense_update.html'
    form_class = ExpensesForm

    def post(self, request, pk):
        with transaction.atomic():
            expense = Expenses.objects.get(pk=pk)
            form = ExpensesForm(request.POST or None, instance=expense)
            envelope = Envelopes.objects.get(pk=expense.envelope_id)
            expense_amount = expense.amount
            envelope.current_amount = envelope.current_amount + expense_amount
            envelope.save()
            if envelope.cash is False:
                account = Accounts.objects.get(id=envelope.account.id)
                account.current_amount = account.current_amount + expense_amount
                account.save()
            if form.is_valid():
                form.save()
                return redirect('/expenses/')
            else:
                message = "Expense didn't update, some problem occurred"
                return redirect('/expenses/', message=message)


def expenses_by_envelope(request, envelope):
    selected_envelope = Envelopes.objects.get(name=envelope)
    filtered_expenses = Expenses.objects.all().filter(envelope=selected_envelope.id)
    sum_filtered_expenses = filtered_expenses.aggregate(total=Sum('amount'))
    return render(request, 'expenses/expenses_selected.html',
                  {'expenses': filtered_expenses, 'sum': sum_filtered_expenses})


def regular_expenses(request):
    all_regular_expenses = RegularMonthlyExpenses.objects.all()
    sum_regular_expenses = RegularMonthlyExpenses.objects.all().aggregate(total=Sum('amount'))
    return render(request, 'expenses/regular_expenses.html', {'expenses': all_regular_expenses, 'sum': sum_regular_expenses})