from django.shortcuts import render, get_object_or_404, redirect
from .models import Master, Client, Appointment
from .forms import BookingForm
from datetime import datetime, timedelta


def index(request):
    masters = Master.objects.all()

    # 1. Работа с датой
    date_param = request.GET.get('date')
    if date_param:
        try:
            target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.now().date()
    else:
        target_date = datetime.now().date()

    # Навигация
    today = datetime.now().date()
    if target_date < today: target_date = today  # Нельзя в прошлое

    prev_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)
    show_prev = target_date > today

    # 2. Логика расписания (Matrix) с ID записей
    # Используем словарь: {(id_мастера, час): объект_записи}
    occupied_map = {}

    appointments = Appointment.objects.filter(date=target_date)

    # Финансовый расчет
    total_income = 0

    for app in appointments:
        total_income += app.master.price  # Считаем деньги

        start_hour = app.time_slot.hour
        duration = app.master.duration

        # Заполняем карту занятости
        for i in range(duration):
            hour = start_hour + i
            if i == 0:
                # Если это первый час процедуры - сохраняем САМУ ЗАПИСЬ (чтобы был ID для удаления)
                occupied_map[(app.master.id, hour)] = app
            else:
                # Если это второй/третий час - просто помечаем как занятое (ID = None)
                occupied_map[(app.master.id, hour)] = 'busy_continuation'

    # Делим деньги
    admin_share = int(total_income * 0.40)
    masters_share = int(total_income * 0.60)

    # 3. Генерация таблицы
    current_hour = datetime.now().hour
    start_hour = 9
    if target_date == today:
        start_hour = max(9, current_hour + 1)

    schedule = []
    for hour in range(start_hour, 21):
        time_str = f"{hour:02d}:00"
        row = {'time': time_str, 'slots': []}

        for master in masters:
            # Получаем данные из карты: это может быть ОбъектЗаписи, Строка 'busy' или None
            slot_data = occupied_map.get((master.id, hour))

            is_taken = slot_data is not None
            appointment_obj = slot_data if isinstance(slot_data, Appointment) else None

            row['slots'].append({
                'master': master,
                'is_taken': is_taken,
                'appointment': appointment_obj,  # Передаем объект записи, если он есть
                'time_str': time_str,
                'date_str': target_date.strftime("%Y-%m-%d")
            })
        schedule.append(row)

    context = {
        'masters': masters,
        'schedule': schedule,
        'target_date': target_date,
        'next_date': next_date.strftime("%Y-%m-%d"),
        'prev_date': prev_date.strftime("%Y-%m-%d"),
        'show_prev': show_prev,
        'total_income': total_income,
        'admin_share': admin_share,
        'masters_share': masters_share,
    }
    return render(request, 'salon/index.html', context)


# --- ФУНКЦИЯ ОТМЕНЫ ---
def cancel_appointment(request, appointment_id):
    # Разрешаем удалять только Админу (Staff)
    if not request.user.is_staff:
        return redirect('index')

    app = get_object_or_404(Appointment, id=appointment_id)
    date_str = app.date.strftime("%Y-%m-%d")

    app.delete()  # Удаляем из базы

    # Возвращаемся на ту же дату
    return redirect(f'/?date={date_str}')


# --- ФУНКЦИЯ ЗАПИСИ (Без изменений) ---
def book(request, master_id, time_str, date_str):
    master = get_object_or_404(Master, id=master_id)
    booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            client, _ = Client.objects.get_or_create(phone=phone, defaults={'name': name})
            appointment_time = datetime.strptime(time_str, "%H:%M").time()

            # Проверка (упрощенная)
            if not Appointment.objects.filter(master=master, time_slot=appointment_time, date=booking_date).exists():
                Appointment.objects.create(master=master, client=client, time_slot=appointment_time, date=booking_date)

            return redirect(f'/?date={date_str}')
    else:
        form = BookingForm()

    return render(request, 'salon/book.html', {'master': master, 'time': time_str, 'date': booking_date, 'form': form})