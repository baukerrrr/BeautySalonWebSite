from django.db import models

class Master(models.Model):
    first_name = models.CharField("Имя", max_length = 25)
    last_name = models.CharField("Фамилия", max_length = 25)
    specialization = models.CharField("Специализация", max_length = 50)
    price = models.IntegerField("Цена (тг)", default=5000)
    duration = models.IntegerField("Длительность (часов)", default=1)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

class Client(models.Model):
    name = models.CharField("Имя клиента", max_length = 30)
    phone = models.CharField("Номер телефона", max_length = 30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

class Appointment(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name="Мастер")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    date = models.DateField("Дата")
    time_slot = models.TimeField("Время")

    def __str__(self):
        return f"{self.date} {self.time_slot} - {self.master}"

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"