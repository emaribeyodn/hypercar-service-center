from collections import deque
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.views import View


tickets_queue = {
    'change_oil': deque(),
    'inflate_tires': deque(),
    'diagnostic': deque(),
    'ticket_number': 1,
    'next': 0
}
CHANGE_OIL_WAITING_MINUTE = 2
INFLATE_TIRES_WAITING_MINUTE = 5
DIAGNOSTIC_WAITING_MINUTE = 30

def time_to_wait(service_name):
    if service_name == 'change_oil':
        return len(tickets_queue['change_oil']) * CHANGE_OIL_WAITING_MINUTE
    elif service_name == 'inflate_tires':
        return len(tickets_queue['change_oil']) * CHANGE_OIL_WAITING_MINUTE + \
               len(tickets_queue['inflate_tires']) * INFLATE_TIRES_WAITING_MINUTE
    elif service_name == 'diagnostic':
        return len(tickets_queue['change_oil']) * CHANGE_OIL_WAITING_MINUTE + \
               len(tickets_queue['inflate_tires']) * INFLATE_TIRES_WAITING_MINUTE + \
               len(tickets_queue['diagnostic']) * DIAGNOSTIC_WAITING_MINUTE
    else:
        return 0

def remove_processed_ticket():
    if len(tickets_queue['change_oil']) > 0:
        return tickets_queue['change_oil'].popleft()
    elif len(tickets_queue['inflate_tires']) > 0:
        return tickets_queue['inflate_tires'].popleft()
    elif len(tickets_queue['diagnostic']) > 0:
        return tickets_queue['diagnostic'].popleft()
    else:
        return 0

def next_ticket_number():
    return tickets_queue['next']

# Create your views here.

class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        output = f"""
        <a href="/get_ticket/change_oil">Change oil</a><br />
        <a href="/get_ticket/inflate_tires">Inflate tires</a><br />
        <a href="/get_ticket/diagnostic">Get diagnostic test</a><br />
        """
        return HttpResponse(output)


class GetTicketView(View):
    def get(self, request, service_name, *args, **kwargs):
        if service_name not in ['change_oil', 'inflate_tires', 'diagnostic']:
            return Http404('Service not found')
        
        minute_to_wait = time_to_wait(service_name)
        ticket_number = tickets_queue['ticket_number']
        tickets_queue['ticket_number'] += 1
        tickets_queue[service_name].append(ticket_number)

        output = f"""
        <h2>Your number is {ticket_number}</h2>
        <h3>Please wait around {minute_to_wait} minutes</h3>
        """
        return HttpResponse(output)


class ProcessingView(View):
    def get(self, request, *args, **kwargs):
        change_oil_queue_size = len(tickets_queue['change_oil'])
        inflate_tires_queue_size = len(tickets_queue['inflate_tires'])
        diagnostic_queue_size = len(tickets_queue['diagnostic'])
        
        context = {
            'change_oil_queue_size': change_oil_queue_size,
            'inflate_tires_queue_size': inflate_tires_queue_size,
            'diagnostic_queue_size': diagnostic_queue_size,
        }
        return render(request, 'tickets/processing.html', context)

    def post(self, request, *args, **kwargs):
        tickets_queue['next'] = remove_processed_ticket()
        return redirect('/processing/')


class NextView(View):
    def get(self, request, *args, **kwargs):
        next_ticket = next_ticket_number()
        if next_ticket == 0:
            return HttpResponse("<div>Waiting for the next client</div>")
        else:
            return HttpResponse(f"<div>Ticket #{next_ticket}</div>")