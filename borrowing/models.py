from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from books.models import Book


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')

    def save(self, *args, **kwargs):
        if not self.pk and not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status == 'borrowed' and timezone.now().date() > self.due_date

    @property
    def days_remaining(self):
        if self.status != 'borrowed':
            return None
        return (self.due_date - timezone.now().date()).days

    def __str__(self):
        return f'{self.student.username} - {self.book.title} ({self.status})'

    class Meta:
        ordering = ['-borrow_date']
