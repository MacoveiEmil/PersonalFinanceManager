from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO

def home(request):
    transactions = Transaction.objects.all()
    return render(request, 'transactions/home.html', {'transactions': transactions})

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})

def report(request):
    transactions = Transaction.objects.all()
    categories = [t.category for t in transactions]
    amounts = [t.amount for t in transactions]

    # Create a pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Spending by Category')

    # Convert plot to PNG image
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf, content_type='image/png')