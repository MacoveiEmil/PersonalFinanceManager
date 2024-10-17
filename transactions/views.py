from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
import matplotlib.pyplot as plt
from django.http import HttpResponse,JsonResponse
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.db.models import Sum
from django.utils.timezone import now


def home(request):
    transactions = Transaction.objects.all()
    return render(request, 'transactions/index.html', {'transactions': transactions})

def add_transaction(request):
    if request.method == "POST":
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)
            description = data.get('description')
            amount = data.get('amount')
            date_str = data.get('date')

            # Parse the date to ensure it's in the correct format
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Validate the data
            if not (description and amount and date):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            # Save the transaction
            transaction = Transaction(description=description, amount=amount, date=date)
            transaction.save()

            # Return the new transaction data as JSON
            return JsonResponse({
                'description': transaction.description,
                'amount': transaction.amount,
                'date': transaction.date
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif request.method == "GET":
        # If the request is GET, render the form for adding transactions
        return render(request, 'add_transaction.html')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

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

def index(request):

    transactions = Transaction.objects.all()

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    # Filter transactions based on the provided dates
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    
    # Calculate spending_by_date
    spending_by_date = transactions.values('date').annotate(total_amount=Sum('amount')).order_by('date')

    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'spending_by_date': list(spending_by_date),  # Ensure this is serializable to JSON
            'transactions': list(transactions.values('description', 'amount', 'date'))  # Serialize transactions
        }
        return JsonResponse(data)

    # Render the index.html template with the spending data
    return render(request, 'index.html', {
        'spending_by_date': spending_by_date,
        'transactions' : transactions,
    })

def delete_transaction(request, id):
    if request.method == 'DELETE':
        try:
            transaction = Transaction.objects.get(id=id)
            transaction.delete()
            return JsonResponse({'message': 'Transaction deleted successfully!'}, status=204)
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found!'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)