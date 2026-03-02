
from django.db import models

class Кафедра(models.Model):
    название = models.CharField("Название кафедры", max_length=255)
    def __str__(self):
        return self.название

class Группа(models.Model):
    название = models.CharField("Название группы", max_length=50)
    def __str__(self):
        return self.название

class Дисциплина(models.Model):
    название = models.CharField("Название дисциплины", max_length=255)
    def __str__(self):
        return self.название

class Преподаватель(models.Model):
    фио = models.CharField("ФИО преподавателя", max_length=255)
    кафедра = models.ForeignKey(Кафедра, on_delete=models.CASCADE)
    def __str__(self):
        return self.фио

class ПроверкаЗнаний(models.Model):
    группа = models.ForeignKey(Группа, on_delete=models.CASCADE)
    профиль = models.CharField("Профиль подготовки", max_length=255)
    дисциплина = models.ForeignKey(Дисциплина, on_delete=models.CASCADE)
    преподаватель = models.ForeignKey(Преподаватель, on_delete=models.CASCADE)
    дата_проведения = models.DateField("Дата проведения")
    время_проведения = models.TimeField("Время проведения")
